from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import os
import shutil
import zipfile

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'  # 你的文件存储路径
ZIP_FOLDER = 'zip'  # ZIP 文件存储路径

# 确保文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(ZIP_FOLDER):
    os.makedirs(ZIP_FOLDER)

@app.route('/')
def index():
    path = request.args.get('path', '')
    current_path = os.path.join(UPLOAD_FOLDER, path)
    if not os.path.exists(current_path):
        flash('路径不存在')
        return render_template('index.html', error="路径不存在")
    
    # 计算上一级路径
    parent_path = os.path.dirname(path) if path else ''
    
    files = []
    folders = []
    for item in os.listdir(current_path):
        full_path = os.path.join(current_path, item)
        item_type = '文件' if os.path.isfile(full_path) else '文件夹'
        if item_type == '文件':
            files.append((item, item_type, os.path.join(path, item)))
        else:
            folders.append((item, item_type, os.path.join(path, item)))

    items = folders + files
    
    return render_template('index.html', items=items, current_path=path, parent_path=parent_path)

@app.route('/download/<filename>')
def download_file(filename):
    path = request.args.get('path', '')
    file_path = os.path.join(UPLOAD_FOLDER, path, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    path = request.form.get('path', '')
    full_path = os.path.join(UPLOAD_FOLDER, path, filename)
    if os.path.exists(full_path):
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            shutil.rmtree(full_path)
        flash(f'删除 {filename} 成功')
    else:
        flash(f'{filename} 不存在')
    return redirect(url_for('index', path=path))

@app.route('/upload', methods=['POST'])
def upload_file():
    path = request.form.get('path', '')
    file = request.files['file']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, path, file.filename))
        flash('文件上传成功')
    return redirect(url_for('index', path=path))

@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    path = request.form.get('path', '')
    files = request.files.getlist('files')
    for file in files:
        directory = os.path.join(UPLOAD_FOLDER, path, os.path.dirname(file.filename))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.save(os.path.join(UPLOAD_FOLDER, path, file.filename))
    flash('文件夹上传成功')
    return redirect(url_for('index', path=path))

@app.route('/create_folder', methods=['POST'])
def create_folder():
    path = request.form.get('path', '')
    folder_name = request.form.get('folder_name')
    new_folder_path = os.path.join(UPLOAD_FOLDER, path, folder_name)
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
        flash(f'文件夹 {folder_name} 创建成功')
    else:
        flash(f'文件夹 {folder_name} 已存在')
    return redirect(url_for('index', path=path))

@app.route('/create_file', methods=['POST'])
def create_file():
    path = request.form.get('path', '')
    file_name = request.form.get('file_name')
    new_file_path = os.path.join(UPLOAD_FOLDER, path, file_name)
    if not os.path.exists(new_file_path):
        with open(new_file_path, 'w') as f:
            f.write('')
        flash(f'文件 {file_name} 创建成功')
    else:
        flash(f'文件 {file_name} 已存在')
    return redirect(url_for('index', path=path))

@app.route('/open_folder/<foldername>')
def open_folder(foldername):
    return redirect(url_for('index', path=foldername))

@app.route('/download_folder/<foldername>')
def download_folder(foldername):
    path = request.args.get('path', '')
    folder_path = os.path.join(UPLOAD_FOLDER, path, foldername)
    
    if not os.path.exists(folder_path):
        flash('文件夹不存在')
        return redirect(url_for('index', path=path))
    
    zip_filename = foldername + '.zip'
    zip_path = os.path.join(ZIP_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, UPLOAD_FOLDER)
                zipf.write(file_path, arcname)

    return send_file(zip_path, as_attachment=True)

@app.route('/rename', methods=['POST'])
def rename():
    path = request.form.get('path', '')
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')
    old_path = os.path.join(UPLOAD_FOLDER, path, old_name)
    new_path = os.path.join(UPLOAD_FOLDER, path, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        flash(f'{old_name} 重命名为 {new_name} 成功')
    else:
        flash(f'{old_name} 不存在')
    return redirect(url_for('index', path=path))

if __name__ == '__main__':
    app.run(debug=True)
