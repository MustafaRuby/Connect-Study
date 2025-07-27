import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sql')
DB_FILE = os.path.join(os.path.dirname(__file__), 'connectstudy.db')

def get_db_connection():
    """Ottiene una connessione al database SQLite"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Abilita i vincoli di chiave esterna per questa connessione
    conn.execute('PRAGMA foreign_keys = ON')
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

def update_argomento_full(id, titolo, colore, contenuto_md, etichetta_preparazione):
    """Aggiorna tutti i campi di un argomento"""
    conn = get_db_connection()
    conn.execute('UPDATE argomenti SET titolo = ?, colore = ?, contenuto_md = ?, etichetta_preparazione = ? WHERE id = ?', 
                (titolo, colore, contenuto_md, etichetta_preparazione, id))
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

def update_collegamento(id, titolo, dettagli, etichetta_qualita, id_argomento1=None, id_argomento2=None):
    """Aggiorna un collegamento esistente"""
    conn = get_db_connection()
    
    if id_argomento1 is not None and id_argomento2 is not None:
        # Aggiorna tutti i campi inclusi gli argomenti
        conn.execute('''UPDATE collegamenti SET titolo = ?, dettagli = ?, etichetta_qualita = ?, 
                        id_argomento1 = ?, id_argomento2 = ? WHERE id = ?''', 
                    (titolo, dettagli, etichetta_qualita, id_argomento1, id_argomento2, id))
    else:
        # Aggiorna solo titolo, dettagli ed etichetta (compatibilità con codice esistente)
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

def search_collegamenti(query_titolo='', query_dettagli='', etichetta_qualita='', query_argomenti='', query_materia=''):
    """Cerca collegamenti per titolo, dettagli, etichetta qualità, argomenti e/o materia"""
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
    
    if query_argomenti:
        where_conditions.append('(a1.titolo LIKE ? OR a2.titolo LIKE ?)')
        params.append(f'%{query_argomenti}%')
        params.append(f'%{query_argomenti}%')
    
    if query_materia:
        where_conditions.append('(m1.nome LIKE ? OR m2.nome LIKE ?)')
        params.append(f'%{query_materia}%')
        params.append(f'%{query_materia}%')
    
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

# === SIMULAZIONI OPERATIONS ===

def get_all_simulazioni():
    """Ottiene tutte le simulazioni ordinate per data di creazione"""
    conn = get_db_connection()
    simulazioni = conn.execute('SELECT * FROM simulazioni ORDER BY data_creazione DESC').fetchall()
    conn.close()
    return simulazioni

def add_simulazione(spunto_testo='', spunto_immagine=None):
    """Aggiunge una nuova simulazione"""
    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO simulazioni (spunto_testo, spunto_immagine) VALUES (?, ?)', 
                (spunto_testo, spunto_immagine))
    conn.commit()
    simulazione_id = cursor.lastrowid
    conn.close()
    return simulazione_id

def get_simulazione_by_id(id):
    """Ottiene una simulazione per ID"""
    conn = get_db_connection()
    simulazione = conn.execute('SELECT * FROM simulazioni WHERE id = ?', (id,)).fetchone()
    conn.close()
    return simulazione

def update_simulazione(id, spunto_testo='', spunto_immagine=None):
    """Aggiorna una simulazione esistente"""
    conn = get_db_connection()
    conn.execute('UPDATE simulazioni SET spunto_testo = ?, spunto_immagine = ? WHERE id = ?', 
                (spunto_testo, spunto_immagine, id))
    conn.commit()
    conn.close()

def delete_simulazione(id):
    """Elimina una simulazione e tutti i suoi fili e collegamenti associati"""
    conn = get_db_connection()
    conn.execute('DELETE FROM simulazioni WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# === FILI COLLEGAMENTO OPERATIONS ===

def get_fili_by_simulazione(id_simulazione):
    """Ottiene tutti i fili di una simulazione"""
    conn = get_db_connection()
    fili = conn.execute('''
        SELECT fc.*, COUNT(cs.id) as num_collegamenti
        FROM fili_collegamento fc
        JOIN simulazioni_fili sf ON fc.id = sf.id_filo
        LEFT JOIN collegamenti_simulazione cs ON fc.id = cs.id_filo
        WHERE sf.id_simulazione = ?
        GROUP BY fc.id
        ORDER BY fc.id ASC
    ''', (id_simulazione,)).fetchall()
    conn.close()
    return fili

def add_filo_collegamento(id_simulazione):
    """Aggiunge un nuovo filo di collegamento a una simulazione"""
    conn = get_db_connection()
    
    # Crea il filo
    cursor = conn.execute('INSERT INTO fili_collegamento (nome) VALUES (?)', ('temp',))
    filo_id = cursor.lastrowid
    
    # Genera il nome corretto
    nome_filo = f"filo-{id_simulazione}-{filo_id}"
    conn.execute('UPDATE fili_collegamento SET nome = ? WHERE id = ?', (nome_filo, filo_id))
    
    # Collega il filo alla simulazione
    conn.execute('INSERT INTO simulazioni_fili (id_simulazione, id_filo) VALUES (?, ?)', 
                (id_simulazione, filo_id))
    
    conn.commit()
    conn.close()
    return filo_id

def get_filo_by_id(id):
    """Ottiene un filo per ID"""
    conn = get_db_connection()
    filo = conn.execute('SELECT * FROM fili_collegamento WHERE id = ?', (id,)).fetchone()
    conn.close()
    return filo

def delete_filo_collegamento(id):
    """Elimina un filo di collegamento e tutti i suoi collegamenti"""
    conn = get_db_connection()
    try:
        # Prima elimina tutti i collegamenti di simulazione associati al filo
        conn.execute('DELETE FROM collegamenti_simulazione WHERE id_filo = ?', (id,))
        
        # Poi elimina il filo stesso
        conn.execute('DELETE FROM fili_collegamento WHERE id = ?', (id,))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# === COLLEGAMENTI SIMULAZIONE OPERATIONS ===

def get_collegamenti_simulazione_by_filo(id_filo):
    """Ottiene tutti i collegamenti di simulazione di un filo ordinati per numero d'ordine"""
    conn = get_db_connection()
    collegamenti = conn.execute('''
        SELECT cs.*, 
               a1.titolo as argomento1_titolo, a1.id_materia as argomento1_materia,
               a2.titolo as argomento2_titolo, a2.id_materia as argomento2_materia,
               m1.nome as materia1_nome, m1.colore as materia1_colore,
               m2.nome as materia2_nome, m2.colore as materia2_colore
        FROM collegamenti_simulazione cs
        LEFT JOIN argomenti a1 ON cs.id_argomento1 = a1.id
        JOIN argomenti a2 ON cs.id_argomento2 = a2.id
        LEFT JOIN materie m1 ON a1.id_materia = m1.id
        JOIN materie m2 ON a2.id_materia = m2.id
        WHERE cs.id_filo = ?
        ORDER BY cs.numero_ordine ASC
    ''', (id_filo,)).fetchall()
    conn.close()
    return collegamenti

def get_collegamento_simulazione_by_id(collegamento_id):
    """Ottiene un singolo collegamento di simulazione per ID"""
    conn = get_db_connection()
    collegamento = conn.execute('''
        SELECT cs.*, 
               a1.titolo as argomento1_titolo, a1.id_materia as argomento1_materia,
               a2.titolo as argomento2_titolo, a2.id_materia as argomento2_materia,
               m1.nome as materia1_nome, m1.colore as materia1_colore,
               m2.nome as materia2_nome, m2.colore as materia2_colore
        FROM collegamenti_simulazione cs
        LEFT JOIN argomenti a1 ON cs.id_argomento1 = a1.id
        JOIN argomenti a2 ON cs.id_argomento2 = a2.id
        LEFT JOIN materie m1 ON a1.id_materia = m1.id
        JOIN materie m2 ON a2.id_materia = m2.id
        WHERE cs.id = ?
    ''', (collegamento_id,)).fetchone()
    conn.close()
    return collegamento

def add_collegamento_simulazione(id_filo, titolo, id_argomento2, id_argomento1=None, dettagli='', 
                                etichetta_qualita='collegamento media qualità'):
    """Aggiunge un nuovo collegamento di simulazione"""
    conn = get_db_connection()
    
    # Ottieni il prossimo numero d'ordine
    max_ordine = conn.execute('SELECT MAX(numero_ordine) FROM collegamenti_simulazione WHERE id_filo = ?', 
                             (id_filo,)).fetchone()[0]
    numero_ordine = (max_ordine or 0) + 1
    
    conn.execute('''INSERT INTO collegamenti_simulazione 
                    (id_filo, titolo, id_argomento1, id_argomento2, dettagli, etichetta_qualita, numero_ordine) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                (id_filo, titolo, id_argomento1, id_argomento2, dettagli, etichetta_qualita, numero_ordine))
    conn.commit()
    conn.close()

def copy_collegamento_to_simulazione(collegamento_id, id_filo):
    """Copia un collegamento normale in un filo di simulazione"""
    conn = get_db_connection()
    
    # Ottieni il collegamento originale
    collegamento = conn.execute('SELECT * FROM collegamenti WHERE id = ?', (collegamento_id,)).fetchone()
    if not collegamento:
        conn.close()
        return None
    
    # Ottieni il prossimo numero d'ordine
    max_ordine = conn.execute('SELECT MAX(numero_ordine) FROM collegamenti_simulazione WHERE id_filo = ?', 
                             (id_filo,)).fetchone()[0]
    numero_ordine = (max_ordine or 0) + 1
      # Crea la copia nella tabella collegamenti_simulazione
    cursor = conn.execute('''INSERT INTO collegamenti_simulazione 
                    (id_filo, titolo, id_argomento1, id_argomento2, dettagli, etichetta_qualita, numero_ordine) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                (id_filo, collegamento['titolo'], collegamento['id_argomento1'], 
                 collegamento['id_argomento2'], collegamento['dettagli'], 
                 collegamento['etichetta_qualita'], numero_ordine))
    conn.commit()
    nuovo_id = cursor.lastrowid
    conn.close()
    return nuovo_id

def get_collegamento_simulazione_by_id(id):
    """Ottiene i dati completi di un collegamento di simulazione per l'editing"""
    conn = get_db_connection()
    collegamento = conn.execute('''
        SELECT cs.*, 
               a1.titolo as argomento1_titolo, 
               a2.titolo as argomento2_titolo
        FROM collegamenti_simulazione cs
        LEFT JOIN argomenti a1 ON cs.id_argomento1 = a1.id
        LEFT JOIN argomenti a2 ON cs.id_argomento2 = a2.id
        WHERE cs.id = ?
    ''', (id,)).fetchone()
    conn.close()
    return dict(collegamento) if collegamento else None

def update_collegamento_simulazione(id, titolo, dettagli, etichetta_qualita, id_argomento1=None, id_argomento2=None):
    """Aggiorna un collegamento di simulazione esistente"""
    conn = get_db_connection()
    
    # Aggiorna sempre tutti i campi, gestendo None come valori validi
    conn.execute('''UPDATE collegamenti_simulazione SET titolo = ?, dettagli = ?, etichetta_qualita = ?, 
                    id_argomento1 = ?, id_argomento2 = ? WHERE id = ?''', 
                (titolo, dettagli, etichetta_qualita, id_argomento1, id_argomento2, id))
    
    conn.commit()
    conn.close()

def delete_collegamento_simulazione(id):
    """Elimina un collegamento di simulazione e riordina automaticamente i rimanenti"""
    conn = get_db_connection()
    
    try:
        # Prima otteniamo i dati del collegamento da eliminare
        collegamento_info = conn.execute(
            'SELECT id_filo, numero_ordine FROM collegamenti_simulazione WHERE id = ?', 
            (id,)
        ).fetchone()
        
        if not collegamento_info:
            conn.close()
            return False
            
        id_filo = collegamento_info['id_filo']
        numero_ordine_eliminato = collegamento_info['numero_ordine']
        
        # Elimina il collegamento
        conn.execute('DELETE FROM collegamenti_simulazione WHERE id = ?', (id,))
        
        # Riordina tutti i collegamenti con numero d'ordine superiore al collegamento eliminato
        # decrementando il loro numero_ordine di 1 per riempire il vuoto
        conn.execute('''
            UPDATE collegamenti_simulazione 
            SET numero_ordine = numero_ordine - 1 
            WHERE id_filo = ? AND numero_ordine > ?
        ''', (id_filo, numero_ordine_eliminato))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def reorder_collegamento_simulazione(collegamento_id, new_order):
    """Cambia l'ordine di un collegamento di simulazione scambiando con quello che ha il nuovo ordine"""
    conn = get_db_connection()
    
    try:
        # Ottieni il collegamento corrente e il suo filo
        collegamento_corrente = conn.execute(
            'SELECT id, numero_ordine, id_filo FROM collegamenti_simulazione WHERE id = ?', 
            (collegamento_id,)
        ).fetchone()
        
        if not collegamento_corrente:
            conn.close()
            return False
            
        old_order = collegamento_corrente['numero_ordine']
        id_filo = collegamento_corrente['id_filo']
        
        # Se l'ordine è lo stesso, non fare nulla
        if old_order == new_order:
            conn.close()
            return True
            
        # Trova il collegamento che ha già il nuovo ordine
        collegamento_target = conn.execute(
            'SELECT id, numero_ordine FROM collegamenti_simulazione WHERE id_filo = ? AND numero_ordine = ?',
            (id_filo, new_order)
        ).fetchone()
        
        if collegamento_target:
            # Scambia gli ordini
            conn.execute(
                'UPDATE collegamenti_simulazione SET numero_ordine = ? WHERE id = ?',
                (new_order, collegamento_id)
            )
            conn.execute(
                'UPDATE collegamenti_simulazione SET numero_ordine = ? WHERE id = ?', 
                (old_order, collegamento_target['id'])
            )
        else:
            # Se nessun collegamento ha il nuovo ordine, aggiorna solo quello corrente
            conn.execute(
                'UPDATE collegamenti_simulazione SET numero_ordine = ? WHERE id = ?',
                (new_order, collegamento_id)
            )
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def get_max_order_in_filo(id_filo):
    """Ottiene il numero d'ordine massimo in un filo"""
    conn = get_db_connection()
    max_order = conn.execute(
        'SELECT MAX(numero_ordine) FROM collegamenti_simulazione WHERE id_filo = ?', 
        (id_filo,)
    ).fetchone()[0]
    conn.close()
    return max_order or 0

def search_argomenti(query):
    """Cerca argomenti per titolo"""
    conn = get_db_connection()
    argomenti = conn.execute('''
        SELECT a.*, m.nome as materia_nome 
        FROM argomenti a
        JOIN materie m ON a.id_materia = m.id
        WHERE a.titolo LIKE ? 
        ORDER BY a.titolo ASC
        LIMIT 20
    ''', (f'%{query}%',)).fetchall()
    conn.close()
    return argomenti
