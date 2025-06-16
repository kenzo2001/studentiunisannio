import os
from app import app, db, mongo, Department, DegreeProgram, Course, Note # Aggiunto Note
from werkzeug.security import generate_password_hash

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

        # 2. Popolamento Dipartimenti e Corsi di Laurea (se mancano)
        if not Department.query.first():
            print("INIT_DB: Popolando Dipartimenti e Corsi di Laurea...")
            # (Codice completo per Dipartimenti e Corsi di Laurea)
            ding = Department(name='DING'); dst = Department(name='DST'); demm = Department(name='DEMM')
            db.session.add_all([ding, dst, demm])
            db.session.commit()
            db.session.add_all([
                DegreeProgram(name='Ingegneria Energetica', department=ding),
                DegreeProgram(name='Ingegneria Civile', department=ding),
                DegreeProgram(name='Ingegneria Informatica', department=ding),
                DegreeProgram(name='Ingegneria Biomedica', department=ding),
                DegreeProgram(name='Scienze Biologiche', department=dst),
                DegreeProgram(name='Chimica', department=dst),
                DegreeProgram(name='Economia Aziendale', department=demm),
                DegreeProgram(name='Management', department=demm)
            ])
            db.session.commit()
            print("INIT_DB: Dipartimenti e Corsi di Laurea aggiunti.")
        else:
            print("INIT_DB: Dipartimenti e Corsi di Laurea già presenti.")

        # 3. FORZIAMO IL POPOLAMENTO DEGLI ESAMI
        print("INIT_DB: ESEGUENDO POPOLAMENTO FORZATO DEGLI ESAMI...")
        try:
            # NUOVO: Cancelliamo prima gli Appunti (Note) per risolvere l'errore di ForeignKeyViolation
            num_notes_deleted = db.session.query(Note).delete()
            if num_notes_deleted > 0:
                 print(f"INIT_DB: Cancellati {num_notes_deleted} appunti esistenti per pulizia.")

            # Ora cancelliamo i Corsi
            num_courses_deleted = db.session.query(Course).delete()
            if num_courses_deleted > 0:
                print(f"INIT_DB: Cancellati {num_courses_deleted} corsi esistenti per pulizia.")
            
            db.session.commit()

            # Ora recuperiamo i corsi di laurea e inseriamo quelli nuovi
            ing_energetica = DegreeProgram.query.filter_by(name='Ingegneria Energetica').first()
            ing_civile = DegreeProgram.query.filter_by(name='Ingegneria Civile').first()
            ing_informatica = DegreeProgram.query.filter_by(name='Ingegneria Informatica').first()
            ing_biomedica = DegreeProgram.query.filter_by(name='Ingegneria Biomedica').first()

            if all([ing_energetica, ing_civile, ing_informatica, ing_biomedica]):
                # Inserisci la lista completa di tutti gli esami
                db.session.add_all([
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_energetica), Course(name='Fisica Generale I', year=1, degree_program=ing_energetica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_energetica), Course(name='Chimica', year=1, degree_program=ing_energetica), Course(name='Informatica', year=1, degree_program=ing_energetica), Course(name='Disegno Tecnico Industriale', year=1, degree_program=ing_energetica), Course(name='Analisi Matematica II', year=2, degree_program=ing_energetica), Course(name='Fisica Generale II', year=2, degree_program=ing_energetica), Course(name='Meccanica Razionale', year=2, degree_program=ing_energetica), Course(name='Termodinamica Applicata', year=2, degree_program=ing_energetica), Course(name='Fondamenti di Elettrotecnica', year=2, degree_program=ing_energetica), Course(name='Scienza delle Costruzioni', year=2, degree_program=ing_energetica), Course(name='Macchine a Fluido', year=3, degree_program=ing_energetica), Course(name='Impianti Termotecnici', year=3, degree_program=ing_energetica), Course(name='Economia ed Estimo Civile', year=3, degree_program=ing_energetica), Course(name='Energie Rinnovabili', year=3, degree_program=ing_energetica), Course(name='Sistemi Energetici', year=3, degree_program=ing_energetica), Course(name='Ingegneria della Sicurezza', year=3, degree_program=ing_energetica),
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_civile), Course(name='Fisica Generale I', year=1, degree_program=ing_civile), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_civile), Course(name='Chimica', year=1, degree_program=ing_civile), Course(name='Informatica', year=1, degree_program=ing_civile), Course(name='Disegno', year=1, degree_program=ing_civile), Course(name='Analisi Matematica II', year=2, degree_program=ing_civile), Course(name='Fisica Generale II', year=2, degree_program=ing_civile), Course(name='Meccanica Razionale', year=2, degree_program=ing_civile), Course(name='Scienza delle Costruzioni', year=2, degree_program=ing_civile), Course(name='Geotecnica', year=2, degree_program=ing_civile), Course(name='Idraulica', year=2, degree_program=ing_civile), Course(name='Tecnica delle Costruzioni', year=3, degree_program=ing_civile), Course(name='Costruzioni Idrauliche', year=3, degree_program=ing_civile), Course(name='Topografia e Cartografia', year=3, degree_program=ing_civile), Course(name='Trasporti', year=3, degree_program=ing_civile), Course(name='Estimo', year=3, degree_program=ing_civile), Course(name='Urbanistica', year=3, degree_program=ing_civile),
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_informatica), Course(name='Fisica Generale I', year=1, degree_program=ing_informatica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_informatica), Course(name='Programmazione I', year=1, degree_program=ing_informatica), Course(name='Fondamenti di Informatica', year=1, degree_program=ing_informatica), Course(name='Calcolo Numerico', year=1, degree_program=ing_informatica), Course(name='Analisi Matematica II', year=2, degree_program=ing_informatica), Course(name='Fisica Generale II', year=2, degree_program=ing_informatica), Course(name='Architetture dei Calcolatori', year=2, degree_program=ing_informatica), Course(name='Sistemi Operativi', year=2, degree_program=ing_informatica), Course(name='Programmazione II', year=2, degree_program=ing_informatica), Course(name='Algoritmi e Strutture Dati', year=2, degree_program=ing_informatica), Course(name='Basi di Dati', year=3, degree_program=ing_informatica), Course(name='Reti di Calcolatori', year=3, degree_program=ing_informatica), Course(name='Ingegneria del Software', year=3, degree_program=ing_informatica), Course(name='Sicurezza dei Sistemi', year=3, degree_program=ing_informatica), Course(name='Intelligenza Artificiale', year=3, degree_program=ing_informatica), Course(name='Sistemi Distribuiti', year=3, degree_program=ing_informatica),
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_biomedica), Course(name='Fisica Generale I', year=1, degree_program=ing_biomedica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_biomedica), Course(name='Biologia', year=1, degree_program=ing_biomedica), Course(name='Chimica', year=1, degree_program=ing_biomedica), Course(name='Informatica', year=1, degree_program=ing_biomedica), Course(name='Analisi Matematica II', year=2, degree_program=ing_biomedica), Course(name='Fisica Generale II', year=2, degree_program=ing_biomedica), Course(name='Meccanica Razionale', year=2, degree_program=ing_biomedica), Course(name='Fisiologia', year=2, degree_program=ing_biomedica), Course(name='Elettrotecnica', year=2, degree_program=ing_biomedica), Course(name='Elettronica', year=2, degree_program=ing_biomedica), Course(name='Bioingegneria dei Sistemi', year=3, degree_program=ing_biomedica), Course(name='Strumentazione Biomedica', year=3, degree_program=ing_biomedica), Course(name='Elaborazione dei Segnali Biomedici', year=3, degree_program=ing_biomedica), Course(name='Modellistica e Simulazione', year=3, degree_program=ing_biomedica), Course(name='Materiali Biomedici', year=3, degree_program=ing_biomedica), Course(name='Bioetica e Legislazione', year=3, degree_program=ing_biomedica),
                ])
                db.session.commit()
                print("INIT_DB: Inserimento forzato degli esami di Ingegneria COMPLETATO.")
            else:
                print("ERRORE INIT_DB: Non è stato possibile trovare i Corsi di Laurea per associare gli esami.")
        except Exception as e:
            db.session.rollback()
            print(f"ERRORE INIT_DB durante il popolamento forzato dei corsi: {e}")
            raise

        # 4. Inizializzazione utente admin su MongoDB
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