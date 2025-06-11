document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.navbar a');
    const header = document.querySelector('header'); 

    // URL base per le API del backend (Fly.io)
    // Sostituisci con l'URL della tua app Fly.io o il tuo dominio personalizzato
    const API_BASE_URL = 'https://studentiunisannio1991.fly.dev/api'; 
    // const API_BASE_URL = 'https://studentiunisannio.it/api'; // Se il tuo dominio funziona già

    // Mappa i nomi delle specializzazioni ai loro ID nel database
    const degreeProgramIds = {
        'energetica': 1, 
        'civile': 2,    
        'informatica': 3, 
        'biomedica': 4 
    };

    // Funzione per attivare il tab della navigazione principale e colorare l'header
    function activateMainTabAndHeader() { 
        navLinks.forEach(link => {
            link.classList.remove('active-home', 'active-ding', 'active-dst', 'active-demm', 'active-contatti');
        });
        
        header.classList.remove('header-home', 'header-ding', 'header-dst', 'header-demm', 'header-contatti', 'header-ingegneria');

        const isIngPage = currentPage.startsWith('ing_energetica.html') ||
                          currentPage.startsWith('ing_civile.html') ||
                          currentPage.startsWith('ing_informatica.html') ||
                          currentPage.startsWith('ing_biomedica.html');
        
        const isUploadPage = currentPage === 'upload_note.html'; // Nuova variabile per la pagina di upload

        if (isIngPage || isUploadPage) { // Ora include anche la pagina di upload nel rosso
            header.classList.add('header-ingegneria');
        } else {
            navLinks.forEach(link => {
                const linkFileName = link.href.split('/').pop(); 
                
                if ((currentPage === '' || currentPage === 'index.html') && linkFileName === 'index.html') {
                    link.classList.add('active-home');
                    header.classList.add('header-home');
                } 
                else if (currentPage === linkFileName) {
                    const tabId = link.id; 
                    if (tabId && tabId.startsWith('nav-')) {
                        const tabName = tabId.replace('nav-', ''); 
                        link.classList.add('active-' + tabName);
                        header.classList.add('header-' + tabName);
                    }
                }
            });
        }
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

                fetch(`${API_BASE_URL}/degree_programs/${degreeProgramId}/courses/${year}`)
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
                                event.preventDefault(); // Impedisce al link di navigare
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

    // NUOVA FUNZIONE: Carica gli appunti per un dato corso
    function loadNotesForCourse(courseId, containerElement) {
        console.log(`loadNotesForCourse chiamato per courseId: ${courseId}`);
        containerElement.innerHTML = `<p style="color: black;">Caricamento appunti...</p>`; 
        
        fetch(`${API_BASE_URL}/courses/${courseId}/notes`)
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
                        const downloadUrl = `${API_BASE_URL}/notes/${note.id}/download`;
                        notesHtml += `
                            <div class="note-item">
                                <h4>${note.title}</h4>
                                <p>${note.description || 'Nessuna descrizione.'}</p>
                                <p>Caricato da: ${note.uploader_name} il ${new Date(note.upload_date).toLocaleDateString()}</p>
                                <a href="${downloadUrl}" class="download-note-btn" target="_blank">Scarica Appunto</a>
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

    // NUOVA FUNZIONE: Inizializzazione della pagina di upload
    // Questa funzione viene chiamata solo se la pagina corrente è upload_note.html
    function setupUploadPage() {
        const departmentSelect = document.getElementById('departmentSelect');
        const degreeProgramSelect = document.getElementById('degreeProgramSelect');
        const courseSelect = document.getElementById('courseSelect');
        const uploadNoteForm = document.getElementById('uploadNoteForm');
        const uploadMessage = document.getElementById('upload-message');

        // Funzione per caricare i dipartimenti
        async function loadDepartments() {
            try {
                const response = await fetch(`${API_BASE_URL}/departments`);
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
                const response = await fetch(`${API_BASE_URL}/departments/${departmentId}/degree_programs`);
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
                    const response = await fetch(`${API_BASE_URL}/degree_programs/${degreeProgramId}/courses/${year}`);
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
                const response = await fetch(`${API_BASE_URL}/upload_note`, {
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

    // Al caricamento del DOM, controlla quale pagina siamo e inizializza le funzionalità.
    if (currentPage === 'upload_note.html') {
        setupUploadPage();
        // Attiva il tab "DING" nella navbar per la pagina di upload
        const navDing = document.getElementById('nav-ding');
        if (navDing) {
            navDing.classList.add('active-ding'); 
        }
    }
});