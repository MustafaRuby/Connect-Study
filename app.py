from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sql')
DB_FILE = os.path.join(os.path.dirname(__file__), 'connectstudy.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Inizializzazione DB se non esiste
if not os.path.exists(DB_FILE):
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = sqlite3.connect(DB_FILE)
    conn.executescript(sql)
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    materie = conn.execute('SELECT * FROM materie ORDER BY ordinamento ASC').fetchall()
    conn.close()
    return render_template('index.html', materie=materie)

@app.route('/add_materia', methods=['POST'])
def add_materia():
    nome = request.form['nome']
    colore = request.form.get('colore', '#cccccc')
    conn = get_db_connection()
    max_ord = conn.execute('SELECT COALESCE(MAX(ordinamento), 0) FROM materie').fetchone()[0]
    conn.execute('INSERT INTO materie (nome, colore, ordinamento) VALUES (?, ?, ?)', (nome, colore, max_ord+1))
    conn.commit()
    conn.close()
    socketio.emit('update_materie')
    return ('', 204)

@app.route('/edit_materia/<int:id>', methods=['POST'])
def edit_materia(id):
    nome = request.form['nome']
    colore = request.form.get('colore', '#cccccc')
    conn = get_db_connection()
    conn.execute('UPDATE materie SET nome = ?, colore = ? WHERE id = ?', (nome, colore, id))
    conn.commit()
    conn.close()
    socketio.emit('update_materie')
    return ('', 204)

@app.route('/delete_materia/<int:id>', methods=['DELETE'])
def delete_materia(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM materie WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    socketio.emit('update_materie')
    return ('', 204)

@socketio.on('reorder_materie')
def reorder_materie(data):
    # data: lista di id materie nell'ordine nuovo
    conn = get_db_connection()
    for idx, id_materia in enumerate(data['order']):
        conn.execute('UPDATE materie SET ordinamento = ? WHERE id = ?', (idx, id_materia))
    conn.commit()
    conn.close()
    emit('update_materie', broadcast=True)

@app.route('/api/materie')
def api_materie():
    conn = get_db_connection()
    materie = conn.execute('SELECT * FROM materie ORDER BY ordinamento ASC').fetchall()
    conn.close()
    return jsonify([dict(m) for m in materie])

if __name__ == '__main__':
    socketio.run(app, debug=True)
