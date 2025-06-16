import os
from app import app, db, mongo, Department, DegreeProgram, Course, Note
from werkzeug.security import generate_password_hash

def initialize_database():
    print("INIT_DB: Inizio inizializzazione database.")
    with app.app_context():
        # 1. Creazione di tutte le tabelle SQL (se non esistono)
        db.create_all()
        print("INIT_DB: Struttura tabelle SQL verificata/creata.")

        # 2. Popolamento Dipartimenti e Corsi di Laurea (SOLO se mancano)
        if not Department.query.first():
            print("INIT_DB: Popolando Dipartimenti e Corsi di Laurea...")
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
        
        # 3. Popolamento degli Esami (SOLO se mancano)
        if not Course.query.first():
            print("INIT_DB: Popolando gli esami di Ingegneria...")
            ing_energetica = DegreeProgram.query.filter_by(name='Ingegneria Energetica').first()
            ing_civile = DegreeProgram.query.filter_by(name='Ingegneria Civile').first()
            ing_informatica = DegreeProgram.query.filter_by(name='Ingegneria Informatica').first()
            ing_biomedica = DegreeProgram.query.filter_by(name='Ingegneria Biomedica').first()
            if all([ing_energetica, ing_civile, ing_informatica, ing_biomedica]):
                db.session.add_all([
                    # (la lunga lista di corsi che era qui)
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_energetica), Course(name='Fisica Generale I', year=1, degree_program=ing_energetica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_energetica), # ... e tutti gli altri
                ])
                db.session.commit()
                print("INIT_DB: Esami aggiunti.")

        # 4. Inizializzazione utente admin su MongoDB (SOLO se manca)
        try:
            if mongo.db.users.count_documents({"username": "admin"}) == 0:
                print("INIT_DB: Aggiungendo utente 'admin' in MongoDB...")
                mongo.db.users.insert_one({"username": "admin", "email": "admin@example.com", "password_hash": generate_password_hash("password")})
                print("INIT_DB: Utente 'admin' aggiunto.")
        except Exception as e:
            print(f"ERRORE INIT_DB: Errore durante l'operazione su MongoDB: {e}")
            raise

if __name__ == '__main__':
    initialize_database()