# Usa un'immagine base Python
FROM python:3.9-slim-buster

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Copia il file requirements.txt e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice sorgente nella directory di lavoro (include app.py e init_db.py)
COPY . .

# Crea la directory 'uploads' per i file caricati (non verrà usata con S3, ma è una buona pratica)
RUN mkdir -p uploads

# NUOVA RIGA: Esegui lo script di inizializzazione del DB durante la build
# Questo script creerà le tabelle e popolerà il database SQLite.
RUN python init_db.py

