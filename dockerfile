# Usa un'immagine base Python
FROM python:3.9-slim-buster

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice sorgente nella directory di lavoro (include app.py e init_db.py)
COPY . .

# Crea la directory 'uploads' per i file caricati (Fly.io gestirà la persistenza con volumi)
RUN mkdir -p uploads

# NUOVA RIGA: Esegui lo script di inizializzazione del DB durante la build
# Questo script creerà le tabelle e popolerà il database SQLite.
RUN python init_db.py

# Espone la porta su cui l'applicazione Flask ascolterà
EXPOSE 8080

# Comando per avviare l'applicazione usando Gunicorn
# 'app:app' significa: nel file 'app.py', trova l'istanza di Flask chiamata 'app'
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]