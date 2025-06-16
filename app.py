import os
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

print("DEBUG: Avvio app.py")

app = Flask(__name__, static_folder='.', static_url_path='/')

# --- Configurazione Chiave Segreta & Dominio ---
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'fallback-secret-key-per-sviluppo-locale')
app.config['SESSION_COOKIE_DOMAIN'] = '.studentiunisannio.it'
app.config['ALLOWED_EMAIL_DOMAINS'] = ['unisannio.it', 'studenti.unisannio.it', 'example.com'] 

# --- Configurazione Database SQL (per corsi, appunti, etc.) ---
db_url = os.environ.get('DATABASE_URL')
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace('postgres://', 'postgresql+psycopg2://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unisannio_appunti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

# --- Configurazione MongoDB (per utenti) ---
mongo_uri_from_env = os.environ.get("MONGO_URI")
# RIGA DI DEBUG: Stampa la URI che viene letta dall'ambiente
print(f"DEBUG: La MONGO_URI letta dall'ambiente è: {mongo_uri_from_env}")
app.config["MONGO_URI"] = mongo_uri_from_env
mongo = PyMongo(app)

# --- Configurazione AWS S3 ---
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_REGION = os.environ.get("S3_REGION")

s3_client = None
if S3_KEY and S3_SECRET and S3_REGION and S3_BUCKET:
    try:
        s3_client = boto3.client('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET, region_name=S3_REGION)
    except Exception as e:
        print(f"ERRORE DEBUG: Errore nell'inizializzazione del client S3: {e}")
else:
    print("ERRORE DEBUG: Variabili d'ambiente AWS S3 non impostate.")

# --- Configurazione Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({"error": "Accesso non autorizzato. Effettua il login."}), 401
    return redirect(url_for('serve_login_page'))

# --- DEFINIZIONE DEI MODELLI ---

# Nuovo Modello Utente per MongoDB
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}

# Modelli SQL esistenti
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
    def to_dict(self): return {"id": self.id, "title": self.title, "description": self.description, "s3_key": self.s3_key, "upload_date": self.upload_date.isoformat(), "course_id": self.course_id, "uploader_name": self.uploader_name}

# --- GESTIONE UTENTI CON MONGO DB ---

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not all([username, email, password]):
        return jsonify({"error": "Dati mancanti"}), 400
    if mongo.db.users.find_one({"username": username}):
        return jsonify({"error": "Username già in uso"}), 409
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"error": "Email già in uso"}), 409
    mongo.db.users.insert_one({
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password)
    })
    return jsonify({"message": "Registrazione avvenuta con successo!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user_data = mongo.db.users.find_one({"username": username})
    if user_data and check_password_hash(user_data['password_hash'], password):
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

# --- VECCHIE API (NON TOCCATE) ---
# ... (tutte le altre tue rotte per dipartimenti, corsi, appunti, etc. rimangono qui invariate)

# NUOVA ROTTA DA AGGIUNGERE PER CARICARE I CORSI
@app.route('/api/degree_programs/<int:degree_program_id>/courses/<int:year>', methods=['GET'])
def get_courses_by_year(degree_program_id, year):
    """
    Fornisce la lista dei corsi per un dato corso di laurea e anno.
    """
    # Cerca i corsi nel database filtrando per ID del corso di laurea e per anno.
    courses = Course.query.filter_by(degree_program_id=degree_program_id, year=year).order_by(Course.name).all()

    # Se non trova corsi, restituisce un messaggio che lo script può interpretare.
    if not courses:
        return jsonify({"message": "Nessun corso trovato per questo anno."}), 404

    # Se trova i corsi, li converte in formato JSON e li invia.
    return jsonify([course.to_dict() for course in courses]), 200

# Aggiungi questa nuova rotta nel file app.py

@app.route('/api/departments', methods=['GET'])
def get_departments():


  
    """
    Fornisce la lista di tutti i dipartimenti presenti nel database.
    """
    try:
        # Interroga il database per ottenere tutti i record dalla tabella Department
        all_departments = Course.query.order_by(Course.name).all()
        
        # Converte la lista di oggetti in un formato JSON e la restituisce
        return jsonify([Course.to_dict() for department in all_departments]), 200
    except Exception as e:
        # In caso di errore, lo stampa sul log del server e restituisce un errore generico
        print(f"Errore durante il recupero dei dipartimenti: {e}")
        return jsonify({"error": "Errore interno nel recupero dei dati"}), 500
# --- ROTTE PER SERVIRE FILE STATICI ---


@app.route('/api/departments/<int:department_id>/degree_programs', methods=['GET'])
def get_degree_programs_by_department(department_id):
    """
    Fornisce la lista dei corsi di laurea per un dato dipartimento.
    """
    # Cerca il dipartimento per l'ID fornito, se non lo trova restituisce errore 404.
    department = Department.query.get_or_404(department_id)
    
    # Trova tutti i corsi di laurea associati a quel dipartimento.
    degree_programs = DegreeProgram.query.filter_by(department_id=department.id).order_by(DegreeProgram.name).all()
    
    # Se non ce ne sono, restituisce un messaggio.
    if not degree_programs:
        return jsonify({"message": "Nessun corso di laurea trovato per questo dipartimento."}), 404
        
    # Restituisce la lista in formato JSON.
    return jsonify([program.to_dict() for program in degree_programs]), 200
@app.route('/')
def serve_home():
# --- ROTTE PER SERVIRE FILE STATICI ---

    return send_from_directory('.', 'index.html')

@app.route('/login.html')
def serve_login_page():
    return send_from_directory('.', 'login.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('.', filename)