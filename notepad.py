import flask
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename
import io
from datetime import datetime
import random

app = Flask(__name__, static_folder='static')

# Define the EMOJIS list
EMOJIS = ['😀', '😎', '🤔', '🥳', '🐱', '🐶', '🦄', '🌈', '🍕', '🚀', '🎨', '🎵', '🌺', '🍉', '🏖️', '🎮', '🚲', '📚', '🍿', '🧘']

# Database setup
def init_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    
    # Create the notes table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  is_voice BOOLEAN DEFAULT FALSE)''')
    
    # Check if emoji column exists, if not, add it
    c.execute("PRAGMA table_info(notes)")
    columns = [column[1] for column in c.fetchall()]
    if 'emoji' not in columns:
        c.execute("ALTER TABLE notes ADD COLUMN emoji TEXT")
    
    conn.commit()
    conn.close()

# Call init_db at the start of the application
init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    notes = c.fetchall()
    conn.close()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        emoji = random.choice(EMOJIS)
        conn = sqlite3.connect('notes.db')
        c = conn.cursor()
        c.execute("INSERT INTO notes (title, content, emoji) VALUES (?, ?, ?)", (title, content, emoji))
        conn.commit()
        conn.close()
        return '', 204  # Return no content, but a successful status code

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
        
        conn = sqlite3.connect('notes.db')
        c = conn.cursor()
        c.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?',
                     (title, content, id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    note = c.execute('SELECT * FROM notes WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    return render_template('edit.html', note=note)

UPLOAD_FOLDER = 'static/audio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_voice', methods=['POST'])
def add_voice_note():
    if 'audio' not in request.files:
        return 'No audio file', 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return 'No selected file', 400
    
    if audio_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(f"voice_note_{timestamp}.wav")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        audio_file.save(file_path)
        
        emoji = random.choice(EMOJIS)
        conn = sqlite3.connect('notes.db')
        c = conn.cursor()
        c.execute("INSERT INTO notes (title, content, is_voice, emoji) VALUES (?, ?, ?, ?)", 
                  (f"Voice Note {timestamp}", filename, True, emoji))
        conn.commit()
        conn.close()
        return '', 204  # Return no content, but a successful status code
    
    return 'Failed to save audio', 400

if __name__ == '__main__':
    app.run(debug=True)
