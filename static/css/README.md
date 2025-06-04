# CSS Modular Structure - ConnectStudy

## File CSS Modulari

La struttura CSS è stata organizzata in file modulari per migliorare la manutenibilità e l'organizzazione del codice.

### Ordine di importazione raccomandato:

1. **base.css** - Stili globali, tipografia, layout di base, menu contestuale, breadcrumb
2. **animations.css** - Animazioni e transizioni
3. **buttons.css** - Stili per tutti i tipi di pulsanti
4. **cards.css** - Stili per cards (materie, argomenti), etichette, stati di ricerca
5. **modals.css** - Popup, modali, overlay
6. **forms.css** - Stili per form, input, upload file, radio button
7. **search.css** - Funzionalità di ricerca avanzata e filtri
8. **markdown.css** - Editor markdown, syntax highlighting, contenuto renderizzato
9. **allegati.css** - Gestione allegati e file
10. **context-menu.css** - Menu contestuali e modal di conferma
11. **responsive.css** - Media queries e stili responsive
12. **[page-specific].css** - File specifici per pagina (argomenti-page.css, argomento-page.css)

### Struttura dei file:

#### base.css (96 linee)
- Stili del body e layout globale
- Header e navigazione
- Menu contestuale delle materie
- Breadcrumb navigation
- Utility classes globali
- Placeholder per drag & drop

#### animations.css (149 linee)
- Keyframe animations
- Transizioni standard
- Effetti hover e focus

#### buttons.css (35 linee)
- Add button e Cancel button
- Stili hover e active
- Gradient e shadow effects

#### cards.css (Esteso)
- Materia cards con gestione colori
- Argomento cards con preview
- Etichette di preparazione
- Gestione drag & drop
- Stati di ricerca
- Fix per hypertext decoration

#### modals.css (Esteso)
- Popup base e popup-large
- Modal delete confirmation
- Animazioni di apparizione
- Scrollbar personalizzate
- Layout responsive

#### forms.css (Esteso)
- Form groups e input styling
- File upload con animazioni
- Radio button groups
- Select styling
- Focus e hover states

#### search.css (Esteso)
- Search filters section
- Input e select styling
- Highlight dei risultati
- Stati attivi di ricerca
- Navigation in-content
- Results styling

#### markdown.css (Nuovo - 367 linee)
- Editor markdown completo
- Tabs e preview
- Syntax highlighting avanzato
- Contenuto renderizzato
- Language-specific styling
- Scrollbar personalizzate

#### allegati.css (Nuovo - 73 linee)
- Sezione allegati
- Card allegati
- Actions (view/delete)
- Hover effects

#### context-menu.css (Nuovo - 78 linee)
- Context menu styling
- Modal confirmations
- Button styles
- Input constraints

#### responsive.css (Nuovo - 154 linee)
- Media queries per mobile/tablet
- Layout responsive
- Font size adaptations
- Button responsive behavior

### Template aggiornati:

- **index.html**: base, animations, buttons, cards, modals, forms, context-menu, responsive
- **argomenti.html**: tutti i file + argomenti-page.css
- **argomento.html**: tutti i file + argomento-page.css

### Benefici della modularizzazione:

1. **Manutenibilità**: Ogni componente ha il suo file
2. **Riusabilità**: File CSS riutilizzabili tra pagine
3. **Performance**: Possibilità di caricare solo i CSS necessari
4. **Organizzazione**: Struttura logica e chiara
5. **Debugging**: Più facile trovare e modificare stili specifici
6. **Collaborazione**: Team può lavorare su componenti diversi
7. **Caching**: Browser può cachare file singoli

### Note:

- Tutti gli stili sono stati preservati e organizzati logicamente
- L'ordine di importazione è importante per evitare conflitti CSS
- I file sono compatibili con tutti i browser moderni
