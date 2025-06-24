# init_db.py modificato

import os
from app import app, db, mongo, Department, DegreeProgram, Course, Note
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

        # 2. Popolamento Dipartimenti e Corsi di Laurea (solo se mancano)
        if not Department.query.first():
            print("INIT_DB: Popolando Dipartimenti e Corsi di Laurea...")
            ding = Department(name='DING'); dst = Department(name='DST'); demm = Department(name='DEMM')
            db.session.add_all([ding, dst, demm])
            db.session.commit() # Commit per rendere i dipartimenti disponibili
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

        # 3. POPOLAMENTO CONDIZIONALE DEGLI ESAMI (versione corretta)
        # Questo blocco viene eseguito solo se non ci sono corsi nel database.
        if not Course.query.first():
            print("INIT_DB: Nessun corso trovato. Eseguendo popolamento iniziale degli esami...")
            try:
                # Recuperiamo i corsi di laurea per associare gli esami
                ing_energetica = DegreeProgram.query.filter_by(name='Ingegneria Energetica').first()
                ing_civile = DegreeProgram.query.filter_by(name='Ingegneria Civile').first()
                ing_informatica = DegreeProgram.query.filter_by(name='Ingegneria Informatica').first()
                ing_biomedica = DegreeProgram.query.filter_by(name='Ingegneria Biomedica').first()

                if all([ing_energetica, ing_civile, ing_informatica, ing_biomedica]):
                    # Inserisci qui la lista completa di tutti gli esami (la stessa che avevi prima)
                    db.session.add_all([
                        # ... ESEMPIO ...
                        Course(name='Analisi Matematica I', year=1, degree_program=ing_informatica),
                        Course(name='Programmazione I', year=1, degree_program=ing_informatica),
                        # ... INSERISCI QUI TUTTI GLI ALTRI CORSI COME NEL FILE ORIGINALE ...
                    ])
                    db.session.commit()
                    print("INIT_DB: Inserimento iniziale degli esami di Ingegneria COMPLETATO.")
                else:
                    print("ERRORE INIT_DB: Non è stato possibile trovare i Corsi di Laurea per associare gli esami.")
            except Exception as e:
                db.session.rollback()
                print(f"ERRORE INIT_DB durante il popolamento dei corsi: {e}")
                raise
        else:
            print("INIT_DB: I corsi sono già presenti nel database. Salto il popolamento.")

        # 4. Inizializzazione utente admin su MongoDB (solo se manca)
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