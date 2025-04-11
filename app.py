from flask import Flask, render_template, request, redirect, session, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'sikapi_secret_key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    with sqlite3.connect("db/database.db") as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS kinerja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            tugas TEXT,
            capaian TEXT,
            filename TEXT,
            status TEXT)""")
        conn.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1, 'admin', 'admin', 'admin')")
        conn.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (2, 'pegawai', 'pegawai', 'pegawai')")

init_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect("db/database.db") as conn:
            user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd)).fetchone()
        if user:
            session['user'] = user[1]
            session['role'] = user[3]
            return redirect('/dashboard')
        else:
            return "Login gagal"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    role = session['role']
    with sqlite3.connect("db/database.db") as conn:
        data = conn.execute("SELECT * FROM kinerja").fetchall()
    if role == 'admin':
        return render_template('dashboard_admin.html', data=data)
    else:
        return render_template('dashboard_pegawai.html', data=data)

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nama = session['user']
        tugas = request.form['tugas']
        capaian = request.form['capaian']
        file = request.files['file']
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with sqlite3.connect("db/database.db") as conn:
            conn.execute("INSERT INTO kinerja (nama, tugas, capaian, filename, status) VALUES (?, ?, ?, ?, ?)",
                         (nama, tugas, capaian, filename, "Menunggu"))
        return redirect('/dashboard')
    return render_template('tambah_kinerja.html')

@app.route('/approve/<int:id>/<string:status>')
def approve(id, status):
    with sqlite3.connect("db/database.db") as conn:
        conn.execute("UPDATE kinerja SET status=? WHERE id=?", (status, id))
    return redirect('/dashboard')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
