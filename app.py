from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
import uuid
from datetime import datetime
from docx import Document
import PyPDF2
import markdown
from werkzeug.utils import secure_filename
import db_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def convert_docx_to_markdown(file_path):
    """Converte un file .docx in markdown con formattazione avanzata"""
    try:
        doc = Document(file_path)
        
        # Prima passata: analizza tutte le dimensioni dei font per creare una mappa dei livelli
        font_sizes = analyze_font_sizes(doc)
        
        markdown_content = []
        
        for paragraph in doc.paragraphs:
            if not paragraph.text.strip():
                markdown_content.append('')
                continue
                
            # Gestione dei titoli basata sullo stile
            if paragraph.style.name.startswith('Heading'):
                level = int(paragraph.style.name[-1]) if paragraph.style.name[-1].isdigit() else 1
                markdown_content.append('#' * level + ' ' + paragraph.text.strip())
                markdown_content.append('')
                continue
              # Gestione delle liste
            if paragraph.style.name.startswith('List'):
                if 'Bullet' in paragraph.style.name:
                    markdown_content.append('- ' + process_paragraph_formatting(paragraph, font_sizes))
                else:
                    # Per le liste numerate, controlla se è davvero una lista o un titolo
                    formatted_text = process_paragraph_formatting(paragraph, font_sizes)
                    if formatted_text.strip().startswith('#'):
                        # È un titolo, non una lista
                        markdown_content.append(formatted_text)
                    else:
                        # È una vera lista numerata
                        markdown_content.append('1. ' + formatted_text)
                continue
            
            # Gestione dei paragrafi normali con formattazione
            formatted_text = process_paragraph_formatting(paragraph, font_sizes)
            if formatted_text.strip():
                markdown_content.append(formatted_text)
                markdown_content.append('')
        
        # Gestione delle tabelle
        for table in doc.tables:
            markdown_content.append(convert_table_to_markdown(table))
            markdown_content.append('')
        
        return '\n'.join(markdown_content).strip()
    except Exception as e:
        return f"Errore nella conversione del file Word: {str(e)}"

def analyze_font_sizes(doc):
    """Analizza tutte le dimensioni dei font nel documento per creare una mappa dei livelli"""
    font_sizes = set()
    
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if run.font.size and run.font.size.pt:
                font_sizes.add(run.font.size.pt)
    
    # Ordina le dimensioni in ordine decrescente
    sorted_sizes = sorted(font_sizes, reverse=True)
    
    # Crea una mappa: dimensione -> livello di titolo
    size_to_level = {}
    
    if len(sorted_sizes) <= 1:
        # Se c'è solo una dimensione o nessuna, non creare titoli automatici
        return size_to_level
    
    # Assegna livelli solo se ci sono significative differenze di dimensione
    for i, size in enumerate(sorted_sizes):
        if i == 0:
            # La dimensione più grande diventa h1 solo se significativamente più grande
            if len(sorted_sizes) > 1 and size - sorted_sizes[1] >= 4:
                size_to_level[size] = 1
        elif i == 1:
            # La seconda più grande diventa h2 solo se significativamente più grande del testo normale
            if len(sorted_sizes) > 2 and size - sorted_sizes[-1] >= 2:
                size_to_level[size] = 2
        elif i == 2:
            # La terza più grande diventa h3 solo se significativamente più grande del testo normale
            if size - sorted_sizes[-1] >= 1:
                size_to_level[size] = 3
    
    return size_to_level

def process_paragraph_formatting(paragraph, font_sizes_map):
    """Processa la formattazione di un paragrafo"""
    result = []
    paragraph_has_heading = False
    full_text = paragraph.text.strip()
    
    # Controlla se questo paragrafo è un titolo numerato (es: "1. Titolo", "2. Titolo")
    is_numbered_heading = is_numbered_title(full_text, font_sizes_map, paragraph)
    
    # Controlla se questo paragrafo dovrebbe essere un titolo basato sulla dimensione del font
    for run in paragraph.runs:
        if run.font.size and run.font.size.pt in font_sizes_map:
            level = font_sizes_map[run.font.size.pt]
            # Se questo run ha una dimensione che corrisponde a un titolo
            if not paragraph_has_heading:
                if is_numbered_heading:
                    # Per titoli numerati, usa il formato: ## 1. Titolo
                    result.append('#' * level + ' ')
                else:
                    result.append('#' * level + ' ')
                paragraph_has_heading = True
            break
    
    for run in paragraph.runs:
        text = run.text
        if not text:
            continue
            
        # Applica formattazione basata sulle proprietà del run
        formatted_text = apply_run_formatting(run, text, font_sizes_map, paragraph_has_heading)
        result.append(formatted_text)
    
    return ''.join(result)

def is_numbered_title(text, font_sizes_map, paragraph):
    """Determina se un paragrafo è un titolo numerato"""
    # Controlla se inizia con un numero seguito da punto e spazio
    import re
    
    # Pattern per titoli numerati: "1. ", "2. ", "3.1 ", etc.
    numbered_pattern = r'^\d+(\.\d+)*\.\s+'
    
    if re.match(numbered_pattern, text):
        # Controlla se ha una dimensione di font che indica un titolo
        for run in paragraph.runs:
            if run.font.size and run.font.size.pt in font_sizes_map:
                return True
        
        # Anche se non ha font size specifico, se il testo è corto e sembra un titolo
        remaining_text = re.sub(numbered_pattern, '', text).strip()
        if len(remaining_text) < 100 and len(remaining_text.split()) <= 15:
            return True
    
    return False

def apply_run_formatting(run, text, font_sizes_map, is_heading_paragraph):
    """Applica la formattazione markdown basata sulle proprietà del run"""
    if not text.strip():
        return text
    
    formatted = text
    
    # Non applicare formattazione di titolo se siamo già in un paragrafo di titolo
    # o se la dimensione del font non è significativamente diversa
    apply_font_size_formatting = not is_heading_paragraph
    
    # Grassetto
    if run.bold:
        formatted = f"**{formatted}**"
    
    # Corsivo
    if run.italic:
        formatted = f"*{formatted}*"
    
    # Sottolineato (usando HTML per compatibilità)
    if run.underline:
        formatted = f"<u>{formatted}</u>"
    
    # Barrato
    if getattr(run.font, 'strike', False):
        formatted = f"~~{formatted}~~"
    
    # Apice (superscript)
    if run.font.superscript:
        formatted = f"<sup>{formatted}</sup>"
    
    # Pedice (subscript)
    if run.font.subscript:
        formatted = f"<sub>{formatted}</sub>"
    
    # Colore del testo (se diverso dal nero)
    if run.font.color.rgb and run.font.color.rgb != (0, 0, 0):
        rgb = run.font.color.rgb
        color_hex = f"#{rgb.red:02x}{rgb.green:02x}{rgb.blue:02x}"
        formatted = f'<span style="color: {color_hex};">{formatted}</span>'
    
    # Dimensione del font - ora gestita in modo intelligente
    if apply_font_size_formatting and run.font.size and run.font.size.pt:
        size = run.font.size.pt
        # Solo per testo molto piccolo, usa <small>
        if size < 9:
            formatted = f"<small>{formatted}</small>"
        # Non applicare più automaticamente ### per dimensioni medie
    
    # Evidenziazione (highlight)
    if run.font.highlight_color and run.font.highlight_color != 0:
        formatted = f"=={formatted}=="
    
    # Font famiglia (se diversa dalla standard)
    if run.font.name and run.font.name.lower() in ['courier new', 'consolas', 'monaco', 'monospace']:
        formatted = f"`{formatted}`"
    
    return formatted

def convert_table_to_markdown(table):
    """Converte una tabella Word in formato Markdown"""
    markdown_rows = []
    
    for i, row in enumerate(table.rows):
        cells = []
        for cell in row.cells:
            cell_text = cell.text.strip().replace('\n', ' ')
            cells.append(cell_text)
        
        # Riga della tabella
        markdown_rows.append('| ' + ' | '.join(cells) + ' |')
        
        # Separatore dopo la prima riga (header)
        if i == 0:
            separator = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
            markdown_rows.append(separator)
    
    return '\n'.join(markdown_rows)

def convert_pdf_to_markdown(file_path):
    """Converte un file .pdf in markdown con miglior gestione del testo"""
    try:
        markdown_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    markdown_content.append(f"## Pagina {page_num + 1}")
                    markdown_content.append('')
                    
                    # Processamento del testo per migliorare la formattazione
                    processed_text = process_pdf_text(text)
                    markdown_content.append(processed_text)
                    markdown_content.append('')
        
        return '\n'.join(markdown_content).strip()
    except Exception as e:
        return f"Errore nella conversione del file PDF: {str(e)}"

def process_pdf_text(text):
    """Processa il testo estratto dal PDF per migliorare la formattazione"""
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Riconosce titoli numerati (es: "1. Introduzione", "2.1 Metodi")
        import re
        numbered_title_pattern = r'^\d+(\.\d+)*\.\s+\w+'
        if re.match(numbered_title_pattern, line) and len(line) < 100:
            # Determina il livello basandosi sulla numerazione
            number_part = re.match(r'^(\d+(\.\d+)*)', line).group(1)
            dots_count = number_part.count('.')
            level = min(dots_count + 1, 4)  # Massimo h4
            processed_lines.append('#' * level + ' ' + line)
            continue
            
        # Riconosce possibili titoli (linee più corte in maiuscolo)
        if len(line) < 60 and line.isupper() and len(line.split()) <= 6:
            processed_lines.append(f"### {line.title()}")
        # Riconosce possibili sottotitoli (iniziano con maiuscola e sono più corti)
        elif len(line) < 80 and line[0].isupper() and line.count('.') == 0 and len(line.split()) <= 10:
            # Controlla se potrebbe essere un titolo
            words = line.split()
            if all(word[0].isupper() for word in words if len(word) > 2):
                processed_lines.append(f"#### {line}")
            else:
                processed_lines.append(line)
        # Riconosce liste (iniziano con numero o simbolo) ma non titoli numerati
        elif line.startswith(('•', '-', '*', '◦')) or (line[0].isdigit() and line[1:3] in ['. ', ') '] and not re.match(numbered_title_pattern, line)):
            if not line.startswith(('- ', '* ')):
                if line.startswith(('•', '◦')):
                    line = '- ' + line[1:].strip()
                elif line[0].isdigit() and not re.match(numbered_title_pattern, line):
                    line = '1. ' + line[2:].strip()
            processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    return '\n\n'.join(processed_lines)

def convert_file_to_markdown(file_path, filename):
    """Converte un file in markdown basandosi sulla sua estensione"""
    ext = filename.lower().split('.')[-1]
    
    if ext == 'docx':
        return convert_docx_to_markdown(file_path)
    elif ext == 'doc':
        # Per i file .doc, prova prima a convertirli (richiede python-docx2txt)
        try:
            import docx2txt
            text = docx2txt.process(file_path)
            return f"# Documento convertito da {filename}\n\n{text}"
        except ImportError:
            return "Formato .doc non supportato. Installa docx2txt o converti in .docx"
    elif ext == 'pdf':
        return convert_pdf_to_markdown(file_path)
    elif ext in ['md', 'markdown']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                return f"Errore nella lettura del file Markdown: {str(e)}"
    elif ext == 'txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Converte il testo semplice in markdown basico
                return convert_txt_to_markdown(content, filename)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    return convert_txt_to_markdown(content, filename)
            except Exception as e:
                return f"Errore nella lettura del file di testo: {str(e)}"
    elif ext in ['rtf']:
        return "Formato RTF non ancora supportato. Converti in .docx o .txt"
    else:
        return f"Formato file .{ext} non supportato. Usa .docx, .pdf, .md, .txt"

def convert_txt_to_markdown(content, filename):
    """Converte un file di testo semplice in markdown con formattazione basica"""
    lines = content.split('\n')
    markdown_lines = [f"# {filename.replace('.txt', '')}", ""]
    
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        # Riga vuota - termina il paragrafo corrente
        if not line:
            if current_paragraph:
                markdown_lines.append(' '.join(current_paragraph))
                markdown_lines.append('')
                current_paragraph = []
            continue
        
        # Possibile titolo (riga corta, maiuscola, poche parole)
        if (len(line) < 50 and 
            line.isupper() and 
            len(line.split()) <= 6 and 
            not any(char in line for char in '.,;:!?')):
            if current_paragraph:
                markdown_lines.append(' '.join(current_paragraph))
                markdown_lines.append('')
                current_paragraph = []
            markdown_lines.append(f"## {line.title()}")
            markdown_lines.append('')
          # Lista numerata normale (non titolo)
        elif line.startswith(tuple(f"{i}." for i in range(1, 100))) and len(line.split()) > 10:
            if current_paragraph:
                markdown_lines.append(' '.join(current_paragraph))
                markdown_lines.append('')
                current_paragraph = []
            markdown_lines.append(line)
        
        # Titolo numerato (es: "1. Introduzione", "2. Metodologia")
        elif line.startswith(tuple(f"{i}." for i in range(1, 100))) and len(line.split()) <= 10:
            if current_paragraph:
                markdown_lines.append(' '.join(current_paragraph))
                markdown_lines.append('')
                current_paragraph = []
            # Determina il livello dal numero di punti nella numerazione
            import re
            number_match = re.match(r'^(\d+(\.\d+)*)', line)
            if number_match:
                number_part = number_match.group(1)
                level = min(number_part.count('.') + 2, 4)  # h2 minimo, h4 massimo
                markdown_lines.append('#' * level + ' ' + line)
            else:
                markdown_lines.append(f"## {line}")
            markdown_lines.append('')
        
        # Lista puntata
        elif line.startswith(('-', '*', '•')):
            if current_paragraph:
                markdown_lines.append(' '.join(current_paragraph))
                markdown_lines.append('')
                current_paragraph = []
            if not line.startswith('- '):
                line = '- ' + line[1:].strip()
            markdown_lines.append(line)
        
        # Testo normale
        else:
            current_paragraph.append(line)
    
    # Aggiungi l'ultimo paragrafo se presente
    if current_paragraph:
        markdown_lines.append(' '.join(current_paragraph))
    
    return '\n'.join(markdown_lines).strip()

# Inizializzazione DB se non esiste
db_manager.init_database()

@app.route('/')
def index():
    materie = db_manager.get_all_materie()
    return render_template('index.html', materie=materie)

@app.route('/add_materia', methods=['POST'])
def add_materia():
    nome = request.form['nome']
    colore = request.form.get('colore', '#cccccc')
    db_manager.add_materia(nome, colore)
    socketio.emit('update_materie')
    return ('', 204)

@app.route('/edit_materia/<int:id>', methods=['POST'])
def edit_materia(id):
    nome = request.form['nome']
    colore = request.form.get('colore', '#cccccc')
    db_manager.update_materia(id, nome, colore)
    socketio.emit('update_materie')
    return ('', 204)

@app.route('/delete_materia/<int:id>', methods=['DELETE'])
def delete_materia(id):
    db_manager.delete_materia(id)
    socketio.emit('update_materie')
    return ('', 204)

@socketio.on('reorder_materie')
def reorder_materie(data):
    # data: lista di id materie nell'ordine nuovo
    db_manager.reorder_materie(data['order'])
    emit('update_materie', broadcast=True)

@app.route('/api/materie')
def api_materie():
    materie = db_manager.get_all_materie()
    return jsonify([dict(m) for m in materie])

@app.route('/api/argomenti/materia/<int:id_materia>')
def api_argomenti_by_materia(id_materia):
    """API endpoint per ottenere argomenti di una materia specifica"""
    argomenti = db_manager.get_argomenti_by_materia(id_materia)
    return jsonify([dict(a) for a in argomenti])

@app.route('/materia/<int:id>')
def materia_argomenti(id):
    materia = db_manager.get_materia_by_id(id)
    if not materia:
        return "Materia non trovata", 404
    argomenti = db_manager.get_argomenti_by_materia(id)
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
    
    db_manager.add_argomento(id_materia, titolo, contenuto_md, colore, etichetta_preparazione)
    socketio.emit('update_argomenti', {'id_materia': id_materia})
    return ('', 204)

@app.route('/api/argomenti/<int:id_materia>')
def api_argomenti(id_materia):
    argomenti = db_manager.get_argomenti_by_materia(id_materia)
    return jsonify([dict(a) for a in argomenti])

# Route per il singolo argomento
@app.route('/argomento/<int:id>')
def argomento_dettaglio(id):
    argomento = db_manager.get_argomento_by_id(id)
    if not argomento:
        return "Argomento non trovato", 404
    
    materia = db_manager.get_materia_by_id(argomento['id_materia'])
    allegati = db_manager.get_allegati_by_argomento(id)
    
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
    
    # Aggiorna contenuto e etichetta
    etichetta_preparazione = request.form.get('etichetta_preparazione')
    if etichetta_preparazione:
        db_manager.update_argomento_content_and_label(id, contenuto_md, etichetta_preparazione)
    else:
        db_manager.update_argomento_content(id, contenuto_md)
    
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
        original_filename = secure_filename(file.filename)
        base_name, ext = os.path.splitext(original_filename)
        
        # Usa timestamp e UUID per garantire unicità
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{base_name}_{timestamp}_{unique_id}{ext}"
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
          # Salva nel database
        db_manager.add_allegato(id_argomento, filename, f'static/argomenti/{filename}')
        
        socketio.emit('update_allegati', {'id_argomento': id_argomento})
        return ('', 204)

# Route per eliminare allegati
@app.route('/delete_allegato/<int:id>', methods=['DELETE'])
def delete_allegato(id):
    allegato = db_manager.get_allegato_by_id(id)
    if allegato:
        # Rimuovi il file fisico
        file_path = os.path.join(os.path.dirname(__file__), allegato['percorso'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Rimuovi dal database
        db_manager.delete_allegato(id)
        id_argomento = allegato['id_argomento']
        
        socketio.emit('update_allegati', {'id_argomento': id_argomento})
        return ('', 204)
    
    return ('File non trovato', 404)

# Route per eliminare un argomento
@app.route('/delete_argomento/<int:id>', methods=['DELETE'])
def delete_argomento(id):
    argomento = db_manager.get_argomento_by_id(id)
    if not argomento:
        return 'Argomento non trovato', 404
    
    # Elimina tutti gli allegati associati
    allegati = db_manager.get_allegati_by_argomento(id)
    for allegato in allegati:
        file_path = os.path.join(os.path.dirname(__file__), allegato['percorso'])
        if os.path.exists(file_path):
            os.remove(file_path)
        db_manager.delete_allegato(allegato['id'])
    
    # Elimina l'argomento
    db_manager.delete_argomento(id)
    socketio.emit('update_argomenti', {'id_materia': argomento['id_materia']})
    return ('', 204)

# API per ottenere allegati di un argomento
@app.route('/api/allegati/<int:id_argomento>')
def api_allegati(id_argomento):
    allegati = db_manager.get_allegati_by_argomento(id_argomento)
    return jsonify([dict(a) for a in allegati])

# === COLLEGAMENTI ROUTES ===

@app.route('/collegamenti')
def collegamenti_list():
    """Pagina con tutti i collegamenti"""
    collegamenti = db_manager.get_all_collegamenti()
    materie = db_manager.get_all_materie()
    return render_template('collegamenti.html', collegamenti=collegamenti, materie=materie)

@app.route('/collegamenti/materia/<int:id_materia>')
def collegamenti_materia(id_materia):
    """Pagina con i collegamenti di una materia specifica"""
    materia = db_manager.get_materia_by_id(id_materia)
    if not materia:
        return "Materia non trovata", 404
    collegamenti = db_manager.get_collegamenti_by_materia(id_materia)
    materie = db_manager.get_all_materie()
    return render_template('collegamenti.html', collegamenti=collegamenti, materie=materie, 
                         materia_selezionata=materia)

@app.route('/collegamento/<int:id>')
def collegamento_dettaglio(id):
    """Pagina dettaglio di un collegamento"""
    collegamento = db_manager.get_collegamento_by_id(id)
    if not collegamento:
        return "Collegamento non trovato", 404
    return render_template('collegamento.html', collegamento=collegamento)

@app.route('/add_collegamento', methods=['POST'])
def add_collegamento():
    """Aggiunge un nuovo collegamento"""
    try:
        titolo = request.form['titolo']
        id_argomento1 = request.form['id_argomento1']
        id_argomento2 = request.form['id_argomento2']
        dettagli = request.form.get('dettagli', '')
        etichetta_qualita = request.form.get('etichetta_qualita', 'collegamento media qualità')
        
        # Verifica che gli argomenti siano diversi
        if id_argomento1 == id_argomento2:
            return jsonify({'success': False, 'error': 'Non puoi collegare un argomento a se stesso'})
        
        db_manager.add_collegamento(titolo, id_argomento1, id_argomento2, dettagli, etichetta_qualita)
        socketio.emit('update_collegamenti')
        return jsonify({'success': True, 'message': 'Collegamento creato con successo'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/update_collegamento/<int:id>', methods=['POST'])
def update_collegamento(id):
    """Aggiorna un collegamento esistente"""
    try:
        titolo = request.form['titolo']
        dettagli = request.form.get('dettagli', '')
        etichetta_qualita = request.form.get('etichetta_qualita', 'collegamento media qualità')
        
        db_manager.update_collegamento(id, titolo, dettagli, etichetta_qualita)
        socketio.emit('update_collegamenti')
        return jsonify({'success': True, 'message': 'Collegamento aggiornato con successo'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_collegamento/<int:id>', methods=['DELETE'])
def delete_collegamento(id):
    """Elimina un collegamento"""
    db_manager.delete_collegamento(id)
    socketio.emit('update_collegamenti')
    return ('', 204)

# API per ottenere collegamenti
@app.route('/api/collegamenti')
def api_collegamenti():
    """API per ottenere tutti i collegamenti"""
    collegamenti = db_manager.get_all_collegamenti()
    return jsonify([dict(c) for c in collegamenti])

@app.route('/api/collegamenti/materia/<int:id_materia>')
def api_collegamenti_materia(id_materia):
    """API per ottenere i collegamenti di una materia"""
    collegamenti = db_manager.get_collegamenti_by_materia(id_materia)
    return jsonify([dict(c) for c in collegamenti])

@app.route('/api/collegamenti/argomento/<int:id_argomento>')
def api_collegamenti_argomento(id_argomento):
    """API per ottenere i collegamenti di un argomento"""
    collegamenti = db_manager.get_collegamenti_by_argomento(id_argomento)
    return jsonify([dict(c) for c in collegamenti])

@app.route('/api/search_collegamenti')
def api_search_collegamenti():
    """API per cercare collegamenti"""
    query_titolo = request.args.get('titolo', '')
    query_dettagli = request.args.get('dettagli', '')
    etichetta_qualita = request.args.get('etichetta_qualita', '')
    
    collegamenti = db_manager.search_collegamenti(query_titolo, query_dettagli, etichetta_qualita)
    return jsonify([dict(c) for c in collegamenti])

if __name__ == '__main__':
    socketio.run(app, debug=True)
