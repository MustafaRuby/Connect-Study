from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import os
from docx import Document
import PyPDF2
import markdown
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sql')
DB_FILE = os.path.join(os.path.dirname(__file__), 'connectstudy.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def convert_docx_to_markdown(file_path):
    """Converte un file .docx in markdown"""
    try:
        doc = Document(file_path)
        markdown_content = []
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                # Gestione dei titoli basata sullo stile
                if paragraph.style.name.startswith('Heading'):
                    level = int(paragraph.style.name[-1]) if paragraph.style.name[-1].isdigit() else 1
                    markdown_content.append('#' * level + ' ' + text)
                else:
                    markdown_content.append(text)
                markdown_content.append('')  # Riga vuota tra i paragrafi
        
        return '\n'.join(markdown_content).strip()
    except Exception as e:
        return f"Errore nella conversione del file Word: {str(e)}"

def convert_pdf_to_markdown(file_path):
    """Converte un file .pdf in markdown"""
    try:
        markdown_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    markdown_content.append(f"## Pagina {page_num + 1}")
                    markdown_content.append(text.strip())
                    markdown_content.append('')
        
        return '\n'.join(markdown_content).strip()
    except Exception as e:
        return f"Errore nella conversione del file PDF: {str(e)}"

def convert_file_to_markdown(file_path, filename):
    """Converte un file in markdown basandosi sulla sua estensione"""
    ext = filename.lower().split('.')[-1]
    
    if ext == 'docx':
        return convert_docx_to_markdown(file_path)
    elif ext == 'pdf':
        return convert_pdf_to_markdown(file_path)
    elif ext == 'md':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Errore nella lettura del file Markdown: {str(e)}"
    else:
        return "Formato file non supportato. Usa .docx, .pdf o .md"

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

@app.route('/materia/<int:id>')
def materia_argomenti(id):
    conn = get_db_connection()
    materia = conn.execute('SELECT * FROM materie WHERE id = ?', (id,)).fetchone()
    if not materia:
        return "Materia non trovata", 404
    argomenti = conn.execute('SELECT * FROM argomenti WHERE id_materia = ? ORDER BY id ASC', (id,)).fetchall()
    conn.close()
    return render_template('argomenti.html', materia=materia, argomenti=argomenti)

@app.route('/add_argomento', methods=['POST'])
def add_argomento():
    id_materia = request.form['id_materia']
    titolo = request.form['titolo']
    contenuto_md = request.form.get('contenuto_md', '')
    colore = request.form.get('colore', '#cccccc')
    etichetta_preparazione = request.form.get('etichetta_preparazione', 'scarsa preparazione')
    
    # Gestione file caricato
    if 'file_content' in request.files:
        file = request.files['file_content']
        if file.filename != '' and file.filename is not None:
            # Salva temporaneamente il file
            filename = secure_filename(file.filename)
            temp_path = os.path.join(os.path.dirname(__file__), 'temp_' + filename)
            file.save(temp_path)
            
            try:
                # Converte il file in markdown
                file_markdown = convert_file_to_markdown(temp_path, filename)
                
                # Gestisce la modalità di inserimento
                file_mode = request.form.get('file_mode', 'replace')
                if file_mode == 'replace':
                    contenuto_md = file_markdown
                elif file_mode == 'prepend':
                    contenuto_md = file_markdown + '\n\n' + contenuto_md if contenuto_md else file_markdown
                elif file_mode == 'append':
                    contenuto_md = contenuto_md + '\n\n' + file_markdown if contenuto_md else file_markdown
                
            finally:
                # Rimuove il file temporaneo
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    conn = get_db_connection()
    conn.execute('INSERT INTO argomenti (id_materia, titolo, contenuto_md, colore, etichetta_preparazione) VALUES (?, ?, ?, ?, ?)', 
                (id_materia, titolo, contenuto_md, colore, etichetta_preparazione))
    conn.commit()
    conn.close()
    socketio.emit('update_argomenti', {'id_materia': id_materia})
    return ('', 204)

@app.route('/api/argomenti/<int:id_materia>')
def api_argomenti(id_materia):
    conn = get_db_connection()
    argomenti = conn.execute('SELECT * FROM argomenti WHERE id_materia = ? ORDER BY id ASC', (id_materia,)).fetchall()
    conn.close()
    return jsonify([dict(a) for a in argomenti])

# Route per il singolo argomento
@app.route('/argomento/<int:id>')
def argomento_dettaglio(id):
    conn = get_db_connection()
    argomento = conn.execute('SELECT * FROM argomenti WHERE id = ?', (id,)).fetchone()
    if not argomento:
        return "Argomento non trovato", 404
    
    materia = conn.execute('SELECT * FROM materie WHERE id = ?', (argomento['id_materia'],)).fetchone()
    allegati = conn.execute('SELECT * FROM allegati WHERE id_argomento = ? ORDER BY nome_file ASC', (id,)).fetchall()
    conn.close()
    
    return render_template('argomento.html', argomento=argomento, materia=materia, allegati=allegati)

# Route per aggiornare il contenuto dell'argomento
@app.route('/update_argomento/<int:id>', methods=['POST'])
def update_argomento(id):
    contenuto_md = request.form.get('contenuto_md', '')
    
    # Gestione file caricato per aggiornamento
    if 'file_content' in request.files:
        file = request.files['file_content']
        if file.filename != '' and file.filename is not None:
            filename = secure_filename(file.filename)
            temp_path = os.path.join(os.path.dirname(__file__), 'temp_' + filename)
            file.save(temp_path)
            
            try:
                file_markdown = convert_file_to_markdown(temp_path, filename)
                
                file_mode = request.form.get('file_mode', 'replace')
                if file_mode == 'replace':
                    contenuto_md = file_markdown
                elif file_mode == 'prepend':
                    contenuto_md = file_markdown + '\n\n' + contenuto_md if contenuto_md else file_markdown
                elif file_mode == 'append':
                    contenuto_md = contenuto_md + '\n\n' + file_markdown if contenuto_md else file_markdown
                
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    conn = get_db_connection()
    conn.execute('UPDATE argomenti SET contenuto_md = ? WHERE id = ?', (contenuto_md, id))
    conn.commit()
    conn.close()
    
    socketio.emit('update_argomento', {'id': id})
    return ('', 204)

# Route per caricare allegati
@app.route('/add_allegato/<int:id_argomento>', methods=['POST'])
def add_allegato(id_argomento):
    if 'file' not in request.files:
        return 'Nessun file caricato', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'Nessun file selezionato', 400
    
    if file:
        # Crea la directory se non esiste
        upload_dir = os.path.join(app.static_folder, 'argomenti')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Genera un nome file sicuro e univoco
        filename = secure_filename(file.filename)
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(upload_dir, filename)):
            filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Salva nel database
        conn = get_db_connection()
        conn.execute('INSERT INTO allegati (id_argomento, nome_file, percorso_file) VALUES (?, ?, ?)', 
                    (id_argomento, filename, f'static/argomenti/{filename}'))
        conn.commit()
        conn.close()
        
        socketio.emit('update_allegati', {'id_argomento': id_argomento})
        return ('', 204)

# Route per eliminare allegati
@app.route('/delete_allegato/<int:id>', methods=['DELETE'])
def delete_allegato(id):
    conn = get_db_connection()
    allegato = conn.execute('SELECT * FROM allegati WHERE id = ?', (id,)).fetchone()
    if allegato:
        # Rimuovi il file fisico
        file_path = os.path.join(os.path.dirname(__file__), allegato['percorso_file'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Rimuovi dal database
        conn.execute('DELETE FROM allegati WHERE id = ?', (id,))
        conn.commit()
        id_argomento = allegato['id_argomento']
        socketio.emit('update_allegati', {'id_argomento': id_argomento})
    
    conn.close()
    return ('', 204)

# API per ottenere allegati di un argomento
@app.route('/api/allegati/<int:id_argomento>')
def api_allegati(id_argomento):
    conn = get_db_connection()
    allegati = conn.execute('SELECT * FROM allegati WHERE id_argomento = ? ORDER BY nome_file ASC', (id_argomento,)).fetchall()
    conn.close()
    return jsonify([dict(a) for a in allegati])

if __name__ == '__main__':
    socketio.run(app, debug=True)
