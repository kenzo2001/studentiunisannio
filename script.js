document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    // URL base per le API del backend
    const API_BASE_URL = 'https://studentiunisannio.it';

    const degreeProgramIds = {
        'energetica': 1,
        'civile': 2,
        'informatica': 3,
        'biomedica': 4
    };

    // Funzione principale che organizza l'inizializzazione della pagina
    function initializePage() {
        activateMainTabAndHeader();
        checkLoginStatus(); // Gestisce la UI di login e gli annunci AdSense

        // Esegue le funzioni specifiche per ogni pagina
        if (currentPage.startsWith('ing_')) {
            const firstYearButton = document.querySelector('.year-tabs button');
            if (firstYearButton) firstYearButton.click();
        }
        if (currentPage === 'login.html') setupLoginPage();
        if (currentPage === 'register.html') setupRegisterPage();
        if (currentPage === 'upload_note.html') setupUploadPage();
    }

    function activateMainTabAndHeader() {
        const navLinks = document.querySelectorAll('.navbar a');
        const header = document.querySelector('header');
        const navbar = document.querySelector('.navbar');
        if (!header || !navbar) return;

        // Resetta le classi
        navLinks.forEach(link => link.className = link.className.replace(/ active-.*|navbar-.*/g, ''));
        header.className = header.className.replace(/ header-.*|navbar-.*/g, '');
        navbar.className = navbar.className.replace(/ header-.*|navbar-.*/g, '');

        const isIngPage = currentPage.startsWith('ing_');
        const isAuthPage = ['upload_note.html', 'login.html', 'register.html'].includes(currentPage);

        if (isIngPage || isAuthPage) {
            header.classList.add('header-ingegneria');
            navbar.classList.add('navbar-ingegneria');
        }

        navLinks.forEach(link => {
            const linkFileName = link.href.split('/').pop();
            const isCurrentPage = currentPage === linkFileName || (currentPage === 'index.html' && (linkFileName === '' || linkFileName === 'index.html'));

            if (isCurrentPage) {
                const tabId = link.id;
                if (tabId && tabId.startsWith('nav-')) {
                    const tabName = tabId.replace('nav-', '');
                    link.classList.add('active-' + tabName);
                    header.classList.add('header-' + tabName);
                    navbar.classList.add('navbar-' + tabName);
                }
            }
        });
    }

    async function checkLoginStatus() {
        function loadAdSenseScript() {
            if (document.getElementById('adsense-script')) return;
            const script = document.createElement('script');
            script.id = 'adsense-script';
            script.async = true;
            script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8614560189633962`;
            script.crossOrigin = 'anonymous';
            document.head.appendChild(script);
        }

        const userStatusElement = document.getElementById('user-status');
        const loginLink = document.getElementById('nav-login');
        const registerLink = document.getElementById('nav-register');
        const logoutLink = document.getElementById('nav-logout');
        const uploadNoteLink = document.getElementById('nav-upload');
        const adContainers = document.querySelectorAll('.adsense-container');

        try {
            const response = await fetch(`${API_BASE_URL}/api/status`, { credentials: 'include' });
            const data = await response.json();

            if (data.logged_in) {
                if(userStatusElement) userStatusElement.textContent = `Benvenuto, ${data.user.username}!`;
                if(loginLink) loginLink.style.display = 'none';
                if(registerLink) registerLink.style.display = 'none';
                if(logoutLink) logoutLink.style.display = 'inline-block';
                if(uploadNoteLink) uploadNoteLink.style.display = 'inline-block';
                adContainers.forEach(c => c.style.display = 'none');
            } else {
                if(userStatusElement) userStatusElement.textContent = '';
                if(loginLink) loginLink.style.display = 'inline-block';
                if(registerLink) registerLink.style.display = 'inline-block';
                if(logoutLink) logoutLink.style.display = 'none';
                if(uploadNoteLink) uploadNoteLink.style.display = 'none';
                loadAdSenseScript();
                adContainers.forEach(c => c.style.display = 'block');
            }
        } catch (error) {
            console.error('Errore nel controllo stato login:', error);
        }

        if (logoutLink) {
            logoutLink.addEventListener('click', async (e) => {
                e.preventDefault();
                try {
                    await fetch(`${API_BASE_URL}/api/logout`, { method: 'POST', credentials: 'include' });
                    window.location.href = 'login.html';
                } catch (error) { console.error('Errore logout:', error); }
            });
        }
    }
    
    // Funzioni specifiche per le pagine
    function setupLoginPage() { /* ... */ }
    function setupRegisterPage() { /* ... */ }

    function setupUploadPage() {
        const departmentSelect = document.getElementById('departmentSelect');
        const degreeProgramSelect = document.getElementById('degreeProgramSelect');
        const courseSelect = document.getElementById('courseSelect');
        const uploadNoteForm = document.getElementById('uploadNoteForm');
        const uploadMessage = document.getElementById('upload-message');
        if (!uploadNoteForm) return;

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
            } catch (error) { console.error('Errore caricamento dipartimenti:', error); }
        }

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
            } catch (error) { console.error('Errore caricamento corsi di laurea:', error); }
        }

        async function loadCourses(degreeProgramId) {
            courseSelect.innerHTML = '<option value="">Seleziona Esame/Materia</option>';
            courseSelect.disabled = true;
            if (!degreeProgramId) return;
            try {
                let allCourses = [];
                for (let year = 1; year <= 5; year++) { // Increased to 5 years for safety
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
            } catch (error) { console.error('Errore caricamento esami:', error); }
        }

        departmentSelect.addEventListener('change', (e) => loadDegreePrograms(e.target.value));
        degreeProgramSelect.addEventListener('change', (e) => loadCourses(e.target.value));
        
        uploadNoteForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            uploadMessage.textContent = 'Caricamento in corso...';
            uploadMessage.className = '';
            const formData = new FormData(this);
            try {
                const response = await fetch(`${API_BASE_URL}/api/upload_note`, {
                    method: 'POST',
                    body: formData,
                    credentials: 'include'
                });
                const result = await response.json();
                if (response.ok) {
                    uploadMessage.textContent = 'Appunto caricato con successo!';
                    uploadMessage.className = 'success';
                    uploadNoteForm.reset();
                    // Reset dropdowns
                } else {
                    uploadMessage.textContent = `Errore: ${result.error || 'Qualcosa è andato storto'}`;
                    uploadMessage.className = 'error';
                }
            } catch (error) {
                uploadMessage.textContent = 'Errore di rete.';
                uploadMessage.className = 'error';
            }
        });
        
        loadDepartments();
    }
    
    // Altre funzioni...
    window.openYearTab = function(evt, tabName) { /* ... codice esistente ... */ };
    function loadNotesForCourse(courseId, containerElement) { /* ... codice esistente ... */ };

    // Esecuzione all'avvio
    initializePage();
});