import os
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS 

# Inizializza l'app Flask
app = Flask(__name__, static_folder='.', static_url_path='/') 

# --- Configurazione del Database ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unisannio_appunti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# Inizializza SQLAlchemy SENZA passare 'app' al costruttore
db = SQLAlchemy() 
# Collega l'estensione SQLAlchemy all'app dopo la configurazione
db.init_app(app) 

# Configurazione CORS per permettere richieste dal frontend
CORS(app) 

# --- Configurazione per il caricamento dei PDF ---
UPLOAD_FOLDER = 'uploads' 
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'} 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Definizione dei Modelli del Database ---
# Queste classi definiscono le tabelle del tuo database.

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
    file_path = db.Column(db.String(255), nullable=False) 
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    uploader_name = db.Column(db.String(80), nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
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
    # Flask di default serve i file statici dalla cartella specificata in static_folder.
    # Tuttavia, questa rotta è utile per catturare file specifici o .html non radice.
    return send_from_directory('.', filename)


# --- Rotte API (come nel passo precedente, non cambiano) ---

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

@app.route('/api/courses/<int:course_id>/notes', methods=['GET'])
def get_notes_by_course(course_id):
    notes = Note.query.filter_by(course_id=course_id).all()
    if not notes:
        return jsonify({"message": "Nessun appunto trovato per questo esame"}), 404
    return jsonify([n.to_dict() for n in notes])

@app.route('/api/upload_note', methods=['POST'])
def upload_note():
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file fornito"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Nome file vuoto"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(file_path)
        except Exception as e:
            return jsonify({"error": f"Errore nel salvataggio del file: {str(e)}"}), 500

        title = request.form.get('title')
        description = request.form.get('description', '')
        course_id = request.form.get('course_id')
        uploader_name = request.form.get('uploader_name', 'Anonimo')

        if not title or not course_id:
            os.remove(file_path) 
            return jsonify({"error": "Titolo e ID corso sono obbligatori"}), 400

        try:
            new_note = Note(
                title=title,
                description=description,
                file_path=file_path,
                course_id=int(course_id),
                uploader_name=uploader_name
            )
            db.session.add(new_note)
            db.session.commit()
            return jsonify({"message": "Appunto caricato con successo!", "note": new_note.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            os.remove(file_path)
            return jsonify({"error": f"Errore nel salvataggio nel database: {str(e)}"}), 500
    else:
        return jsonify({"error": "Tipo di file non permesso o file non valido"}), 400

@app.route('/api/notes/<int:note_id>/download', methods=['GET'])
def download_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({"message": "Appunto non trovato"}), 404
    
    directory = app.config['UPLOAD_FOLDER']
    filename = os.path.basename(note.file_path) 
    
    full_path = os.path.join(directory, filename)
    if not os.path.exists(full_path):
        return jsonify({"message": "File non trovato sul server"}), 404

    return send_from_directory(directory=directory, path=filename, as_attachment=True)

# L'esecuzione dell'app è gestita da Gunicorn in produzione,
# quindi il blocco `if __name__ == '__main__':` con `app.run(debug=True)` non serve qui.
# La logica di inizializzazione del DB è spostata in init_db.py.