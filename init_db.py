import os
from app import app, db, mongo, Department, DegreeProgram, Course, Note
from werkzeug.security import generate_password_hash
from sqlalchemy.orm.exc import NoResultFound

def initialize_database():
    print("INIT_DB: Inizio inizializzazione database.")
    with app.app_context():
        # 1. Creazione di tutte le tabelle SQL (se non esistono)
        try:
            db.create_all()
            print("INIT_DB: Struttura tabelle SQL verificata/creata.")
        except Exception as e:
            print(f"ERRORE INIT_DB: Errore durante la creazione delle tabelle SQL: {e}")
            raise

        # 2. Popolamento Dipartimenti (se mancano)
        departments_to_ensure = ['DING', 'DST', 'DEMM']
        for dept_name in departments_to_ensure:
            if not Department.query.filter_by(name=dept_name).first():
                db.session.add(Department(name=dept_name))
                print(f"INIT_DB: Aggiunto dipartimento '{dept_name}'.")
        db.session.commit()

        # 3. Popolamento Corsi di Laurea (se mancano)
        ding_dept = Department.query.filter_by(name='DING').one()
        dst_dept = Department.query.filter_by(name='DST').one()
        demm_dept = Department.query.filter_by(name='DEMM').one()
        
        degree_programs_to_ensure = [
            {'name': 'Ingegneria Energetica', 'department': ding_dept},
            {'name': 'Ingegneria Civile', 'department': ding_dept},
            {'name': 'Ingegneria Informatica', 'department': ding_dept},
            {'name': 'Ingegneria Biomedica', 'department': ding_dept},
            {'name': 'Scienze Biologiche', 'department': dst_dept},
            {'name': 'Chimica', 'department': dst_dept},
            {'name': 'Economia Aziendale', 'department': demm_dept},
            {'name': 'Management', 'department': demm_dept}
        ]
        for dp_data in degree_programs_to_ensure:
            if not DegreeProgram.query.filter_by(name=dp_data['name']).first():
                db.session.add(DegreeProgram(name=dp_data['name'], department=dp_data['department']))
                print(f"INIT_DB: Aggiunto corso di laurea '{dp_data['name']}'.")
        db.session.commit()

        # 4. Popolamento robusto degli Esami (aggiunge solo quelli mancanti)
        print("INIT_DB: Verificando e aggiungendo esami mancanti...")
        try:
            # Recupera gli ID dei corsi di laurea una sola volta
            programs = {
                'Ingegneria Energetica': DegreeProgram.query.filter_by(name='Ingegneria Energetica').one(),
                'Ingegneria Civile': DegreeProgram.query.filter_by(name='Ingegneria Civile').one(),
                'Ingegneria Informatica': DegreeProgram.query.filter_by(name='Ingegneria Informatica').one(),
                'Ingegneria Biomedica': DegreeProgram.query.filter_by(name='Ingegneria Biomedica').one()
            }

            courses_to_add = [
                # Ingegneria Energetica
                ('Analisi Matematica I', 1, programs['Ingegneria Energetica']), ('Fisica Generale I', 1, programs['Ingegneria Energetica']), ('Geometria e Algebra Lineare', 1, programs['Ingegneria Energetica']), ('Chimica', 1, programs['Ingegneria Energetica']), ('Informatica', 1, programs['Ingegneria Energetica']), ('Disegno Tecnico Industriale', 1, programs['Ingegneria Energetica']),
                ('Analisi Matematica II', 2, programs['Ingegneria Energetica']), ('Fisica Generale II', 2, programs['Ingegneria Energetica']), ('Meccanica Razionale', 2, programs['Ingegneria Energetica']), ('Termodinamica Applicata', 2, programs['Ingegneria Energetica']), ('Fondamenti di Elettrotecnica', 2, programs['Ingegneria Energetica']), ('Scienza delle Costruzioni', 2, programs['Ingegneria Energetica']),
                ('Macchine a Fluido', 3, programs['Ingegneria Energetica']), ('Impianti Termotecnici', 3, programs['Ingegneria Energetica']), ('Economia ed Estimo Civile', 3, programs['Ingegneria Energetica']), ('Energie Rinnovabili', 3, programs['Ingegneria Energetica']), ('Sistemi Energetici', 3, programs['Ingegneria Energetica']), ('Ingegneria della Sicurezza', 3, programs['Ingegneria Energetica']),
                # Ingegneria Civile
                ('Analisi Matematica I', 1, programs['Ingegneria Civile']), ('Fisica Generale I', 1, programs['Ingegneria Civile']), ('Geometria e Algebra Lineare', 1, programs['Ingegneria Civile']), ('Chimica', 1, programs['Ingegneria Civile']), ('Informatica', 1, programs['Ingegneria Civile']), ('Disegno', 1, programs['Ingegneria Civile']),
                ('Analisi Matematica II', 2, programs['Ingegneria Civile']), ('Fisica Generale II', 2, programs['Ingegneria Civile']), ('Meccanica Razionale', 2, programs['Ingegneria Civile']), ('Scienza delle Costruzioni', 2, programs['Ingegneria Civile']), ('Geotecnica', 2, programs['Ingegneria Civile']), ('Idraulica', 2, programs['Ingegneria Civile']),
                ('Tecnica delle Costruzioni', 3, programs['Ingegneria Civile']), ('Costruzioni Idrauliche', 3, programs['Ingegneria Civile']), ('Topografia e Cartografia', 3, programs['Ingegneria Civile']), ('Trasporti', 3, programs['Ingegneria Civile']), ('Estimo', 3, programs['Ingegneria Civile']), ('Urbanistica', 3, programs['Ingegneria Civile']),
                # Ingegneria Informatica
                ('Analisi Matematica I', 1, programs['Ingegneria Informatica']), ('Fisica Generale I', 1, programs['Ingegneria Informatica']), ('Geometria e Algebra Lineare', 1, programs['Ingegneria Informatica']), ('Programmazione I', 1, programs['Ingegneria Informatica']), ('Fondamenti di Informatica', 1, programs['Ingegneria Informatica']), ('Calcolo Numerico', 1, programs['Ingegneria Informatica']),
                ('Analisi Matematica II', 2, programs['Ingegneria Informatica']), ('Fisica Generale II', 2, programs['Ingegneria Informatica']), ('Architetture dei Calcolatori', 2, programs['Ingegneria Informatica']), ('Sistemi Operativi', 2, programs['Ingegneria Informatica']), ('Programmazione II', 2, programs['Ingegneria Informatica']), ('Algoritmi e Strutture Dati', 2, programs['Ingegneria Informatica']),
                ('Basi di Dati', 3, programs['Ingegneria Informatica']), ('Reti di Calcolatori', 3, programs['Ingegneria Informatica']), ('Ingegneria del Software', 3, programs['Ingegneria Informatica']), ('Sicurezza dei Sistemi', 3, programs['Ingegneria Informatica']), ('Intelligenza Artificiale', 3, programs['Ingegneria Informatica']), ('Sistemi Distribuiti', 3, programs['Ingegneria Informatica']),
                # Ingegneria Biomedica
                ('Analisi Matematica I', 1, programs['Ingegneria Biomedica']), ('Fisica Generale I', 1, programs['Ingegneria Biomedica']), ('Geometria e Algebra Lineare', 1, programs['Ingegneria Biomedica']), ('Biologia', 1, programs['Ingegneria Biomedica']), ('Chimica', 1, programs['Ingegneria Biomedica']), ('Informatica', 1, programs['Ingegneria Biomedica']),
                ('Analisi Matematica II', 2, programs['Ingegneria Biomedica']), ('Fisica Generale II', 2, programs['Ingegneria Biomedica']), ('Meccanica Razionale', 2, programs['Ingegneria Biomedica']), ('Fisiologia', 2, programs['Ingegneria Biomedica']), ('Elettrotecnica', 2, programs['Ingegneria Biomedica']), ('Elettronica', 2, programs['Ingegneria Biomedica']),
                ('Bioingegneria dei Sistemi', 3, programs['Ingegneria Biomedica']), ('Strumentazione Biomedica', 3, programs['Ingegneria Biomedica']), ('Elaborazione dei Segnali Biomedici', 3, programs['Ingegneria Biomedica']), ('Modellistica e Simulazione', 3, programs['Ingegneria Biomedica']), ('Materiali Biomedici', 3, programs['Ingegneria Biomedica']), ('Bioetica e Legislazione', 3, programs['Ingegneria Biomedica']),
            ]
            
            for name, year, program_obj in courses_to_add:
                exists = Course.query.filter_by(name=name, degree_program_id=program_obj.id).first()
                if not exists:
                    course = Course(name=name, year=year, degree_program=program_obj)
                    db.session.add(course)
                    print(f"INIT_DB: Aggiunto esame '{name}' per {program_obj.name}.")
            
            db.session.commit()
            print("INIT_DB: Popolamento esami completato.")

        except NoResultFound as e:
            db.session.rollback()
            print(f"ERRORE INIT_DB: Impossibile trovare un corso di laurea necessario per l'associazione. Dettagli: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"ERRORE INIT_DB durante il popolamento degli esami: {e}")
            raise

        # 5. Inizializzazione utente admin su MongoDB (solo se manca)
        try:
            if mongo.db.users.count_documents({"username": "admin"}) == 0:
                print("INIT_DB: Aggiungendo utente 'admin' di esempio in MongoDB...")
                mongo.db.users.insert_one({"username": "admin", "email": "admin@example.com", "password_hash": generate_password_hash("password")})
                print("INIT_DB: Utente 'admin' aggiunto in MongoDB.")
            else:
                print("INIT_DB: Utente 'admin' di esempio già presente in MongoDB.")
        except Exception as e:
            print(f"ERRORE INIT_DB: Errore durante l'operazione su MongoDB: {e}")
            raise

if __name__ == '__main__':
    initialize_database()