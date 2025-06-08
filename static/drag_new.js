// drag_new.js: Simplified drag & drop for materie
const socket = io();
let isDragging = false;

// Funzione per calcolare la luminosità di un colore e determinare il contrasto
function getContrastClass(hexColor) {
    const hex = hexColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? 'light-bg' : 'dark-bg';
}

function fetchMaterie() {
    fetch('/api/materie')
        .then(r => r.json())
        .then(materie => {
            console.log('Materie aggiornate:', materie);
            renderMaterie(materie);
        })
        .catch(error => {
            console.error('Error fetching materie:', error);
        });
}

function renderMaterie(materie) {
    const list = document.getElementById('materie-list');
    if (!list) {
        console.error('❌ materie-list element not found');
        return;
    }
    
    list.innerHTML = '';
    materie.forEach(m => {
        // Crea wrapper senza href per evitare conflitti
        const wrapper = document.createElement('div');
        wrapper.className = 'materia-wrapper';
        wrapper.setAttribute('data-id', m.id);
        wrapper.setAttribute('data-href', `/materia/${m.id}`);
        
        // Crea la card
        const card = document.createElement('div');
        card.className = 'materia-card';
        card.style.background = m.colore;
        card.draggable = true;
        
        // Aggiungi il testo
        const span = document.createElement('span');
        span.textContent = m.nome;
        card.appendChild(span);
        
        // Imposta classe per contrasto
        card.classList.add(getContrastClass(m.colore));
        
        // Click handler per navigazione (solo se non in drag)
        wrapper.addEventListener('click', function(e) {
            if (!isDragging) {
                window.location.href = wrapper.getAttribute('data-href');
            }
        });
        
        // Context menu
        card.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            showMateriaMenu(e, m);
        });
        
        wrapper.appendChild(card);
        list.appendChild(wrapper);
    });
    
    enableDrag();
}

// Drag & Drop functionality
function enableDrag() {
    const list = document.getElementById('materie-list');
    const wrappers = document.querySelectorAll('.materia-wrapper');
    
    console.log(`🔧 Setting up drag for ${wrappers.length} materia wrappers`);
    
    let dragSrc = null;
    let placeholder = null;
      wrappers.forEach((wrapper) => {
        const card = wrapper.querySelector('.materia-card');
        if (!card) return;
        
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        // Remove individual wrapper event listeners since we use global ones
    });
    
    function handleDragStart(e) {
        const wrapper = this.parentElement;
        const id = wrapper.getAttribute('data-id');
        console.log('🚀 Drag start for materia:', id);
        
        dragSrc = wrapper;
        isDragging = true;
        this.classList.add('dragging');
        
        // Create placeholder
        placeholder = document.createElement('div');
        placeholder.className = 'materia-wrapper placeholder';
        placeholder.innerHTML = '<div class="materia-card placeholder-card">Drop here</div>';
        
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.outerHTML);
        
        wrapper.style.opacity = '0.5';
        list.classList.add('drag-active');
        
        setTimeout(() => {
            wrapper.style.display = 'none';
        }, 0);
    }
      function handleDragEnd(e) {
        console.log('🏁 Drag end');
        const wrapper = this.parentElement;
        
        this.classList.remove('dragging');
        wrapper.style.opacity = '';
        wrapper.style.display = '';
        list.classList.remove('drag-active');
        isDragging = false;
        
        if (placeholder && placeholder.parentElement) {
            placeholder.remove();
        }
        placeholder = null; // Reset placeholder
    }    // Global list handlers
    list.addEventListener('dragover', function(e) {
        e.preventDefault();
        if (!isDragging || !placeholder) return;
        
        const afterElement = getDragAfterElement(list, e.clientX, e.clientY);
        
        // Remove placeholder if already present
        if (placeholder.parentElement) {
            placeholder.remove();
        }
        
        if (!afterElement) {
            list.appendChild(placeholder);
        } else {
            list.insertBefore(placeholder, afterElement);
        }
    });
      list.addEventListener('drop', function(e) {
        e.preventDefault();
        console.log('📦 Drop event');
        
        if (!isDragging || !dragSrc || !placeholder) return;
        
        if (placeholder.parentElement) {
            placeholder.parentElement.insertBefore(dragSrc, placeholder);
            placeholder.remove();
        }
        
        placeholder = null; // Reset placeholder
        updateOrder();
    });
}

function getDragAfterElement(container, clientX, clientY) {
    const draggableElements = [...container.querySelectorAll('.materia-wrapper:not(.placeholder)')];
    
    let closest = null;
    let closestDistance = Number.POSITIVE_INFINITY;
    
    for (const child of draggableElements) {
        const box = child.getBoundingClientRect();
        const centerX = box.left + box.width / 2;
        const centerY = box.top + box.height / 2;
        
        // Calculate distance from mouse to center of element
        const distance = Math.sqrt(
            Math.pow(clientX - centerX, 2) + Math.pow(clientY - centerY, 2)
        );
        
        // Check if mouse is to the left of the element center (should insert before)
        const isLeftOfCenter = clientX < centerX;
        
        if (distance < closestDistance && isLeftOfCenter) {
            closestDistance = distance;
            closest = child;
        }
    }
    
    return closest;
}

function updateOrder() {
    const wrappers = document.querySelectorAll('.materia-wrapper:not(.placeholder)');
    const order = Array.from(wrappers).map(w => w.getAttribute('data-id'));
    console.log('📋 Updating order:', order);
    
    if (order.length > 0) {
        socket.emit('reorder_materie', { order });
    }
}

// Context menu
let materiaMenu = null;
function showMateriaMenu(e, materia) {
    if (materiaMenu) materiaMenu.remove();
    materiaMenu = document.createElement('div');
    materiaMenu.className = 'materia-menu';
    materiaMenu.innerHTML = `
        <button class="menu-edit">Modifica</button>
        <button class="menu-delete">Elimina</button>
    `;
    document.body.appendChild(materiaMenu);
    materiaMenu.style.top = e.clientY + 'px';
    materiaMenu.style.left = e.clientX + 'px';
    
    materiaMenu.querySelector('.menu-edit').onclick = () => {
        materiaMenu.remove();
        openEditMateriaPopup(materia);
    };
    materiaMenu.querySelector('.menu-delete').onclick = () => {
        materiaMenu.remove();
        openDeleteMateriaPopup(materia);
    };
    document.addEventListener('click', closeMateriaMenu, { once: true });
}

function closeMateriaMenu() {
    if (materiaMenu) materiaMenu.remove();
}

// Edit materia popup
function openEditMateriaPopup(materia) {
    const popupBg = document.getElementById('materiaPopup');
    const form = document.getElementById('addMateriaForm');
    popupBg.style.display = 'flex';
    form.querySelector('input[name="nome"]').value = materia.nome;
    form.querySelector('input[name="colore"]').value = materia.colore;
    form.dataset.editId = materia.id;
}

// Delete materia popup
function openDeleteMateriaPopup(materia) {
    const modal = document.createElement('div');
    modal.className = 'popup-bg';
    modal.innerHTML = `
      <div class="popup">
        <h2>Elimina materia</h2>
        <p>Per eliminare <b>${materia.nome}</b>, scrivi il nome esatto qui sotto e conferma:</p>
        <input type="text" id="deleteMateriaInput" placeholder="${materia.nome}">
        <div class="popup-actions">
          <button class="add-btn" id="confirmDeleteMateria">Elimina</button>
          <button class="cancel-btn" id="cancelDeleteMateria">Annulla</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.querySelector('#cancelDeleteMateria').onclick = () => modal.remove();
    modal.querySelector('#confirmDeleteMateria').onclick = () => {
      const val = modal.querySelector('#deleteMateriaInput').value.trim();
      if (val !== materia.nome) {
        alert('Il nome inserito non corrisponde.');
        return;
      }
      if (!confirm(`Sei sicuro di voler eliminare la materia "${materia.nome}"?`)) return;
      fetch(`/delete_materia/${materia.id}`, { method: 'DELETE' })
        .then(() => modal.remove());
    };
}

// Popup management
document.addEventListener('DOMContentLoaded', function() {
    const openBtn = document.getElementById('openMateriaPopup');
    const popupBg = document.getElementById('materiaPopup');
    const closeBtn = document.getElementById('closeMateriaPopup');
    const form = document.getElementById('addMateriaForm');

    if (openBtn) {
        openBtn.onclick = () => {
            popupBg.style.display = 'flex';
            setTimeout(() => {
                form.querySelector('input[name="nome"]').focus();
            }, 100);
        };
    }

    if (closeBtn) {
        closeBtn.onclick = () => {
            popupBg.style.display = 'none';
            form.reset();
            delete form.dataset.editId;
        };
    }

    if (popupBg) {
        popupBg.onclick = e => {
            if (e.target === popupBg) {
                popupBg.style.display = 'none';
                form.reset();
                delete form.dataset.editId;
            }
        };
    }

    // Form submission
    if (form) {
        form.onsubmit = function(e) {
            e.preventDefault();
            const data = new FormData(form);
            const editId = form.dataset.editId;
            let url = '/add_materia', method = 'POST';
            if (editId) {
                url = `/edit_materia/${editId}`;
                method = 'POST';
            }
            fetch(url, { method, body: data })
                .then(response => {
                    if (response.ok) {
                        form.reset();
                        popupBg.style.display = 'none';
                        delete form.dataset.editId;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        };
    }

    // Initialize
    console.log('📄 DOM loaded, initializing materie...');
    fetchMaterie();
});

// SocketIO updates
socket.on('update_materie', () => {
    console.log('📡 Received update_materie event');
    fetchMaterie();
});
