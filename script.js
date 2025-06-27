document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();

    // --- MODIFICA CHIAVE QUI ---
    // Imposta dinamicamente l'URL dell'API in base all'ambiente
    const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
    const API_BASE_URL = isLocal ? 'http://127.0.0.1:5000' : 'https://studentiunisannio.it';
    // Quando sei in locale, tutte le chiamate API saranno fatte a http://127.0.0.1:5000/api/...
    // Quando il sito sarà online, le chiamate saranno fatte a https://studentiunisannio.it/api/...
    
     // --- MAPPATURA AMPLIATA DEGLI ID DEI CORSI DI LAUREA ---
    const degreeProgramIds = {
        'ing_energetica': 1,
        'ing_civile': 2,
        'ing_informatica': 3,
        'ing_biomedica': 4,
        'scienze_biologiche': 7,
        'biotecnologie': 8,
        'scienze_naturali': 9, // Nome file semplificato
        'scienze_motorie': 10
    };
    
    // --- MAPPATURA AMPLIATA DEI TAB ---
    const tabInfoMapping = {
        // Ingegneria
        'primoAnnoEnergetica': { degree_name: 'ing_energetica', year: 1 },'secondoAnnoEnergetica': { degree_name: 'ing_energetica', year: 2 },'terzoAnnoEnergetica': { degree_name: 'ing_energetica', year: 3 },
        'primoAnnoCivile': { degree_name: 'ing_civile', year: 1 },'secondoAnnoCivile': { degree_name: 'ing_civile', year: 2 },'terzoAnnoCivile': { degree_name: 'ing_civile', year: 3 },
        'primoAnnoInformatica': { degree_name: 'ing_informatica', year: 1 },'secondoAnnoInformatica': { degree_name: 'ing_informatica', year: 2 },'terzoAnnoInformatica': { degree_name: 'ing_informatica', year: 3 },
        'primoAnnoBiomedica': { degree_name: 'ing_biomedica', year: 1 },'secondoAnnoBiomedica': { degree_name: 'ing_biomedica', year: 2 },'terzoAnnoBiomedica': { degree_name: 'ing_biomedica', year: 3 },
        // DST
        'primoAnnoBiologia': { degree_name: 'scienze_biologiche', year: 1 }, 'secondoAnnoBiologia': { degree_name: 'scienze_biologiche', year: 2 }, 'terzoAnnoBiologia': { degree_name: 'scienze_biologiche', year: 3 },
        'primoAnnoBiotecnologie': { degree_name: 'biotecnologie', year: 1 }, 'secondoAnnoBiotecnologie': { degree_name: 'biotecnologie', year: 2 }, 'terzoAnnoBiotecnologie': { degree_name: 'biotecnologie', year: 3 },
        'primoAnnoNaturali': { degree_name: 'scienze_naturali', year: 1 }, 'secondoAnnoNaturali': { degree_name: 'scienze_naturali', year: 2 }, 'terzoAnnoNaturali': { degree_name: 'scienze_naturali', year: 3 },
        'primoAnnoMotorie': { degree_name: 'scienze_motorie', year: 1 }, 'secondoAnnoMotorie': { degree_name: 'scienze_motorie', year: 2 }, 'terzoAnnoMotorie': { degree_name: 'scienze_motorie', year: 3 }
    };

    // --- FUNZIONI GLOBALI ESEGUITE SU TUTTE LE PAGINE ---
    // ============== Logica per il Pop-up Donazioni (Modificata) ==============
if (currentPage === 'index.html' || currentPage === '') {
    const modalOverlay = document.getElementById('donation-modal-overlay');
    const closeModalBtn = document.getElementById('modal-close-btn');

    // La condizione che controllava localStorage è stata rimossa.
    // Mostra il pop-up dopo 3 secondi ad ogni visita della pagina.
    if (modalOverlay) {
        setTimeout(() => {
            modalOverlay.style.display = 'flex';
        }, 3000);
    }

    // Funzione per chiudere il pop-up
    const closeModal = () => {
        if (modalOverlay) {
            modalOverlay.style.display = 'none';
        }
    };

    // Event listener per chiudere cliccando sulla 'X'
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    // Event listener per chiudere cliccando sullo sfondo
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(event) {
            if (event.target === modalOverlay) {
                closeModal();
            }
        });
    }
}
// =======================================================================
    // ============== Logica per il Pop-up Donazioni ==============
if (currentPage === 'index.html' || currentPage === '') {
    const modalOverlay = document.getElementById('donation-modal-overlay');
    const closeModalBtn = document.getElementById('modal-close-btn');

    // La condizione che controllava localStorage è stata rimossa.
    // Mostra il pop-up dopo 3 secondi ad ogni visita della pagina.
    if (modalOverlay) {
        setTimeout(() => {
            modalOverlay.style.display = 'flex';
        }, 3000);
    }

    // Funzione per chiudere il pop-up
    const closeModal = () => {
        if (modalOverlay) {
            modalOverlay.style.display = 'none';
        }
    };

    // Event listener per chiudere cliccando sulla 'X'
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    // Event listener per chiudere cliccando sullo sfondo
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(event) {
            if (event.target === modalOverlay) {
                closeModal();
            }
        });
    }
}
// =======================================================================
    // ==========================================================
    function activateMainTabAndHeader() {
        const navLinks = document.querySelectorAll('.navbar a');
        const header = document.querySelector('header');
        const navbar = document.querySelector('.navbar');

        header.className = '';
        navbar.className = 'navbar';
        navLinks.forEach(link => {
            if (link.id) {
                const tabName = link.id.replace('nav-', '');
                link.classList.remove(`active-${tabName}`);
            }
        });

        const isIngPage = currentPage.startsWith('ing_');
        const isAuthPage = ['upload_note.html', 'login.html', 'register.html'].includes(currentPage);

        let activeTab = '';
        if (isIngPage || isAuthPage) {
            activeTab = 'ding';
            header.classList.add('header-ingegneria');
            navbar.classList.add('navbar-ingegneria');
        } else if (currentPage === '' || currentPage === 'index.html') {
            activeTab = 'home';
        } else {
            const foundLink = Array.from(navLinks).find(l => l.href.endsWith(currentPage));
            if (foundLink && foundLink.id) {
                activeTab = foundLink.id.replace('nav-', '');
            }
        }

        if (activeTab) {
            const activeLink = document.getElementById(`nav-${activeTab}`);
            if (activeLink) activeLink.classList.add(`active-${activeTab}`);
            if (!header.classList.contains('header-ingegneria')) header.classList.add(`header-${activeTab}`);
            if (!navbar.classList.contains('navbar-ingegneria')) navbar.classList.add(`navbar-${activeTab}`);
        }
    }

    async function updateUserStatusNavbar() {
        const userStatusElement = document.getElementById('user-status');
        const loginLink = document.getElementById('nav-login');
        const registerLink = document.getElementById('nav-register');
        const logoutLink = document.getElementById('nav-logout');
        const uploadNoteLink = document.getElementById('nav-upload');

        if (userStatusElement) userStatusElement.style.display = 'none';
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'none';
        if (uploadNoteLink) uploadNoteLink.style.display = 'none';

        try {
            const response = await fetch(`${API_BASE_URL}/api/status`);
            const data = await response.json();
            if (data.logged_in) {
                if (userStatusElement) {
                    userStatusElement.textContent = `Benvenuto, ${data.user.username}!`;
                    userStatusElement.style.display = 'inline-block';
                }
                if (logoutLink) logoutLink.style.display = 'inline-block';
                if (uploadNoteLink) uploadNoteLink.style.display = 'inline-block';
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

    activateMainTabAndHeader();
    updateUserStatusNavbar();

    const logoutLink = document.getElementById('nav-logout');
    if (logoutLink) {
        logoutLink.addEventListener('click', async function(e) {
            e.preventDefault();
            try {
                await fetch(`${API_BASE_URL}/api/logout`, { method: 'POST' });
                window.location.href = 'login.html';
            } catch (error) {
                console.error('Errore durante il logout:', error);
            }
        });
    }

    // --- LOGICA SPECIFICA PER PAGINE ---

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
        container.innerHTML = `<h3 style="color: black;">Caricamento corsi ${year}° Anno per Ingegneria ${degreeName}...</h3>`;
        fetch(`${API_BASE_URL}/api/degree_programs/${degreeProgramId}/courses/${year}`)
            .then(response => {
                if (response.status === 404) {
                    return [];
                }
                if (!response.ok) {
                    throw new Error(`Errore dal server: ${response.status}`);
                }
                return response.json();
            })
            .then(coursesData => {
                let coursesHtml = `<h3>Corsi ${year}° Anno</h3><div class="course-list"><ul>`;
                if (Array.isArray(coursesData) && coursesData.length > 0) {
                    coursesData.forEach(course => {
                        coursesHtml += `
                            <li id="course-${course.id}">
                                <span>${course.name}</span>
                                <a href="#" class="view-notes-btn" data-course-id="${course.id}">Vedi Appunti</a>
                                <div class="notes-container" id="notes-for-course-${course.id}" style="display: none;"></div>
                            </li>`;
                    });
                } else {
                    coursesHtml += `<li>Nessun corso trovato per questo anno.</li>`;
                }
                coursesHtml += `</ul></div>`;
                container.innerHTML = coursesHtml;

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
                container.innerHTML = `<h3 style="color: black;">Errore nel caricamento dei corsi.</h3>`;
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

        const tabInfoMapping = {
            'primoAnnoEnergetica': { degree_name: 'energetica', year: 1 },'secondoAnnoEnergetica': { degree_name: 'energetica', year: 2 },'terzoAnnoEnergetica': { degree_name: 'energetica', year: 3 },
            'primoAnnoCivile': { degree_name: 'civile', year: 1 },'secondoAnnoCivile': { degree_name: 'civile', year: 2 },'terzoAnnoCivile': { degree_name: 'civile', year: 3 },
            'primoAnnoInformatica': { degree_name: 'informatica', year: 1 },'secondoAnnoInformatica': { degree_name: 'informatica', year: 2 },'terzoAnnoInformatica': { degree_name: 'informatica', year: 3 },
            'primoAnnoBiomedica': { degree_name: 'biomedica', year: 1 },'secondoAnnoBiomedica': { degree_name: 'biomedica', year: 2 },'terzoAnnoBiomedica': { degree_name: 'biomedica', year: 3 }
        };

        const info = tabInfoMapping[tabName];
        if (info) {
            const degreeProgramId = degreeProgramIds[info.degree_name];
            if (degreeProgramId) {
                loadCoursesForYear(degreeProgramId, info.year, currentContentDiv, info.degree_name);
            }
        }
    }

    if (currentPage.startsWith('ing_') && document.querySelector('.year-tabs button')) {
        document.querySelector('.year-tabs button').click();
    }

    if (['upload_note.html', 'login.html', 'register.html'].includes(currentPage)) {
        setupAuthAndUploadPages();
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
                    for (let year = 1; year <= 3; year++) {
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

        if (currentPage === 'login.html') {
            const loginForm = document.getElementById('loginForm');
            const messageDiv = document.getElementById('login-message');
            loginForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                messageDiv.textContent = 'Accesso in corso...';
                const username = e.target.username.value;
                const password = e.target.password.value;
                try {
                    const response = await fetch(`${API_BASE_URL}/api/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    const result = await response.json();
                    if (response.ok) {
                        window.location.href = 'index.html';
                    } else {
                        messageDiv.textContent = `Errore: ${result.error || 'Login fallito'}`;
                        messageDiv.className = 'auth-message error';
                    }
                } catch (error) {
                    messageDiv.textContent = 'Errore di rete. Riprova.';
                    messageDiv.className = 'auth-message error';
                }
            });
        }

        if (currentPage === 'register.html') {
            const registerForm = document.getElementById('registerForm');
            const messageDiv = document.getElementById('register-message');
            registerForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                messageDiv.textContent = 'Registrazione in corso...';
                const username = e.target.username.value;
                const email = e.target.email.value;
                const password = e.target.password.value;
                const confirmPassword = e.target.confirm_password.value;

                if (password !== confirmPassword) {
                    messageDiv.textContent = 'Le password non corrispondono.';
                    messageDiv.className = 'error';
                    return;
                }

                 try {
                    const response = await fetch(`${API_BASE_URL}/api/register`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, email, password })
                    });
                    const result = await response.json();
                    if (response.ok) {
                         messageDiv.textContent = 'Registrazione avvenuta con successo! Puoi effettuare il login.';
                         messageDiv.className = 'success';
                         registerForm.reset();
                    } else {
                        messageDiv.textContent = `Errore: ${result.error || 'Registrazione fallita'}`;
                        messageDiv.className = 'error';
                    }
                } catch (error) {
                    messageDiv.textContent = `Errore di rete: ${error.message}`;
                    messageDiv.className = 'error';
                }
            });
        }
    }
});

// *** FUNZIONE GLOBALE PER IL LOGIN CON GOOGLE ***
function onSignIn(googleUser) {
    const isLocal = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';
    const API_BASE_URL = isLocal ? 'http://127.0.0.1:5000' : 'https://studentiunisannio.it';
  
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