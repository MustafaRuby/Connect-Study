# ConnectStudy

## Panoramica

**ConnectStudy** è un'applicazione web avanzata progettata per preparare gli studenti all'esame orale di maturità italiana. L'applicazione facilita la gestione dei contenuti disciplinari, la creazione di collegamenti interdisciplinari e offre simulazioni realistiche dell'esame.

Durante l'orale dell'esame di stato, lo studente riceve uno spunto iniziale (citazione, immagine, grafico) e deve costruire collegamenti interdisciplinari tra tutte le materie coinvolte nel tempo limitato di 10 minuti. ConnectStudy replica questo processo, permettendo agli studenti di esercitarsi costantemente su percorsi multidisciplinari, organizzare i propri argomenti per materia e simulare le dinamiche reali dell'esame con spunti testuali o visivi.

## Caratteristiche Principali

### Gestione Contenuti
L'applicazione consente l'inserimento e l'organizzazione sistematica degli argomenti per ciascuna materia, con supporto completo per contenuti in formato Markdown, incluse formule matematiche tramite KaTeX. Gli studenti possono importare file `.docx`, `.pdf` e `.md` che vengono automaticamente convertiti in Markdown, e possono allegare file di supporto di qualsiasi formato.

### Editor Avanzato
L'editor integrato CodeMirror offre evidenziazione della sintassi, modalità fullscreen per la concentrazione massima e anteprima live del Markdown. Gli studenti possono modificare contenuti con controlli professionali per salvataggio e annullamento delle operazioni.

### Sistema di Collegamenti
Il cuore dell'applicazione risiede nel sistema di collegamenti interdisciplinari. Gli studenti possono creare connessioni logiche tra argomenti di materie diverse, assegnare etichette di qualità ai collegamenti e utilizzare popup interattivi per la gestione completa delle relazioni tra contenuti.

### Simulazioni Esame
Le simulazioni replicano fedelmente l'esperienza dell'esame orale, con timer integrato di 10 minuti, spunti testuali o visivi randomizzati e la possibilità di costruire percorsi di collegamento in tempo reale.

### Esportazione Professionale
ConnectStudy include funzionalità avanzate di esportazione che permettono di generare documenti Markdown (.md) e Word (.docx) formattati professionalmente. L'esportazione Word converte intelligentemente headers, paragrafi e liste mantenendo la struttura originale del contenuto. Le funzioni sono accessibili tramite il menu azioni laterale con download automatico e gestione completa degli errori.

## Architettura Tecnica

### Backend
L'applicazione utilizza **Python Flask** come framework principale con database **SQLite** e gestione modularizzata delle query tramite `db_manager.py`. Gli aggiornamenti in tempo reale sono gestiti da **Flask-SocketIO** con polling intelligente attivo solo sulle pagine aperte. Il sistema di file processing supporta conversione automatica di documenti Word, PDF e Markdown tramite le librerie `python-docx`, `PyPDF2`, `markdown` e `beautifulsoup4`.

### Frontend
L'interfaccia utilizza **Jinja2** come template engine con CSS3 modulare per componenti separati e JavaScript vanilla strutturato. L'editor CodeMirror integra evidenziazione della sintassi, supporto KaTeX e modalità fullscreen. L'interfaccia è completamente responsiva con drag & drop per riordinamento, card interattive e ricerche live istantanee.

## Struttura del Progetto

```
ConnectStudy/
├── app.py                 # Applicazione Flask principale
├── db_manager.py          # Gestione query database
├── db.sql                 # Schema database SQLite
├── requirements.txt       # Dipendenze Python
├── static/                # Risorse statiche
│   ├── css/              # Fogli di stile modulari
│   ├── js/               # JavaScript strutturato
│   ├── libs/             # Librerie esterne
│   ├── simulazioni/      # Immagini per simulazioni
│   └── uploads/          # File allegati utenti
└── templates/            # Template HTML Jinja2
```

## Installazione e Setup

### Prerequisiti
- Python 3.8+
- pip (Python package manager)

### Installazione Rapida
```bash
cd ConnectStudy
pip install -r requirements.txt
python app.py
```

L'applicazione sarà disponibile su `localhost:5000` con database SQLite locale (`connectstudy.db`) e file statici serviti direttamente da Flask.

## Schema Database

Il database è strutturato in modo ottimizzato per supportare le relazioni complesse tra materie, argomenti, collegamenti e simulazioni:

### Entità Principali
- **Materie**: gestiscono colori personalizzati e ordinamento drag & drop
- **Argomenti**: contengono contenuto Markdown, etichette di preparazione e colori personalizzati  
- **Collegamenti**: definiscono relazioni tra argomenti con dettagli e etichette di qualità
- **Simulazioni**: includono spunti testuali/visivi e fili di collegamento ordinabili
- **Allegati**: supportano file di qualsiasi formato separati dal contenuto Markdown

### Funzionalità Avanzate
Gli aggiornamenti in tempo reale propagano automaticamente le modifiche tramite Flask-SocketIO. Il sistema di file gestisce conversioni automatiche, pulizia dei temporanei e separazione tra contenuti e allegati. Le ricerche live operano su titoli, contenuti e metadati con integrazione completa dei filtri.

## Funzionalità Operative

### Gestione Argomenti
Gli argomenti sono organizzati per materia con etichette di preparazione (scarsa, media, buona) e supporto per contenuti Markdown complessi. L'editor integrato permette modifica diretta con anteprima live, importazione di file esterni e gestione di allegati separati dal contenuto principale.

### Collegamenti Interdisciplinari
Il sistema di collegamenti facilita la creazione di relazioni logiche tra argomenti di materie diverse. Ogni collegamento include titolo, spiegazione dettagliata e etichetta di qualità, con interfaccia popup per gestione completa e navigazione visuale tra le connessioni.

### Simulazioni Esame
Le simulazioni replicano l'esperienza reale dell'esame orale con spunti randomizzati, timer di 10 minuti e costruzione di percorsi di collegamento in tempo reale. Gli studenti possono creare fili tematici, riordinare collegamenti tramite drag & drop e visualizzare statistiche delle performance.

## Troubleshooting

### Problemi Comuni
**Database non inizializzato**: `python -c "import db_manager; db_manager.init_db()"`  
**Editor non responsivo**: Verificare caricamento librerie CodeMirror nella console browser  
**Real-time inattivo**: Controllare connessione SocketIO e impostazioni firewall  
**Esportazione fallita**: Verificare installazione `python-docx` e `beautifulsoup4`, controllare permessi file temporanei

### Debug
I log backend sono disponibili nella console Flask, mentre i log frontend sono accessibili tramite console browser (F12). Le query database includono logging dettagliato in `db_manager.py`.

---

**ConnectStudy** - Preparazione professionale per l'esame di maturità  
*Sviluppato per scopi educativi - Giugno 2025*
