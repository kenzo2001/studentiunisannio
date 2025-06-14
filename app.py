import os
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session, current_app 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename 
from datetime import datetime
from flask_cors import CORS 
import boto3 
from botocore.exceptions import NoCredentialsError, ClientError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user 

print("DEBUG: Avvio app.py") 

# Inizializza l'app Flask
app = Flask(__name__, static_folder='.', static_url_path='/') 

# --- Configurazione del Database (unica e corretta per PostgreSQL) ---
# Usa la variabile d'ambiente DATABASE_URL fornita da Fly.io per PostgreSQL.
# La parte .replace('postgres://', 'postgresql+psycopg2://') forza il dialetto corretto per SQLAlchemy.
# Il fallback 'sqlite:///unisannio_appunti.db' è solo per sviluppo locale senza DB esterno.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql+psycopg2://') \
                                        if os.environ.get('DATABASE_URL') else 'sqlite:///unisannio_appunti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# Chiave segreta per le sessioni Flask (ESSENZIALE per sicurezza e mantenimento sessione)
# Prende da variabile d'ambiente FLASK_SECRET_KEY su Fly.io, con un fallback per lo sviluppo locale.
# DEVI IMPOSTARE FLASK_SECRET_KEY SU FLY.IO con una stringa lunga e casuale!
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'la_tua_chiave_segreta_iniziale_di_fallback_sicura')

# --- Configurazione per il Dominio del Cookie di Sessione ---
# Questo è CRUCIALE per i domini personalizzati e i sottodomini.
# Imposta il dominio del cookie per includere tutti i sottodomini (nota il '.' iniziale)
# CAMBIA QUESTO VALORE IN BASE AL DOMINIO CHE STAI EFFETTIVAMENTE USANDO PER ACCEDERE ALL'APP IN PRODUZIONE.
# Se usi studentiunisannio1991.fly.dev: app.config['SESSION_COOKIE_DOMAIN'] = '.studentiunisannio1991.fly.dev'
# Se usi studentiunisannio.it o www.studentiunisannio.it:
app.config['SESSION_COOKIE_DOMAIN'] = '.studentiunisannio.it' 

# --- Configurazione per i Domini Email Permessi per la Registrazione ---
app.config['ALLOWED_EMAIL_DOMAINS'] = ['unisannio.it', 'studenti.unisannio.it', 'example.com'] # <--- CAMBIA QUESTI DOMINI!

# Inizializza SQLAlchemy e collegalo all'app
db = SQLAlchemy() 
db.init_app(app) 

# Configurazione CORS (con supports_credentials=True, NECESSARIO per i cookie di sessione cross-origin)
CORS(app, supports_credentials=True) 

# --- Configurazione Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)

# Funzione richiesta da Flask-Login per caricare un utente dato il suo ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Funzione per gestire l'accesso non autorizzato (richiesta da Flask-Login)
@login_manager.unauthorized_handler
def unauthorized():
    # Se la richiesta è AJAX (API), restituisci 401 JSON
    if request.path.startswith('/api/'):
        return jsonify({"error": "Accesso non autorizzato. Effettua il login."}), 401
    # Se la richiesta è una navigazione diretta del browser, reindirizza alla pagina di login
    return redirect(url_for('serve_login_page')) 

# --- Configurazione AWS S3 ---
# Prende le credenziali e la regione dalle variabili d'ambiente di Fly.io
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_REGION = os.environ.get("S3_REGION") 

s3_client = None
if S3_KEY and S3_SECRET and S3_REGION and S3_BUCKET:
    print("DEBUG: Variabili d'ambiente AWS S3 trovate. Tentativo di inizializzazione client S3.") 
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            region_name=S3_REGION
        )
        print("DEBUG: Client S3 inizializzato con successo.") 
    except Exception as e:
        print(f"ERRORE DEBUG: Errore nell'inizializzazione del client S3: {e}") 
else:
    print("ERRORE DEBUG: Variabili d'ambiente AWS S3 non impostate. Le operazioni S3 falliranno.") 

# --- Validazione Tipo File ---
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'} 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Definizione dei Modelli del Database ---
class User(UserMixin, db.Model): 
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

class Department(db.Model):
    __tablename__ = 'departments' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    degree_programs = db.relationship('DegreeProgram', backref='department', lazy=True)
    def to_dict(self):
        return {"id": self.id, "name": self.name}

class DegreeProgram(db.Model):
    __tablename__ = 'degree_programs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    courses = db.relationship('Course', backref='degree_program', lazy=True)
    def to_dict(self):
        return {"id": self.id, "name": self.name, "department_id": self.department_id}

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False) 
    degree_program_id = db.Column(db.Integer, db.ForeignKey('degree_programs.id'), nullable=False)
    notes = db.relationship('Note', backref='course', lazy=True)
    def to_dict(self):
        return {
            "id": self.id, 
            "name": self.name, 
            "year": self.year, 
            "degree_program_id": self.degree_program_id
        }

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    s3_key = db.Column(db.String(255), nullable=False) 
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    uploader_name = db.Column(db.String(80), nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "s3_key": self.s3_key, 
            "upload_date": self.upload_date.isoformat(),
            "course_id": self.course_id,
            "uploader_name": self.uploader_name
        }


# --- Rotte per Servire i File del Frontend ---

# NUOVA LOGICA PER LA HOMEPAGE: Reindirizza al login se non autenticato
@app.route('/')
def serve_home_or_login():
    if current_user.is_authenticated:
        return send_from_directory('.', 'index.html')
    else:
        return redirect(url_for('serve_login_page'))

# Rotta per servire la pagina di login
@app.route('/login.html')
def serve_login_page():
    return send_from_directory('.', 'login.html')

# Rotta per servire la pagina di registrazione
@app.route('/register.html')
def serve_register_page():
    return send_from_directory('.', 'register.html')

# Rotta generica per servire tutti gli altri file statici (es. ding.html, style.css, script.js)
# Questa rotta deve stare DOPO le rotte specifiche come /login.html e /register.html
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('.', filename)


# --- Rotte API ---

# API per la registrazione
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Username, email e password sono obbligatori"}), 400

    # Validazione del dominio email
    allowed_domains = app.config.get('ALLOWED_EMAIL_DOMAINS', [])
    email_domain = email.split('@')[-1]

    if allowed_domains and email_domain not in allowed_domains: 
        return jsonify({"error": f"Registrazione non consentita per il dominio {email_domain}. Sono ammessi solo domini: {', '.join(allowed_domains)}"}), 403

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username già registrato"}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email già registrata"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registrazione avvenuta con successo!"}), 201

# API per il login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user) 
        return jsonify({"message": "Login avvenuto con successo!", "user": user.to_dict()}), 200
    else:
        return jsonify({"error": "Username o password non validi"}), 401

# API per il logout
@app.route('/api/logout', methods=['POST'])
@login_required 
def logout():
    logout_user() 
    return jsonify({"message": "Logout avvenuto con successo!"}), 200

# API per controllare lo stato di login dell'utente corrente
@app.route('/api/status', methods=['GET'])
def get_status():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "user": current_user.to_dict()}), 200
    else:
        return jsonify({"logged_in": False}), 200

# API per ottenere tutti i dipartimenti
@app.route('/api/departments', methods=['GET'])
def get_departments():
    departments = Department.query.all()
    return jsonify([d.to_dict() for d in departments])

@app.route('/api/departments/<int:department_id>/degree_programs', methods=['GET'])
def get_degree_programs_by_department(department_id):
    degree_programs = DegreeProgram.query.filter_by(department_id=department_id).all()
    if not degree_programs:
        return jsonify({"message": "Nessun corso di laurea trovato per questo dipartimento"}), 404
    return jsonify([dp.to_dict() for dp in degree_programs])

@app.route('/api/degree_programs/<int:degree_program_id>/courses/<int:year>', methods=['GET'])
def get_courses_by_degree_and_year(degree_program_id, year):
    courses = Course.query.filter_by(degree_program_id=degree_program_id, year=year).all()
    if not courses:
        return jsonify({"message": "Nessun corso trovato per questo corso di laurea e anno"}), 404
    return jsonify([c.to_dict() for c in courses])

# API per ottenere tutti gli appunti di un esame
@app.route('/api/courses/<int:course_id>/notes', methods=['GET'])
def get_notes_by_course(course_id):
    notes = Note.query.filter_by(course_id=course_id).all()
    if not notes:
        return jsonify({"message": "Nessun appunto trovato per questo esame"}), 404
    return jsonify([n.to_dict() for n in notes]) 

# API per caricare un nuovo appunto su S3 (PROTETTA: richiede login)
@app.route('/api/upload_note', methods=['POST'])
@login_required 
def upload_note():
    if not s3_client:
        return jsonify({"error": "Servizio S3 non inizializzato. Controlla le variabili d'ambiente AWS."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "Nessun file fornito"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Nome file vuoto"}), 400
    
    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        key = f"{timestamp}_{secure_filename(file.filename)}" 
        
        try:
            s3_client.upload_fileobj(file, S3_BUCKET, key)
            print(f"File {key} caricato con successo nel bucket S3: {S3_BUCKET}")
        except NoCredentialsError:
            return jsonify({"error": "Credenziali AWS non disponibili"}), 500
        except ClientError as e: 
            return jsonify({"error": f"Errore client S3: {e.response['Error']['Message']}"}), 500
        except Exception as e:
            return jsonify({"error": f"Errore generico caricamento su S3: {str(e)}"}), 500

        title = request.form.get('title')
        description = request.form.get('description', '')
        course_id = request.form.get('course_id')
        
        # Il nome dell'uploader è preso dall'utente attualmente loggato
        uploader_name = current_user.username if current_user.is_authenticated else 'Anonimo' 

        if not title or not course_id:
            try:
                s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
            except Exception as e:
                print(f"Attenzione: Impossibile eliminare file S3 dopo errore dati: {e}")
            return jsonify({"error": "Titolo e ID corso sono obbligatori"}), 400

        try:
            new_note = Note(
                title=title,
                description=description,
                s3_key=key, 
                course_id=int(course_id),
                uploader_name=uploader_name 
            )
            db.session.add(new_note)
            db.session.commit()
            return jsonify({"message": "Appunto caricato con successo!", "note": new_note.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            try:
                s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
            except Exception as e_s3:
                print(f"Attenzione: Impossibile eliminare file S3 dopo errore DB: {e_s3}")
            return jsonify({"error": f"Errore nel salvataggio nel database: {str(e)}"}), 500
    else:
        return jsonify({"error": "Tipo di file non permesso o file non valido"}), 400

# API per scaricare un appunto da S3 (restituisce URL pre-firmato)
@app.route('/api/notes/<int:note_id>/download', methods=['GET'])
def download_note(note_id):
    if not s3_client:
        return jsonify({"error": "Servizio S3 non inizializzato. Controlla le variabili d'ambiente AWS."}), 500

    note = Note.query.get(note_id)
    if not note:
        return jsonify({"message": "Appunto non trovato"}), 404
    
    try:
        s3_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': note.s3_key},
            ExpiresIn=300 
        )
        return jsonify({"download_url": s3_url}) 
    except NoCredentialsError:
        return jsonify({"error": "Credenziali AWS non disponibili"}), 500
    except ClientError as e:
        return jsonify({"error": f"Errore client S3: {e.response['Error']['Message']}"}), 500
    except Exception as e:
        return jsonify({"error": f"Errore generico generazione URL S3: {str(e)}"}), 500

# L'esecuzione dell'app è gestita da Gunicorn in produzione.
# La logica di inizializzazione del DB è spostata in init_db.py.