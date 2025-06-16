# init_db.py
import os
# Importa app e db (dall'istanza globale in app.py) e i modelli del database
from app import app, db, Department, DegreeProgram, Course, User 
from werkzeug.security import generate_password_hash # Per hashare la password di un utente admin di prova

# Questo script è pensato per essere eseguito SOLO DURANTE IL BUILD O L'INIZIALIZZAZIONE.
# NON DEVE ESSERE INVOCATO DURANTE IL NORMALE FUNZIONAMENTO DELL'APP IN PRODUZIONE.

def initialize_database():
    print("INIT_DB: Inizio inizializzazione database.") # LOG: Inizio
    
    # Questo blocco 'with app.app_context()' è fondamentale per operare sul database
    # perché SQLAlchemy ha bisogno del contesto dell'applicazione Flask.
    with app.app_context():
        # LOG: Mostra l'URL del database che lo script sta tentando di usare
        print(f"INIT_DB: URL del database in uso: {app.config['SQLALCHEMY_DATABASE_URI']}") 

        try:
            # Crea tutte le tabelle definite dai modelli (User, Department, DegreeProgram, Course, Note)
            db.create_all() 
            print("INIT_DB: Database e tabelle create (o già esistenti) in PostgreSQL.") # LOG: Successo creazione tabelle
        except Exception as e:
            # LOG: Cattura e stampa qualsiasi errore durante la creazione delle tabelle
            print(f"ERRORE INIT_DB: Errore durante la creazione delle tabelle: {e}") 
            # Rilancia l'eccezione per far fallire il build, indicando il problema
            raise 

        # --- Popolamento Dati di Esempio (solo se il DB è vuoto) ---
        # Questo controllo `if not Department.query.first():` è cruciale per evitare duplicati
        # se lo script viene eseguito più volte su un database persistente.
        try:
            if not Department.query.first(): 
                print("INIT_DB: Popolando il database con dati di esempio (Dipartimenti, Corsi, Esami)...") # LOG: Inizio popolamento

                # Dipartimenti
                ding = Department(name='DING')
                dst = Department(name='DST')
                demm = Department(name='DEMM')
                db.session.add_all([ding, dst, demm]) 
                db.session.commit() # Esegui il commit per salvare i dipartimenti e ottenere i loro ID
                print("INIT_DB: Dipartimenti aggiunti.") # LOG

                # Corsi di Laurea per DING
                ing_energetica = DegreeProgram(name='Ingegneria Energetica', department=ding)
                ing_civile = DegreeProgram(name='Ingegneria Civile', department=ding)
                ing_informatica = DegreeProgram(name='Ingegneria Informatica', department=ding)
                ing_biomedica = DegreeProgram(name='Ingegneria Biomedica', department=ding)
                db.session.add_all([ing_energetica, ing_civile, ing_informatica, ing_biomedica])
                db.session.commit() # Esegui il commit per salvare i corsi di laurea
                print("INIT_DB: Corsi di laurea per DING aggiunti.") # LOG

                # Corsi di Laurea per DST
                scienze_biologiche = DegreeProgram(name='Scienze Biologiche', department=dst)
                chimica = DegreeProgram(name='Chimica', department=dst)
                db.session.add_all([scienze_biologiche, chimica])
                db.session.commit()

                # Corsi di Laurea per DEMM
                economia_aziendale = DegreeProgram(name='Economia Aziendale', department=demm)
                management = DegreeProgram(name='Management', department=demm)
                db.session.add_all([economia_aziendale, management])
                db.session.commit()

                # --- Inserimento di Esami per le Ingegnerie (DING) ---
                db.session.add_all([
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_energetica), Course(name='Fisica Generale I', year=1, degree_program=ing_energetica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_energetica), Course(name='Chimica', year=1, degree_program=ing_energetica), Course(name='Informatica', year=1, degree_program=ing_energetica), Course(name='Disegno Tecnico Industriale', year=1, degree_program=ing_energetica), Course(name='Analisi Matematica II', year=2, degree_program=ing_energetica), Course(name='Fisica Generale II', year=2, degree_program=ing_energetica), Course(name='Meccanica Razionale', year=2, degree_program=ing_energetica), Course(name='Termodinamica Applicata', year=2, degree_program=ing_energetica), Course(name='Fondamenti di Elettrotecnica', year=2, degree_program=ing_energetica), Course(name='Scienza delle Costruzioni', year=2, degree_program=ing_energetica), Course(name='Macchine a Fluido', year=3, degree_program=ing_energetica), Course(name='Impianti Termotecnici', year=3, degree_program=ing_energetica), Course(name='Economia ed Estimo Civile', year=3, degree_program=ing_energetica), Course(name='Energie Rinnovabili', year=3, degree_program=ing_energetica), Course(name='Sistemi Energetici', year=3, degree_program=ing_energetica), Course(name='Ingegneria della Sicurezza', year=3, degree_program=ing_energetica),
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_civile), Course(name='Fisica Generale I', year=1, degree_program=ing_civile), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_civile), Course(name='Chimica', year=1, degree_program=ing_civile), Course(name='Informatica', year=1, degree_program=ing_civile), Course(name='Disegno', year=1, degree_program=ing_civile), Course(name='Analisi Matematica II', year=2, degree_program=ing_civile), Course(name='Fisica Generale II', year=2, degree_program=ing_civile), Course(name='Meccanica Razionale', year=2, degree_program=ing_civile), Course(name='Scienza delle Costruzioni', year=2, degree_program=ing_civile), Course(name='Geotecnica', year=2, degree_program=ing_civile), Course(name='Idraulica', year=2, degree_program=ing_civile), Course(name='Tecnica delle Costruzioni', year=3, degree_program=ing_civile), Course(name='Costruzioni Idrauliche', year=3, degree_program=ing_civile), Course(name='Topografia e Cartografia', year=3, degree_program=ing_civile), Course(name='Trasporti', year=3, degree_program=ing_civile), Course(name='Estimo', year=3, degree_program=ing_civile), Course(name='Urbanistica', year=3, degree_program=ing_civile),
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_informatica), Course(name='Fisica Generale I', year=1, degree_program=ing_informatica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_informatica), Course(name='Programmazione I', year=1, degree_program=ing_informatica), Course(name='Fondamenti di Informatica', year=1, degree_program=ing_informatica), Course(name='Calcolo Numerico', year=1, degree_program=ing_informatica), Course(name='Analisi Matematica II', year=2, degree_program=ing_informatica), Course(name='Fisica Generale II', year=2, degree_program=ing_informatica), Course(name='Architetture dei Calcolatori', year=2, degree_program=ing_informatica), Course(name='Sistemi Operativi', year=2, degree_program=ing_informatica), Course(name='Programmazione II', year=2, degree_program=ing_informatica), Course(name='Algoritmi e Strutture Dati', year=2, degree_program=ing_informatica), Course(name='Basi di Dati', year=3, degree_program=ing_informatica), Course(name='Reti di Calcolatori', year=3, degree_program=ing_informatica), Course(name='Ingegneria del Software', year=3, degree_program=ing_informatica), Course(name='Sicurezza dei Sistemi', year=3, degree_program=ing_informatica), Course(name='Intelligenza Artificiale', year=3, degree_program=ing_informatica), Course(name='Sistemi Distribuiti', year=3, degree_program=ing_informatica),
                    Course(name='Analisi Matematica I', year=1, degree_program=ing_biomedica), Course(name='Fisica Generale I', year=1, degree_program=ing_biomedica), Course(name='Geometria e Algebra Lineare', year=1, degree_program=ing_biomedica), Course(name='Biologia', year=1, degree_program=ing_biomedica), Course(name='Chimica', year=1, degree_program=ing_biomedica), Course(name='Informatica', year=1, degree_program=ing_biomedica), Course(name='Analisi Matematica II', year=2, degree_program=ing_biomedica), Course(name='Fisica Generale II', year=2, degree_program=ing_biomedica), Course(name='Meccanica Razionale', year=2, degree_program=ing_biomedica), Course(name='Fisiologia', year=2, degree_program=ing_biomedica), Course(name='Elettrotecnica', year=2, degree_program=ing_biomedica), Course(name='Elettronica', year=2, degree_program=ing_biomedica), Course(name='Bioingegneria dei Sistemi', year=3, degree_program=ing_biomedica), Course(name='Strumentazione Biomedica', year=3, degree_program=ing_biomedica), Course(name='Elaborazione dei Segnali Biomedici', year=3, degree_program=ing_biomedica), Course(name='Modellistica e Simulazione', year=3, degree_program=ing_biomedica), Course(name='Materiali Biomedici', year=3, degree_program=ing_biomedica), Course(name='Bioetica e Legislazione', year=3, degree_program=ing_biomedica),
                ])
                db.session.commit()
                print("INIT_DB: Dati di esempio per Dipartimenti, Corsi di Laurea ed Esami aggiunti.") # LOG
            else:
                print("INIT_DB: Database già popolato con dati. Salto l'inserimento dei dati di esempio.") # LOG

            # Aggiungi un utente amministratore di esempio (se non esiste)
            if not User.query.filter_by(username='admin').first():
                print("INIT_DB: Aggiungendo utente 'admin' di esempio...") # LOG
                admin_user = User(username='admin', email='admin@example.com')
                admin_user.set_password('password') 
                db.session.add(admin_user)
                db.session.commit()
                print("INIT_DB: Utente 'admin' aggiunto.") # LOG
            else:
                print("INIT_DB: Utente 'admin' di esempio già presente.") # LOG
        except Exception as e:
            # LOG: Cattura e stampa qualsiasi errore durante il popolamento dei dati
            print(f"ERRORE INIT_DB: Errore durante il popolamento dei dati: {e}") 
            # Rilancia l'eccezione per far fallire il build, indicando il problema
            raise 

# Questo file viene eseguito direttamente.
if __name__ == '__main__':
    initialize_database()