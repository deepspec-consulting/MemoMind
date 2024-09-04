import flask
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
import io

app = Flask(__name__, static_folder='static')

# Database setup
def init_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  is_voice BOOLEAN DEFAULT FALSE)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    notes = c.fetchall()
    conn.close()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn = sqlite3.connect('notes.db')
        c = conn.cursor()
        c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        c.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    c.execute("SELECT * FROM notes WHERE id = ?", (id,))
    note = c.fetchone()
    conn.close()
    return render_template('edit.html', note=note)

@app.route('/delete/<int:id>')
def delete_note(id):
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_note(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        conn = get_db_connection()
        conn.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?',
                     (title, content, id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    return render_template('edit.html', note=note)

UPLOAD_FOLDER = 'static/audio'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_voice', methods=['GET', 'POST'])
def add_voice_note():
    if request.method == 'POST':
        title = request.form['title']
        audio_file = request.files['audio']
        
        if audio_file:
            filename = secure_filename(f"{title}.wav")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(file_path)
            
            conn = sqlite3.connect('notes.db')
            c = conn.cursor()
            c.execute("INSERT INTO notes (title, content, is_voice) VALUES (?, ?, ?)", 
                      (title, file_path, True))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add_voice.html')

if __name__ == '__main__':
    app.run(debug=True)
