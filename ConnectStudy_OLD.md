## Esame di stato

L'idea è di fare un'applicazione che mi permetta di studiare per la fase orale dell'esame di stato, il quale si svolge nella seguente modalità:
- Lo studente è richiamato dentro l'aula, e gli viene fornito uno spunto, che potrebbe essere una citazione, una foto, una mappa, quello che è;
- Nella commissione ci sono professori che insegnano certe materie;
- Lo studente deve connettere lo spunto dato a tutte le materie della commissione entro 10 minuti oralmente.

## Funzionamento dell'applicazione

L'applicazione deve usare Python-Flask con SQLi (senza SQLAlchemy, e con un file esterno .sql per la creazione delle tabelle con sintassi SQLi) come backend. Deve usare il templating di Flask e HTML CSS e JS nel frontend per semplicità. Si ha un file db_manager per gestire le funzionalità dei database, e si importano le sue funzioni nel file principale, app.py

## Materie e argomenti

L'idea è di permettere allo studente di inserire le materie che desidera, dimostrati graficamente come dei card con colori a scelta dell'utente.

Cliccando sulla materia si va in una nuova pagina. 

Dentro la singola materia l'utente può inserire "argomenti", gli argomenti sono propri della materia e hanno un titolo e un contenuto. Gli argomenti sono comunque dei card con dei colori assegnabili. All'argomento sono assegnabili delle etichette dette, "scarsa preparazione" - "media preparazione" - "buona preparazione".

Dentro ogni argomento si apre una pagina dove si trovano le spiegazioni dell'argomento, in formato .md, con la possibilità di inserire un documento word con la spiegazione che viene trasformato in .md, un documento PDF che trasforma il testo comunque in .md oppure un documento .md che si memorizza nell'argomento. Quello che l'utente vede è ovviamente il preview, ma cliccando sull'apposito bottone di modifica si può modificare il contenuto in markdown. Quando inserisci un file .docx, PDF o .md l'app ti chiede se vuoi sostituire il contenuto dell'argomento, inserire questo nuovo contenuto all'inizio o inserirlo alla fine. Per ora non possiamo inserire foto nell'argomento ma ci lavoriamo dopo.

I file word, pdf o markdown che vengono inseriti per modificare il contenuto dell'argomento non vengono memorizzati, bensì trasformati in .md e scartati, le immagini vengono ignorate. Invece c'è una sezione "allegati" dove puoi allegare file di tutti i tipi e che puoi vedere tramite i popup.

## Collegamenti

Dentro ogni argomento, lo studente può creare dentro ogni argomento, un collegamento. Un collegamento è caratterizzato da:
- è sempre presente e si rappresenta come una card, si vedono in un menu espandibile a sinistra, come dei card;
- I card dei collegamenti presenti nel menu di sinistra devono, al click su di loro, aprono un popup che contiene tutti i dettagli riguardanti il singolo collegamento, devono avere lo stesso stile dei popup già fatti, e la sezione dove vedi i dettagli ha un'altezza massima con uno scroll in caso il contenuto sia più lungo. Il modal deve avere una lunghezza massima con uno scroll anch'esso.
- Un collegamento è formato da un titolo, dagli argomenti estremi, che possono essere della stessa materia o di diversa materia, e il modo di collegamento, che sarebbe un testo che spiega come entrambi gli argomenti sono connessi. Questo testo lo si vede tramite un un bottone che in realtà è un rettangolo che si trova sotto il titolo, cliccando su questo esce un popup chiudibile che contiene il testo della spiegazione. 
- Se sei dentro l'argomento nella pagina apposita, C'è un bottone che si chiama collega, e cliccando su quello ti apre un popup con un input per il titolo, due slot, uno già riempito con l'argomento in cui si era dentro ma si può annullare. Cliccando su un bottone che ti permette di riempire lo slot dell'argomento dentro il collegamento, esce un altro popup con i card delle materia, cliccando sulla materia puoi tornare indietro di nuovo per le materie oppure scegliere un argomento, dopo aver scelto l'argomento questo viene messo nello slot vuoto e si chiude il popup delle materie e si trova solo con il popup dell'inserimento del collegamento. Successivamente lo studente può inserire tramite un input apposito i dettagli sul collegamento. Si può cliccare annulla o chiudere i popup per eliminare le modifica o cliccare salva per salvare il collegamento
- Il bottone "collega" si trova anche nel menu di sinistra, ma con i slot degli argomenti vuoti quando apri il popup.
- Ogni collegamento può essere assegnato un etichetta: "collegamento forzato" - "collegamento media qualità" - "collegmento buona qualità" - "collegamento alta qualità";
- Dentro ogni materia puoi vedere un bottone che si chiama collegamenti, se lo clicchi, ti manda in una pagina apposita dove carica i card del collegamento, cliccando sul collegamento esce un popup con i dettagli

## Sezione simulazioni

C'è anche una sezione simulazioni accessibile da ovunque tramite un bottone.

Cliccando sul bottone si apre una pagina nuova. Dentro questa pagina si hanno i cosiddetti simulazioni. Lo studente può creare queste simulazioni che venono rappresentati da apposite card. Ogni simulazione contiene:
- Lo spunto, che potrebbe essere un immagine oppure del testo, se è un immagine lo studente può inserirlo, se è un testo lo studente può scriverlo.

Avendo inserito lo spunto si è creata una simulazione. Dentro la simulazione puoi inserire i cosiddetti fili di collegamento, dentro ogni filo puoi inserire i cosiddetti collegamentiSimulazione tramite un bottone apposito, una tabella separata ma con duplice funzionamento rispetto al collegamento normale e propria solo della simulazione, puoi usare comunque collegamenti normali, che compilano comunque un nuovo record in collegamntiSimulazione. Questi qua possono partitre sia dallo spunto della simulazione, nel quale caso il campo dell'argomento 1 sarà null, sia da un'altro argomento, altrimenti funzionano esattamente come gli altri collegamenti normali e appaiono dentro la simulazione come dei card. Se si vede nella visualizzazione del collegmanto che arogmento 1 è null, allora si dice che è connesso allo spunto. 

La struttura nel db sarebbe: Simulazione (con immagine), filo (proprio della simulazione), collegamentoSimulazione (proprio del filo). Ogni simulazione può avere più linee, e viceversa (cardinalità N:M), e lo stesso anche per i fili-collegamentiSimulazione.

All'inserimento del collegamento all'interno del filo di collegamento, l'utente è garantito la possibilità di scegliere di importare un "collegamento esterno", o altre alternative discusse di seguito, dove i collegamenti esterni sono i collegamenti normali, mentre i collegamenti simulazioni sono i collegamenti nella tabella CollegamentoSimulazione. Se un utente sceglie di usare un collegamento esterno, al salvataggio del collegamento nel filo, si salva una diretta copia del database nella tabella CollegamentoSimulazione, ovviamente con la chiave esterna del filo in cui si è, e si salva quella nel filo, non il collegamento normale, quindi un collegamento normale non deve avere a che fare con il la simulazione. Altre alternative sono: di importare un "collegamento di simulazione", non necessitando di copiare i dati, oppure la creazione di un collegamento all'interno della simulazione, esattamente come si creerebbe un collegamento normale, solo che si salva nel filo in cui è e si crea semplicemente un record di CollegamentoSimulazione.

I fili di collegamento hanno nomi semplici, filo-id_simulazione-id_filo, ricavabile quindi automaticamente.

Ogni collegamento dentro il filo è dotato di un numero d'ordine all'interno del filo, il display dei card dei collegamenti avviene secondo questo numero d'ordine, e nel card ci sono queste due freccioline, uno diretto verso sopra e l'altro verso sotto, solo così l'utente può cambiare il numero d'ordine. Quando cambi il numero d'ordine, scambi posizioni con quello che poi avrebbe il tuo stesso numero, per esempio se io abbasso al numero 2, il collegamento che era numero 2 diventa numero tre, e quello che ho scelto diveta 2. Viceversa se dovessi essere 3, e alzassi a 4, il 4 diventerebbe il 3 e quello che ho scelto diventa 4.

Il card del collegamento non è grande come nella pagina di collegamenti, è più ridotta, i dettagli riguardo il collegamento però si vedono con un bottone come con il card nella pagina collegamenti.

E' presente una ricerca dinamica, come nella pagina di collegamenti, per ogni filo di collegamenti. Si cerca il titolo del collegamento, i dettagli e gli argomenti coinvolti, con un bottone che pulisce i filtri

## Dettagli tecnici

Quando inserisci una materia, argomento o collegamento, le sezioni apposite vengono aggiornati tramite un polling automaticamente, in modo tale da non causare il refresh della pagina ogni volta e di avere i dati sempre aggiornati.

Le card delle materie nella loro pagina possono essere riordinati con drag e drop. Questo ordine viene salvato con un attributo nel db alla materia, secondo le quali viene disposta la materia nella pagina.

C'è una cartella static che contiene altre cartelle per le immagini. Le immagini delle simulazioni vengono messi in static/simulazioni, prendono nomi univochi, e il loro percorso viene memorizzato nel database per il singolo spunto per riprenderlo.

Mentre si è nella pagina di argomenti o collegamenti, ci sono sempre due input che aiutano a implementare una ricerca live, una per il titolo, e una per il testo dell'argomento oppure i dettagli del collegamento. Questa ricerca c'è anche durante l'inserimento di un argomento dentro i collegamenti (normali o di simulazione). Le etichette di preparazione ad un argomento o qualità di un collegamento sono anche filtrabili tramite un input list.

Per il polling usa Flask-SocketIO per l'aggiornamento in tempo reale solo quando è necessario, e limita il polling a 15 secondi solo nelle pagine già attive.

Dovrebbe essere possibile, laddove si debba scrivere in markdown, mettere a schermo intero. Dev'essere un editor di testo di tipologia katex per una migliore esperienza all'utente, e deve usare anche i colori per i linguaggi di programmazione.

