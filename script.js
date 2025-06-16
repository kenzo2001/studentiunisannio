document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.navbar a');
    const header = document.querySelector('header');

    // URL base per le API del backend (Fly.io)
    // Sostituisci con l'URL della tua app Fly.io o il tuo dominio personalizzato
    const API_BASE_URL = 'https://studentiunisannio.it'; // Se il tuo dominio funziona già

    // Mappa i nomi delle specializzazioni ai loro ID nel database
    const degreeProgramIds = {
        'energetica': 1,
        'civile': 2,
        'informatica': 3,
        'biomedica': 4
    };

    // Funzione per attivare il tab della navigazione principale e colorare l'header
    // Sostituisci la vecchia funzione con questa
function activateMainTabAndHeader() {
    const navLinks = document.querySelectorAll('.navbar a');
    const header = document.querySelector('header');
    const navbar = document.querySelector('.navbar'); // Aggiunta questa riga

    // Resetta le classi di colore
    navLinks.forEach(link => {
        link.classList.remove('active-home', 'active-ding', 'active-dst', 'active-demm', 'active-contatti');
    });
    header.classList.remove('header-home', 'header-ding', 'header-dst', 'header-demm', 'header-contatti', 'header-ingegneria');
    navbar.classList.remove('navbar-home', 'navbar-ding', 'navbar-dst', 'navbar-demm', 'navbar-contatti', 'navbar-ingegneria'); // Aggiunta questa riga

    const currentPage = window.location.pathname.split('/').pop();
    const isIngPage = currentPage.startsWith('ing_');
    const isAuthPage = ['upload_note.html', 'login.html', 'register.html'].includes(currentPage);

    if (isIngPage || isAuthPage) {
        header.classList.add('header-ingegneria');
        navbar.classList.add('navbar-ingegneria'); // Aggiunta questa riga
    }

    navLinks.forEach(link => {
        const linkFileName = link.href.split('/').pop();

        if ((currentPage === '' || currentPage === 'index.html') && linkFileName === 'index.html') {
            link.classList.add('active-home');
            header.classList.add('header-home');
            navbar.classList.add('navbar-home'); // Aggiunta questa riga
        } else if (currentPage === linkFileName) {
            const tabId = link.id;
            if (tabId && tabId.startsWith('nav-')) {
                const tabName = tabId.replace('nav-', '');
                link.classList.add('active-' + tabName);
                header.classList.add('header-' + tabName);
                navbar.classList.add('navbar-' + tabName); // Aggiunta questa riga
            }
        }
    });
}

    // Inizializza la navigazione principale e l'header
    activateMainTabAndHeader();


    // Funzione GLOBALE per gestire l'apertura/chiusura dei tab degli anni e caricare i corsi
    window.openYearTab = function(evt, tabName) {
        console.log(`openYearTab chiamato per: ${tabName}`);

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
        if (!currentContentDiv) {
            console.error(`Errore: Div con ID "${tabName}" non trovato.`);
            return;
        }
        currentContentDiv.style.display = "block";
        currentContentDiv.classList.add("active");
        evt.currentTarget.classList.add("active");

        const tabInfoMapping = {
            'primoAnnoEnergetica': { degree_name: 'energetica', year: 1 },
            'secondoAnnoEnergetica': { degree_name: 'energetica', year: 2 },
            'terzoAnnoEnergetica': { degree_name: 'energetica', year: 3 },
            'primoAnnoCivile': { degree_name: 'civile', year: 1 },
            'secondoAnnoCivile': { degree_name: 'civile', year: 2 },
            'terzoAnnoCivile': { degree_name: 'civile', year: 3 },
            'primoAnnoInformatica': { degree_name: 'informatica', year: 1 },
            'secondoAnnoInformatica': { degree_name: 'informatica', year: 2 },
            'terzoAnnoInformatica': { degree_name: 'informatica', year: 3 },
            'primoAnnoBiomedica': { degree_name: 'biomedica', year: 1 },
            'secondoAnnoBiomedica': { degree_name: 'biomedica', year: 2 },
            'terzoAnnoBiomedica': { degree_name: 'biomedica', year: 3 }
        };

        const info = tabInfoMapping[tabName];
        if (info) {
            const degreeProgramId = degreeProgramIds[info.degree_name];
            const year = info.year;

            if (degreeProgramId) {
                currentContentDiv.innerHTML = `<h3 style="color: black;">Caricamento corsi ${year}° Anno per Ingegneria ${info.degree_name}...</h3>`;
                console.log(`Richiesta corsi per degreeProgramId: ${degreeProgramId}, anno: ${year}`);

                fetch(`${API_BASE_URL}/api/degree_programs/${degreeProgramId}/courses/${year}`)
                    .then(response => {
                        console.log(`Risposta API status: ${response.status}`);
                        if (!response.ok) {
                            if (response.status === 404) {
                                return { message: "Nessun corso trovato per questo anno e specializzazione." };
                            }
                            throw new Error(`Errore HTTP! Stato: ${response.status} - ${response.statusText}`);
                        }
                        return response.json();
                    })
                    .then(coursesData => {
                        console.log('Dati corsi ricevuti:', coursesData);
                        let coursesHtml = `<h3>Corsi ${year}° Anno</h3><div class="course-list"><ul>`;

                        if (Array.isArray(coursesData) && coursesData.length > 0) {
                            coursesData.forEach(course => {
                                coursesHtml += `
                                    <li id="course-${course.id}">
                                        <span>${course.name}</span>
                                        <span>(CFU non specificati)</span>
                                        <a href="#" class="view-notes-btn" data-course-id="${course.id}">Vedi Appunti</a>
                                        <div class="notes-container" id="notes-for-course-${course.id}" style="display: none;">
                                            </div>
                                    </li>
                                `;
                            });
                        } else if (coursesData.message) {
                            coursesHtml += `<li>${coursesData.message}</li>`;
                        } else {
                            coursesHtml += `<li>Nessun corso trovato per questo anno.</li>`;
                        }
                        coursesHtml += `</ul></div>`;
                        currentContentDiv.innerHTML = coursesHtml;

                        currentContentDiv.querySelectorAll('.view-notes-btn').forEach(button => {
                            button.addEventListener('click', function(event) {
                                event.preventDefault();
                                const courseId = this.dataset.courseId;
                                const notesContainer = document.getElementById(`notes-for-course-${courseId}`);
                                if (notesContainer.style.display === 'none') {
                                    loadNotesForCourse(courseId, notesContainer);
                                    notesContainer.style.display = 'block';
                                    this.textContent = 'Nascondi Appunti';
                                } else {
                                    notesContainer.style.display = 'none';
                                    this.textContent = 'Vedi Appunti';
                                }
                            });
                        });

                    })
                    .catch(error => {
                        console.error('Errore nel caricamento dei corsi:', error);
                        currentContentDiv.innerHTML = `<h3 style="color: black;">Errore nel caricamento dei corsi: ${error.message}. Assicurati che il backend sia in esecuzione (${API_BASE_URL}) e che i dati siano presenti.</h3>`;
                    });
            } else {
                currentContentDiv.innerHTML = `<h3 style="color: black;">Errore: ID Corso di Laurea non trovato per ${info.degree_name}. Controlla la mappa 'degreeProgramIds' nello script.</h3>`;
            }
        }
    }

    // FUNZIONE CORRETTA: Carica gli appunti per un dato corso
    function loadNotesForCourse(courseId, containerElement) {
        console.log(`loadNotesForCourse chiamato per courseId: ${courseId}`);
        containerElement.innerHTML = `<p style="color: black;">Caricamento appunti...</p>`;

        fetch(`${API_BASE_URL}/api/courses/${courseId}/notes`)
            .then(response => {
                console.log(`Risposta API appunti status: ${response.status}`);
                if (response.status === 404) {
                    return { message: "Nessun appunto trovato per questo corso." };
                }
                if (!response.ok) {
                    throw new Error(`Errore HTTP! Stato: ${response.status} - ${response.statusText}`);
                }
                return response.json();
            })
            .then(notesData => {
                console.log('Dati appunti ricevuti:', notesData);
                let notesHtml = `<div class="course-notes-list">`;
                if (Array.isArray(notesData) && notesData.length > 0) {
                    notesData.forEach(note => {
                        const downloadApiUrl = `${API_BASE_URL}/api/notes/${note.id}/download`;
                        notesHtml += `
                            <div class="note-item">
                                <h4>${note.title}</h4>
                                <p>${note.description || 'Nessuna descrizione.'}</p>
                                <p>Caricato da: ${note.uploader_name || 'Anonimo'} il ${new Date(note.upload_date).toLocaleDateString()}</p>
                                <a href="${downloadApiUrl}" class="download-note-btn" target="_blank">Scarica Appunto</a>
                            </div>
                        `;
                    });
                } else if (notesData.message) {
                    notesHtml += `<p>${notesData.message}</p>`;
                } else {
                    notesHtml += `<p>Nessun appunto disponibile per questo corso.</p>`;
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
                                    console.error('URL di download non trovato nella risposta API:', data);
                                    alert('Impossibile ottenere il link per il download.');
                                }
                            })
                            .catch(error => {
                                console.error('Errore durante il recupero del link di download:', error);
                                alert('Si è verificato un errore di rete.');
                            });
                    });
                });
            })
            .catch(error => {
                console.error('Errore nel caricamento degli appunti:', error);
                containerElement.innerHTML = `<p style="color: black;">Errore nel caricamento degli appunti: ${error.message}.</p>`;
            });
    }

    // Attiva il primo tab per gli anni al caricamento delle pagine di ingegneria
    if (currentPage.startsWith('ing_') && document.querySelector('.year-tabs button')) {
        const firstYearButton = document.querySelector('.year-tabs button');
        firstYearButton.click();
    }

    // Gestione dell'inizializzazione della pagina di upload/registrazione/login
    if (currentPage === 'upload_note.html' || currentPage === 'login.html' || currentPage === 'register.html') {
        setupAuthPages();
    }

    // NUOVA FUNZIONE: Inizializzazione delle pagine di autenticazione
    function setupAuthPages() {
        // --- LOGICA PER UPLOAD_NOTE.HTML ---
        if (currentPage === 'upload_note.html') {
            const departmentSelect = document.getElementById('departmentSelect');
            const degreeProgramSelect = document.getElementById('degreeProgramSelect');
            const courseSelect = document.getElementById('courseSelect');
            const uploadNoteForm = document.getElementById('uploadNoteForm');
            const uploadMessage = document.getElementById('upload-message');

            // Funzione per caricare i dipartimenti
            async function loadDepartments() {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/departments`);
                    const departments = await response.json();

                    departmentSelect.innerHTML = '<option value="">Seleziona Dipartimento</option>';
                    departments.forEach(dept => {
                        const option = document.createElement('option');
                        option.value = dept.id;
                        option.textContent = dept.name;
                        departmentSelect.appendChild(option);
                    });
                } catch (error) {
                    console.error('Errore nel caricamento dei dipartimenti:', error);
                    uploadMessage.textContent = 'Errore nel caricamento dei dipartimenti.';
                    uploadMessage.className = 'error';
                }
            }

            // Funzione per caricare i corsi di laurea in base al dipartimento selezionato
            async function loadDegreePrograms(departmentId) {
                degreeProgramSelect.innerHTML = '<option value="">Seleziona Corso di Laurea</option>';
                degreeProgramSelect.disabled = true;
                courseSelect.innerHTML = '<option value="">Seleziona Esame/Materia</option>';
                courseSelect.disabled = true;

                if (!departmentId) return;

                try {
                    const response = await fetch(`${API_BASE_URL}/api/departments/${departmentId}/degree_programs`);
                    const degreePrograms = await response.json();

                    degreePrograms.forEach(dp => {
                        const option = document.createElement('option');
                        option.value = dp.id;
                        option.textContent = dp.name;
                        degreeProgramSelect.appendChild(option);
                    });
                    degreeProgramSelect.disabled = false;
                } catch (error) {
                    console.error('Errore nel caricamento dei corsi di laurea:', error);
                    uploadMessage.textContent = 'Errore nel caricamento dei corsi di laurea.';
                    uploadMessage.className = 'error';
                }
            }

            // Funzione per caricare gli esami in base al corso di laurea selezionato
            async function loadCourses(degreeProgramId) {
                courseSelect.innerHTML = '<option value="">Seleziona Esame/Materia</option>';
                courseSelect.disabled = true;

                if (!degreeProgramId) return;

                try {
                    let allCourses = [];
                    for (let year = 1; year <= 3; year++) {
                        const response = await fetch(`${API_BASE_URL}/api/degree_programs/${degreeProgramId}/courses/${year}`);
                        if (response.ok) {
                            const coursesByYear = await response.json();
                            allCourses = allCourses.concat(coursesByYear);
                        }
                    }

                    allCourses.sort((a,b) => a.name.localeCompare(b.name));
                    allCourses.forEach(course => {
                        const option = document.createElement('option');
                        option.value = course.id;
                        option.textContent = `${course.name} (${course.year}° Anno)`;
                        courseSelect.appendChild(option);
                    });
                    courseSelect.disabled = false;
                } catch (error) {
                    console.error('Errore nel caricamento degli esami:', error);
                    uploadMessage.textContent = 'Errore nel caricamento degli esami.';
                    uploadMessage.className = 'error';
                }
            }

            // Gestione eventi Change
            departmentSelect.addEventListener('change', (e) => loadDegreePrograms(e.target.value));
            degreeProgramSelect.addEventListener('change', (e) => loadCourses(e.target.value));

            // Gestione del submit del form
            uploadNoteForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                uploadMessage.textContent = 'Caricamento in corso...';
                uploadMessage.className = '';

                const formData = new FormData(this);

                try {
                    const response = await fetch(`${API_BASE_URL}/api/upload_note`, {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (response.ok) {
                        uploadMessage.textContent = 'Appunto caricato con successo!';
                        uploadMessage.className = 'success';
                        uploadNoteForm.reset();
                        degreeProgramSelect.innerHTML = '<option value="">Seleziona Corso di Laurea</option>';
                        degreeProgramSelect.disabled = true;
                        courseSelect.innerHTML = '<option value="">Seleziona Esame/Materia</option>';
                        courseSelect.disabled = true;
                    } else {
                        uploadMessage.textContent = `Errore: ${result.error || 'Qualcosa è andato storto'}`;
                        uploadMessage.className = 'error';
                    }
                } catch (error) {
                    console.error('Errore durante l\'upload:', error);
                    uploadMessage.textContent = `Errore di rete o server non raggiungibile: ${error.message}`;
                    uploadMessage.className = 'error';
                }
            });

            // Carica i dipartimenti all'apertura della pagina
            loadDepartments();
        }

        // --- LOGICA PER LOGIN.HTML ---
        if (currentPage === 'login.html') {
            const loginForm = document.getElementById('loginForm');
            const loginMessage = document.getElementById('login-message');

            if (loginForm) {
                loginForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    loginMessage.textContent = 'Accesso in corso...';
                    loginMessage.className = '';

                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;

                    try {
                        const response = await fetch(`${API_BASE_URL}/api/login`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ username, password })
                        });

                        const result = await response.json();

                        if (response.ok) {
                            loginMessage.textContent = 'Login avvenuto con successo! Reindirizzamento...';
                            loginMessage.className = 'success';
                            // Salva lo stato di login (es. in localStorage o session cookie)
                            localStorage.setItem('user_logged_in', 'true');
                            localStorage.setItem('username', result.user.username);
                            // Reindirizza alla home o a una pagina protetta
                            window.location.href = 'index.html';
                        } else {
                            loginMessage.textContent = `Errore: ${result.error || 'Login fallito'}`;
                            loginMessage.className = 'error';
                        }
                    } catch (error) {
                        console.error('Errore durante il login:', error);
                        loginMessage.textContent = `Errore di rete o server non raggiungibile: ${error.message}`;
                        loginMessage.className = 'error';
                    }
                });
            }
        }

        // --- LOGICA PER REGISTER.HTML ---
        if (currentPage === 'register.html') {
            const registerForm = document.getElementById('registerForm');
            const registerMessage = document.getElementById('register-message');

            if (registerForm) {
                registerForm.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    registerMessage.textContent = 'Registrazione in corso...';
                    registerMessage.className = '';

                    const username = document.getElementById('reg-username').value;
                    const email = document.getElementById('reg-email').value;
                    const password = document.getElementById('reg-password').value;
                    const confirmPassword = document.getElementById('confirm-password').value;

                    if (password !== confirmPassword) {
                        registerMessage.textContent = 'Le password non corrispondono.';
                        registerMessage.className = 'error';
                        return;
                    }

                    try {
                        const response = await fetch(`${API_BASE_URL}/api/register`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ username, email, password })
                        });

                        const result = await response.json();

                        if (response.ok) {
                            registerMessage.textContent = 'Registrazione avvenuta con successo! Puoi effettuare il login.';
                            registerMessage.className = 'success';
                            registerForm.reset();
                        } else {
                            registerMessage.textContent = `Errore: ${result.error || 'Registrazione fallita'}`;
                            registerMessage.className = 'error';
                        }
                    } catch (error) {
                        console.error('Errore durante la registrazione:', error);
                        registerMessage.textContent = `Errore di rete o server non raggiungibile: ${error.message}`;
                        registerMessage.className = 'error';
                    }
                });
            }
        }

        // Gestione della UI per lo stato di login/logout nella navbar
        const userStatusElement = document.getElementById('user-status');
        const loginLink = document.getElementById('nav-login');
        const registerLink = document.getElementById('nav-register');
        const logoutLink = document.getElementById('nav-logout');
        const uploadNoteLink = document.getElementById('nav-upload'); // Assumi un ID per il link di upload

        async function checkLoginStatus() {
            try {
                // NOTA: il check dello stato di login basato su cookie è gestito dal backend
                const response = await fetch(`${API_BASE_URL}/api/status`);
                if (!response.ok) { // Se il server restituisce errore (es. 500)
                    throw new Error('Errore server nel controllo stato');
                }
                const data = await response.json();

                if (data.logged_in && userStatusElement) {
                    userStatusElement.textContent = `Benvenuto, ${data.user.username}!`;
                    if(loginLink) loginLink.style.display = 'none';
                    if(registerLink) registerLink.style.display = 'none';
                    if(logoutLink) logoutLink.style.display = 'inline-block';
                    if(uploadNoteLink) uploadNoteLink.style.display = 'inline-block';
                } else if(userStatusElement) {
                     userStatusElement.textContent = ''; // Non mostrare nulla se non loggato
                    if(loginLink) loginLink.style.display = 'inline-block';
                    if(registerLink) registerLink.style.display = 'inline-block';
                    if(logoutLink) logoutLink.style.display = 'none';
                    if(uploadNoteLink) uploadNoteLink.style.display = 'none';
                }
            } catch (error) {
                console.error('Errore nel controllo stato login:', error);
                if (userStatusElement) {
                    userStatusElement.textContent = ''; // Nascondi in caso di errore
                }
            }
        }

        if (userStatusElement) {
            checkLoginStatus(); // Controlla lo stato al caricamento di ogni pagina
        }

        if (logoutLink) {
            logoutLink.addEventListener('click', async function(e) {
                e.preventDefault();
                try {
                    const response = await fetch(`${API_BASE_URL}/api/logout`, { method: 'POST' });
                    const result = await response.json();
                    if (response.ok) {
                        alert(result.message);
                        window.location.href = 'login.html'; // Reindirizza al login dopo il logout
                    } else {
                        alert(`Errore logout: ${result.error}`);
                    }
                } catch (error) {
                    console.error('Errore durante il logout:', error);
                    alert('Errore di rete durante il logout.');
                }
            });
        }
    }
});