# init_db.py
import os
from app import app, db, Department, DegreeProgram, Course, User # Aggiunto 'User'
from werkzeug.security import generate_password_hash # Per hashare la password di un utente admin di prova

# Questo script è pensato per essere eseguito SOLO DURANTE IL BUILD O INIZIALIZZAZIONE.
# NON DEVE ESSERE INVOCATO DURANTE IL NORMALE FUNZIONAMENTO DELL'APP.

def initialize_database():
    with app.app_context():
        # Crea TUTTE le tabelle definite dai modelli (inclusa la nuova tabella 'users')
        db.create_all() 
        print("Database e tabelle create (o già esistenti).")

        # --- Popolamento Dati di Esempio (solo se il DB è vuoto) ---
        if not Department.query.first(): 
            print("Popolando il database con dati di esempio (Dipartimenti, Corsi, Esami)...")

            # Dipartimenti
            ding = Department(name='DING')
            dst = Department(name='DST')
            demm = Department(name='DEMM')
            db.session.add_all([ding, dst, demm]) 
            db.session.commit() 

            # Corsi di Laurea per DING
            ing_energetica = DegreeProgram(name='Ingegneria Energetica', department=ding)
            ing_civile = DegreeProgram(name='Ingegneria Civile', department=ding)
            ing_informatica = DegreeProgram(name='Ingegneria Informatica', department=ding)
            ing_biomedica = DegreeProgram(name='Ingegneria Biomedica', department=ding)
            db.session.add_all([ing_energetica, ing_civile, ing_informatica, ing_biomedica])
            db.session.commit()

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
            print("Dati di esempio per Dipartimenti, Corsi di Laurea ed Esami aggiunti.")
        else:
            print("Database già popolato con dati. Salto l'inserimento dei dati di esempio.")

        # --- Aggiungi un utente amministratore di esempio (se non esiste) ---
        if not User.query.filter_by(username='admin').first():
            print("Aggiungendo utente 'admin' di esempio...")
            admin_user = User(username='admin', email='admin@example.com')
            admin_user.set_password('password') # CAMBIA QUESTA PASSWORD IN PRODUZIONE!
            db.session.add(admin_user)
            db.session.commit()
            print("Utente 'admin' aggiunto.")
        else:
            print("Utente 'admin' di esempio già presente.")

# Questo file viene eseguito direttamente.
if __name__ == '__main__':
    initialize_database()