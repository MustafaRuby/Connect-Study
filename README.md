# ConnectStudy

## 📋 Panoramica

**ConnectStudy** è un'applicazione web progettata per aiutare gli studenti a prepararsi all'esame orale di maturità italiana. L'app consente di gestire contenuti disciplinari, creare connessioni interdisciplinari e simulare le dinamiche reali dell’esame.

### 🎯 Obiettivo

L'orale dell’esame di stato si svolge così:
1. Lo studente viene chiamato in aula.
2. Gli viene fornito uno spunto iniziale (citazione, immagine, grafico, ecc.).
3. La commissione, composta da professori di diverse materie, valuta la capacità dello studente di costruire collegamenti interdisciplinari.
4. Lo studente ha 10 minuti per collegare oralmente lo spunto a tutte le materie coinvolte.

**ConnectStudy** consente:
- Inserimento e organizzazione degli argomenti per ciascuna materia
- Creazione di collegamenti tra argomenti
- Simulazione realistica con spunti testuali o visivi
- Navigazione visuale tra le connessioni
- Esercizio costante su percorsi multidisciplinari

---

## 🏗️ Architettura Tecnica

### Backend
- **Framework**: Python Flask
- **Database**: SQLite con file `.sql` esterno per la creazione tabelle (no ORM)
- **Modularità**: Funzioni del database centralizzate in `db_manager.py`, importate in `app.py`
- **Real-time**: Gestione aggiornamenti tramite Flask-SocketIO
- **File Processing**:
  - `python-docx` per Word (.docx)
  - `PyPDF2` per PDF
  - `markdown` per Markdown

### Frontend
- **Template Engine**: Jinja2
- **Styling**: CSS3 modulare per componenti
- **JavaScript**: Vanilla JS strutturato in moduli
- **Editor**: CodeMirror, con:
  - Evidenziazione della sintassi
  - Supporto KaTeX per formule matematiche
  - Modalità fullscreen
  - Anteprima Markdown live

### Funzionalità grafiche aggiuntive:
- Drag & drop per riordinamento delle materie
- Card interattive per materie, argomenti e collegamenti
- Popup dinamici per visualizzare e modificare i dettagli
- Ricerche live su titoli e contenuti
- Modalità responsive per PC, tablet e smartphone

---

## 📁 Struttura del Progetto

ConnectStudy/
├── app.py                 # App Flask principale
├── db\_manager.py          # Gestione delle query
├── db.sql                 # Schema del database SQLite
├── requirements.txt       # Librerie necessarie
├── static/                # File statici (CSS, JS, immagini)
│   ├── css/
│   ├── js/
│   ├── libs/
│   └── simulazioni/       # Spunti immagine salvati con nomi univoci
├── templates/             # Template HTML (Jinja2)
└── \[uploads]/             # File allegati dagli utenti

---

## ⚙️ Caratteristiche Tecniche Avanzate

### Real-time Updates
- **Flask-SocketIO**: gli aggiornamenti a materie, argomenti, collegamenti e simulazioni avvengono in tempo reale.
- **Polling intelligente**: limitato a 15 secondi e attivo solo nelle pagine attualmente aperte.
- **Eventi gestiti**: creazione, modifica, eliminazione di contenuti con propagazione automatica.

### Gestione File
- **Conversione automatica**: i file `.docx`, `.pdf` e `.md` vengono trasformati in testo Markdown.
- **Pulizia dei file**: dopo la conversione, i file temporanei vengono eliminati.
- **Allegati**: memorizzati in modo separato dal contenuto testuale, mantenuti con nomi univoci.
- **Percorso statico**: immagini caricate per simulazioni vengono archiviate in `static/simulazioni/`.

### Interfaccia Utente
- **Design responsivo**: compatibile con desktop, tablet e mobile.
- **CSS modulare**: ogni componente ha i propri stili separati.
- **Animazioni fluide**: transizioni CSS3 per una UX naturale.
- **Accessibilità**: compatibilità con screen reader e tastiera.

### Performance
- **Query ottimizzate**: utilizzo di indici nel database SQLite.
- **Lazy loading**: caricamento on-demand di contenuti pesanti.
- **Caching**: applicato su dati di uso frequente.
- **Compressione**: asset minificati in produzione.

---

## 📊 Schema Database

Il database utilizza **SQLite** con definizione esplicita delle tabelle tramite file SQL esterno. Le tabelle sono progettate per supportare la logica relazionale tra materie, argomenti, collegamenti e simulazioni, garantendo estensibilità e performance.

---

### Tabelle Principali

#### 🟨 `materie`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Identificativo univoco |
| `nome` | TEXT | Nome della materia |
| `colore` | TEXT | Colore HEX scelto dall’utente |
| `ordinamento` | INTEGER | Ordine per drag & drop |

- Le **card delle materie** sono ordinabili graficamente.
- Il campo `ordinamento` determina la posizione nel layout.

---

#### 🟧 `argomenti`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Identificativo univoco |
| `id_materia` | INTEGER | Chiave esterna verso `materie` |
| `titolo` | TEXT | Titolo dell’argomento |
| `contenuto_md` | TEXT | Contenuto in formato Markdown |
| `colore` | TEXT | Colore opzionale del card |
| `etichetta_preparazione` | TEXT | Livello di preparazione: `scarsa`, `media`, `buona` |

**Note aggiuntive:**
- Ogni argomento è visualizzato come una card colorata cliccabile.
- L’editor consente modifiche con CodeMirror, preview live e modalità fullscreen.
- All'importazione di file Word, PDF o Markdown:
  - L’utente può scegliere se **sostituire**, **inserire all’inizio** o **appendere alla fine** del contenuto esistente.
  - I file sono **trasformati in Markdown** e poi **scartati**.
  - Le immagini vengono **ignorate** durante la conversione.
  - Gli allegati restano separati nella tabella `allegati`.

---

#### 🗂️ `allegati`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Identificativo univoco |
| `id_argomento` | INTEGER | Collegamento all’argomento |
| `nome_file` | TEXT | Nome originale del file |
| `percorso` | TEXT | Path del file salvato |
| `data_caricamento` | TEXT | Timestamp upload |

- Gli allegati possono essere di qualsiasi tipo.
- Visualizzati tramite popup dedicati.
- Mantenuti separati dal contenuto Markdown.

---

#### 🔗 `collegamenti`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | INTEGER PRIMARY KEY |
| `titolo` | TEXT | Titolo del collegamento |
| `id_argomento1` | INTEGER | Primo argomento collegato |
| `id_argomento2` | INTEGER | Secondo argomento collegato |
| `dettagli` | TEXT | Spiegazione testuale |
| `etichetta_qualita` | TEXT | Qualità: `forzato`, `media qualità`, `buona qualità`, `alta qualità` |

**Funzionalità:**
- I collegamenti sono visibili come card interattive.
- Popup con dettagli espandibili.
- Si possono creare da:
  - Pagina argomento (slot precompilato)
  - Menu laterale (entrambi gli slot vuoti)
- Slot argomenti gestiti tramite popup di selezione con filtri e ricerca.

---

#### 🧪 `simulazioni`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | INTEGER PRIMARY KEY |
| `spunto_testo` | TEXT | Spunto testuale (Markdown) |
| `spunto_immagine` | TEXT | Path immagine spunto |
| `data_creazione` | TEXT | Timestamp |

- Ogni simulazione può contenere uno spunto testuale o un’immagine.
- Le immagini vengono salvate in `static/simulazioni/` con nome univoco.

---

#### 🧵 `fili_collegamento`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | INTEGER PRIMARY KEY |
| `nome` | TEXT | Nome generato automaticamente: `filo-{id_simulazione}-{id_filo}` |

- Ogni filo è una sequenza logica di collegamenti che parte da uno spunto.

---

#### 🔄 `simulazioni_fili` (N:M)
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id_simulazione` | INTEGER | FK su `simulazioni` |
| `id_filo` | INTEGER | FK su `fili_collegamento` |

- Relazione molti-a-molti: una simulazione può contenere più fili, e viceversa.

---

#### 🧷 `collegamenti_simulazione`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | INTEGER PRIMARY KEY |
| `id_filo` | INTEGER | FK al filo in cui si trova |
| `titolo` | TEXT |
| `id_argomento1` | INTEGER | Può essere NULL se parte dallo spunto |
| `id_argomento2` | INTEGER |
| `dettagli` | TEXT |
| `etichetta_qualita` | TEXT |
| `numero_ordine` | INTEGER | Posizione ordinata nel filo |

**Logiche speciali:**
- Se `id_argomento1` è NULL, il collegamento parte dallo spunto.
- I collegamenti sono ordinati in base a `numero_ordine`.
- Possono essere:
  1. Creati da zero
  2. Importati dai collegamenti standard (duplicazione nel DB)
  3. Riutilizzati da altri collegamentiSimulazione (senza duplicazione)

- Riordinamento: spostando un collegamento, si scambia la posizione con quello adiacente.
- Il display si adatta: card più compatte, ma dettagli accessibili via popup.

---

### 🔍 Ricerche dinamiche

- In **ogni sezione (argomenti, collegamenti, simulazioni)** è presente una **ricerca live** per:
  - Titolo
  - Contenuto
  - Materia coinvolta
  - Etichette
- Pulsante per **resettare i filtri**

---

Perfetto! Procedo ora con la **Parte 3 – Gestione Materie e Argomenti**, includendo tutte le funzionalità, comportamenti interattivi e logiche operative che emergono dal file OLD, mantenendo però la chiarezza e la struttura del file NEW.

---

## 🎨 Gestione Materie e Argomenti

### 1. 📘 Gestione Materie

#### Caratteristiche:
- Ogni **materia** viene rappresentata tramite una **card colorata**.
- Le card sono **trascinabili** per modificare l'ordine, il quale viene salvato nel database tramite l'attributo `ordinamento`.
- Le materie sono **personalizzabili**:
  - Nome
  - Colore (HEX)
- È possibile eliminare o modificare una materia direttamente dalla card.

#### Interfaccia:
- Visualizzazione a **griglia responsiva**.
- Card cliccabili: accedono alla pagina con gli **argomenti** della materia.
- **Feedback visivo** durante il drag & drop per migliorare l’usabilità.

---

### 2. 📄 Gestione Argomenti

#### Struttura degli Argomenti:
- Ogni materia contiene uno o più **argomenti**, visualizzati anch’essi come card colorate.
- Ogni argomento ha:
  - Titolo
  - Contenuto in formato **Markdown**
  - Colore opzionale personalizzato
  - Etichetta di preparazione: `scarsa`, `media`, `buona`

---

### ✍️ Creazione e Modifica Argomenti

#### Editor integrato (CodeMirror):
- Evidenziazione della sintassi (Markdown, linguaggi di programmazione)
- Supporto **KaTeX** per formule matematiche
- Modalità **fullscreen** disponibile
- Anteprima **live** del Markdown
- Controlli per modifica/salvataggio/annullamento

#### Modalità di Importazione:
L’utente può caricare file `.docx`, `.pdf` o `.md` per inserire contenuto nell’argomento.

- L’applicazione **trasforma il contenuto del file in Markdown**
- Le immagini vengono **ignorate**
- Il file **non viene conservato**, ma solo convertito in testo `.md`
- L’utente può scegliere tra tre modalità:
  1. **Sostituire** il contenuto esistente
  2. **Inserire all'inizio**
  3. **Appendere alla fine**

#### Funzionalità Avanzate:
- Il testo può essere modificato manualmente tramite l’editor.
- È possibile aprire un file caricato in **anteprima**, modificare e salvare.
- Modalità dedicata per fullscreen editing per una migliore concentrazione.

---

### 📎 Allegati

- Ogni argomento può avere **allegati separati** dal contenuto Markdown.
- Possono essere **di qualsiasi tipo** (immagini, PDF, ZIP, ecc.).
- Gli allegati vengono **visualizzati tramite popup** con design coerente al resto dell’app.
- Salvati nel filesystem (`[uploads]`) con nome originale e percorso nel DB.

---

### 🎓 Etichette di Preparazione

Sistema utile per monitorare lo stato della preparazione di ogni argomento:

- Etichette disponibili:
  - `Scarsa preparazione`
  - `Media preparazione`
  - `Buona preparazione`
- Visualizzate tramite **badge colorati**
- Possono essere **filtrate** nella pagina argomenti
- Statistiche aggregate disponibili per ogni materia

---

### 🔍 Ricerca Live

- Presente barra di ricerca nella pagina argomenti
- Si può cercare per:
  - Titolo dell’argomento
  - Contenuto Markdown
- Ricerca **istantanea** durante la digitazione
- Integrazione con i filtri per etichette

---

### 🔁 Aggiornamenti in Tempo Reale

- Ogni modifica (creazione, aggiornamento, eliminazione di materia o argomento) viene **propagata automaticamente** tramite Flask-SocketIO.
- La pagina non viene ricaricata, ma aggiornata in modo reattivo.
- Il polling intelligente avviene solo **nelle pagine attive** ogni 15 secondi.

---

Perfetto! Procedo ora con la **Parte 4 – Sistema dei Collegamenti**, includendo tutte le funzionalità presenti nel file `NEW` ma integrando ogni dettaglio tecnico-operativo descritto nel file `OLD`, come i popup interattivi, la struttura della UI e la logica di inserimento.

---

## 🔗 Sistema dei Collegamenti

Il sistema dei collegamenti consente agli studenti di costruire relazioni logiche tra due argomenti, anche di materie diverse, facilitando l'interdisciplinarità richiesta all'esame orale.

---

### ✏️ Struttura del Collegamento

Ogni collegamento è costituito da:
- **Titolo** del collegamento
- **Argomento 1** e **Argomento 2** (di qualsiasi materia)
- **Dettagli**: spiegazione testuale della connessione (in Markdown)
- **Etichetta di qualità**:
  - `Collegamento forzato`
  - `Collegamento media qualità`
  - `Collegamento buona qualità`
  - `Collegamento alta qualità`

---

### 🧭 Creazione dei Collegamenti

Ci sono due modalità principali:

1. **Dalla pagina di un argomento**:
   - Si clicca su un bottone `Collega`
   - Viene aperto un **popup** con due slot per gli argomenti:
     - Uno precompilato con l’argomento corrente
     - L’altro selezionabile tramite navigazione tra le **card delle materie**
   - L’utente può scegliere l’altro argomento tramite un secondo popup a cascata:
     - Si apre un menu con tutte le materie
     - Cliccando sulla materia si apre la lista degli argomenti
     - Selezionando l’argomento, questo riempie lo slot e si torna al popup principale

2. **Dal menu laterale “Collegamenti”**:
   - Slot vuoti per entrambi gli argomenti
   - Selezione libera tramite lo stesso meccanismo a cascata

In entrambi i casi, si può:
- Inserire un **titolo**
- Scrivere la **spiegazione** del collegamento
- Assegnare l’**etichetta di qualità**
- Salvare o annullare l’operazione tramite i controlli del popup

---

### 🖼️ Interfaccia Utente dei Collegamenti

#### Menu laterale
- All’interno della pagina argomento è presente un **menu laterale espandibile** con tutte le card dei collegamenti legati all’argomento.
- Ogni collegamento è mostrato come una **card compatta** con:
  - Titolo
  - Icona della qualità
  - Pulsante per aprire il dettaglio

#### Popup Dettagli
- Cliccando su una card si apre un **popup** (modal) che mostra tutti i dettagli del collegamento:
  - Titolo
  - Argomenti collegati
  - Testo della spiegazione
  - Etichetta qualità
- Il popup ha:
  - Altezza massima con scroll interno se il contenuto è lungo
  - Pulsante per chiudere
  - Design coerente con gli altri popup dell’app

---

### 🧮 Gestione dei Collegamenti

Ogni collegamento può essere:
- Modificato
- Eliminato
- Duplicato

L’interfaccia consente di:
- Navigare facilmente tra le materie e i collegamenti associati
- Accedere a una pagina dedicata con la lista completa di tutti i collegamenti
- Nella pagina collegamenti, cliccando su una card si apre il dettaglio con le stesse modalità dei popup

---

### 🔍 Ricerca e Filtri

Sistema dinamico per facilitare la gestione anche con molti collegamenti.

- **Ricerca live**:
  - Titolo
  - Dettagli testuali (Markdown)
- **Filtri disponibili**:
  - Etichetta di qualità
  - Materia coinvolta
- **Reset dei filtri** con un solo click

Tutte le ricerche sono **istantanee** e si aggiornano durante la digitazione.

---

### 🔁 Aggiornamenti in Tempo Reale

- Qualsiasi modifica ai collegamenti viene aggiornata in tempo reale tramite Flask-SocketIO.
- L'interfaccia non richiede refresh: i popup, le card e le pagine si aggiornano dinamicamente.

---

Perfetto! Procedo ora con la **Parte 5 – Sistema delle Simulazioni**, che è una delle sezioni più complesse e ricche di logica descrittiva e tecnica, soprattutto grazie al contributo dettagliato del file OLD. Integrerò tutto in uno schema chiaro, mantenendo lo stile professionale.

---

## 🧪 Sistema delle Simulazioni

Le simulazioni rappresentano una modalità interattiva per esercitarsi realisticamente alla prova orale dell’esame di maturità. L'utente può creare scenari simulati con uno spunto iniziale e costruire percorsi logici composti da collegamenti tra argomenti.

---

### 🧠 Struttura Gerarchica

```

Simulazione
├── Spunto (testo o immagine)
├── Filo 1
│   ├── Collegamento A (spunto → argomento)
│   ├── Collegamento B (argomento → argomento)
│   └── Collegamento C (argomento → argomento)
├── Filo 2
│   └── \[Altri collegamenti...]
└── \[Altri fili...]

```

Ogni **simulazione** è composta da:
- Uno **spunto** iniziale
- Uno o più **fili di collegamento** (filo-{id_simulazione}-{id_filo})
- Ogni filo contiene **collegamentiSimulazione**, che possono partire dallo spunto o da altri argomenti

---

### ✍️ Creazione Simulazione

- Accessibile ovunque tramite un bottone dedicato
- Nuova simulazione = creazione di uno spunto
- Tipologie di spunto:
  1. **Spunto testuale**: editor Markdown integrato
  2. **Spunto immagine**: upload immagini (PNG, JPG, ecc.)

Lo spunto viene salvato in:
- `static/simulazioni/` (path memorizzato nel DB)
- Con **nome univoco** per evitare conflitti

---

### 🧵 Fili di Collegamento

Ogni simulazione può contenere uno o più fili:

- Ciascun filo è un contenitore sequenziale di collegamentiSimulazione
- Il nome del filo è generato automaticamente: `filo-{id_simulazione}-{id_filo}`
- I fili sono riutilizzabili: possono appartenere a più simulazioni (relazione N:M)
- Visualizzazione ordinata dei collegamenti in base al campo `numero_ordine`

---

### 🔗 CollegamentiSimulazione

I collegamenti contenuti in un filo hanno lo stesso schema dei collegamenti standard, ma sono gestiti in una tabella separata.

Ogni collegamentoSimulazione ha:
- `titolo`
- `id_argomento1` (può essere NULL se parte dallo spunto)
- `id_argomento2`
- `dettagli` in Markdown
- `etichetta_qualita`
- `numero_ordine` (usato per il riordinamento all’interno del filo)

---

### ➕ Modalità di Inserimento Collegamenti nella Simulazione

Tre modalità alternative:

1. **Nuovo collegamento simulazione**
   - Creato ex novo all'interno del filo
   - Identico per struttura a un collegamento standard, ma salvato nella tabella `collegamenti_simulazione`

2. **Importa collegamento esterno**
   - Copia di un collegamento standard
   - Il collegamento viene **duplicato** nel DB (non solo referenziato)
   - Collegato al filo specificato
   - Il collegamento standard originale rimane indipendente

3. **Riferimento a collegamento di simulazione già esistente**
   - Nessuna duplicazione
   - Si crea solo una nuova associazione al filo
   - Utile per percorsi che condividono snodi comuni

---

### 🔃 Ordinamento dei Collegamenti

- Ogni collegamento all’interno di un filo ha un numero d’ordine (`numero_ordine`)
- Due **frecce** (↑ / ↓) permettono all’utente di modificare l’ordine
- Lo spostamento avviene per **scambio** di posizioni:
  - Esempio: se un collegamento passa da posizione 3 a 2, quello che era in 2 passa a 3

---

### 🖼️ Visualizzazione e UI

- I collegamenti nella simulazione appaiono come **card compatte**
- Ogni card mostra:
  - Titolo
  - Collegamento tra due argomenti (o spunto → argomento)
  - Etichetta qualità
  - Dettagli espandibili tramite popup (stile coerente con altri popup)
- I popup sono:
  - Scrollabili verticalmente
  - Chiedono conferma in caso di modifica o cancellazione

---

### 🔍 Ricerca Dinamica per Filo

Ogni filo ha un motore di ricerca dedicato:
- Campi ricercabili:
  - Titolo del collegamento
  - Dettagli
  - Argomenti coinvolti
- Presente pulsante per **resettare i filtri**

Le ricerche sono **instantanee** e aggiornano i risultati in tempo reale.

---

### 🔁 Aggiornamenti e Polling

- Il sistema utilizza **Flask-SocketIO** per aggiornamenti live
- Il polling è **limitato a 15 secondi** e attivo **solo nelle pagine aperte**
- I collegamenti vengono aggiornati dinamicamente senza ricaricare la pagina

---

### 📥 Logica di salvataggio dati

- I collegamenti simulazione NON influiscono sui collegamenti standard
- Le immagini vengono salvate fisicamente e richiamate tramite path
- Il database mantiene tutte le relazioni tra simulazione, filo e collegamenti in modo coerente

---

## 🚀 Setup e Installazione

### Prerequisiti
- Python 3.8+
- pip (Python package manager)

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
- Database SQLite locale (`connectstudy.db`)
- Server di sviluppo Flask (`localhost:5000`)
- File statici serviti direttamente da Flask

---

## 🐛 Troubleshooting

### Problemi Comuni

**Database non inizializzato**
```bash
python -c "import db_manager; db_manager.init_db()"
```

**File non caricabili**
- Verifica i permessi sulla cartella `static/`
- Controlla che la dimensione del file non superi i limiti

**Editor non funziona**
- Verifica il caricamento delle librerie CodeMirror
- Controlla la console del browser per errori JavaScript

**Real-time non funziona**
- Verifica la connessione SocketIO
- Controlla impostazioni di firewall o proxy

### Log e Debug
- Log backend: console Flask
- Log frontend: console del browser (F12)
- Query DB: log disponibile in `db_manager.py`

---

## 📄 Licenza

Progetto sviluppato a scopo educativo. Distribuzione non consentita senza autorizzazione.

---

## 👥 Contributi

I contributi sono benvenuti! Per segnalare bug o proporre nuove funzionalità:
1. Descrivere chiaramente il problema
2. Fornire i passaggi per riprodurlo
3. Includere dettagli sull’ambiente (browser, OS, versione Python)

---

*Ultima modifica: Giugno 2025*
