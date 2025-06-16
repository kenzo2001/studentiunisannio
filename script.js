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
            if (currentPage === linkFileName || (currentPage === 'index.html' && linkFileName === '')) {
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
    
    // Funzioni specifiche per le pagine di autenticazione e upload
    function setupLoginPage() {
        const loginForm = document.getElementById('loginForm');
        if (!loginForm) return;
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            try {
                const response = await fetch(`${API_BASE_URL}/api/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password }),
                    credentials: 'include'
                });
                if (response.ok) window.location.href = 'index.html';
                else alert('Credenziali non valide.');
            } catch (error) { console.error('Errore di rete:', error); }
        });
    }

    function setupRegisterPage() {
        const registerForm = document.getElementById('registerForm');
        if(!registerForm) return;
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('reg-username').value;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const messageEl = document.getElementById('register-message');
            if (password !== confirmPassword) {
                messageEl.textContent = 'Le password non corrispondono.';
                return;
            }
            try {
                const response = await fetch(`${API_BASE_URL}/api/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password }),
                    credentials: 'include'
                });
                const result = await response.json();
                if (response.ok) {
                    messageEl.textContent = 'Registrazione avvenuta con successo!';
                    messageEl.className = 'auth-message success';
                } else {
                    messageEl.textContent = `Errore: ${result.error}`;
                    messageEl.className = 'auth-message error';
                }
            } catch (error) { console.error('Errore di rete:', error); }
        });
    }

    function setupUploadPage() {
        // Qui andrebbe la logica per la pagina di upload, se necessaria
    }

    // Esecuzione
    initializePage();
});