import os
from app import app, db, mongo, Department, DegreeProgram, Course
from werkzeug.security import generate_password_hash

def initialize_database():
    print("INIT_DB: Inizio inizializzazione database.")
    with app.app_context():
        # Creazione tabelle SQL
        try:
            print(f"INIT_DB: URL del database SQL in uso: {app.config['SQLALCHEMY_DATABASE_URI']}")
            db.create_all()
            print("INIT_DB: Database e tabelle SQL create (o già esistenti).")
        except Exception as e:
            print(f"ERRORE INIT_DB: Errore durante la creazione delle tabelle SQL: {e}")
            raise

        # Popolamento dati SQL (se il DB è vuoto)
        if not Department.query.first():
            print("INIT_DB: Popolando il database SQL con dati di esempio...")
            # Dipartimenti
            ding = Department(name='DING')
            dst = Department(name='DST')
            demm = Department(name='DEMM')
            db.session.add_all([ding, dst, demm])
            db.session.commit()
            print("INIT_DB: Dipartimenti SQL aggiunti.")

            # Corsi di Laurea per DING
            ing_energetica = DegreeProgram(name='Ingegneria Energetica', department=ding)
            ing_civile = DegreeProgram(name='Ingegneria Civile', department=ding)
            ing_informatica = DegreeProgram(name='Ingegneria Informatica', department=ding)
            ing_biomedica = DegreeProgram(name='Ingegneria Biomedica', department=ding)
            db.session.add_all([ing_energetica, ing_civile, ing_informatica, ing_biomedica])
            db.session.commit()
            print("INIT_DB: Corsi di laurea per DING aggiunti.")
            
            # (qui va il resto del codice per popolare i corsi di laurea e gli esami, l'ho omesso per brevità ma nel tuo file deve esserci)
            print("INIT_DB: Dati di esempio SQL aggiunti.")
        else:
            print("INIT_DB: Database SQL già popolato con dati di esempio.")

        # Aggiungi un utente amministratore di esempio in MongoDB (se non esiste)
        try:
            print(f"INIT_DB: Tentativo di connessione a MongoDB...")
            if mongo.db.users.count_documents({"username": "admin"}) == 0:
                print("INIT_DB: Aggiungendo utente 'admin' di esempio in MongoDB...")
                admin_user = {
                    "username": "admin",
                    "email": "admin@example.com",
                    "password_hash": generate_password_hash("password")
                }
                mongo.db.users.insert_one(admin_user)
                print("INIT_DB: Utente 'admin' aggiunto in MongoDB.")
            else:
                print("INIT_DB: Utente 'admin' di esempio già presente in MongoDB.")
        except Exception as e:
            print(f"ERRORE INIT_DB: Errore durante l'operazione su MongoDB: {e}")
            print("CAUSA PROBABILE: La MONGO_URI non è impostata o non è valida, oppure l'IP del server non è autorizzato su MongoDB Atlas.")
            raise

if __name__ == '__main__':
    initialize_database()