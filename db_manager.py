import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sql')
DB_FILE = os.path.join(os.path.dirname(__file__), 'connectstudy.db')

def get_db_connection():
    """Ottiene una connessione al database SQLite"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inizializza il database se non esiste"""
    if not os.path.exists(DB_FILE):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            sql = f.read()
        conn = sqlite3.connect(DB_FILE)
        conn.executescript(sql)
        conn.close()

# === MATERIE OPERATIONS ===

def get_all_materie():
    """Ottiene tutte le materie ordinate per ordinamento"""
    conn = get_db_connection()
    materie = conn.execute('SELECT * FROM materie ORDER BY ordinamento ASC').fetchall()
    conn.close()
    return materie

def add_materia(nome, colore='#cccccc'):
    """Aggiunge una nuova materia"""
    conn = get_db_connection()
    max_ord = conn.execute('SELECT COALESCE(MAX(ordinamento), 0) FROM materie').fetchone()[0]
    conn.execute('INSERT INTO materie (nome, colore, ordinamento) VALUES (?, ?, ?)', (nome, colore, max_ord+1))
    conn.commit()
    conn.close()

def update_materia(id, nome, colore='#cccccc'):
    """Aggiorna una materia esistente"""
    conn = get_db_connection()
    conn.execute('UPDATE materie SET nome = ?, colore = ? WHERE id = ?', (nome, colore, id))
    conn.commit()
    conn.close()

def delete_materia(id):
    """Elimina una materia"""
    conn = get_db_connection()
    conn.execute('DELETE FROM materie WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def reorder_materie(order_list):
    """Riordina le materie secondo la lista fornita"""
    conn = get_db_connection()
    for idx, id_materia in enumerate(order_list):
        conn.execute('UPDATE materie SET ordinamento = ? WHERE id = ?', (idx, id_materia))
    conn.commit()
    conn.close()

def get_materia_by_id(id):
    """Ottiene una materia per ID"""
    conn = get_db_connection()
    materia = conn.execute('SELECT * FROM materie WHERE id = ?', (id,)).fetchone()
    conn.close()
    return materia

# === ARGOMENTI OPERATIONS ===

def get_argomenti_by_materia(id_materia):
    """Ottiene tutti gli argomenti di una materia"""
    conn = get_db_connection()
    argomenti = conn.execute('SELECT * FROM argomenti WHERE id_materia = ? ORDER BY id ASC', (id_materia,)).fetchall()
    conn.close()
    return argomenti

def add_argomento(id_materia, titolo, contenuto_md='', colore='#cccccc', etichetta_preparazione='scarsa preparazione'):
    """Aggiunge un nuovo argomento"""
    conn = get_db_connection()
    conn.execute('INSERT INTO argomenti (id_materia, titolo, contenuto_md, colore, etichetta_preparazione) VALUES (?, ?, ?, ?, ?)', 
                (id_materia, titolo, contenuto_md, colore, etichetta_preparazione))
    conn.commit()
    conn.close()

def get_argomento_by_id(id):
    """Ottiene un argomento per ID"""
    conn = get_db_connection()
    argomento = conn.execute('SELECT * FROM argomenti WHERE id = ?', (id,)).fetchone()
    conn.close()
    return argomento

def update_argomento_content(id, contenuto_md):
    """Aggiorna il contenuto markdown di un argomento"""
    conn = get_db_connection()
    conn.execute('UPDATE argomenti SET contenuto_md = ? WHERE id = ?', (contenuto_md, id))
    conn.commit()
    conn.close()

def update_argomento_content_and_label(id, contenuto_md, etichetta_preparazione):
    """Aggiorna il contenuto markdown e l'etichetta di preparazione di un argomento"""
    conn = get_db_connection()
    conn.execute('UPDATE argomenti SET contenuto_md = ?, etichetta_preparazione = ? WHERE id = ?', 
                (contenuto_md, etichetta_preparazione, id))
    conn.commit()
    conn.close()

def delete_argomento(id):
    """Elimina un argomento"""
    conn = get_db_connection()
    conn.execute('DELETE FROM argomenti WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# === ALLEGATI OPERATIONS ===

def get_allegati_by_argomento(id_argomento):
    """Ottiene tutti gli allegati di un argomento"""
    conn = get_db_connection()
    allegati = conn.execute('SELECT * FROM allegati WHERE id_argomento = ? ORDER BY nome_file ASC', (id_argomento,)).fetchall()
    conn.close()
    return allegati

def add_allegato(id_argomento, nome_file, percorso):
    """Aggiunge un nuovo allegato"""
    conn = get_db_connection()
    conn.execute('INSERT INTO allegati (id_argomento, nome_file, percorso) VALUES (?, ?, ?)', 
                (id_argomento, nome_file, percorso))
    conn.commit()
    conn.close()

def get_allegato_by_id(id):
    """Ottiene un allegato per ID"""
    conn = get_db_connection()
    allegato = conn.execute('SELECT * FROM allegati WHERE id = ?', (id,)).fetchone()
    conn.close()
    return allegato

def delete_allegato(id):
    """Elimina un allegato dal database"""
    conn = get_db_connection()
    conn.execute('DELETE FROM allegati WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# === COLLEGAMENTI OPERATIONS ===

def get_all_collegamenti():
    """Ottiene tutti i collegamenti con i dettagli degli argomenti"""
    conn = get_db_connection()
    collegamenti = conn.execute('''
        SELECT c.*, 
               a1.titolo as argomento1_titolo, a1.id_materia as argomento1_materia,
               a2.titolo as argomento2_titolo, a2.id_materia as argomento2_materia,
               m1.nome as materia1_nome, m1.colore as materia1_colore,
               m2.nome as materia2_nome, m2.colore as materia2_colore
        FROM collegamenti c
        JOIN argomenti a1 ON c.id_argomento1 = a1.id
        JOIN argomenti a2 ON c.id_argomento2 = a2.id
        JOIN materie m1 ON a1.id_materia = m1.id
        JOIN materie m2 ON a2.id_materia = m2.id
        ORDER BY c.id DESC
    ''').fetchall()
    conn.close()
    return collegamenti

def get_collegamenti_by_materia(id_materia):
    """Ottiene tutti i collegamenti che coinvolgono argomenti di una materia"""
    conn = get_db_connection()
    collegamenti = conn.execute('''
        SELECT c.*, 
               a1.titolo as argomento1_titolo, a1.id_materia as argomento1_materia,
               a2.titolo as argomento2_titolo, a2.id_materia as argomento2_materia,
               m1.nome as materia1_nome, m1.colore as materia1_colore,
               m2.nome as materia2_nome, m2.colore as materia2_colore
        FROM collegamenti c
        JOIN argomenti a1 ON c.id_argomento1 = a1.id
        JOIN argomenti a2 ON c.id_argomento2 = a2.id
        JOIN materie m1 ON a1.id_materia = m1.id
        JOIN materie m2 ON a2.id_materia = m2.id
        WHERE a1.id_materia = ? OR a2.id_materia = ?
        ORDER BY c.id DESC
    ''', (id_materia, id_materia)).fetchall()
    conn.close()
    return collegamenti

def get_collegamenti_by_argomento(id_argomento):
    """Ottiene tutti i collegamenti che coinvolgono un argomento specifico"""
    conn = get_db_connection()
    collegamenti = conn.execute('''
        SELECT c.*, 
               a1.titolo as argomento1_titolo, a1.id_materia as argomento1_materia,
               a2.titolo as argomento2_titolo, a2.id_materia as argomento2_materia,
               m1.nome as materia1_nome, m1.colore as materia1_colore,
               m2.nome as materia2_nome, m2.colore as materia2_colore
        FROM collegamenti c
        JOIN argomenti a1 ON c.id_argomento1 = a1.id
        JOIN argomenti a2 ON c.id_argomento2 = a2.id
        JOIN materie m1 ON a1.id_materia = m1.id
        JOIN materie m2 ON a2.id_materia = m2.id
        WHERE c.id_argomento1 = ? OR c.id_argomento2 = ?
        ORDER BY c.id DESC
    ''', (id_argomento, id_argomento)).fetchall()
    conn.close()
    return collegamenti

def add_collegamento(titolo, id_argomento1, id_argomento2, dettagli='', etichetta_qualita='collegamento media qualità'):
    """Aggiunge un nuovo collegamento"""
    conn = get_db_connection()
    conn.execute('''INSERT INTO collegamenti (titolo, id_argomento1, id_argomento2, dettagli, etichetta_qualita) 
                    VALUES (?, ?, ?, ?, ?)''', 
                (titolo, id_argomento1, id_argomento2, dettagli, etichetta_qualita))
    conn.commit()
    conn.close()

def get_collegamento_by_id(id):
    """Ottiene un collegamento per ID con tutti i dettagli"""
    conn = get_db_connection()
    collegamento = conn.execute('''
        SELECT c.*, 
               a1.titolo as argomento1_titolo, a1.id_materia as argomento1_materia,
               a2.titolo as argomento2_titolo, a2.id_materia as argomento2_materia,
               m1.nome as materia1_nome, m1.colore as materia1_colore,
               m2.nome as materia2_nome, m2.colore as materia2_colore
        FROM collegamenti c
        JOIN argomenti a1 ON c.id_argomento1 = a1.id
        JOIN argomenti a2 ON c.id_argomento2 = a2.id
        JOIN materie m1 ON a1.id_materia = m1.id
        JOIN materie m2 ON a2.id_materia = m2.id
        WHERE c.id = ?
    ''', (id,)).fetchone()
    conn.close()
    return collegamento

def update_collegamento(id, titolo, dettagli, etichetta_qualita):
    """Aggiorna un collegamento esistente"""
    conn = get_db_connection()
    conn.execute('''UPDATE collegamenti SET titolo = ?, dettagli = ?, etichetta_qualita = ? 
                    WHERE id = ?''', (titolo, dettagli, etichetta_qualita, id))
    conn.commit()
    conn.close()

def delete_collegamento(id):
    """Elimina un collegamento"""
    conn = get_db_connection()
    conn.execute('DELETE FROM collegamenti WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def search_collegamenti(query_titolo='', query_dettagli='', etichetta_qualita=''):
    """Cerca collegamenti per titolo, dettagli e/o etichetta qualità"""
    conn = get_db_connection()
    
    where_conditions = []
    params = []
    
    if query_titolo:
        where_conditions.append('c.titolo LIKE ?')
        params.append(f'%{query_titolo}%')
    
    if query_dettagli:
        where_conditions.append('c.dettagli LIKE ?')
        params.append(f'%{query_dettagli}%')
    
    if etichetta_qualita:
        where_conditions.append('c.etichetta_qualita = ?')
        params.append(etichetta_qualita)
    
    where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
    
    query = f'''
        SELECT c.*, 
               a1.titolo as argomento1_titolo, a1.id_materia as argomento1_materia,
               a2.titolo as argomento2_titolo, a2.id_materia as argomento2_materia,
               m1.nome as materia1_nome, m1.colore as materia1_colore,
               m2.nome as materia2_nome, m2.colore as materia2_colore
        FROM collegamenti c
        JOIN argomenti a1 ON c.id_argomento1 = a1.id
        JOIN argomenti a2 ON c.id_argomento2 = a2.id
        JOIN materie m1 ON a1.id_materia = m1.id
        JOIN materie m2 ON a2.id_materia = m2.id
        WHERE {where_clause}
        ORDER BY c.id DESC
    '''
    
    collegamenti = conn.execute(query, params).fetchall()
    conn.close()
    return collegamenti
