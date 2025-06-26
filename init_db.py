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
        departments_to_ensure = ['DING', 'DST', 'DEMM']
        for dept_name in departments_to_ensure:
            if not Department.query.filter_by(name=dept_name).first():
                db.session.add(Department(name=dept_name))
        db.session.commit()

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
        db.session.commit()
        # ... (il resto del codice SQL rimane uguale)
        print("INIT_DB: Dati SQL verificati/creati.")

    print("INIT_DB: Inizio operazione su MongoDB...")
    mongo_client = None
    try:
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI non trovata.")

        # --- MODIFICA CHIAVE QUI ---
        # Aggiungiamo il nome del database alla fine della stringa di connessione
        # Se non è già presente, lo aggiungiamo.
        if "retryWrites" in mongo_uri and "/" not in mongo_uri.split("?")[0]:
             # Inseriamo il nome del database prima dei parametri
             db_name = "studenti_db"
             parts = mongo_uri.split("?")
             mongo_uri_with_db = f"{parts[0]}/{db_name}?{parts[1]}"
        else:
            mongo_uri_with_db = mongo_uri

        mongo_client = MongoClient(mongo_uri_with_db)
        # Selezioniamo il database esplicitamente
        db_mongo = mongo_client.get_database() # Questo ora funzionerà
        
        print(f"INIT_DB: Connesso a MongoDB, database: {db_mongo.name}")
        
        users_collection = db_mongo.users
        if users_collection.count_documents({"username": "admin"}) == 0:
            print("INIT_DB: Aggiungendo utente 'admin'...")
            users_collection.insert_one({
                "username": "admin", "email": "admin@example.com", "password_hash": generate_password_hash("password")
            })
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