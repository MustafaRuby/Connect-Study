# ConnectStudy

## 📋 Panoramica

**ConnectStudy** è un'applicazione web avanzata progettata per supportare gli studenti nella preparazione all'esame orale di maturità. L'applicazione facilita la creazione di collegamenti interdisciplinari tra argomenti di diverse materie, simulando la dinamica dell'esame di stato italiano.

### 🎯 Obiettivo Principale

L'esame orale di maturità si svolge secondo questa modalità specifica:
1. **Chiamata in aula**: Lo studente viene richiamato dentro l'aula
2. **Presentazione spunto**: Gli viene fornito uno **spunto iniziale** (citazione, foto, mappa, documento, grafico, ecc.)
3. **Commissione**: È composta da professori che insegnano diverse materie
4. **Collegamento orale**: Lo studente deve **connettere lo spunto a tutte le materie** della commissione **entro 10 minuti oralmente**

ConnectStudy permette agli studenti di:
- Organizzare i propri argomenti per materia
- Creare e gestire collegamenti tra argomenti
- Simulare l'esame con spunti personalizzati
- Esercitarsi nella costruzione di percorsi interdisciplinari

---

## 🏗️ Architettura Tecnica

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite senza ORM
- **Real-time**: Flask-SocketIO per aggiornamenti live
- **File Processing**: 
  - `python-docx` per documenti Word
  - `PyPDF2` per estrazione testo PDF
  - `markdown` per rendering Markdown

### Frontend
- **Template Engine**: Jinja2
- **Styling**: CSS3 modulare organizzato per componenti
- **JavaScript**: Vanilla JS con approccio modulare
- **Editor**: CodeMirror con:
  - Syntax highlighting per linguaggi di programmazione
  - Supporto KaTeX per formule matematiche
  - Preview Markdown in tempo reale
  - Modalità fullscreen

### Struttura del Progetto
```
ConnectStudy/
├── app.py                 # Applicazione principale Flask
├── db_manager.py          # Gestione database e query
├── db.sql                 # Schema database SQLite
├── requirements.txt       # Dipendenze Python
├── static/               # Risorse statiche
│   ├── css/             # Fogli di stile modulari
│   ├── js/              # Script JavaScript
│   ├── libs/            # Librerie esterne
│   └── [uploads]/       # File caricati dagli utenti
└── templates/           # Template Jinja2
```

---

## 📊 Schema Database

### Tabelle Principali

#### **materie**
- `id`: Chiave primaria
- `nome`: Nome della materia
- `colore`: Colore hex per visualizzazione
- `ordinamento`: Posizione nell'interfaccia (drag & drop)

#### **argomenti**
- `id`: Chiave primaria
- `id_materia`: Riferimento alla materia
- `titolo`: Titolo dell'argomento
- `contenuto_md`: Contenuto in formato Markdown
- `colore`: Colore personalizzabile
- `etichetta_preparazione`: Livello di preparazione
  - "scarsa preparazione"
  - "media preparazione"
  - "buona preparazione"

#### **allegati**
- `id`: Chiave primaria
- `id_argomento`: Riferimento all'argomento
- `nome_file`: Nome originale del file
- `percorso`: Path nel filesystem
- `data_caricamento`: Timestamp di upload

#### **collegamenti**
- `id`: Chiave primaria
- `titolo`: Titolo del collegamento
- `id_argomento1`: Primo argomento collegato
- `id_argomento2`: Secondo argomento collegato
- `dettagli`: Spiegazione del collegamento (Markdown)
- `etichetta_qualita`: Qualità del collegamento
  - "collegamento forzato"
  - "collegamento media qualità"
  - "collegamento buona qualità"
  - "collegamento alta qualità"

#### **simulazioni**
- `id`: Chiave primaria
- `spunto_testo`: Spunto testuale
- `spunto_immagine`: Path dell'immagine di spunto
- `data_creazione`: Timestamp di creazione

#### **fili_collegamento**
- `id`: Chiave primaria
- `nome`: Nome generato automaticamente (filo-{id_simulazione}-{id_filo})

#### **simulazioni_fili** (N:M)
- Relazione molti-a-molti tra simulazioni e fili

#### **collegamenti_simulazione**
- `id`: Chiave primaria
- `id_filo`: Riferimento al filo
- `titolo`: Titolo del collegamento
- `id_argomento1`: Primo argomento (NULL se parte dallo spunto)
- `id_argomento2`: Secondo argomento
- `dettagli`: Spiegazione del collegamento
- `etichetta_qualita`: Qualità del collegamento
- `numero_ordine`: Posizione nel filo

---

## 🎨 Funzionalità Dettagliate

### 1. Gestione Materie

**Caratteristiche:**
- Card colorate riordinabili tramite drag & drop
- Personalizzazione nome e colore
- Salvataggio automatico dell'ordinamento
- Navigazione diretta agli argomenti

**Interfaccia:**
- Griglia responsiva di card
- Controlli inline per modifica/eliminazione
- Feedback visivo durante il riordinamento

### 2. Gestione Argomenti

#### **Creazione e Modifica**
- **Editor integrato**: CodeMirror con:
  - Syntax highlighting
  - Supporto KaTeX per formule
  - Preview live del Markdown
  - Modalità fullscreen
- **Import da file**: Supporto per Word, PDF e Markdown
- **Gestione allegati**: Upload e visualizzazione in popup dedicati

#### **Modalità di Import**
Quando si carica un file, l'utente può scegliere:
1. **Sostituire** completamente il contenuto esistente
2. **Inserire all'inizio** del contenuto esistente
3. **Appendere alla fine** del contenuto esistente

#### **Etichette di Preparazione**
Sistema di auto-valutazione per tracciare il livello di preparazione:
- Visualizzazione con badge colorati
- Filtro per livello di preparazione
- Statistiche aggregate per materia

### 3. Sistema dei Collegamenti

#### **Collegamenti Standard**
- **Struttura**: Titolo + Due argomenti + Dettagli + Etichetta qualità
- **Creazione**: 
  - Da pagina argomento (un slot pre-compilato)
  - Da pagina collegamenti (entrambi slot vuoti)
  - Modal per selezione argomenti con ricerca
- **Visualizzazione**: Card compatte con popup dettagli
- **Gestione**: Modifica, eliminazione, duplicazione

#### **Ricerca e Filtri**
- **Ricerca live** su titolo e dettagli
- **Filtro per etichetta** qualità
- **Filtro per materia** coinvolta
- **Reset filtri** con un click

### 4. Sistema delle Simulazioni

#### **Struttura Gerarchica**
```
Simulazione
├── Spunto (testo o immagine)
├── Filo 1
│   ├── Collegamento A (da spunto → argomento)
│   ├── Collegamento B (da argomento → argomento)
│   └── Collegamento C (da argomento → argomento)
├── Filo 2
│   └── [Altri collegamenti...]
└── [Altri fili...]
```

#### **Creazione Spunti**
- **Spunto testuale**: Editor Markdown integrato
- **Spunto immagine**: Upload con preview
- **Storage**: File salvati in `static/simulazioni/` con nomi univoci

#### **Fili di Collegamento**
- **Nomenclatura automatica**: `filo-{id_simulazione}-{id_filo}`
- **Ordinamento**: Riordinamento dei collegamenti
- **Relazioni N:M**: Una simulazione può avere più fili, un filo può essere condiviso

#### **Collegamenti di Simulazione**
Tre modalità di creazione:
1. **Nuovo collegamento**: Creato direttamente nella simulazione
2. **Import collegamento esterno**: Copia dei dati da collegamenti standard
3. **Riferimento collegamento simulazione**: Riuso di collegamenti esistenti

#### **Gestione Ordine**
- **Numero d'ordine**: Ogni collegamento ha una posizione nel filo
- **Controlli**: Frecce su/giù per riordinamento
- **Logica**: Scambio posizioni tra collegamenti adiacenti

#### **Ricerca Dinamica**
- **Ambito**: Per singolo filo
- **Campi**: Titolo, dettagli, argomenti coinvolti
- **Reset**: Pulsante per pulire i filtri

---

## ⚙️ Caratteristiche Tecniche Avanzate

### Real-time Updates
- **Flask-SocketIO**: Aggiornamenti automatici quando altri utenti modificano dati
- **Polling intelligente**: Limitato a 15 secondi nelle pagine attive
- **Eventi**: Notifiche per creazione, modifica, eliminazione

### Gestione File
- **Conversione automatica**: Word e PDF → Markdown
- **Pulizia**: File temporanei eliminati dopo conversione
- **Allegati persistenti**: Mantenuti separatamente dal contenuto testuale
- **Nomi univoci**: Prevenzione conflitti con timestamp e hash

### Interfaccia Utente
- **Design responsivo**: Ottimizzato per desktop, tablet e mobile
- **CSS modulare**: Organizzato per componenti riusabili
- **Animazioni fluide**: Transizioni CSS3 per feedback visivo
- **Accessibilità**: Supporto tastiera e screen reader

### Performance
- **Query ottimizzate**: Indici database per performance
- **Lazy loading**: Caricamento contenuti on-demand
- **Caching**: Strategie di cache per dati frequenti
- **Compressione**: Asset minificati in produzione

---

## 🚀 Setup e Installazione

### Prerequisiti
- Python 3.8+
- pip (gestore pacchetti Python)

### Installazione
```bash
# Clona o scarica il progetto
cd ConnectStudy

# Installa le dipendenze
pip install -r requirements.txt

# Avvia l'applicazione
python app.py
```

### Configurazione
L'applicazione è configurata per funzionare immediatamente con:
- Database SQLite locale (`connectstudy.db`)
- Server di sviluppo Flask su `localhost:5000`
- File statici serviti direttamente da Flask

---

## 📝 Dipendenze

| Libreria | Versione | Scopo |
|----------|----------|-------|
| flask | Latest | Framework web principale |
| flask-socketio | Latest | Real-time communication |
| python-socketio | Latest | WebSocket support |
| python-engineio | Latest | Engine.IO support |
| python-docx | Latest | Elaborazione documenti Word |
| PyPDF2 | Latest | Estrazione testo PDF |
| markdown | Latest | Parsing e rendering Markdown |
| werkzeug | Latest | Utilities WSGI |

---

## 🔧 Personalizzazione e Estensioni

### Aggiunta Nuove Funzionalità
- **API endpoints**: Facilmente estendibili in `app.py`
- **Database operations**: Nuove funzioni in `db_manager.py`
- **Frontend components**: CSS e JS modulari per componenti riusabili

### Temi e Stili
- **CSS variables**: Personalizzazione colori e font
- **Component-based**: Stili organizzati per componente
- **Responsive design**: Breakpoint configurabili

### Integrazioni
- **Export**: Possibilità di esportare simulazioni in PDF/Word
- **Import**: Estensione per altri formati di file
- **Sincronizzazione**: Potenziale integrazione con cloud storage

---

## 📚 Best Practices per l'Uso

### Organizzazione Contenuti
1. **Struttura materie**: Organizza per programma ministeriale
2. **Denominazione argomenti**: Usa titoli chiari e specifici
3. **Collegamenti significativi**: Evita collegamenti forzati
4. **Etichette oneste**: Valuta realisticamente la preparazione

### Preparazione Esame
1. **Simulazioni regolari**: Pratica con spunti diversificati
2. **Tempo limitato**: Esercitati con cronometro
3. **Varietà argomenti**: Copri tutto il programma
4. **Review collegamenti**: Rivedi e migliora i collegamenti deboli

### Manutenzione Dati
1. **Backup regolari**: Esporta dati periodicamente
2. **Pulizia**: Rimuovi argomenti obsoleti
3. **Aggiornamenti**: Mantieni contenuti aggiornati
4. **Validazione**: Verifica completezza informazioni

---

## 🐛 Troubleshooting

### Problemi Comuni

**Database non inizializzato**
```bash
python -c "import db_manager; db_manager.init_db()"
```

**File non caricabili**
- Verifica permessi cartella `static/`
- Controlla dimensione file (limitata dal server)

**Editor non funziona**
- Controlla caricamento librerie CodeMirror
- Verifica console browser per errori JavaScript

**Real-time non funziona**
- Controlla connessione SocketIO
- Verifica firewall/proxy settings

### Log e Debug
- Log applicazione: Console Flask
- Errori frontend: Console browser (F12)
- Database: Query log in `db_manager.py`

---

## 📄 Licenza

Progetto sviluppato per scopi educativi. Distribuzione non libera e necessita permesso.

---

## 👥 Contributi

Contributi benvenuti! Per segnalazioni bug o richieste funzionalità:
1. Documenta il problema dettagliatamente
2. Fornisci steps per riprodurre
3. Includi informazioni ambiente (browser, OS, Python version)

---

*Ultima modifica: Giugno 2025*
