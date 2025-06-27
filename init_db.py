import os
from app import app, db, Department, DegreeProgram, Course, Note
from werkzeug.security import generate_password_hash
from sqlalchemy.orm.exc import NoResultFound
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def initialize_database():
    print("INIT_DB: Inizio inizializzazione database.")

    with app.app_context():
        try:
            db.create_all()
            print("INIT_DB: Struttura tabelle SQL verificata/creata.")
        except Exception as e:
            print(f"ERRORE INIT_DB (SQL): {e}")
            raise

        print("INIT_DB: Verificando e aggiungendo dati SQL...")
        
        # --- 1. Popolamento Dipartimenti ---
        departments_to_ensure = ['DING', 'DST', 'DEMM']
        for dept_name in departments_to_ensure:
            if not Department.query.filter_by(name=dept_name).first():
                db.session.add(Department(name=dept_name))
        db.session.commit()

        # --- 2. Popolamento Corsi di Laurea Triennale ---
        ding_dept = Department.query.filter_by(name='DING').one()
        dst_dept = Department.query.filter_by(name='DST').one()
        demm_dept = Department.query.filter_by(name='DEMM').one()
        
        # MODIFICA: Nomi resi coerenti, semplici e minuscoli
        degree_programs_to_ensure = [
            # DING
            {'name': 'Ingegneria Energetica', 'department': ding_dept},
            {'name': 'Ingegneria Civile', 'department': ding_dept},
            {'name': 'Ingegneria Informatica', 'department': ding_dept},
            {'name': 'Ingegneria Biomedica', 'department': ding_dept},
        
            # DST
            {'name': 'scienze_biologiche', 'department': dst_dept},
            {'name': 'biotecnologie', 'department': dst_dept},
            {'name': 'scienze_naturali', 'department': dst_dept},
            {'name': 'scienze_motorie', 'department': dst_dept},
        ]
        for dp_data in degree_programs_to_ensure:
            if not DegreeProgram.query.filter_by(name=dp_data['name']).first():
                db.session.add(DegreeProgram(name=dp_data['name'], department=dp_data['department']))
        db.session.commit()

        # --- 3. Popolamento Esami ---
        try:
            # MODIFICA: Usiamo i nuovi nomi coerenti per recuperare gli oggetti
            programs = {
                'Ingegneria Energetica': DegreeProgram.query.filter_by(name='Ingegneria Energetica').one(),
                'Ingegneria Civile': DegreeProgram.query.filter_by(name='Ingegneria Civile').one(),
                'Ingegneria Informatica': DegreeProgram.query.filter_by(name='Ingegneria Informatica').one(),
                'Ingegneria Biomedica': DegreeProgram.query.filter_by(name='Ingegneria Biomedica').one(),
                'scienze_biologiche': DegreeProgram.query.filter_by(name='scienze_biologiche').one(),
                'biotecnologie': DegreeProgram.query.filter_by(name='biotecnologie').one(),
                'scienze_naturali': DegreeProgram.query.filter_by(name='scienze_naturali').one(),
                'scienze_motorie': DegreeProgram.query.filter_by(name='scienze_motorie').one(),
            }

            courses_to_add = [
                # Ingegneria Energetica
                ('Analisi Matematica I', 1, programs['Ingegneria Energetica']), ('Analisi Matematica II', 1, programs['Ingegneria Energetica']),('Fisica Generale I', 1, programs['Ingegneria Energetica']),('Fisica Generale II', 1, programs['Ingegneria Energetica']), ('Algebra Lineare Geometria e ricerca operativa', 1, programs['Ingegneria Energetica']), ('Chimica', 1, programs['Ingegneria Energetica']), ('Elementi di Informatica', 1, programs['Ingegneria Energetica']), ('Fondamenti della misurazione', 1, programs['Ingegneria Energetica']),('Inglese', 1, programs['Ingegneria Energetica']),
                ('Modelli di Reattori Chimici', 2, programs['Ingegneria Energetica']),('Sistemi Elettrici per L^Energia', 2, programs['Ingegneria Energetica']),('Termofluido Dinamica e Trasmissione del Calore', 2, programs['Ingegneria Energetica']), ('Meccanica Applicata alle Macchine', 2, programs['Ingegneria Energetica']), ('Elettrotecnica', 2, programs['Ingegneria Energetica']), ('Fisica Tecnica', 2, programs['Ingegneria Energetica']),('Processi di Combustione', 2, programs['Ingegneria Energetica']),('Macchine a Fluido', 2, programs['Ingegneria Energetica']),
                ('Impianti Chimici per L^Energia', 3, programs['Ingegneria Energetica']), ('Impianti Industriali', 3, programs['Ingegneria Energetica']), ('Energetica', 3, programs['Ingegneria Energetica']), ('Tecnologie delle Fonti Rinnovabili', 3, programs['Ingegneria Energetica']), ('Sistemi Elettrici Industriali', 3, programs['Ingegneria Energetica']), ('Elementi di Ingegneria Strutturali', 3, programs['Ingegneria Energetica']),
                
                # Ingegneria Civile
                ('Analisi Matematica I', 1, programs['Ingegneria Civile']), ('Analisi Matematica II', 1, programs['Ingegneria Civile']),('Fisica Generale ', 1, programs['Ingegneria Civile']),('Geometria e Algebra Lineare', 1, programs['Ingegneria Civile']),('Elementi di Informatica', 1, programs['Ingegneria Civile']), ('Scienze e tecnologia dei Materiali', 1, programs['Ingegneria Civile']),('Inglese', 1, programs['Ingegneria Civile']),
                ('Meccanica Razionale', 2, programs['Ingegneria Civile']), ('Scienza delle Costruzioni', 2, programs['Ingegneria Civile']), ('Fisica Tecnica', 2, programs['Ingegneria Civile']), ('Idraulica', 2, programs['Ingegneria Civile']),('Tecnica Urbanistica', 2, programs['Ingegneria Civile']),('Ingegneria dei Sistemi di trasporto I', 2, programs['Ingegneria Civile']),('Ingegneria dei Sistemi di trasporto II', 2, programs['Ingegneria Civile']),('Fondamenti di Infrastrutture Viaree', 2, programs['Ingegneria Civile']),('Climatologia dell Ambiente Costruito', 2, programs['Ingegneria Civile']),
                ('Tecnica delle Costruzioni I', 3, programs['Ingegneria Civile']),('Tecnica delle Costruzioni II', 3, programs['Ingegneria Civile']), ('Costruzioni Idrauliche', 3, programs['Ingegneria Civile']), ('Topografia e Cartografia', 3, programs['Ingegneria Civile']), ('Principi di Geotecnica', 3, programs['Ingegneria Civile']), ('Fondazioni ed Opere di Sostegno', 3, programs['Ingegneria Civile']),
                
                # Ingegneria Informatica
                ('Analisi Matematica I', 1, programs['Ingegneria Informatica']), ('Analisi Matematica II', 1, programs['Ingegneria Informatica']), ('Fisica Generale II', 1, programs['Ingegneria Informatica']),('Fisica Generale I', 1, programs['Ingegneria Informatica']), ('Matematica per l Ingegneria dell Informazione', 1, programs['Ingegneria Informatica']), ('Programmazione I', 1, programs['Ingegneria Informatica']), ('Inglese', 1, programs['Ingegneria Informatica']), ('Calcolatori Elettronici', 1, programs['Ingegneria Informatica']),('Economia Aziendale', 1, programs['Ingegneria Informatica']),
                ('Fondamenti di Telecomunicazione', 2, programs['Ingegneria Informatica']), ('Sistemi Operativi', 2, programs['Ingegneria Informatica']), ('Programmazione II', 2, programs['Ingegneria Informatica']),
                ('Elettrotecnica', 2, programs['Ingegneria Informatica']),('Elettronica', 2, programs['Ingegneria Informatica']),('Sistemi Dinamici ', 2, programs['Ingegneria Informatica']),('Controlli Automatici', 2, programs['Ingegneria Informatica']), ('Basi di Dati', 3, programs['Ingegneria Informatica']), ('Misure Elettroniche', 3, programs['Ingegneria Informatica']), ('Ingegneria del Software', 3, programs['Ingegneria Informatica']),('Algoritmi e Strutture Dati', 3, programs['Ingegneria Informatica']), ('Computazione Pervasiva', 3, programs['Ingegneria Informatica']), ('Data analycist', 3, programs['Ingegneria Informatica']), ('PSR ', 3, programs['Ingegneria Informatica']),

                # Ingegneria Biomedica
                ('Analisi Matematica I', 1, programs['Ingegneria Biomedica']),('Analisi Matematica II', 1, programs['Ingegneria Biomedica']), ('Fisica Generale II', 1, programs['Ingegneria Biomedica']), ('Fisica Generale I', 1, programs['Ingegneria Biomedica']), ('Geometria e Algebra Lineare', 1, programs['Ingegneria Biomedica']), ('Inglese', 1, programs['Ingegneria Biomedica']), ('Chimica', 1, programs['Ingegneria Biomedica']), ('Programmazione I', 1, programs['Ingegneria Biomedica']),('Programmazione II ed Inteligenza Artificiale', 1, programs['Ingegneria Biomedica']),
                ('Misure Elettroniche', 2, programs['Ingegneria Biomedica']), ('Elementi di Biochimica', 2, programs['Ingegneria Biomedica']), ('Elettrotecnica', 2, programs['Ingegneria Biomedica']), ('Elettronica', 2, programs['Ingegneria Biomedica']),('Matematica II', 2, programs['Ingegneria Biomedica']),('Sistemi Dinamici', 2, programs['Ingegneria Biomedica']),('Probabilità e segnali', 2, programs['Ingegneria Biomedica']),('Elaborazione Numerica dei segnali', 2, programs['Ingegneria Biomedica']),
                ('BioElettromagnetismo', 3, programs['Ingegneria Biomedica']),('Sistemi di Acquisizione Dati', 3, programs['Ingegneria Biomedica']),('Sistemi Biomedicali', 3, programs['Ingegneria Biomedica']),('Laboratorio di BioElettronica', 3, programs['Ingegneria Biomedica']),('Laboratorio di Misure Elettroniche per Applicazioni Medicali', 3, programs['Ingegneria Biomedica']),
                
                # MODIFICA: Usiamo le nuove chiavi per associare i corsi
                # Scienze Biologiche
                ('BIOLOGIA E SISTEMATICA VEGETALE', 1, programs['scienze_biologiche']), ('CHIMICA GENERALE', 1, programs['scienze_biologiche']), ('CHIMICA ORGANICA', 1, programs['scienze_biologiche']), ('CITOLOGIA ED ISTOLOGIA', 1, programs['scienze_biologiche']), ('ENGLISH FOR BIOLOGICAL SCIENCES', 1, programs['scienze_biologiche']), ('FISICA ED ELEMENTI DI MATEMATICA PER LA BIOLOGIA', 1, programs['scienze_biologiche']), ('FONDAMENTI DI INFORMATICA', 1, programs['scienze_biologiche']), ('LABORATORIO DI BIOLOGIA DI BASE', 1, programs['scienze_biologiche']),
                ('BIOCHIMICA', 2, programs['scienze_biologiche']), ('BIOLOGIA MOLECOLARE', 2, programs['scienze_biologiche']), ('FISIOLOGIA GENERALE', 2, programs['scienze_biologiche']), ('GENETICA', 2, programs['scienze_biologiche']), ('MICROBIOLOGIA GENERALE', 2, programs['scienze_biologiche']), ('ZOOLOGIA', 2, programs['scienze_biologiche']),
                ('ECOLOGIA', 3, programs['scienze_biologiche']), ('EMBRIOLOGIA E ANATOMIA COMPARATA', 3, programs['scienze_biologiche']), ('FARMACOLOGIA', 3, programs['scienze_biologiche']), ('FISIOLOGIA VEGETALE', 3, programs['scienze_biologiche']), ('LABORATORIO DI BIOLOGIA SPERIMENTALE', 3, programs['scienze_biologiche']),

                # Biotecnologie
                ('BIOLOGIA CELLULARE', 1, programs['biotecnologie']), ('BIOTECNOLOGIE E DIRITTO DELL UNIONE EUROPEA', 1, programs['biotecnologie']), ('CHIMICA GENERALE E INORGANICA (Biotecnologie)', 1, programs['biotecnologie']), ('CHIMICA ORGANICA (Biotecnologie)', 1, programs['biotecnologie']), ('FISICA CON LABORATORIO', 1, programs['biotecnologie']), ('GENETICA (Biotecnologie)', 1, programs['biotecnologie']), ('LINGUA INGLESE', 1, programs['biotecnologie']), ('MATEMATICA', 1, programs['biotecnologie']),
                ('BIOCHIMICA (Biotecnologie)', 2, programs['biotecnologie']), ('BIOLOGIA APPLICATA', 2, programs['biotecnologie']), ('BIOLOGIA MOLECOLARE (Biotecnologie)', 2, programs['biotecnologie']), ('CHIMICA FISICA', 2, programs['biotecnologie']), ('MICROBIOLOGIA', 2, programs['biotecnologie']), ('PRINCIPI DI BIOINFORMATICA', 2, programs['biotecnologie']), ('STATISTICA', 2, programs['biotecnologie']),
                ('BIOTECNOLOGIE INDUSTRIALI', 3, programs['biotecnologie']), ('CARATTERIZZAZIONE STRUTTURALE DEI COMPOSTI CHIMICI', 3, programs['biotecnologie']), ('FARMACOLOGIA E TOSSICOLOGIA', 3, programs['biotecnologie']), ('FITOCHIMICA E SUE APPLICAZIONI BIOTECNOLOGICHE', 3, programs['biotecnologie']), ('LABORATORI INTEGRATI', 3, programs['biotecnologie']),

                # Scienze Naturali
                ('CHIMICA GENERALE E INORGANICA (Scienze Naturali)', 1, programs['scienze_naturali']), ('CHIMICA ORGANICA CON ELEMENTI DI BIOCHIMICA', 1, programs['scienze_naturali']), ('FONDAMENTI DI BIOLOGIA', 1, programs['scienze_naturali']), ('FONDAMENTI DI SCIENZE DELLA TERRA', 1, programs['scienze_naturali']), ('GEOCHIMICA ED ANALISI DEI DATI AMBIENTALI', 1, programs['scienze_naturali']), ('INGLESE (Scienze Naturali)', 1, programs['scienze_naturali']), ('MATEMATICA E STATISTICA', 1, programs['scienze_naturali']),
                ('FISICA CON LABORATORIO (Scienze Naturali)', 2, programs['scienze_naturali']), ('GEOMORFOLOGIA', 2, programs['scienze_naturali']), ('IDROGEOLOGIA', 2, programs['scienze_naturali']), ('MINERALOGIA', 2, programs['scienze_naturali']), ('PALEONTOLOGIA, PALEOECOLOGIA E LABORATORIO', 2, programs['scienze_naturali']), ('PETROGRAFIA', 2, programs['scienze_naturali']), ('ZOOLOGIA GENERALE E SISTEMATICA', 2, programs['scienze_naturali']), ('BOTANICA GENERALE E SISTEMATICA', 2, programs['scienze_naturali']),
                ('ANATOMIA COMPARATA', 3, programs['scienze_naturali']), ('ECOLOGIA (Scienze Naturali)', 3, programs['scienze_naturali']), ('GENETICA (Scienze Naturali)', 3, programs['scienze_naturali']), ('GEOFISICA DELLA TERRA SOLIDA', 3, programs['scienze_naturali']), ('SOSTENIBILITÀ AMBIENTALE E PROTEZIONE DELLA NATURA', 3, programs['scienze_naturali']),
            
                # Scienze Motorie
                ('Anatomia Umana', 1, programs['scienze_motorie']), ('Biologia applicata', 1, programs['scienze_motorie']), ('Biochimica (Scienze Motorie)', 1, programs['scienze_motorie']), ('Fisica con elementi di biomeccanica', 1, programs['scienze_motorie']), ('Principi di diritto e management dello sport', 1, programs['scienze_motorie']), ('Inglese scientifico', 1, programs['scienze_motorie']), ('Teoria del movimento e tecnica dell\'attività motoria e sportiva', 1, programs['scienze_motorie']), ('Pedagogia e sociologia della comunicazione', 1, programs['scienze_motorie']),
                ('Informatica e Statistica', 2, programs['scienze_motorie']), ('Metodologie didattiche per le attivita\' sportive', 2, programs['scienze_motorie']), ('Didattica e pedagogia speciale', 2, programs['scienze_motorie']), ('Fisiologia umana applicata alle scienze motorie', 2, programs['scienze_motorie']), ('Teoria dell\'allenamento e metodi di valutazione motoria', 2, programs['scienze_motorie']), ('Bioingegneria applicata alle scienze motorie', 2, programs['scienze_motorie']),
                ('Basi di nutrizione applicata allo sport', 3, programs['scienze_motorie']), ('Igiene', 3, programs['scienze_motorie']), ('Genetica e performance sportiva', 3, programs['scienze_motorie']), ('Patologia generale', 3, programs['scienze_motorie']), ('Farmacologia applicata allo sport', 3, programs['scienze_motorie']),
            ]
            
            for name, year, program_obj in courses_to_add:
                if not Course.query.filter_by(name=name, degree_program_id=program_obj.id).first():
                    db.session.add(Course(name=name, year=year, degree_program=program_obj))
            
            db.session.commit()
            print("INIT_DB: Popolamento esami SQL completato.")
        except Exception as e:
            db.session.rollback()
            print(f"ERRORE INIT_DB (SQL Popolamento Esami): {e}")
            raise

    # --- Sezione MongoDB (invariata) ---
    print("INIT_DB: Inizio operazione su MongoDB...")
    mongo_client = None
    try:
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI non trovata.")

        db_name = "studenti_db"
        if "retryWrites" in mongo_uri and "/" not in mongo_uri.split("?")[0]:
            parts = mongo_uri.split("?")
            mongo_uri_with_db = f"{parts[0]}/{db_name}?{parts[1]}"
        else:
            mongo_uri_with_db = mongo_uri

        mongo_client = MongoClient(mongo_uri_with_db)
        db_mongo = mongo_client.get_database()
        
        print(f"INIT_DB: Connesso a MongoDB, database: {db_mongo.name}")
        
        users_collection = db_mongo.users
        if users_collection.count_documents({"username": "admin"}) == 0:
            print("INIT_DB: Aggiungendo utente 'admin'...")
            users_collection.insert_one({"username": "admin", "email": "admin@example.com", "password_hash": generate_password_hash("password")})
            print("INIT_DB: Utente 'admin' aggiunto.")
        else:
            print("INIT_DB: Utente 'admin' già presente.")
    except Exception as e:
        print(f"ERRORE INIT_DB (MONGO): {e}")
    finally:
        if mongo_client:
            mongo_client.close()
            print("INIT_DB: Connessione a MongoDB chiusa.")

if __name__ == '__main__':
    initialize_database()