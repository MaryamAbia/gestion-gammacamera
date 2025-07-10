import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Connexion base de données
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# Création des tables
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

# Email
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
        st.error(f"Erreur email : {e}")
        return False

# CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f7f7;
        font-family: 'Segoe UI', sans-serif;
    }
    .banner {
        position: relative;
        width: 100%;
        height: 250px;
        background-color: white;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .banner img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 12px;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 0;
    }
    .banner-text {
        position: relative;
        z-index: 1;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px 40px;
        border-radius: 10px;
        color: #1f005c;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        animation: fadeIn 2s ease-in-out;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    .section-container {
        border-radius: 15px;
        padding: 70px 40px;
        margin-bottom: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        color: black;
        background-color: rgba(255, 255, 255, 0.85);
        background-repeat: no-repeat;
        background-size: cover;
        background-position: center;
    }
    .section-container-gestion_intervenants {
        background-image: url('https://cdn-icons-png.flaticon.com/512/3135/3135715.png');
    }
    .section-container-controle_qualite {
        background-image: url('https://cdn-icons-png.flaticon.com/512/889/889392.png');
    }
    .section-container-suivi_pannes {
        background-image: url('https://cdn-icons-png.flaticon.com/512/564/564619.png');
    }
    .section-container-pieces_detachees {
        background-image: url('https://cdn-icons-png.flaticon.com/512/2983/2983462.png');
    }
    .section-container-gestion_documents {
        background-image: url('https://cdn-icons-png.flaticon.com/512/3221/3221823.png');
    }
    .section-container-rappels_controles {
        background-image: url('https://cdn-icons-png.flaticon.com/512/597/597177.png');
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")
st.markdown("""
<div class="banner">
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQM-dBRMUkW1hvMqfePbhnc2qzNIqEb2ivYV2F4BKLx963SrQ23JS6zvTthRjBlzImiRLY&usqp=CAU" alt="banner" />
    <div class="banner-text">Bienvenue dans l'interface de gestion - Gamma Caméra</div>
</div>
""", unsafe_allow_html=True)
st.markdown("Développée par **Maryam Abia**")

# Fonction générique pour section

def section_container(key, label, content_func):
    css = f"section-container section-container-{key}"
    st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
    st.header(label)
    content_func()
    st.markdown('</div>', unsafe_allow_html=True)

# Contenus des sections

# ... (reste du code inchangé, tes fonctions contenu_* restent les mêmes)

# Appel des sections
section_container("gestion_intervenants", "👥 Gestion des intervenants", contenu_gestion_intervenants)
section_container("controle_qualite", "🗕️ Suivi des contrôles", contenu_controle_qualite)
section_container("suivi_pannes", "🛠️ Suivi des pannes", contenu_suivi_pannes)
section_container("pieces_detachees", "🔧 Pièces détachées", contenu_pieces_detachees)
section_container("gestion_documents", "📂 Gestion documentaire", contenu_gestion_documents)
section_container("rappels_controles", "🔔 Rappels des contrôles", contenu_rappels_controles)
