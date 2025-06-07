-- db.sql: Struttura tabelle per ConnectStudy (SQLi/SQLite)

-- Tabella materie
CREATE TABLE materie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    colore TEXT DEFAULT '#cccccc',
    ordinamento INTEGER DEFAULT 0
);

-- Tabella argomenti
CREATE TABLE argomenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_materia INTEGER NOT NULL,
    titolo TEXT NOT NULL,
    contenuto_md TEXT,
    colore TEXT DEFAULT '#cccccc',
    etichetta_preparazione TEXT CHECK(etichetta_preparazione IN ('scarsa preparazione', 'media preparazione', 'buona preparazione')),
    FOREIGN KEY (id_materia) REFERENCES materie(id) ON DELETE CASCADE
);

-- Tabella allegati (per ogni argomento)
CREATE TABLE allegati (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_argomento INTEGER NOT NULL,
    nome_file TEXT NOT NULL,
    percorso TEXT NOT NULL,
    data_caricamento DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_argomento) REFERENCES argomenti(id) ON DELETE CASCADE
);

-- Tabella collegamenti
CREATE TABLE collegamenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titolo TEXT NOT NULL,
    id_argomento1 INTEGER NOT NULL,
    id_argomento2 INTEGER NOT NULL,
    dettagli TEXT,
    etichetta_qualita TEXT CHECK(etichetta_qualita IN ('collegamento forzato', 'collegamento media qualità', 'collegamento buona qualità', 'collegamento alta qualità')),
    FOREIGN KEY (id_argomento1) REFERENCES argomenti(id) ON DELETE CASCADE,
    FOREIGN KEY (id_argomento2) REFERENCES argomenti(id) ON DELETE CASCADE
);

-- Tabella simulazioni
CREATE TABLE simulazioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spunto_testo TEXT,
    spunto_immagine TEXT, -- percorso file se immagine
    data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabella fili_collegamento
CREATE TABLE fili_collegamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL -- filo-id_simulazione-id_filo generato automaticamente
);

-- Tabella simulazioni_fili (relazione N:M tra simulazioni e fili)
CREATE TABLE simulazioni_fili (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_simulazione INTEGER NOT NULL,
    id_filo INTEGER NOT NULL,
    FOREIGN KEY (id_simulazione) REFERENCES simulazioni(id) ON DELETE CASCADE,
    FOREIGN KEY (id_filo) REFERENCES fili_collegamento(id) ON DELETE CASCADE,
    UNIQUE(id_simulazione, id_filo)
);

-- Tabella collegamenti_simulazione
CREATE TABLE collegamenti_simulazione (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_filo INTEGER NOT NULL,
    titolo TEXT NOT NULL,
    id_argomento1 INTEGER, -- può essere NULL se parte dallo spunto
    id_argomento2 INTEGER NOT NULL,
    dettagli TEXT,
    etichetta_qualita TEXT CHECK(etichetta_qualita IN ('collegamento forzato', 'collegamento media qualità', 'collegamento buona qualità', 'collegamento alta qualità')),
    numero_ordine INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_filo) REFERENCES fili_collegamento(id) ON DELETE CASCADE,
    FOREIGN KEY (id_argomento1) REFERENCES argomenti(id) ON DELETE SET NULL,
    FOREIGN KEY (id_argomento2) REFERENCES argomenti(id) ON DELETE CASCADE
);

-- Indici utili
CREATE INDEX idx_materie_ordinamento ON materie(ordinamento);
CREATE INDEX idx_argomenti_materia ON argomenti(id_materia);
CREATE INDEX idx_allegati_argomento ON allegati(id_argomento);
CREATE INDEX idx_collegamenti_argomento1 ON collegamenti(id_argomento1);
CREATE INDEX idx_collegamenti_argomento2 ON collegamenti(id_argomento2);
CREATE INDEX idx_simulazioni_fili_simulazione ON simulazioni_fili(id_simulazione);
CREATE INDEX idx_simulazioni_fili_filo ON simulazioni_fili(id_filo);
CREATE INDEX idx_collegamenti_simulazione_filo ON collegamenti_simulazione(id_filo);
CREATE INDEX idx_collegamenti_simulazione_ordine ON collegamenti_simulazione(id_filo, numero_ordine);
