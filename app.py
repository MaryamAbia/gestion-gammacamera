import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
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

# Email function
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

# CSS for big images, spacing, fonts
st.markdown("""
<style>
    .stApp {
        padding: 0 40px 50px 40px !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 18px !important;
        background-color: #f7f7f7;
    }
    .banner {
        position: relative;
        width: 100%;
        height: 350px !important;
        border-radius: 12px;
        margin-bottom: 40px !important;
        overflow: hidden;
    }
    .banner img {
        width: 100%;
        height: 100% !important;
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
        background-color: rgba(255, 255, 255, 0.85);
        padding: 30px 50px;
        border-radius: 15px;
        color: #1f005c;
        text-align: center;
        font-size: 36px !important;
        font-weight: 700;
        animation: fadeIn 2s ease-in-out;
        max-width: 900px;
        margin: auto;
        top: 50%;
        transform: translateY(-50%);
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    .section-container {
        border-radius: 30px;
        padding: 80px 60px 70px 60px !important;
        margin-bottom: 70px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        color: black;
        background-color: rgba(255, 255, 255, 0.9);
        background-repeat: no-repeat;
        background-size: cover;
        background-position: center;
    }
    .section-title {
        font-size: 32px !important;
        margin-bottom: 25px !important;
        font-weight: 700;
        color: #1f005c;
        text-align: center;
    }
    .section-image {
        max-height: 400px !important;
        width: 100%;
        margin-bottom: 40px !important;
        border-radius: 15px;
        object-fit: cover;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .dataframe-container {
        margin-top: 30px !imp
