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
                ('Analisi Matematica I', 1, programs['Ingegneria Energetica']), ('Analisi Matematica II', 1, programs['Ingegneria Energetica']),('Fisica Generale I', 1, programs['Ingegneria Energetica']),('Fisica Generale II', 1, programs['Ingegneria Energetica']),  ('Algebra Lineare Geometria e ricerca operativa', 1, programs['Ingegneria Energetica']), ('Chimica', 1, programs['Ingegneria Energetica']), ('Elementi di Informatica', 1, programs['Ingegneria Energetica']), ('Fondamenti della misurazione', 1, programs['Ingegneria Energetica']),('Inglese', 1, programs['Ingegneria Energetica']),
                ('Modelli di Reattori Chimici', 2, programs['Ingegneria Energetica']),('Sistemi Elettrici per L^Energia', 2, programs['Ingegneria Energetica']),('Termofluido Dinamica e Trasmissione del Calore', 2, programs['Ingegneria Energetica']), ('Meccanica Applicata alle Macchine', 2, programs['Ingegneria Energetica']), ('Elettrotecnica', 2, programs['Ingegneria Energetica']), ('Fisica Tecnica', 2, programs['Ingegneria Energetica']),('Processi di Combustione', 2, programs['Ingegneria Energetica']),('Macchine a Fluido', 2, programs['Ingegneria Energetica']),
                ('Impianti Chimici per L^Energia', 3, programs['Ingegneria Energetica']), ('Impianti Industriali', 3, programs['Ingegneria Energetica']), ('Energetica', 3, programs['Ingegneria Energetica']), ('Tecnologie delle Fonti Rinnovabili', 3, programs['Ingegneria Energetica']), ('Sistemi Elettrici Industriali', 3, programs['Ingegneria Energetica']), ('Elementi di Ingegneria Strutturali', 3, programs['Ingegneria Energetica']),
                # Ingegneria Civile
                ('Analisi Matematica I', 1, programs['Ingegneria Civile']), ('Analisi Matematica II', 1, programs['Ingegneria Civile']),('Fisica Generale ', 1, programs['Ingegneria Civile']),('Geometria e Algebra Lineare', 1, programs['Ingegneria Civile']),('Elementi di Informatica', 1, programs['Ingegneria Civile']), ('Scienze e tecnologia dei Materiali', 1, programs['Ingegneria Civile']),('Inglese', 1, programs['Ingegneria Civile']),
                ('Meccanica Razionale', 2, programs['Ingegneria Civile']), ('Scienza delle Costruzioni', 2, programs['Ingegneria Civile']), ('Fisica Tecnica', 2, programs['Ingegneria Civile']), ('Idraulica', 2, programs['Ingegneria Civile']),('Tecnica Urbanistica', 2, programs['Ingegneria Civile']),('Ingegneria dei Sistemi di trasporto I', 2, programs['Ingegneria Civile']),('Ingegneria dei Sistemi di trasporto II', 2, programs['Ingegneria Civile']),('Fondamenti di Infrastrutture Viaree', 2, programs['Ingegneria Civile']),('Climatologia dell Ambiente Costruito', 2, programs['Ingegneria Civile']),
                ('Tecnica delle Costruzioni I', 3, programs['Ingegneria Civile'])('Tecnica delle Costruzioni II', 3, programs['Ingegneria Civile']), ('Costruzioni Idrauliche', 3, programs['Ingegneria Civile']), ('Topografia e Cartografia', 3, programs['Ingegneria Civile']), ('Principi di Geotecnica', 3, programs['Ingegneria Civile']), ('Fondazioni ed Opere di Sostegno', 3, programs['Ingegneria Civile']), 
                # Ingegneria Informatica
                ('Analisi Matematica I', 1, programs['Ingegneria Informatica']),  ('Analisi Matematica II', 1, programs['Ingegneria Informatica']), ('Fisica Generale II', 1, programs['Ingegneria Informatica']),('Fisica Generale I', 1, programs['Ingegneria Informatica']), ('Matematica per l Ingegneria dell Informazione', 1, programs['Ingegneria Informatica']), ('Programmazione I', 1, programs['Ingegneria Informatica']), ('Inglese', 1, programs['Ingegneria Informatica']), ('Calcolatori Elettronici', 1, programs['Ingegneria Informatica']),('Economia Aziendale', 1, programs['Ingegneria Informatica']),
                ('Fondamenti di Telecomunicazione', 2, programs['Ingegneria Informatica']), ('Sistemi Operativi', 2, programs['Ingegneria Informatica']), ('Programmazione II', 2, programs['Ingegneria Informatica']),('Elettrotecnica', 3, programs['Ingegneria Informatica']),('Elettronica', 3, programs['Ingegneria Informatica']),('Sistemi Dinamici ', 3, programs['Ingegneria Informatica']),('Controlli Automatici', 3, programs['Ingegneria Informatica']),
                ('Basi di Dati', 3, programs['Ingegneria Informatica']), ('Misure Elettroniche', 3, programs['Ingegneria Informatica']), ('Ingegneria del Software', 3, programs['Ingegneria Informatica']),('Algoritmi e Strutture Dati', 3, programs['Ingegneria Informatica']), ('Computazione Pervasiva', 3, programs['Ingegneria Informatica']), ('Data analycist', 3, programs['Ingegneria Informatica']), ('PSR ', 3, programs['Ingegneria Informatica']),
                # Ingegneria Biomedica
                ('Analisi Matematica I', 1, programs['Ingegneria Biomedica']),('Analisi Matematica II', 1, programs['Ingegneria Biomedica']), ('Fisica Generale II', 1, programs['Ingegneria Biomedica']), ('Fisica Generale I', 1, programs['Ingegneria Biomedica']), ('Geometria e Algebra Lineare', 1, programs['Ingegneria Biomedica']), ('Inglese', 1, programs['Ingegneria Biomedica']), ('Chimica', 1, programs['Ingegneria Biomedica']), ('Programmazione I', 1, programs['Ingegneria Biomedica']),('Programmazione II ed Inteligenza Artificiale', 1, programs['Ingegneria Biomedica']),
                ('Misure Elettroniche', 2, programs['Ingegneria Biomedica']), ('Elementi di Biochimica', 2, programs['Ingegneria Biomedica']), ('Elettrotecnica', 2, programs['Ingegneria Biomedica']), ('Elettronica', 2, programs['Ingegneria Biomedica']),('Matematica II', 2, programs['Ingegneria Biomedica']),('Sistemi Dinamici', 2, programs['Ingegneria Biomedica']),('Probabilità e segnali', 2, programs['Ingegneria Biomedica']),('Elaborazione Numerica dei segnali', 2, programs['Ingegneria Biomedica']),
                ('BioElettromagnetismo', 3, programs['Ingegneria Biomedica']),('Sistemi di Acquisizione Dati', 3, programs['Ingegneria Biomedica']),('Sistemi Biomedicali', 3, programs['Ingegneria Biomedica']),('Laboratorio di BioElettronica', 3, programs['Ingegneria Biomedica']),('Laboratorio di Misure Elettroniche per Applicazioni Medicali', 3, programs['Ingegneria Biomedica']),
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