// drag.js: drag & drop materie + SocketIO update + popup gestione
const socket = io();

// Funzione per calcolare la luminosità di un colore e determinare il contrasto
function getContrastClass(hexColor) {
    // Rimuovi il # se presente
    const hex = hexColor.replace('#', '');
    
    // Converti hex in RGB
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    // Calcola la luminosità usando la formula standard
    // https://www.w3.org/TR/WCAG20/#relativeluminancedef
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    
    // Se la luminosità è > 0.5, è un colore chiaro, altrimenti scuro
    return luminance > 0.5 ? 'light-bg' : 'dark-bg';
}

function fetchMaterie() {
    fetch('/api/materie')
        .then(r => r.json())
        .then(materie => {
            console.log('Materie aggiornate:', materie); // LOG DI CONTROLLO
            renderMaterie(materie);
        });
}

function renderMaterie(materie) {
    const list = document.getElementById('materie-list');
    list.innerHTML = '';
    materie.forEach(m => {
        // Crea il link wrapper
        const link = document.createElement('a');
        link.href = `/materia/${m.id}`;
        link.className = 'materia-link';
        
        // Crea la card
        const card = document.createElement('div');
        card.className = 'materia-card';
        card.setAttribute('data-id', m.id);
        card.style.background = m.colore;
        card.tabIndex = 0; // make focusable for events
        
        // Aggiungi il testo
        const span = document.createElement('span');
        span.textContent = m.nome;
        card.appendChild(span);
        
        // Imposta classe per contrasto testo
        card.classList.add(getContrastClass(m.colore));
        
        // Right-click context menu su tutto il blocco
        card.oncontextmenu = function(e) {
            e.preventDefault();
            e.stopPropagation(); // Previeni la navigazione
            showMateriaMenu(e, m);
        };
        
        // Drag events - aggiungi solo alla card, non al link
        card.draggable = true;
        
        // Previeni la navigazione durante il drag
        card.ondragstart = function(e) {
            e.stopPropagation();
        };
        
        // Assembla la struttura
        link.appendChild(card);
        list.appendChild(link);
    });
    enableDrag();
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
    // Edit
    materiaMenu.querySelector('.menu-edit').onclick = () => {
        materiaMenu.remove();
        openEditMateriaPopup(materia);
    };
    // Delete
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
    popupBg.style.display = 'flex';
    form.querySelector('input[name="nome"]').value = materia.nome;
    form.querySelector('input[name="colore"]').value = materia.colore;
    form.dataset.editId = materia.id;
}

// Delete materia popup
function openDeleteMateriaPopup(materia) {
    // Simple custom modal
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

// Drag & drop
function enableDrag() {
    const list = document.getElementById('materie-list');
    let dragSrc = null;
    let placeholder = null;
    let isDragging = false;
    
    function removePlaceholder() {
        if (placeholder && placeholder.parentNode) placeholder.parentNode.removeChild(placeholder);
    }
    
    // Rimuovi eventuali listener precedenti
    list.querySelectorAll('.materia-link').forEach(link => {
        const card = link.querySelector('.materia-card');
        if (card) {
            card.ondragstart = null;
            card.ondragend = null;
            card.ondragover = null;
            card.ondrop = null;
        }
    });
    list.ondragover = null;
    list.ondrop = null;
    
    const links = document.querySelectorAll('.materia-link');
    links.forEach((link) => {
        const card = link.querySelector('.materia-card');
        if (!card) return;
        
        card.draggable = true;
        
        card.ondragstart = function(e) {
            dragSrc = link; // Trasciniamo il link, non la card
            isDragging = true;
            card.classList.add('dragging');
            
            // Crea placeholder
            placeholder = document.createElement('a');
            placeholder.className = 'materia-link placeholder';
            const placeholderCard = document.createElement('div');
            placeholderCard.className = 'materia-card';
            placeholderCard.style.height = card.offsetHeight + 'px';
            placeholderCard.style.width = card.offsetWidth + 'px';
            placeholderCard.style.opacity = '0.3';
            placeholderCard.style.background = '#ddd';
            placeholder.appendChild(placeholderCard);
            
            // Previeni la navigazione durante il drag
            e.stopPropagation();
            link.style.pointerEvents = 'none';
            
            // workaround per bug Chrome/Edge: serve un dataTransfer
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', '');
            link.style.visibility = 'hidden';
        };
        
        card.ondragend = function(e) {
            card.classList.remove('dragging');
            link.style.visibility = '';
            link.style.pointerEvents = '';
            isDragging = false;
            removePlaceholder();
        };
        
        card.ondragover = function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!isDragging || link === dragSrc) return;
            
            const bounding = link.getBoundingClientRect();
            const offset = e.clientY - bounding.top;
            const insertBefore = offset < bounding.height / 2;
            
            if (insertBefore) {
                if (link.previousSibling !== placeholder) {
                    removePlaceholder();
                    list.insertBefore(placeholder, link);
                }
            } else {
                if (link.nextSibling !== placeholder) {
                    removePlaceholder();
                    list.insertBefore(placeholder, link.nextSibling);
                }
            }
        };
        
        card.ondrop = function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!isDragging || link === dragSrc) return;
            if (placeholder && placeholder.parentNode) {
                list.insertBefore(dragSrc, placeholder);
                removePlaceholder();
            }
            dragSrc.style.visibility = '';
            dragSrc.style.pointerEvents = '';
            updateOrder();
        };
    });
    
    list.ondragover = function(e) {
        e.preventDefault();
        if (!isDragging) return;
        // Se trascini fuori dalle card, metti il placeholder in fondo
        if (placeholder && list.lastChild !== placeholder) {
            removePlaceholder();
            list.appendChild(placeholder);
        }
    };
    
    list.ondrop = function(e) {
        e.preventDefault();
        if (isDragging && placeholder && placeholder.parentNode) {
            list.insertBefore(dragSrc, placeholder);
            removePlaceholder();
            dragSrc.style.visibility = '';
            dragSrc.style.pointerEvents = '';
            updateOrder();
        }
    };
}

function updateOrder() {
    const order = Array.from(document.querySelectorAll('.materia-link .materia-card')).map(c => c.getAttribute('data-id'));
    socket.emit('reorder_materie', { order });
}

// Popup gestione
const openBtn = document.getElementById('openMateriaPopup');
const popupBg = document.getElementById('materiaPopup');
const closeBtn = document.getElementById('closeMateriaPopup');
const form = document.getElementById('addMateriaForm');

openBtn.onclick = () => {
    popupBg.style.display = 'flex';
    setTimeout(() => {
        form.querySelector('input[name="nome"]').focus();
    }, 100);
};
closeBtn.onclick = () => {
    popupBg.style.display = 'none';
    form.reset();
};
popupBg.onclick = e => {
    if (e.target === popupBg) {
        popupBg.style.display = 'none';
        form.reset();
    }
};

// Modifica/aggiunta materia
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
        .then(() => {
            form.reset();
            popupBg.style.display = 'none';
            delete form.dataset.editId;
        });
};

// SocketIO update
socket.on('update_materie', fetchMaterie);

document.addEventListener('DOMContentLoaded', function() {
    enableDrag();
    // Carica le materie al primo accesso per applicare gli event listener
    fetchMaterie();
});
