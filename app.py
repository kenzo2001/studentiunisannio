import os
import uuid
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS
from functools import wraps 
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv
from functools import wraps # AGGIUNGI QUESTA RIGA PER IMPORTARE wraps

# Carica le variabili d'ambiente una sola volta
load_dotenv()

print("DEBUG: Avvio app.py")

app = Flask(__name__, static_folder='.', static_url_path='/')

# --- CONFIGURAZIONE CORS ---
# Permette al frontend su "www" di comunicare con il backend sul dominio root.
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://studentiunisannio.it", "https://www.studentiunisannio.it"],
        "supports_credentials": True
    }
})

# --- CONFIGURAZIONE GENERALE ---
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-per-sviluppo-locale')
app.config['SESSION_COOKIE_DOMAIN'] = '.studentiunisannio.it'
app.config['ALLOWED_EMAIL_DOMAINS'] = ['unisannio.it', 'studenti.unisannio.it']

# --- CONFIGURAZIONE DATABASE SQL (POSTGRESQL/SQLITE) ---
db_url = os.environ.get('DATABASE_URL')
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace('postgres://', 'postgresql+psycopg2://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unisannio_appunti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- CONFIGURAZIONE DATABASE NOSQL (MONGODB) ---
mongo_uri_from_env = os.environ.get("MONGO_URI")
if not mongo_uri_from_env:
    raise ValueError("ERRORE CRITICO: La variabile d'ambiente MONGO_URI non è stata trovata.")
app.config["MONGO_URI"] = mongo_uri_from_env
mongo = PyMongo(app)

# --- CONFIGURAZIONE AWS S3 ---
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_REGION = os.environ.get("S3_REGION")
s3_client = None
if S3_KEY and S3_SECRET and S3_REGION and S3_BUCKET:
    try:
        s3_client = boto3.client('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET, region_name=S3_REGION)
    except Exception as e:
        print(f"ERRORE DEBUG: Errore inizializzazione client S3: {e}")
else:
    print("ERRORE DEBUG: Variabili d'ambiente AWS S3 non impostate.")

# --- CONFIGURAZIONE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)

# --- MODELLI DATABASE ---

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role', 'user') # Nuovo campo: ruolo utente, default 'user'
    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email, "role": self.role} # Includi il ruolo

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    degree_programs = db.relationship('DegreeProgram', backref='department', lazy=True)
    def to_dict(self): return {"id": self.id, "name": self.name}

class DegreeProgram(db.Model):
    __tablename__ = 'degree_programs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    courses = db.relationship('Course', backref='degree_program', lazy=True)
    def to_dict(self): return {"id": self.id, "name": self.name, "department_id": self.department_id}

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    degree_program_id = db.Column(db.Integer, db.ForeignKey('degree_programs.id'), nullable=False)
    notes = db.relationship('Note', backref='course', lazy=True)
    def to_dict(self): return {"id": self.id, "name": self.name, "year": self.year, "degree_program_id": self.degree_program_id}

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    s3_key = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    uploader_name = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False) # Nuovo campo: stato dell'appunto
    def to_dict(self): return {"id": self.id, "title": self.title, "description": self.description, "s3_key": self.s3_key, "upload_date": self.upload_date.isoformat(), "course_id": self.course_id, "uploader_name": self.uploader_name, "status": self.status} # Includi lo stato

# --- GESTIONE SESSIONE UTENTE ---

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    return User(user_data) if user_data else None

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({"error": "Accesso non autorizzato. Effettua il login."}), 401
    return redirect(url_for('serve_login_page'))

# --- Aggiunta dell'header Cross-Origin-Opener-Policy ---
@app.after_request
def add_coop_header(response):
    # Imposta l'header COOP per consentire l'interazione con i popup cross-origin (come Google Sign-In)
    # Questo header è importante per risolvere gli errori 'Cross-Origin-Opener-Policy policy would block...'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
    return response

# --- ROTTE API ---

@app.route('/api/google-login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        token = data.get('token')
        if not token:
            return jsonify({"error": "Token mancante"}), 400

        idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.environ.get('GOOGLE_CLIENT_ID'))
        user_email = idinfo['email']
        
        domain = user_email.split('@')[-1]
        if domain not in current_app.config['ALLOWED_EMAIL_DOMAINS']:
            return jsonify({"error": "Accesso consentito solo con email istituzionali."}), 403

        user_name = idinfo.get('name', user_email.split('@')[0])
        user_data = mongo.db.users.find_one({"email": user_email})
        
        if not user_data:
            hashed_password = generate_password_hash(os.urandom(24).hex())
            # Nuovo utente: default 'user'
            new_user_data = {"username": user_name, "email": user_email, "password_hash": hashed_password, "source": "google", "role": "user"}
            mongo.db.users.insert_one(new_user_data)
            user_data = mongo.db.users.find_one({"email": user_email})

        user = User(user_data)
        login_user(user)
        return jsonify({"message": "Login/Registrazione avvenuta con successo"}), 200
    except ValueError:
        return jsonify({"error": "Token Google non valido o scaduto."}), 401
    except Exception as e:
        return jsonify({"error": f"Errore interno: {e}"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Dati mancanti"}), 400

    domain = email.split('@')[-1]
    if domain not in current_app.config['ALLOWED_EMAIL_DOMAINS']:
        return jsonify({"error": "Registrazione consentita solo con email istituzionali."}), 403

    if mongo.db.users.find_one({"username": username}) or mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Username o email già in uso"}), 409

    # Nuovo utente: default 'user'
    mongo.db.users.insert_one({"username": username, "email": email, "password_hash": generate_password_hash(password), "source": "manual", "role": "user"})
    return jsonify({"message": "Registrazione avvenuta con successo!"}), 201

@app.route('/api/login', methods=['POST'])
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    # Il frontend invia 'username', che può contenere un username o un'email
    login_identifier = data.get('username')
    password = data.get('password')

    if not login_identifier or not password:
        return jsonify({"error": "Username/email e password sono richiesti."}), 400

    # Cerca l'utente per username O per email
    user_data = mongo.db.users.find_one({
        "$or": [
            {"username": login_identifier},
            {"email": login_identifier}
        ]
    })

    # Controlla la password e che l'utente non sia un utente solo-Google senza password
    if user_data and 'password_hash' in user_data and check_password_hash(user_data['password_hash'], password):
        # Escludi gli utenti registrati con Google che non hanno una password manuale
        if user_data.get('source') == 'google' and not check_password_hash(user_data['password_hash'], password):
             return jsonify({"error": "Questo account è registrato con Google. Usa il login di Google."}), 401
        
        user_obj = User(user_data)
        login_user(user_obj)
        return jsonify({"message": "Login avvenuto con successo!", "user": user_obj.to_dict()}), 200
        
    return jsonify({"error": "Credenziali non valide"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout avvenuto con successo!"}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "user": current_user.to_dict()}), 200
    else:
        return jsonify({"logged_in": False}), 200

@app.route('/api/departments', methods=['GET'])
def get_departments():
    departments = Department.query.order_by(Department.name).all()
    return jsonify([d.to_dict() for d in departments])

@app.route('/api/departments/<int:department_id>/degree_programs', methods=['GET'])
def get_degree_programs_by_department(department_id):
    degree_programs = DegreeProgram.query.filter_by(department_id=department_id).order_by(DegreeProgram.name).all()
    return jsonify([dp.to_dict() for dp in degree_programs])

@app.route('/api/degree_programs/<int:degree_program_id>/courses/<int:year>', methods=['GET'])
def get_courses_by_year(degree_program_id, year):
    courses = Course.query.filter_by(degree_program_id=degree_program_id, year=year).order_by(Course.name).all()
    return jsonify([c.to_dict() for c in courses])

@app.route('/api/courses/<int:course_id>/notes', methods=['GET'])
def get_notes_for_course(course_id):
    # Modificato: recupera solo gli appunti con stato 'approved' per gli utenti normali
    # Gli admin potranno vedere anche gli appunti 'pending' tramite un altro endpoint futuro
    notes = Note.query.filter_by(course_id=course_id, status='approved').order_by(Note.upload_date.desc()).all()
    if not notes:
        return jsonify({"message": "Nessun appunto trovato per questo corso."}), 404
    return jsonify([n.to_dict() for n in notes])

@app.route('/api/upload_note', methods=['POST'])
@login_required
def upload_note():
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file fornito"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome file vuoto"}), 400
    
    title = request.form.get('title')
    course_id_str = request.form.get('course_id')
    description = request.form.get('description', '')
    uploader_name = request.form.get('uploader_name', current_user.username)

    if not all([title, course_id_str]):
        return jsonify({"error": "Titolo e materia sono obbligatori"}), 400
    try:
        course_id = int(course_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "ID materia non valido"}), 400

    if s3_client and file:
        try:
            original_filename = secure_filename(file.filename)
            unique_s3_key = f"notes/{uuid.uuid4().hex}-{original_filename}"
            s3_client.upload_fileobj(file, S3_BUCKET, unique_s3_key)

            # Nuovo appunto: stato iniziale 'pending'
            new_note = Note(title=title, description=description, s3_key=unique_s3_key, course_id=course_id, uploader_name=uploader_name, status='pending')
            db.session.add(new_note)
            db.session.commit()
            return jsonify({"message": "Appunto caricato con successo! In attesa di approvazione."}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Errore interno durante il salvataggio: {e}"}), 500
    return jsonify({"error": "Servizio di upload non configurato."}), 500

@app.route('/api/notes/<int:note_id>/download', methods=['GET'])
@login_required
def download_note(note_id):
    note = Note.query.get_or_404(note_id)
    # Gli utenti possono scaricare solo appunti approvati
    if note.status != 'approved' and current_user.role != 'admin': # Aggiunto controllo ruolo
        return jsonify({"error": "Accesso negato: Appunto non approvato."}), 403

    if not s3_client:
        return jsonify({"error": "Servizio di download non configurato."}), 500
    try:
        presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': note.s3_key}, ExpiresIn=300)
        return jsonify({"download_url": presigned_url})
    except Exception as e:
        return jsonify({"error": "Impossibile generare il link per il download."}), 500


# --- NUOVI ENDPOINT PER ADMIN ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Se non autenticato, reindirizza alla pagina di login
            return redirect(url_for('serve_login_page'))
        if current_user.role != 'admin':
            # Se autenticato ma non admin, nega l'accesso con un messaggio
            # Potresti anche reindirizzare a una home page con un flash message
            return "Accesso negato: Richiede ruolo di amministratore.", 403
        return f(*args, **kwargs)
    return decorated_function

# ... (altre rotte API) ...

@app.route('/admin_dashboard.html') # NUOVA ROTTA
@admin_required # Applica il decoratore per proteggere la pagina
def serve_admin_dashboard_page():
    return send_from_directory('.', 'admin_dashboard.html')

# Endpoint per visualizzare appunti in attesa di approvazione
# NUOVO ENDPOINT: Ottiene TUTTI gli appunti per la gestione amministrativa

# NUOVO ENDPOINT: Ottiene TUTTI gli appunti per la gestione amministrativa
@app.route('/api/admin/all_notes', methods=['GET'])
@login_required
@admin_required
def get_all_notes_for_admin():
    # Recupera tutti gli appunti, indipendentemente dallo stato,
    # e carica anche i dati del corso associato.
    all_notes = db.session.query(Note, Course).join(Course).order_by(Note.upload_date.desc()).all()

    if not all_notes:
        return jsonify({"message": "Nessun appunto trovato nel sistema."}), 404

    notes_data = []
    for note, course in all_notes:
        note_dict = note.to_dict()
        # Aggiungi il nome e l'anno del corso al dizionario dell'appunto
        note_dict['course_name'] = course.name
        note_dict['course_year'] = course.year
        notes_data.append(note_dict)

    return jsonify(notes_data)
# Puoi mantenere get_pending_notes se desideri una sezione separata per solo quelli in attesa,
# ma per la funzionalità richiesta, get_all_notes_for_admin è sufficiente.
# Se vuoi rimuovere get_pending_notes e usare solo get_all_notes_for_admin,
# allora devi aggiornare il frontend per chiamare /api/admin/all_notes.
# Per ora, suggerisco di aggiungere questo e modificare il frontend per usarlo.
# Endpoint per approvare un appunto
@app.route('/api/admin/notes/<int:note_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.status == 'approved':
        return jsonify({"message": "Appunto già approvato."}), 200
    note.status = 'approved'
    db.session.commit()
    return jsonify({"message": "Appunto approvato con successo!"}), 200

# Endpoint per rifiutare un appunto (o marcarlo come non attivo)
@app.route('/api/admin/notes/<int:note_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.status == 'rejected':
        return jsonify({"message": "Appunto già rifiutato."}), 200
    note.status = 'rejected'
    db.session.commit()
    return jsonify({"message": "Appunto rifiutato con successo!"}), 200

# Endpoint per eliminare un appunto
@app.route('/api/admin/notes/<int:note_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    s3_key = note.s3_key

    try:
        # Elimina il file da S3
        if s3_client:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
            print(f"DEBUG: File {s3_key} eliminato da S3.")
        
        # Elimina la voce dal database
        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": "Appunto eliminato con successo!"}), 200
    except ClientError as e:
        db.session.rollback()
        return jsonify({"error": f"Errore S3 durante l'eliminazione: {e}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Errore durante l'eliminazione dell'appunto: {e}"}), 500


# --- ROTTE PER SERVIRE FILE STATICI ---
@app.route('/')
def serve_home():
    return send_from_directory('.', 'index.html')

@app.route('/login.html')
def serve_login_page():
    return send_from_directory('.', 'login.html')


@app.route('/admin_dashboard.html') # NUOVA ROTTA
def serve_admin_dashboard_page():
    return send_from_directory('.', 'admin_dashboard.html')


@app.route('/<path:filename>')
def serve_static_files(filename):
    if filename in ['.env', 'fly.toml', 'requirements.txt', 'password.txt']:
        return "Accesso negato", 403
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)