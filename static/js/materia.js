// === LEFT SIDEBAR FUNCTIONALITY ===
        function toggleSidebar() {
            const sidebar = document.getElementById('left-sidebar');
            const mainContent = document.querySelector('.main-content');
            const toggleIcon = document.querySelector('.toggle-icon');
            
            sidebar.classList.toggle('open');
            mainContent.classList.toggle('sidebar-open');
            
            // Change icon based on sidebar state
            if (sidebar.classList.contains('open')) {
                toggleIcon.textContent = '✖️';
                loadSidebarConnections();
                        } else {
                toggleIcon.textContent = '📋';
            }
        }

        function showCollegamentoModalEmpty() {
            window.location.href = '/collegamenti';
        }

        function loadSidebarConnections() {
            fetch('/api/collegamenti')
                .then(response => response.json())
                .then(collegamenti => {
                    updateSidebarConnections(collegamenti);
                })
                .catch(error => console.error('Error loading sidebar connections:', error));
        }

        function updateSidebarConnections(collegamenti) {
            const sidebarMaterie = document.getElementById('sidebar-materie');
            
            // Group connections by materia
            const materieMap = new Map();
            
            collegamenti.forEach(collegamento => {
                // Add to materia 1
                const materia1 = collegamento.materia1_nome;
                if (!materieMap.has(materia1)) {
                    materieMap.set(materia1, {
                        nome: materia1,
                        colore: collegamento.materia1_colore,
                        collegamenti: []
                    });
                }
                materieMap.get(materia1).collegamenti.push(collegamento);
                
                // Add to materia 2 if different
                const materia2 = collegamento.materia2_nome;
                if (materia2 !== materia1) {
                    if (!materieMap.has(materia2)) {
                        materieMap.set(materia2, {
                            nome: materia2,
                            colore: collegamento.materia2_colore,
                            collegamenti: []
                        });
                    }
                    materieMap.get(materia2).collegamenti.push(collegamento);
                }
            });
            
            // Generate sidebar HTML
            sidebarMaterie.innerHTML = '';
            
            if (materieMap.size === 0) {
                sidebarMaterie.innerHTML = '<p class="no-connections">Nessun collegamento trovato</p>';
                return;
            }
            
            materieMap.forEach((materiaData, materiaNome) => {
                const materiaDiv = document.createElement('div');
                materiaDiv.className = 'sidebar-materia';
                materiaDiv.innerHTML = `
                    <div class="sidebar-materia-header" onclick="toggleMateriaConnections(this)">
                        <div class="sidebar-materia-title">
                            <span class="sidebar-materia-badge" style="background-color: ${materiaData.colore}"></span>
                            ${materiaNome}
                        </div>
                        <span class="sidebar-materia-toggle">▶</span>
                    </div>
                    <div class="sidebar-search-group">
                        <div class="sidebar-search">
                            <input type="text" class="sidebar-search-input" placeholder="Cerca collegamento..." oninput="filterCollegamenti(this, 'collegamento')">
                            <img src="/static/icons/search-icon.svg" class="sidebar-search-icon" width="16" height="16">
                        </div>
                        <div class="sidebar-search">
                            <input type="text" class="sidebar-search-input" placeholder="Cerca argomento..." oninput="filterCollegamenti(this, 'argomento')">
                            <img src="/static/icons/search-icon.svg" class="sidebar-search-icon" width="16" height="16">
                        </div>
                    </div>
                    <div class="sidebar-collegamenti">
                        ${materiaData.collegamenti.map(conn => `
                            <div class="sidebar-collegamento" data-titolo="${conn.titolo.toLowerCase()}" data-argomenti="${conn.argomento1_titolo.toLowerCase()} ${conn.argomento2_titolo.toLowerCase()}" onclick="showSidebarCollegamentoModal(${conn.id})">
                                <div class="collegamento-title">${conn.titolo}</div>
                                <div class="collegamento-endpoints">
                                    ${conn.argomento1_titolo} ↔ ${conn.argomento2_titolo}
                                </div>
                                <div class="collegamento-quality quality-${conn.etichetta_qualita.replace(/\s+/g, '-').replace('collegamento-', '')}">${conn.etichetta_qualita}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
                
                sidebarMaterie.appendChild(materiaDiv);
            });
        }

        function toggleMateriaConnections(headerElement) {
            const materiaDiv = headerElement.parentElement;
            materiaDiv.classList.toggle('expanded');
        }        
        function viewCollegamento(collegamentoId) {
            window.location.href = `/collegamento/${collegamentoId}`;
        }
        
        function filterCollegamenti(inputElement, filterType) {
            const searchTerm = inputElement.value.toLowerCase().trim();
            const materiaDiv = inputElement.closest('.sidebar-materia');
            const collegamenti = materiaDiv.querySelectorAll('.sidebar-collegamento');
            
            collegamenti.forEach(collegamento => {
                let shouldShow = false;
                
                // Get original data if not stored
                if (!collegamento.originalData) {
                    const titleElement = collegamento.querySelector('.collegamento-title');
                    const endpointsElement = collegamento.querySelector('.collegamento-endpoints');
                    collegamento.originalData = {
                        title: titleElement ? titleElement.textContent : '',
                        endpoints: endpointsElement ? endpointsElement.textContent : ''
                    };
                }
                
                if (filterType === 'collegamento') {
                    // Filter by connection title
                    const titolo = collegamento.getAttribute('data-titolo');
                    shouldShow = titolo.includes(searchTerm);
                    
                    // Highlight title if showing and search term exists
                    const titleElement = collegamento.querySelector('.collegamento-title');
                    if (titleElement) {
                        if (shouldShow && searchTerm) {
                            titleElement.innerHTML = highlightText(collegamento.originalData.title, searchTerm);
                        } else {
                            titleElement.textContent = collegamento.originalData.title;
                        }
                    }
                } else if (filterType === 'argomento') {
                    // Filter by argument titles
                    const argomenti = collegamento.getAttribute('data-argomenti');
                    shouldShow = argomenti.includes(searchTerm);
                    
                    // Highlight endpoints if showing and search term exists
                    const endpointsElement = collegamento.querySelector('.collegamento-endpoints');
                    if (endpointsElement) {
                        if (shouldShow && searchTerm) {
                            endpointsElement.innerHTML = highlightText(collegamento.originalData.endpoints, searchTerm);
                        } else {
                            endpointsElement.textContent = collegamento.originalData.endpoints;
                        }
                    }
                }
                
                collegamento.style.display = shouldShow ? 'block' : 'none';
            });
        }

        // Helper function for text highlighting
        function highlightText(text, query) {
            if (!query || !text) return text;
            
            const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
            return text.replace(regex, '<mark class="search-highlight">$1</mark>');
        }
        
        function escapeRegex(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        }

        // Load sidebar connections on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadSidebarConnections();
        });
        
        function showSidebarCollegamentoModal(id) {
            fetch('/api/collegamenti')
                .then(r => r.json())
                .then(collegamenti => {
                    const c = collegamenti.find(x => x.id === id);
                    if (!c) return;
                    let html = `
                        <div class='mini-collegamento-card'>
                            <div class='collegamento-header'><h4>${c.titolo}</h4></div>
                            <div class='collegamento-argomenti'>
                                <div class='argomento-tag' style='border:2.5px solid ${c.materia1_colore}'>
                                    <a href='/argomento/${c.id_argomento1}'>${c.argomento1_titolo}</a>
                                    <span class='materia-name'>${c.materia1_nome}</span>
                                </div>
                                <div class='collegamento-arrow'>⟷</div>
                                <div class='argomento-tag' style='border:2.5px solid ${c.materia2_colore}'>
                                    <a href='/argomento/${c.id_argomento2}'>${c.argomento2_titolo}</a>
                                    <span class='materia-name'>${c.materia2_nome}</span>
                                </div>
                            </div>
                            <div class='collegamento-footer'>
                                <span class='etichetta-qualita ${c.etichetta_qualita.replace(/ /g,'-').toLowerCase()}'>${c.etichetta_qualita}</span>
                            </div>
                            <div class='collegamento-dettagli' style='margin-top:1em;'>
                                ${marked.parse(c.dettagli||'')}
                            </div>
                        </div>
                    `;
                                        document.getElementById('sidebar-collegamento-body').innerHTML = html;
                    document.getElementById('sidebar-collegamento-modal').style.display = 'flex';
                })
                .catch(error => console.error('Error loading connection details:', error));
        }

        function closeSidebarCollegamentoModal() {
            document.getElementById('sidebar-collegamento-modal').style.display = 'none';
        }