document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();

    const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
    const API_BASE_URL = isLocal ? 'http://127.0.0.1:5000' : 'https://studentiunisannio.it';
   
    const degreeProgramIds = {
        'ing_energetica': 1, 'ing_civile': 2, 'ing_informatica': 3, 'ing_biomedica': 4,
        'economia_aziendale': 5, 'giurisprudenza': 6, 'statistica': 7, 'economia_bancaria': 8,
        'scienze_biologiche': 9, 'biotecnologie': 10, 'scienze_naturali': 11, 'scienze_motorie': 12,
    };

    const tabInfoMapping = {
        'primoAnnoEnergetica': { degree_name: 'ing_energetica', year: 1 },'secondoAnnoEnergetica': { degree_name: 'ing_energetica', year: 2 },'terzoAnnoEnergetica': { degree_name: 'ing_energetica', year: 3 },
        'primoAnnoCivile': { degree_name: 'ing_civile', year: 1 },'secondoAnnoCivile': { degree_name: 'ing_civile', year: 2 },'terzoAnnoCivile': { degree_name: 'ing_civile', year: 3 },
        'primoAnnoInformatica': { degree_name: 'ing_informatica', year: 1 },'secondoAnnoInformatica': { degree_name: 'ing_informatica', year: 2 },'terzoAnnoInformatica': { degree_name: 'ing_informatica', year: 3 },
        'primoAnnoBiomedica': { degree_name: 'ing_biomedica', year: 1 },'secondoAnnoBiomedica': { degree_name: 'ing_biomedica', year: 2 },'terzoAnnoBiomedica': { degree_name: 'ing_biomedica', year: 3 },
        'primoAnnoAziendale': { degree_name: 'economia_aziendale', year: 1 }, 'secondoAnnoAziendale': { degree_name: 'economia_aziendale', year: 2 }, 'terzoAnnoAziendale': { degree_name: 'economia_aziendale', year: 3 },
        'primoAnnoBancaria': { degree_name: 'economia_bancaria', year: 1 }, 'secondoAnnoBancaria': { degree_name: 'economia_bancaria', year: 2 }, 'terzoAnnoBancaria': { degree_name: 'economia_bancaria', year: 3 },
        'primoAnnoStatistica': { degree_name: 'statistica', year: 1 }, 'secondoAnnoStatistica': { degree_name: 'statistica', year: 2 }, 'terzoAnnoStatistica': { degree_name: 'statistica', year: 3 },
        'primoAnnoGiurisprudenza': { degree_name: 'giurisprudenza', year: 1 }, 'secondoAnnoGiurisprudenza': { degree_name: 'giurisprudenza', year: 2 }, 'terzoAnnoGiurisprudenza': { degree_name: 'giurisprudenza', year: 3 },
        'quartoAnnoGiurisprudenza': { degree_name: 'giurisprudenza', year: 4 }, 'quintoAnnoGiurisprudenza': { degree_name: 'giurisprudenza', year: 5 },
        'primoAnnoBiologia': { degree_name: 'scienze_biologiche', year: 1 }, 'secondoAnnoBiologia': { degree_name: 'scienze_biologiche', year: 2 }, 'terzoAnnoBiologia': { degree_name: 'scienze_biologiche', year: 3 },
        'primoAnnoBiotecnologie': { degree_name: 'biotecnologie', year: 1 }, 'secondoAnnoBiotecnologie': { degree_name: 'biotecnologie', year: 2 }, 'terzoAnnoBiotecnologie': { degree_name: 'biotecnologie', year: 3 },
        'primoAnnoNaturali': { degree_name: 'scienze_naturali', year: 1 }, 'secondoAnnoNaturali': { degree_name: 'scienze_naturali', year: 2 }, 'terzoAnnoNaturali': { degree_name: 'scienze_naturali', year: 3 },
        'primoAnnoMotorie': { degree_name: 'scienze_motorie', year: 1 }, 'secondoAnnoMotorie': { degree_name: 'scienze_motorie', year: 2 }, 'terzoAnnoMotorie': { degree_name: 'scienze_motorie', year: 3 },
    };

    // --- FUNZIONI DI CONFIGURAZIONE UI ---

    function activateMainTabAndHeader() {
        const navLinks = document.querySelectorAll('.navbar a');
        const header = document.querySelector('header');
        const navbar = document.querySelector('.navbar');
        const body = document.body;

        header.className = '';
        navbar.className = 'navbar';
        body.className = '';
        navLinks.forEach(link => {
            if (link.id) {
                const tabName = link.id.replace('nav-', '');
                link.classList.remove(`active-${tabName}`);
            }
        });

        const isIngPage = currentPage.startsWith('ing_');
        const isDstPage = ['scienze_biologiche.html', 'biotecnologie.html', 'scienze_naturali.html', 'scienze_motorie.html'].includes(currentPage);
        const isDemmPage = ['economia_aziendale.html', 'economia_bancaria.html', 'statistica.html', 'giurisprudenza.html'].includes(currentPage);
        
        let theme = 'home';
        let activeNavLinkId = 'nav-home';

        if (isIngPage || currentPage === 'ding.html') {
            theme = 'ding';
            activeNavLinkId = 'nav-ding';
        } else if (isDstPage || currentPage === 'dst.html') {
            theme = 'dst';
            activeNavLinkId = 'nav-dst';
        } else if (isDemmPage || currentPage === 'demm.html') {
            theme = 'demm';
            activeNavLinkId = 'nav-demm';
        }
        
        header.classList.add(`header-${theme}`);
        navbar.classList.add(`navbar-${theme}`);
        body.classList.add(`page-${theme}`);

        const activeLink = document.getElementById(activeNavLinkId);
        if (activeLink) {
            activeLink.classList.add(`active-${theme}`);
        }
    }

    async function updateUserStatusNavbar() {
        const userStatusElement = document.getElementById('user-status');
        const loginLink = document.getElementById('nav-login');
        const registerLink = document.getElementById('nav-register');
        const logoutLink = document.getElementById('nav-logout');
        const uploadNoteLink = document.getElementById('nav-upload');
        const adminLink = document.getElementById('nav-admin');

        if (userStatusElement) userStatusElement.style.display = 'none';
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'none';
        if (uploadNoteLink) uploadNoteLink.style.display = 'none';
        if (adminLink) adminLink.style.display = 'none';

        try {
            const response = await fetch(`${API_BASE_URL}/api/status`, { credentials: 'include' });
            const data = await response.json();
            if (data.logged_in) {
                if (userStatusElement) {
                    userStatusElement.textContent = `Benvenuto, ${data.user.username}!`;
                    userStatusElement.style.display = 'inline-block';
                }
                if (logoutLink) logoutLink.style.display = 'inline-block';
                if (uploadNoteLink) uploadNoteLink.style.display = 'inline-block';
                if (adminLink && data.user.role === 'admin') {
                    adminLink.style.display = 'inline-block';
                }
            } else {
                if (loginLink) loginLink.style.display = 'inline-block';
                if (registerLink) registerLink.style.display = 'inline-block';
            }
        } catch (error) {
            console.error('Errore nel controllo stato login:', error);
            if (loginLink) loginLink.style.display = 'inline-block';
            if (registerLink) registerLink.style.display = 'inline-block';
        }
    }

    function setupLogout() {
        const logoutButton = document.getElementById('nav-logout');
        if (logoutButton) {
            logoutButton.addEventListener('click', async (event) => {
                event.preventDefault();
                try {
                    const response = await fetch(`${API_BASE_URL}/api/logout`, { method: 'POST', credentials: 'include' });
                    if (response.ok) {
                        alert('Logout avvenuto con successo!');
                        window.location.href = 'login.html';
                    } else {
                        const err = await response.json();
                        throw new Error(err.message || 'Logout fallito');
                    }
                } catch (error) {
                    console.error('Errore di rete nel logout:', error);
                    alert(`Impossibile effettuare il logout: ${error.message}`);
                }
            });
        }
    }

    // --- LOGICA PAGINE DEI CORSI ---

    function loadNotesForCourse(courseId, containerElement) {
        containerElement.innerHTML = `<p style="color: black;">Caricamento appunti...</p>`;
        fetch(`${API_BASE_URL}/api/courses/${courseId}/notes`, { credentials: 'include' })
            .then(response => {
                if (response.status === 404) return { message: "Nessun appunto trovato per questo corso." };
                if (!response.ok) throw new Error(`Errore HTTP: ${response.status}`);
                return response.json();
            })
            .then(notesData => {
                let notesHtml = `<div class="course-notes-list">`;
                if (Array.isArray(notesData) && notesData.length > 0) {
                    notesData.forEach(note => {
                        notesHtml += `
                            <div class="note-item">
                                <h4>${note.title}</h4>
                                <p>${note.description || 'Nessuna descrizione.'}</p>
                                <p>Caricato da: ${note.uploader_name || 'Anonimo'} il ${new Date(note.upload_date).toLocaleDateString()}</p>
                                <button class="download-note-btn" data-note-id="${note.id}">Scarica Appunto</button>
                            </div>`;
                    });
                } else {
                    notesHtml += `<p style="color: black;">${notesData.message || 'Nessun appunto disponibile.'}</p>`;
                }
                notesHtml += `</div>`;
                containerElement.innerHTML = notesHtml;
                containerElement.querySelectorAll('.download-note-btn').forEach(button => {
                    button.addEventListener('click', () => handleNoteAction(button.dataset.noteId, 'download', false));
                });
            })
            .catch(error => {
                console.error('Errore caricamento appunti:', error);
                containerElement.innerHTML = `<p style="color: black;">Errore nel caricamento degli appunti.</p>`;
            });
    }

    window.openYearTab = function(evt, tabName) {
        // ... (la funzione openYearTab rimane invariata)
    };
    
    // --- LOGICA DASHBOARD ADMIN ---

    function setupAdminDashboard() {
        const notesListContainer = document.getElementById('pending-notes-list');
        if (!notesListContainer) return;

        const loadAdminNotes = async () => {
            notesListContainer.innerHTML = `<p class="no-pending-notes">Caricamento appunti...</p>`;
            try {
                const response = await fetch(`${API_BASE_URL}/api/admin/all_notes`, { credentials: 'include' });
                if (!response.ok) {
                    const err = await response.json().catch(() => ({ error: 'Errore generico.' }));
                    throw new Error(err.error || `Errore ${response.status}`);
                }
                const notes = await response.json();
                if (!notes || notes.length === 0) {
                    notesListContainer.innerHTML = `<p class="no-pending-notes">Nessun appunto trovato nel sistema.</p>`;
                    return;
                }
                const pending = notes.filter(n => n.status === 'pending');
                const approved = notes.filter(n => n.status === 'approved');
                const rejected = notes.filter(n => n.status === 'rejected');
                let html = '<h2>Appunti in Attesa di Approvazione</h2>';
                html += pending.length > 0 ? renderNotesList(pending) : '<p class="no-pending-notes">Nessun appunto in attesa.</p>';
                html += '<hr><h2>Appunti Approvati</h2>';
                html += approved.length > 0 ? renderNotesList(approved) : '<p>Nessun appunto approvato.</p>';
                html += '<hr><h2>Appunti Rifiutati</h2>';
                html += rejected.length > 0 ? renderNotesList(rejected) : '<p>Nessun appunto rifiutato.</p>';
                notesListContainer.innerHTML = html;
            } catch (error) {
                notesListContainer.innerHTML = `<p class="no-pending-notes" style="color: red;">${error.message}</p>`;
            }
        };

        const renderNotesList = (notes) => {
            return notes.map(note => `
                <div class="note-admin-item" id="note-admin-${note.id}">
                    <h3>${note.title}</h3>
                    <p><strong>Caricato da:</strong> ${note.uploader_name || 'Anonimo'}</p>
                    <p><strong>Materia:</strong> ${note.course_name || 'N/D'} (${note.course_year}° Anno)</p>
                    <p><strong>Stato:</strong> <span class="status-${note.status}">${note.status}</span></p>
                    <div class="note-actions">
                        <button class="btn-download" data-note-id="${note.id}">Scarica</button>
                        ${note.status !== 'approved' ? `<button class="btn-approve" data-note-id="${note.id}">Approva</button>` : ''}
                        ${note.status !== 'rejected' ? `<button class="btn-reject" data-note-id="${note.id}">Rifiuta</button>` : ''}
                        <button class="btn-delete" data-note-id="${note.id}">Elimina</button>
                    </div>
                </div>`).join('');
        };
        
        notesListContainer.addEventListener('click', (event) => {
            const target = event.target;
            const noteId = target.dataset.noteId;
            if (!noteId) return;
            let action = '';
            if (target.classList.contains('btn-approve')) action = 'approve';
            else if (target.classList.contains('btn-reject')) action = 'reject';
            else if (target.classList.contains('btn-delete')) action = 'delete';
            else if (target.classList.contains('btn-download')) action = 'download';
            if (action) handleNoteAction(noteId, action, true, loadAdminNotes);
        });

        loadAdminNotes();
    }

    // --- FUNZIONE GLOBALE PER AZIONI SUGLI APPUNTI ---
    
    async function handleNoteAction(noteId, action, isAdmin, callbackOnSuccess) {
        const urlMap = {
            approve: { method: 'POST', path: `/api/admin/notes/${noteId}/approve` },
            reject: { method: 'POST', path: `/api/admin/notes/${noteId}/reject` },
            delete: { method: 'DELETE', path: `/api/admin/notes/${noteId}/delete` },
            download: { method: 'GET', path: `/api/notes/${noteId}/download` }
        };
        if (!urlMap[action]) return;

        if (action === 'delete' && !confirm('Sei sicuro di voler eliminare questo appunto? L\'azione è irreversibile.')) return;

        try {
            const response = await fetch(`${API_BASE_URL}${urlMap[action].path}`, { method: urlMap[action].method, credentials: 'include' });
            const result = await response.json();
            if (response.ok) {
                if (action === 'download') {
                    if (result.download_url) window.open(result.download_url, '_blank');
                    else throw new Error('URL di download non trovato.');
                } else {
                    alert(result.message);
                    if (callbackOnSuccess) callbackOnSuccess();
                }
            } else {
                throw new Error(result.error || 'Azione fallita');
            }
        } catch (error) {
            alert(`Errore: ${error.message}`);
        }
    }
    // --- ESECUZIONE ALL'AVVIO ---
    
    activateMainTabAndHeader();
    updateUserStatusNavbar();
    setupLogout();
    if (document.getElementById('logoutLink')) {
        document.getElementById('logoutLink').addEventListener('click', async function(e) {
            e.preventDefault();
            await fetch(`${API_BASE_URL}/api/logout`, { method: 'POST' });
            window.location.href = 'login.html';
        });
    }

    const isCoursePage = currentPage.startsWith('ing_') || 
                         ['scienze_biologiche.html', 'biotecnologie.html', 'scienze_naturali.html', 'scienze_motorie.html', 
                          'economia_aziendale.html', 'economia_bancaria.html', 'statistica.html', 'giurisprudenza.html'].includes(currentPage);
    
    if (isCoursePage && document.querySelector('.year-tabs button')) {
        document.querySelector('.year-tabs button').click();
    }
    
    if (['upload_note.html', 'login.html', 'register.html'].includes(currentPage)) {
        setupAuthAndUploadPages();
    }

    if (currentPage === 'admin_dashboard.html') {
        setupAdminDashboard();
    }

    // Rendi la funzione di login con Google globalmente accessibile
    window.onSignIn = onSignIn;
});