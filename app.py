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
db = SQLAlchemy() # <--- MODIFICA QUI

# Inizializza l'estensione SQLAlchemy con l'app dopo la configurazione
db.init_app(app) # <--- AGGIUNGI QUESTA RIGA

CORS(app) 

# --- Configurazione per il caricamento dei PDF ---
UPLOAD_FOLDER = 'uploads' 
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'} 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Definizione dei Modelli del Database (rimane invariata) ---
class Department(db.Model):
    # ... (il resto della classe)
    __tablename__ = 'departments' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    degree_programs = db.relationship('DegreeProgram', backref='department', lazy=True)
    def to_dict(self):
        return {"id": self.id, "name": self.name}
# ... (tutte le altre classi DegreeProgram, Course, Note) ...
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


# --- Rotte Frontend (rimangono invariate) ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_html_files(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    return send_from_directory('.', filename)

# --- Rotte API (rimangono invariate) ---
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


# --- Esecuzione dell'App ---
if __name__ == '__main__':
    with app.app_context():
        # Crea le tabelle nel database se non esistono (si occupa di questo Flask-SQLAlchemy)
        db.create_all() 
        print("Database e tabelle create (o già esistenti).")

        # --- Dati di esempio (solo per la prima esecuzione) ---
        if not Department.query.first(): 
            print("Popolando il database con dati di esempio...")

            ding = Department(name='DING')
            dst = Department(name='DST')
            demm = Department(name='DEMM')
            db.session.add_all([ding, dst, demm])
            db.session.commit()

            ing_energetica = DegreeProgram(name='Ingegneria Energetica', department=ding)
            ing_civile = DegreeProgram(name='Ingegneria Civile', department=ding)
            ing_informatica = DegreeProgram(name='Ingegneria Informatica', department=ding)
            ing_biomedica = DegreeProgram(name='Ingegneria Biomedica', department=ding)
            db.session.add_all([ing_energetica, ing_civile, ing_informatica, ing_biomedica])
            db.session.commit()

            scienze_biologiche = DegreeProgram(name='Scienze Biologiche', department=dst)
            chimica = DegreeProgram(name='Chimica', department=dst)
            db.session.add_all([scienze_biologiche, chimica])
            db.session.commit()

            economia_aziendale = DegreeProgram(name='Economia Aziendale', department=demm)
            management = DegreeProgram(name='Management', department=demm)
            db.session.add_all([economia_aziendale, management])
            db.session.commit()

            db.session.add_all([
                Course(name='Analisi Matematica I', year=1, degree_program=ing_energetica), Course(name='Fisica Generale I', year=1, degree_program=ing_energetica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_energetica), Course(name='Chimica', year=1, degree_program=ing_energetica), Course(name='Informatica', year=1, degree_program=ing_energetica), Course(name='Disegno Tecnico Industriale', year=1, degree_program=ing_energetica), Course(name='Analisi Matematica II', year=2, degree_program=ing_energetica), Course(name='Fisica Generale II', year=2, degree_program=ing_energetica), Course(name='Meccanica Razionale', year=2, degree_program=ing_energetica), Course(name='Termodinamica Applicata', year=2, degree_program=ing_energetica), Course(name='Fondamenti di Elettrotecnica', year=2, degree_program=ing_energetica), Course(name='Scienza delle Costruzioni', year=2, degree_program=ing_energetica), Course(name='Macchine a Fluido', year=3, degree_program=ing_energetica), Course(name='Impianti Termotecnici', year=3, degree_program=ing_energetica), Course(name='Economia ed Estimo Civile', year=3, degree_program=ing_energetica), Course(name='Energie Rinnovabili', year=3, degree_program=ing_energetica), Course(name='Sistemi Energetici', year=3, degree_program=ing_energetica), Course(name='Ingegneria della Sicurezza', year=3, degree_program=ing_energetica),
                Course(name='Analisi Matematica I', year=1, degree_program=ing_civile), Course(name='Fisica Generale I', year=1, degree_program=ing_civile), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_civile), Course(name='Chimica', year=1, degree_program=ing_civile), Course(name='Informatica', year=1, degree_program=ing_civile), Course(name='Disegno', year=1, degree_program=ing_civile), Course(name='Analisi Matematica II', year=2, degree_program=ing_civile), Course(name='Fisica Generale II', year=2, degree_program=ing_civile), Course(name='Meccanica Razionale', year=2, degree_program=ing_civile), Course(name='Scienza delle Costruzioni', year=2, degree_program=ing_civile), Course(name='Geotecnica', year=2, degree_program=ing_civile), Course(name='Idraulica', year=2, degree_program=ing_civile), Course(name='Tecnica delle Costruzioni', year=3, degree_program=ing_civile), Course(name='Costruzioni Idrauliche', year=3, degree_program=ing_civile), Course(name='Topografia e Cartografia', year=3, degree_program=ing_civile), Course(name='Trasporti', year=3, degree_program=ing_civile), Course(name='Estimo', year=3, degree_program=ing_civile), Course(name='Urbanistica', year=3, degree_program=ing_civile),
                Course(name='Analisi Matematica I', year=1, degree_program=ing_informatica), Course(name='Fisica Generale I', year=1, degree_program=ing_informatica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_informatica), Course(name='Programmazione I', year=1, degree_program=ing_informatica), Course(name='Fondamenti di Informatica', year=1, degree_program=ing_informatica), Course(name='Calcolo Numerico', year=1, degree_program=ing_informatica), Course(name='Analisi Matematica II', year=2, degree_program=ing_informatica), Course(name='Fisica Generale II', year=2, degree_program=ing_informatica), Course(name='Architetture dei Calcolatori', year=2, degree_program=ing_informatica), Course(name='Sistemi Operativi', year=2, degree_program=ing_informatica), Course(name='Programmazione II', year=2, degree_program=ing_informatica), Course(name='Algoritmi e Strutture Dati', year=2, degree_program=ing_informatica), Course(name='Basi di Dati', year=3, degree_program=ing_informatica), Course(name='Reti di Calcolatori', year=3, degree_program=ing_informatica), Course(name='Ingegneria del Software', year=3, degree_program=ing_informatica), Course(name='Sicurezza dei Sistemi', year=3, degree_program=ing_informatica), Course(name='Intelligenza Artificiale', year=3, degree_program=ing_informatica), Course(name='Sistemi Distribuiti', year=3, degree_program=ing_informatica),
                Course(name='Analisi Matematica I', year=1, degree_program=ing_biomedica), Course(name='Fisica Generale I', year=1, degree_program=ing_biomedica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_biomedica), Course(name='Biologia', year=1, degree_program=ing_biomedica), Course(name='Chimica', year=1, degree_program=ing_biomedica), Course(name='Informatica', year=1, degree_program=ing_biomedica), Course(name='Analisi Matematica II', year=2, degree_program=ing_biomedica), Course(name='Fisica Generale II', year=2, degree_program=ing_biomedica), Course(name='Meccanica Razionale', year=2, degree_program=ing_biomedica), Course(name='Fisiologia', year=2, degree_program=ing_biomedica), Course(name='Elettrotecnica', year=2, degree_program=ing_biomedica), Course(name='Elettronica', year=2, degree_program=ing_biomedica), Course(name='Bioingegneria dei Sistemi', year=3, degree_program=ing_biomedica), Course(name='Strumentazione Biomedica', year=3, degree_program=ing_biomedica), Course(name='Elaborazione dei Segnali Biomedici', year=3, degree_program=ing_biomedica), Course(name='Modellistica e Simulazione', year=3, degree_program=ing_biomedica), Course(name='Materiali Biomedici', year=3, degree_program=ing_biomedica), Course(name='Bioetica e Legislazione', year=3, degree_program=ing_biomedica),
            ])
            db.session.commit()

            print("Dati di esempio per Dipartimenti, Corsi di Laurea ed Esami aggiunti.")
        else:
            print("Database già popolato con dati. Salto l'inserimento dei dati di esempio.")
        
    app.run(debug=True)