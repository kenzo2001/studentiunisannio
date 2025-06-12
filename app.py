import os
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS 
import boto3 # <-- AGGIUNGI QUESTO IMPORT
from botocore.exceptions import NoCredentialsError, ClientError # <-- AGGIUNGI QUESTI IMPORT

# Inizializza l'app Flask
app = Flask(__name__, static_folder='.', static_url_path='/') 

# --- Configurazione del Database ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unisannio_appunti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# Inizializza SQLAlchemy e collegalo all'app
db = SQLAlchemy() 
db.init_app(app) 

# Configurazione CORS
CORS(app) 

# --- Configurazione AWS S3 ---
# Prende le credenziali e la regione dalle variabili d'ambiente di Fly.io
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
S3_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_REGION = os.environ.get("S3_REGION") # Verrà impostata da flyctl secrets set

# Inizializza il client S3 solo se le credenziali sono disponibili
s3_client = None
if S3_KEY and S3_SECRET and S3_REGION and S3_BUCKET:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            region_name=S3_REGION
        )
    except Exception as e:
        print(f"Errore nell'inizializzazione del client S3: {e}")
else:
    print("Variabili d'ambiente AWS S3 non impostate. Le operazioni S3 falliranno.")


# --- Validazione Tipo File ---
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'} 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Definizione dei Modelli del Database ---
# MODIFICA: 'file_path' diventa 's3_key' per memorizzare la chiave S3
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
    s3_key = db.Column(db.String(255), nullable=False) # <-- MODIFICA QUI: Salva la chiave S3
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    uploader_name = db.Column(db.String(80), nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "s3_key": self.s3_key, # <-- MODIFICA QUI
            "upload_date": self.upload_date.isoformat(),
            "course_id": self.course_id,
            "uploader_name": self.uploader_name
        }


# --- Rotte per Servire i File del Frontend (HTML, CSS, JS) ---

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('.', filename)


# --- Rotte API ---

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

# ROTTA API: Ottiene gli appunti di un corso
# Restituisce i dettagli dell'appunto, inclusa la chiave S3
@app.route('/api/courses/<int:course_id>/notes', methods=['GET'])
def get_notes_by_course(course_id):
    notes = Note.query.filter_by(course_id=course_id).all()
    if not notes:
        return jsonify({"message": "Nessun appunto trovato per questo esame"}), 404
    return jsonify([n.to_dict() for n in notes]) # Ora to_dict include s3_key

# ROTTA API: Carica un nuovo appunto su S3
@app.route('/api/upload_note', methods=['POST'])
def upload_note():
    if not s3_client:
        return jsonify({"error": "Servizio S3 non inizializzato. Controlla le variabili d'ambiente AWS."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "Nessun file fornito"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Nome file vuoto"}), 400
    
    if file and allowed_file(file.filename):
        # Genera una chiave S3 univoca (per evitare sovrascritture)
        # Combina un timestamp con il nome del file sicuro
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        key = f"{timestamp}_{secure_filename(file.filename)}" # <-- Chiave S3 univoca
        
        try:
            # Carica il file su S3
            s3_client.upload_fileobj(file, S3_BUCKET, key)
            print(f"File {key} caricato con successo nel bucket S3: {S3_BUCKET}")
        except NoCredentialsError:
            return jsonify({"error": "Credenziali AWS non disponibili"}), 500
        except ClientError as e: # Per errori specifici di S3 come bucket non trovato, permessi
            return jsonify({"error": f"Errore client S3: {e.response['Error']['Message']}"}), 500
        except Exception as e:
            return jsonify({"error": f"Errore generico caricamento su S3: {str(e)}"}), 500

        title = request.form.get('title')
        description = request.form.get('description', '')
        course_id = request.form.get('course_id')
        uploader_name = request.form.get('uploader_name', 'Anonimo')

        if not title or not course_id:
            # Se i dati obbligatori non ci sono, elimina il file da S3 (se caricato)
            try:
                s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
            except Exception as e:
                print(f"Attenzione: Impossibile eliminare file S3 dopo errore dati: {e}")
            return jsonify({"error": "Titolo e ID corso sono obbligatori"}), 400

        try:
            new_note = Note(
                title=title,
                description=description,
                s3_key=key, # Salva la chiave S3, non il path locale
                course_id=int(course_id),
                uploader_name=uploader_name
            )
            db.session.add(new_note)
            db.session.commit()
            return jsonify({"message": "Appunto caricato con successo!", "note": new_note.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            # Se c'è un errore DB, prova a eliminare il file da S3
            try:
                s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
            except Exception as e_s3:
                print(f"Attenzione: Impossibile eliminare file S3 dopo errore DB: {e_s3}")
            return jsonify({"error": f"Errore nel salvataggio nel database: {str(e)}"}), 500
    else:
        return jsonify({"error": "Tipo di file non permesso o file non valido"}), 400

# ROTTA API: Scarica un appunto da S3 (restituisce URL pre-firmato)
@app.route('/api/notes/<int:note_id>/download', methods=['GET'])
def download_note(note_id):
    if not s3_client:
        return jsonify({"error": "Servizio S3 non inizializzato. Controlla le variabili d'ambiente AWS."}), 500

    note = Note.query.get(note_id)
    if not note:
        return jsonify({"message": "Appunto non trovato"}), 404
    
    try:
        # Genera un URL pre-firmato per il download da S3
        s3_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': note.s3_key},
            ExpiresIn=300 # URL valido per 5 minuti
        )
        return jsonify({"download_url": s3_url}) # Restituisce l'URL al frontend
    except NoCredentialsError:
        return jsonify({"error": "Credenziali AWS non disponibili"}), 500
    except ClientError as e:
        return jsonify({"error": f"Errore client S3: {e.response['Error']['Message']}"}), 500
    except Exception as e:
        return jsonify({"error": f"Errore generico generazione URL S3: {str(e)}"}), 500

# L'esecuzione dell'app è gestita da Gunicorn in produzione.
# La logica di inizializzazione del DB è spostata in init_db.py.