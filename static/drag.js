// drag.js: drag & drop materie + SocketIO update + popup gestione
const socket = io();

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
        const card = document.createElement('div');
        card.className = 'materia-card';
        card.setAttribute('data-id', m.id);
        card.style.background = m.colore;
        card.tabIndex = 0; // make focusable for events
        // Rendi il titolo un elemento separato ma il testo non deve bloccare il drag
        const span = document.createElement('span');
        span.textContent = m.nome;
        card.appendChild(span);
        // Right-click context menu su tutto il blocco
        card.oncontextmenu = function(e) {
            e.preventDefault();
            showMateriaMenu(e, m);
        };
        // Drag events
        card.draggable = true;
        list.appendChild(card);
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
    list.querySelectorAll('.materia-card').forEach(card => {
        card.ondragstart = null;
        card.ondragend = null;
        card.ondragover = null;
        card.ondrop = null;
    });
    list.ondragover = null;
    list.ondrop = null;
    const cards = document.querySelectorAll('.materia-card');
    cards.forEach((card) => {
        card.draggable = true;
        card.ondragstart = function(e) {
            dragSrc = card;
            isDragging = true;
            card.classList.add('dragging');
            placeholder = document.createElement('div');
            placeholder.className = 'materia-card placeholder';
            placeholder.style.height = card.offsetHeight + 'px';
            placeholder.style.width = card.offsetWidth + 'px';
            // workaround per bug Chrome/Edge: serve un dataTransfer
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', '');
            card.style.visibility = 'hidden';
        };
        card.ondragend = function(e) {
            card.classList.remove('dragging');
            card.style.visibility = '';
            isDragging = false;
            removePlaceholder();
        };
        card.ondragover = function(e) {
            e.preventDefault();
            if (!isDragging || card === dragSrc) return;
            const bounding = card.getBoundingClientRect();
            const offset = e.clientY - bounding.top;
            const insertBefore = offset < bounding.height / 2;
            if (insertBefore) {
                if (card.previousSibling !== placeholder) {
                    removePlaceholder();
                    list.insertBefore(placeholder, card);
                }
            } else {
                if (card.nextSibling !== placeholder) {
                    removePlaceholder();
                    list.insertBefore(placeholder, card.nextSibling);
                }
            }
        };
        card.ondrop = function(e) {
            e.preventDefault();
            if (!isDragging || card === dragSrc) return;
            if (placeholder && placeholder.parentNode) {
                list.insertBefore(dragSrc, placeholder);
                removePlaceholder();
            }
            dragSrc.style.visibility = '';
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
            updateOrder();
        }
    };
}

function updateOrder() {
    const order = Array.from(document.querySelectorAll('.materia-card')).map(c => c.getAttribute('data-id'));
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

document.addEventListener('DOMContentLoaded', enableDrag);
