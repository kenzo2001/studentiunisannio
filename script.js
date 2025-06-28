document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();

    const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
    const API_BASE_URL = isLocal ? 'http://127.0.0.1:5000' : 'https://studentiunisannio.it';
    
    const degreeProgramIds = {
        'ing_energetica': 1, 'ing_civile': 2, 'ing_informatica': 3, 'ing_biomedica': 4,
        'economia_aziendale': 5,'giurisprudenza': 6, 'statistica': 7, 'economia_bancaria': 8,
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

    function activateMainTabAndHeader() {
        const navLinks = document.querySelectorAll('.navbar a');
        const header = document.querySelector('header');
        const navbar = document.querySelector('.navbar');
        const body = document.body;

        // Reset classes
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
        
        let theme = '';
        let activeNavLinkId = '';

        if (currentPage === '' || currentPage === 'index.html' || currentPage === 'upload_note.html') {
             theme = 'home';
             activeNavLinkId = 'nav-home';
        } else if (isIngPage || currentPage === 'ding.html') {
            theme = 'ding';
            activeNavLinkId = 'nav-ding';
        } else if (isDstPage || currentPage === 'dst.html') {
            theme = 'dst';
            activeNavLinkId = 'nav-dst';
        } else if (isDemmPage || currentPage === 'demm.html') {
            theme = 'demm';
            activeNavLinkId = 'nav-demm';
        } else {
            // Fallback per altre pagine come login/register
            theme = 'ding';
            activeNavLinkId = 'nav-ding';
        }
        
        // Applica il tema
        header.classList.add(`header-${theme}`);
        navbar.classList.add(`navbar-${theme}`);
        body.classList.add(`page-${theme}`);

        const activeLink = document.getElementById(activeNavLinkId);
        if (activeLink) {
            const activeClass = `active-${theme}`;
            activeLink.classList.add(activeClass);
        }
    }
    
   async function updateUserStatusNavbar() {
    const userStatusElement = document.getElementById('user-status');
    const loginLink = document.getElementById('nav-login');
    const registerLink = document.getElementById('nav-register');
    const logoutLink = document.getElementById('nav-logout');
    const uploadNoteLink = document.getElementById('nav-upload');
    const adminLink = document.getElementById('nav-admin'); // <-- Variabile per il link admin

    // Nascondi tutti gli elementi all'inizio
    if (userStatusElement) userStatusElement.style.display = 'none';
    if (loginLink) loginLink.style.display = 'none';
    if (registerLink) registerLink.style.display = 'none';
    if (logoutLink) logoutLink.style.display = 'none';
    if (uploadNoteLink) uploadNoteLink.style.display = 'none';
    if (adminLink) adminLink.style.display = 'none'; // <-- Nascondi anche il link admin di default

    try {
        const response = await fetch(`${API_BASE_URL}/api/status`);
        const data = await response.json();

        if (data.logged_in) {
            // Utente loggato
            if (userStatusElement) {
                userStatusElement.textContent = `Benvenuto, ${data.user.username}!`;
                userStatusElement.style.display = 'inline-block';
            }
            if (logoutLink) logoutLink.style.display = 'inline-block';
            if (uploadNoteLink) uploadNoteLink.style.display = 'inline-block';

            // Controlla se l'utente è un admin
            if (adminLink && data.user.role === 'admin') {
                adminLink.style.display = 'inline-block'; // <-- Mostra il link solo per gli admin
            }

        } else {
            // Utente non loggato
            if (loginLink) loginLink.style.display = 'inline-block';
            if (registerLink) registerLink.style.display = 'inline-block';
        }
    } catch (error) {
        console.error('Errore nel controllo stato login:', error);
        // In caso di errore, mostra i link di default per non loggato
        if (loginLink) loginLink.style.display = 'inline-block';
        if (registerLink) registerLink.style.display = 'inline-block';
    }
}


    // Aggiungi questa nuova funzione in script.js
function setupAdminDashboard() {
    const pendingNotesList = document.getElementById('pending-notes-list');
    if (!pendingNotesList) return; // Esegui solo se siamo nella pagina admin_dashboard.html

    const fetchAndRenderNotes = async () => {
        pendingNotesList.innerHTML = `<p class="no-pending-notes">Caricamento appunti...</p>`;
        try {
            const response = await fetch(`${API_BASE_URL}/api/admin/all_notes`);
            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                   throw new Error("Accesso negato. Devi essere un amministratore per visualizzare questa pagina.");
                }
                throw new Error(`Errore dal server: ${response.status}`);
            }
            const notes = await response.json();

            if (!notes || notes.length === 0) {
                pendingNotesList.innerHTML = `<p class="no-pending-notes">Nessun appunto trovato nel sistema.</p>`;
                return;
            }
            
            // Filtra gli appunti per stato
            const pending = notes.filter(n => n.status === 'pending');
            const approved = notes.filter(n => n.status === 'approved');
            const rejected = notes.filter(n => n.status === 'rejected');

            let html = '<h2>Appunti in Attesa di Approvazione</h2>';
            if (pending.length > 0) {
                html += renderNotesList(pending);
            } else {
                html += '<p class="no-pending-notes">Nessun appunto in attesa.</p>';
            }

            html += '<hr style="margin: 40px 0;"><h2>Appunti Approvati</h2>';
            if (approved.length > 0) {
                html += renderNotesList(approved);
            } else {
                html += '<p>Nessun appunto approvato.</p>';
            }

            html += '<hr style="margin: 40px 0;"><h2>Appunti Rifiutati</h2>';
            if (rejected.length > 0) {
                html += renderNotesList(rejected);
            } else {
                html += '<p>Nessun appunto rifiutato.</p>';
            }

            pendingNotesList.innerHTML = html;
            addEventListenersToButtons();

        } catch (error) {
            pendingNotesList.innerHTML = `<p class="no-pending-notes" style="color: red;">${error.message}</p>`;
        }
    };

    const renderNotesList = (notes) => {
        return notes.map(note => `
            <div class="note-admin-item" id="note-admin-${note.id}">
                <h3>${note.title}</h3>
                <p><strong>Caricato da:</strong> ${note.uploader_name || 'Anonimo'}</p>
                <p><strong>Materia:</strong> ${note.course_name || 'N/D'} (${note.course_year}° Anno)</p>
                <p><strong>Descrizione:</strong> ${note.description || 'Nessuna.'}</p>
                <p><strong>Stato:</strong> <span class="status-${note.status}">${note.status}</span></p>
                <div class="note-actions">
                    ${note.status !== 'approved' ? `<button class="btn-approve" data-id="${note.id}">Approva</button>` : ''}
                    ${note.status !== 'rejected' ? `<button class="btn-reject" data-id="${note.id}">Rifiuta</button>` : ''}
                    <button class="btn-delete" data-id="${note.id}">Elimina</button>
                </div>
            </div>
        `).join('');
    };

    const handleAction = async (noteId, action) => {
        if (action === 'delete' && !confirm('Sei sicuro di voler eliminare questo appunto? L\'azione è irreversibile.')) {
            return;
        }
        
        const url = `${API_BASE_URL}/api/admin/notes/${noteId}/${action}`;
        const method = (action === 'delete') ? 'DELETE' : 'POST';

        try {
            const response = await fetch(url, { method: method });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                fetchAndRenderNotes(); // Ricarica la lista
            } else {
                throw new Error(result.error || 'Azione fallita');
            }
        } catch (error) {
            alert(`Errore: ${error.message}`);
        }
    };

    const addEventListenersToButtons = () => {
        document.querySelectorAll('.btn-approve').forEach(b => b.addEventListener('click', () => handleAction(b.dataset.id, 'approve')));
        document.querySelectorAll('.btn-reject').forEach(b => b.addEventListener('click', () => handleAction(b.dataset.id, 'reject')));
        document.querySelectorAll('.btn-delete').forEach(b => b.addEventListener('click', () => handleAction(b.dataset.id, 'delete')));
    };

    fetchAndRenderNotes();
}
    function loadNotesForCourse(courseId, containerElement) {
        containerElement.innerHTML = `<p style="color: black;">Caricamento appunti...</p>`;
        fetch(`${API_BASE_URL}/api/courses/${courseId}/notes`)
            .then(response => {
                if (response.status === 404) return { message: "Nessun appunto trovato per questo corso." };
                if (!response.ok) throw new Error(`Errore HTTP: ${response.status}`);
                return response.json();
            })
            .then(notesData => {
                let notesHtml = `<div class="course-notes-list">`;
                if (Array.isArray(notesData) && notesData.length > 0) {
                    notesData.forEach(note => {
                        const downloadApiUrl = `${API_BASE_URL}/api/notes/${note.id}/download`;
                        notesHtml += `
                            <div class="note-item">
                                <h4>${note.title}</h4>
                                <p>${note.description || 'Nessuna descrizione.'}</p>
                                <p>Caricato da: ${note.uploader_name || 'Anonimo'} il ${new Date(note.upload_date).toLocaleDateString()}</p>
                                <a href="${downloadApiUrl}" class="download-note-btn">Scarica Appunto</a>
                            </div>`;
                    });
                } else {
                    notesHtml += `<p style="color: black;">${notesData.message || 'Nessun appunto disponibile.'}</p>`;
                }
                notesHtml += `</div>`;
                containerElement.innerHTML = notesHtml;

                containerElement.querySelectorAll('.download-note-btn').forEach(button => {
                    button.addEventListener('click', function(event) {
                        event.preventDefault();
                        const apiUrl = this.href;
                        fetch(apiUrl)
                            .then(response => response.json())
                            .then(data => {
                                if (data.download_url) {
                                    window.open(data.download_url, '_blank');
                                } else {
                                    alert('Impossibile ottenere il link per il download.');
                                }
                            })
                            .catch(error => {
                                console.error('Errore recupero link download:', error);
                                alert('Si è verificato un errore di rete.');
                            });
                    });
                });
            })
            .catch(error => {
                console.error('Errore caricamento appunti:', error);
                containerElement.innerHTML = `<p style="color: black;">Errore nel caricamento degli appunti.</p>`;
            });
    }

    function loadCoursesForYear(degreeProgramId, year, container, degreeName) {
        const displayName = degreeName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        container.innerHTML = `<h3 style="color: black;">Caricamento corsi ${year}° Anno per ${displayName}...</h3>`;
        
        fetch(`${API_BASE_URL}/api/degree_programs/${degreeProgramId}/courses/${year}`)
            .then(response => {
                if (response.status === 404) return [];
                if (!response.ok) throw new Error(`Errore dal server: ${response.status}`);
                return response.json();
            })
            .then(coursesData => {
                let listHtml = '';
                if (Array.isArray(coursesData) && coursesData.length > 0) {
                    coursesData.forEach(course => {
                        listHtml += `
                            <li id="course-${course.id}">
                                <span>${course.name}</span>
                                <a href="#" class="view-notes-btn" data-course-id="${course.id}">Vedi Appunti</a>
                                <div class="notes-container" id="notes-for-course-${course.id}" style="display: none;"></div>
                            </li>`;
                    });
                    container.innerHTML = `
                        <h3>Corsi ${year}° Anno</h3>
                        <div class="course-list">
                            <ul>${listHtml}</ul>
                        </div>`;
                } else {
                    container.innerHTML = `
                        <h3>Corsi ${year}° Anno</h3>
                        <p style="color: black; padding: 15px; text-align: left;">Nessun corso trovato per questo anno.</p>`;
                }

                container.querySelectorAll('.view-notes-btn').forEach(button => {
                    button.addEventListener('click', function(event) {
                        event.preventDefault();
                        const courseId = this.dataset.courseId;
                        const notesContainer = document.getElementById(`notes-for-course-${courseId}`);
                        const isHidden = notesContainer.style.display === 'none';
                        notesContainer.style.display = isHidden ? 'block' : 'none';
                        this.textContent = isHidden ? 'Nascondi Appunti' : 'Vedi Appunti';
                        if (isHidden) {
                            loadNotesForCourse(courseId, notesContainer);
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Errore caricamento corsi:', error);
                container.innerHTML = `<h3 style="color: black;">Errore nel caricamento dei corsi.</h3><p>${error.message}</p>`;
            });
    }

    window.openYearTab = function(evt, tabName) {
        let i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("year-tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
            tabcontent[i].classList.remove("active");
        }
        tablinks = document.getElementsByClassName("year-tabs")[0].getElementsByTagName("button");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].classList.remove("active");
        }
        const currentContentDiv = document.getElementById(tabName);
        currentContentDiv.style.display = "block";
        currentContentDiv.classList.add("active");
        evt.currentTarget.classList.add("active");

        const info = tabInfoMapping[tabName];
        if (info) {
            const degreeProgramId = degreeProgramIds[info.degree_name];
            if (degreeProgramId) {
                loadCoursesForYear(degreeProgramId, info.year, currentContentDiv, info.degree_name);
            }
        }
    }
    
    function setupAuthAndUploadPages() {
        if (currentPage === 'upload_note.html') {
            const uploadForm = document.getElementById('uploadNoteForm');
            const messageDiv = document.getElementById('upload-message');
            const departmentSelect = document.getElementById('departmentSelect');
            const degreeProgramSelect = document.getElementById('degreeProgramSelect');
            const courseSelect = document.getElementById('courseSelect');

            const loadDepartments = async () => {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/departments`);
                    const departments = await response.json();
                    departmentSelect.innerHTML = '<option value="">Seleziona Dipartimento</option>';
                    departments.forEach(dept => {
                        departmentSelect.innerHTML += `<option value="${dept.id}">${dept.name}</option>`;
                    });
                } catch (err) { console.error("Errore caricamento dipartimenti", err); }
            };

            const loadDegreePrograms = async (departmentId) => {
                if (!departmentId) return;
                try {
                    const response = await fetch(`${API_BASE_URL}/api/departments/${departmentId}/degree_programs`);
                    const programs = await response.json();
                    degreeProgramSelect.innerHTML = '<option value="">Seleziona Corso di Laurea</option>';
                    programs.forEach(p => {
                        degreeProgramSelect.innerHTML += `<option value="${p.id}">${p.name}</option>`;
                    });
                    degreeProgramSelect.disabled = false;
                } catch(err) { console.error("Errore caricamento corsi di laurea", err); }
            };

             const loadCourses = async (degreeProgramId) => {
                if (!degreeProgramId) return;
                 try {
                    let allCourses = [];
                    for (let year = 1; year <= 5; year++) { // Modificato a 5 per includere giurisprudenza
                        const response = await fetch(`${API_BASE_URL}/api/degree_programs/${degreeProgramId}/courses/${year}`);
                        if (response.ok) {
                            allCourses = allCourses.concat(await response.json());
                        }
                    }
                    courseSelect.innerHTML = '<option value="">Seleziona Esame/Materia</option>';
                    allCourses.sort((a,b) => a.name.localeCompare(b.name)).forEach(c => {
                         courseSelect.innerHTML += `<option value="${c.id}">${c.name} (${c.year}° Anno)</option>`;
                    });
                    courseSelect.disabled = false;
                 } catch(err) { console.error("Errore caricamento esami", err); }
            };

            departmentSelect.addEventListener('change', (e) => loadDegreePrograms(e.target.value));
            degreeProgramSelect.addEventListener('change', (e) => loadCourses(e.target.value));
            
            uploadForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                messageDiv.textContent = 'Caricamento in corso...';
                const formData = new FormData(this);
                try {
                    const response = await fetch(`${API_BASE_URL}/api/upload_note`, { method: 'POST', body: formData });
                    const result = await response.json();
                    if (response.ok) {
                        messageDiv.textContent = 'Appunto caricato con successo!';
                        messageDiv.className = 'success';
                        uploadForm.reset();
                    } else {
                        messageDiv.textContent = `Errore: ${result.error || 'Qualcosa è andato storto'}`;
                        messageDiv.className = 'error';
                    }
                } catch (err) {
                     messageDiv.textContent = `Errore di rete: ${err.message}`;
                     messageDiv.className = 'error';
                }
            });

            loadDepartments();
        }

        if (currentPage === 'login.html' || currentPage === 'register.html') {
            const form = document.getElementById('loginForm') || document.getElementById('registerForm');
            const messageDiv = document.getElementById('login-message') || document.getElementById('register-message');
            
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const isRegister = form.id === 'registerForm';
                const endpoint = isRegister ? '/api/register' : '/api/login';
                messageDiv.textContent = isRegister ? 'Registrazione in corso...' : 'Accesso in corso...';
                
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());

                if (isRegister && data.password !== data.confirm_password) {
                    messageDiv.textContent = 'Le password non corrispondono.';
                    messageDiv.className = 'auth-message error';
                    return;
                }

                try {
                    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    if (response.ok) {
                        if(isRegister){
                            messageDiv.textContent = 'Registrazione avvenuta con successo! Puoi effettuare il login.';
                            messageDiv.className = 'auth-message success';
                            form.reset();
                        } else {
                            window.location.href = 'index.html';
                        }
                    } else {
                        messageDiv.textContent = `Errore: ${result.error || 'Operazione fallita'}`;
                        messageDiv.className = 'auth-message error';
                    }
                } catch (error) {
                    messageDiv.textContent = `Errore di rete: ${error.message}`;
                    messageDiv.className = 'auth-message error';
                }
            });
        }
    }
    
    function onSignIn(googleUser) {
        const messageDiv = document.getElementById('login-message') || document.getElementById('register-message');
        if (messageDiv) {
            messageDiv.textContent = 'Verifica in corso...';
            messageDiv.className = 'auth-message';
        }
    
        const id_token = googleUser.credential;
      
        fetch(`${API_BASE_URL}/api/google-login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: id_token })
        })
        .then(response => {
            if (response.ok) {
                window.location.href = 'index.html';
            } else {
                return response.json().then(err => { throw new Error(err.error || 'Login con Google fallito.'); });
            }
        })
        .catch(error => {
            if (messageDiv) {
                messageDiv.textContent = `Errore: ${error.message}`;
                messageDiv.className = 'auth-message error';
            }
            console.error('Errore durante il login con Google:', error);
        });
    }

    // --- ESECUZIONE ALL'AVVIO ---
    
    activateMainTabAndHeader();
    updateUserStatusNavbar();
    setu
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