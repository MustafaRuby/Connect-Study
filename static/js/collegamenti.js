 const socket = io();
    let currentArgomentoSlot = null;
    let editingCollegamentoId = null;

    // Socket events
    socket.on('update_collegamenti', function() {
        location.reload();
    });    // Search functionality
    let searchTimeout;
    let allCollegamenti = [];
    
    function setupSearch() {
        const searchTitolo = document.getElementById('search-titolo');
        const searchDettagli = document.getElementById('search-dettagli');
        const searchArgomenti = document.getElementById('search-argomenti');
        const filterQualita = document.getElementById('filter-qualita');
        const filterMateria = document.getElementById('filter-materia');

        function performSearch() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const params = new URLSearchParams({
                    titolo: searchTitolo.value,
                    dettagli: searchDettagli.value,
                    argomenti: searchArgomenti ? searchArgomenti.value : '',
                    etichetta_qualita: filterQualita.value,
                    materia: filterMateria ? filterMateria.value : ''
                });
                fetch('/api/search_collegamenti?' + params)
                    .then(response => response.json())
                    .then(collegamenti => {
                        allCollegamenti = collegamenti.map(collegamento => ({
                            ...collegamento,
                            originalTitle: collegamento.titolo,
                            originalDettagli: collegamento.dettagli || '',
                            originalArgomento1: collegamento.argomento1_titolo,
                            originalArgomento2: collegamento.argomento2_titolo
                        }));
                        updateCollegamentiGrid(collegamenti);
                    });
            }, 300);
        }

        searchTitolo.addEventListener('input', performSearch);
        searchDettagli.addEventListener('input', performSearch);
        if (searchArgomenti) searchArgomenti.addEventListener('input', performSearch);
        filterQualita.addEventListener('change', performSearch);
        if (filterMateria) filterMateria.addEventListener('change', performSearch);
    }
    
    // Utility functions for text highlighting
    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    function highlightText(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<mark class="search-highlight">$1</mark>');
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }    function cleanPreviewText(text) {
        if (!text) return '';
        return text
            .replace(/```[\w]*\n[\s\S]*?\n```/g, '[Code Block]')
            .replace(/`([^`]+)`/g, '$1')
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\*(.*?)\*/g, '$1')
            .replace(/#{1,6}\s/g, '')
            .replace(/!\[([^\]]*)\]\([^\)]*\)/g, '[Image: $1]')
            .replace(/\[([^\]]*)\]\([^\)]*\)/g, '$1')
            .replace(/^\s*[-*+]\s/gm, '• ')
            .replace(/^\s*\d+\.\s/gm, '• ')
            .replace(/>\s/g, '')
            .replace(/\$\$[\s\S]*?\$\$/g, '[Math Formula]')
            .replace(/\$([^$\n]+)\$/g, '[Math: $1]')
            .replace(/\n+/g, ' ')
            .replace(/\s+/g, ' ')
            .replace(/[^\w\s\u00C0-\u024F\u1E00-\u1EFF.,!?;:()\[\]{}'"«»""''–—]/g, '')
            .trim();
    }

    function createCleanPreview(content, maxLength = 200) {
        if (!content) return '';
        const cleanText = cleanPreviewText(content);
        if (cleanText.length <= maxLength) {
            return cleanText;
        }
        let breakPoint = maxLength;
        const lastSpace = cleanText.lastIndexOf(' ', maxLength);
        const lastPunctuation = Math.max(
            cleanText.lastIndexOf('.', maxLength),
            cleanText.lastIndexOf('!', maxLength),
            cleanText.lastIndexOf('?', maxLength)
        );
        if (lastPunctuation > maxLength - 50) {
            breakPoint = lastPunctuation + 1;
        } else if (lastSpace > maxLength - 30) {
            breakPoint = lastSpace;
        }
        return cleanText.substring(0, breakPoint).trim() + '...';
    }

    function updateCollegamentiGrid(collegamenti) {
        const grid = document.getElementById('collegamenti-grid');
        const titleQuery = document.getElementById('search-titolo').value.toLowerCase().trim();
        const dettagliQuery = document.getElementById('search-dettagli').value.toLowerCase().trim();
        const argomentiQuery = document.getElementById('search-argomenti') ? document.getElementById('search-argomenti').value.toLowerCase().trim() : '';
        const materiaFilter = document.getElementById('filter-materia') ? document.getElementById('filter-materia').value.toLowerCase().trim() : '';
        let filtered = collegamenti;
        // Filtro lato client per materia se necessario (in caso l'API non lo gestisca)
        if (materiaFilter) {
            filtered = filtered.filter(c =>
                c.materia1_nome.toLowerCase() === materiaFilter ||
                c.materia2_nome.toLowerCase() === materiaFilter
            );
        }
        grid.innerHTML = filtered.length === 0 ? `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-icon">🔍</div>
                <h3>Nessun collegamento trovato</h3>
                <p>Nessun collegamento corrisponde ai criteri di ricerca.</p>
            </div>
        ` : filtered.map(collegamento => {
            // Evidenziazione titolo
            let highlightedTitle = collegamento.titolo;
            if (titleQuery) highlightedTitle = highlightText(escapeHtml(collegamento.titolo), titleQuery);
            // Evidenziazione argomenti
            let highlightedArgomento1 = collegamento.argomento1_titolo;
            let highlightedArgomento2 = collegamento.argomento2_titolo;
            if (argomentiQuery) {
                highlightedArgomento1 = highlightText(escapeHtml(collegamento.argomento1_titolo), argomentiQuery);
                highlightedArgomento2 = highlightText(escapeHtml(collegamento.argomento2_titolo), argomentiQuery);
            }
            // Evidenziazione dettagli/preview
            let dettagliPreview = '';
            let dettagliSnippet = '';
            if (collegamento.dettagli) {
                const cleanDettagli = cleanPreviewText(collegamento.dettagli);
                if (dettagliQuery) {
                    const lowerDettagli = collegamento.dettagli.toLowerCase();
                    const queryPos = lowerDettagli.indexOf(dettagliQuery.toLowerCase());
                    if (queryPos !== -1) {
                        const snippetStart = Math.max(0, queryPos - 50);
                        const snippetEnd = Math.min(collegamento.dettagli.length, queryPos + dettagliQuery.length + 50);
                        let snippet = collegamento.dettagli.substring(snippetStart, snippetEnd);
                        if (snippetStart > 0) snippet = '...' + snippet;
                        if (snippetEnd < collegamento.dettagli.length) snippet = snippet + '...';
                        const highlightedSnippet = highlightText(escapeHtml(snippet), dettagliQuery);
                        dettagliSnippet = `
                            <div class="search-result">
                                <div class="search-snippet">
                                    <strong>Trovato in:</strong> ${highlightedSnippet}
                                </div>
                            </div>
                        `;
                    }
                }
                if (!dettagliSnippet) {
                    dettagliPreview = `
                        <div class="search-result">
                            <div class="search-snippet">
                                ${escapeHtml(createCleanPreview(collegamento.dettagli))}
                            </div>
                        </div>
                    `;
                }
            }
            return `
            <div class="collegamento-card" data-id="${collegamento.id}">
                <div class="collegamento-header">
                    <h3 class="collegamento-title">${highlightedTitle}</h3>
                    <div class="collegamento-actions">
                        <button class="btn-icon" onclick="editCollegamento(${collegamento.id})" title="Modifica">
                            <img src="/static/icons/modify-icon.svg" alt="Modifica">
                        </button>
                        <button class="btn-icon btn-danger" onclick="deleteCollegamento(${collegamento.id})" title="Elimina">
                            <img src="/static/icons/delete-icon.svg" alt="Elimina">
                        </button>
                    </div>
                </div>
                <div class="collegamento-argomenti">
                    <div class="argomento-tag" style="border: 2.5px solid ${collegamento.materia1_colore}">
                        <a href="/argomento/${collegamento.id_argomento1}">
                            ${highlightedArgomento1}
                        </a>
                        <span class="materia-name">${collegamento.materia1_nome}</span>
                    </div>
                    <div class="collegamento-arrow">⟷</div>
                    <div class="argomento-tag" style="border: 2.5px solid ${collegamento.materia2_colore}">
                        <a href="/argomento/${collegamento.id_argomento2}">
                            ${highlightedArgomento2}
                        </a>
                        <span class="materia-name">${collegamento.materia2_nome}</span>
                    </div>
                </div>
                ${dettagliSnippet || dettagliPreview}
                ${collegamento.dettagli && !dettagliSnippet ? `
                <div class="collegamento-dettagli">
                    <button class="dettagli-toggle" onclick="toggleDettagli(${collegamento.id})">
                        <span class="icon">🔎</span> Visualizza dettagli
                    </button>
                </div>
                ` : ''}
                <div class="collegamento-footer">
                    <span class="etichetta-qualita ${collegamento.etichetta_qualita.replace(/ /g, '-').toLowerCase()}">
                        ${collegamento.etichetta_qualita.charAt(0).toUpperCase() + collegamento.etichetta_qualita.slice(1)}
                    </span>
                </div>
            </div>
        `;
        }).join('');
        
        // Add search results info
        updateSearchResults(filtered.length);
    }
    
    function updateSearchResults(count) {
        // Remove existing results info
        const existingInfo = document.querySelector('.search-results-info');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        const searchTitolo = document.getElementById('search-titolo').value;
        const searchDettagli = document.getElementById('search-dettagli').value;
        const filterQualita = document.getElementById('filter-qualita').value;
        
        // Only show results info if search/filter is active
        if (searchTitolo || searchDettagli || filterQualita) {
            const resultsInfo = document.createElement('div');
            resultsInfo.className = 'search-results-info';
            resultsInfo.innerHTML = `
                <span class="results-count">
                    Trovati ${count} collegamenti
                </span>
            `;
            
            const content = document.querySelector('.content');
            content.insertBefore(resultsInfo, content.firstChild);
        }
    }

    // Modal functions
    function showCollegamentoModal(argomentoId = null) {
        editingCollegamentoId = null;
        document.getElementById('modal-title').textContent = 'Nuovo Collegamento';
        document.getElementById('collegamento-form').reset();
        document.getElementById('collegamento-id').value = '';
        
        // Reset argomento selectors
        resetArgomentoSelector(1);
        resetArgomentoSelector(2);
        
        // Pre-fill if coming from an argomento page
        if (argomentoId) {
            // This would be implemented when calling from argomento page
        }
        
        document.getElementById('collegamento-modal').style.display = 'flex';
    }

    function closeCollegamentoModal() {
        document.getElementById('collegamento-modal').style.display = 'none';
    }

    function editCollegamento(id) {
        editingCollegamentoId = id;
        document.getElementById('modal-title').textContent = 'Modifica Collegamento';
        
        fetch(`/api/collegamenti`)
            .then(response => response.json())
            .then(collegamenti => {
                const collegamento = collegamenti.find(c => c.id === id);
                if (collegamento) {
                    document.getElementById('collegamento-id').value = id;
                    document.getElementById('titolo').value = collegamento.titolo;
                    document.getElementById('dettagli').value = collegamento.dettagli || '';
                    document.getElementById('etichetta_qualita').value = collegamento.etichetta_qualita;
                    
                    // Set selected argomenti
                    setSelectedArgomento(1, collegamento.id_argomento1, collegamento.argomento1_titolo, collegamento.materia1_nome);
                    setSelectedArgomento(2, collegamento.id_argomento2, collegamento.argomento2_titolo, collegamento.materia2_nome);
                    
                    document.getElementById('collegamento-modal').style.display = 'flex';
                }
            });
    }

    function deleteCollegamento(id) {
        if (confirm('Sei sicuro di voler eliminare questo collegamento?')) {
            fetch(`/delete_collegamento/${id}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    document.querySelector(`[data-id="${id}"]`).remove();
                }
            });
        }
    }

    function toggleDettagli(id) {
        fetch(`/api/collegamenti`)
            .then(response => response.json())
            .then(collegamenti => {
                const collegamento = collegamenti.find(c => c.id === id);
                if (collegamento && collegamento.dettagli) {
                    document.getElementById('dettagli-content').innerHTML = marked.parse(collegamento.dettagli);
                    document.getElementById('dettagli-modal').style.display = 'flex';
                }
            });
    }

    function closeDettagliModal() {
        document.getElementById('dettagli-modal').style.display = 'none';
    }    // Argomento selection
    function selectArgomento(slot) {
        currentArgomentoSlot = slot;
        document.getElementById('materie-selector-modal').style.display = 'flex';
        loadMaterie();
    }    function closeMaterieSelector() {
        document.getElementById('materie-selector-modal').style.display = 'none';
        
        // Reset modal views
        const materieList = document.getElementById('materie-list');
        const argomentiList = document.getElementById('argomenti-list');
        if (materieList) materieList.style.display = 'block';
        if (argomentiList) argomentiList.style.display = 'none';
        
        currentArgomentoSlot = null;
    }

    function clearArgomento(slot) {
        resetArgomentoSelector(slot);
    }

    function resetArgomentoSelector(slot) {
        const selectedDiv = document.getElementById(`argomento${slot}-selected`);
        selectedDiv.className = 'argomento-selected';
        selectedDiv.innerHTML = '<span class="placeholder">Seleziona argomento</span><button type="button" class="cancel-btn" onclick="clearArgomento(' + slot + ')">&times;</button>';
        document.getElementById(`id_argomento${slot}`).value = '';
    }

    function setSelectedArgomento(slot, id, titolo, materia) {
        const selectedDiv = document.getElementById(`argomento${slot}-selected`);
        selectedDiv.className = 'argomento-selected has-selection';
        selectedDiv.innerHTML = `
            <div class="selected-info">
                <div class="selected-title">${titolo}</div>
                <div class="selected-materia">${materia}</div>
            </div>
            <button type="button" class="cancel-btn" onclick="clearArgomento(${slot})">&times;</button>
        `;
        document.getElementById(`id_argomento${slot}`).value = id;
    }

    function toggleMateriaArgomenti(materiaId) {
        const argomentiDiv = document.getElementById(`argomenti-${materiaId}`);
        const icon = document.querySelector(`[onclick="toggleMateriaArgomenti(${materiaId})"] .expand-icon`);
        
        if (argomentiDiv.style.display === 'none') {
            argomentiDiv.style.display = 'block';
            icon.classList.add('expanded');
            loadMateriaArgomenti(materiaId);
        } else {
            argomentiDiv.style.display = 'none';
            icon.classList.remove('expanded');
        }
    }

    function loadMateriaArgomenti(materiaId) {
        fetch(`/api/argomenti/${materiaId}`)
            .then(response => response.json())
            .then(argomenti => {
                const argomentiDiv = document.getElementById(`argomenti-${materiaId}`);
                argomentiDiv.innerHTML = argomenti.map(argomento => `
                    <div class="argomento-item" onclick="selectArgomentoFromList(${argomento.id}, '${argomento.titolo}', '${argomento.id_materia}')">
                        <div class="argomento-item-title">${argomento.titolo}</div>
                        <span class="argomento-item-preparazione preparazione-${argomento.etichetta_preparazione.split(' ')[0]}">
                            ${argomento.etichetta_preparazione}
                        </span>
                    </div>
                `).join('');
            });
    }    function loadAllMaterieArgomenti() {
        // Load all argomenti for search functionality
        fetch('/api/materie')
            .then(response => response.json())
            .then(materie => {
                materie.forEach(materia => {
                    const argomentiDiv = document.getElementById(`argomenti-${materia.id}`);
                    if (argomentiDiv && argomentiDiv.style.display === 'block') {
                        loadMateriaArgomenti(materia.id);
                    }
                });
            });
    }    function loadMaterie() {
        fetch('/api/materie')
            .then(response => response.json())
            .then(materie => {
                const materieList = document.getElementById('materie-list');
                if (!materieList) {
                    console.error('❌ materie-list element not found');
                    return;
                }
                
                materieList.innerHTML = '';
                
                materie.forEach(materia => {
                    const materiaCard = document.createElement('div');
                    materiaCard.className = 'materia-card';
                    materiaCard.style.backgroundColor = materia.colore;
                    materiaCard.innerHTML = `
                        <h3>${materia.nome}</h3>
                    `;
                    materiaCard.onclick = () => loadArgomenti(materia.id, materia.nome, materia.colore);
                    materieList.appendChild(materiaCard);
                });
            })
            .catch(error => console.error('Error loading materie:', error));
    }    function loadArgomenti(materiaId, materiaNome, materiaColore) {
        fetch(`/api/argomenti/materia/${materiaId}`)
            .then(response => response.json())
            .then(argomenti => {
                const argomentiGrid = document.getElementById('argomenti-grid');
                if (!argomentiGrid) {
                    console.error('❌ argomenti-grid element not found');
                    return;
                }
                
                argomentiGrid.innerHTML = '';
                
                argomenti.forEach(argomento => {
                    const argomentoCard = document.createElement('div');
                    argomentoCard.className = 'argomento-card';
                    argomentoCard.innerHTML = `
                        <div class="argomento-header">
                            <h4>${argomento.titolo}</h4>
                            <span class="materia-badge" style="background-color: ${materiaColore}">${materiaNome}</span>
                        </div>
                        <div class="argomento-preview">${argomento.contenuto_md ? argomento.contenuto_md.substring(0, 100) + '...' : 'Nessun contenuto'}</div>
                    `;
                    argomentoCard.onclick = () => selectArgomentoFromList(argomento.id, argomento.titolo, argomento.id_materia);
                    argomentiGrid.appendChild(argomentoCard);
                });
                  // Switch views
                const materieList = document.getElementById('materie-list');
                const argomentiList = document.getElementById('argomenti-list');
                if (materieList) materieList.style.display = 'none';
                if (argomentiList) argomentiList.style.display = 'block';
            })
            .catch(error => console.error('Error loading argomenti:', error));
    }

    function showMaterieList() {
        const materieList = document.getElementById('materie-list');
        const argomentiList = document.getElementById('argomenti-list');
        
        if (materieList) {
            materieList.style.display = 'block';
        }
        
        if (argomentiList) {
            argomentiList.style.display = 'none';
        }
    }

    function selectArgomentoFromList(id, titolo, materiaId) {
        if (currentArgomentoSlot) {
            // Get materia name
            fetch('/api/materie')
                .then(response => response.json())                .then(materie => {
                    const materia = materie.find(m => m.id == materiaId);
                    setSelectedArgomento(currentArgomentoSlot, id, titolo, materia.nome);
                    closeMaterieSelector();
                });
        }
    }

    // Form submission
    document.getElementById('collegamento-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const id = document.getElementById('collegamento-id').value;
        
        // Validation
        if (!formData.get('id_argomento1') || !formData.get('id_argomento2')) {
            alert('Devi selezionare entrambi gli argomenti');
            return;
        }
        
        if (formData.get('id_argomento1') === formData.get('id_argomento2')) {
            alert('Non puoi collegare un argomento a se stesso');
            return;
        }
        
        const url = id ? `/update_collegamento/${id}` : '/add_collegamento';
        
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                closeCollegamentoModal();
                location.reload();
            }
        });    });
      // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        setupSearch();
        
        // Setup clear filters button
        document.getElementById('clear-filters').addEventListener('click', clearFilters);
          // Make sure modals are initially hidden with display: none
        document.getElementById('dettagli-modal').style.display = 'none';
        document.getElementById('collegamento-modal').style.display = 'none';
        document.getElementById('materie-selector-modal').style.display = 'none';
        
        // Close modals when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    });// Make functions globally available
    window.showCollegamentoModal = showCollegamentoModal;
    window.closeCollegamentoModal = closeCollegamentoModal;
    window.editCollegamento = editCollegamento;
    window.deleteCollegamento = deleteCollegamento;
    window.toggleDettagli = toggleDettagli;    window.closeDettagliModal = closeDettagliModal;    window.selectArgomento = selectArgomento;
    window.closeMaterieSelector = closeMaterieSelector;
    window.clearArgomento = clearArgomento;
    window.toggleMateriaArgomenti = toggleMateriaArgomenti;
    window.selectArgomentoFromList = selectArgomentoFromList;
    window.showMaterieList = showMaterieList;
    window.loadMaterie = loadMaterie;
    window.loadArgomenti = loadArgomenti;
    
    // Clear all filters function
    function clearFilters() {
        document.getElementById('search-titolo').value = '';
        document.getElementById('search-dettagli').value = '';
        if (document.getElementById('search-argomenti')) document.getElementById('search-argomenti').value = '';
        document.getElementById('filter-qualita').value = '';
        if (document.getElementById('filter-materia')) document.getElementById('filter-materia').value = '';
        // Trigger search to reset results
        const searchEvent = new Event('input');
        document.getElementById('search-titolo').dispatchEvent(searchEvent);
    }