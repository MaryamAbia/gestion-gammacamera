import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Connexion à la base de données
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# Création des tables si elles n'existent pas
cursor.execute('''CREATE TABLE IF NOT EXISTS controle_qualite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    intervenant TEXT,
    resultat TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS pannes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    description TEXT,
    intervenant TEXT,
    action TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS pieces_detachees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    ref TEXT,
    date_commande TEXT,
    fournisseur TEXT,
    date_reception TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    type TEXT,
    fichier BLOB
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    role TEXT
)''')

conn.commit()

# Fonction d'envoi d'e-mail
def envoyer_email(destinataire, sujet, message):
    sender_email = "maryamabia14@gmail.com"
    app_password = "wyva itgr vrmu keet"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = destinataire
    msg["Subject"] = sujet
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, destinataire, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        return False

# Mise en page avec background
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url('https://images.unsplash.com/photo-1588776814546-ec9c70d4987d');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding: 2rem;
        margin-top: 10px;
        color: white;
    }

    h1, h2, h3 {
        color: #ffffff;
    }

    div.stButton > button {
        background-color: #5b2a86;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1em;
        font-weight: bold;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #3e1c62;
    }

    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("\ud83c\udfa7 Interface de gestion - Gamma Caméra")
st.markdown("Développée par **Maryam Abia** – Suivi du contrôle qualité en médecine nucléaire")

# SECTION ACCUEIL
with st.expander("\ud83c\udfe0 Accueil", expanded=True):
    st.image("https://depositphotos.com/fr/photo/scientist-virologist-factory-worker-in-coverall-suit-disinfects-himself-in-decontamination-shower-chamber-biohazard-emergency-423247260.html", width=100)
    st.image("https://static9.depositphotos.com/1028436/1127/i/450/depositphotos_11273325-stock-photo-atom.jpg", use_column_width=True)
    st.write("""
    Cette interface innovante a été développée dans le cadre d’un projet de fin d’études pour suivre le contrôle de qualité de la gamma caméra.

    \u2619\ufe0f Radioprotection | \u269b\ufe0f Imagerie nucléaire | \ud83e\uddea Suivi qualité
    """)

# LES AUTRES SECTIONS KAYNA FI LCODE LI DARTI ✅
# PS : Ma-zidtch kolchi hna bach ma ykounch chi limit, 
# walakin n9dro nkemlou chi part si bghiti.

# CONTINUE...
