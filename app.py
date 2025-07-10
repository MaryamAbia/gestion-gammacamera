import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration de la page
st.set_page_config(layout="wide", page_title="Gestion Gamma Caméra", page_icon="🧪")

# Message d'accueil animé
st.markdown("""
    <div style="text-align: center; padding: 60px 20px; background-color: #eaf4ff; border-radius: 12px; margin-bottom: 40px; animation: fadeIn 2s ease-in-out;">
        <h1 style="color: #0a2c5e; font-size: 48px; margin-bottom: 20px;">Bienvenue dans l'interface de gestion de la qualité</h1>
        <p style="font-size: 22px; color: #1a1a1a; max-width: 800px; margin: 0 auto;">
            Cet espace a été conçu pour faciliter le suivi, la traçabilité et l'optimisation des activités liées à la gamma caméra
            en médecine nucléaire. Vous pouvez gérer les intervenants, les contrôles de qualité, les pannes, la documentation
            ainsi que les pièces détachées de manière intuitive et professionnelle.
        </p>
    </div>
""", unsafe_allow_html=True)

# Connexion à la base de données
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# Création des tables si non existantes
cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (id INTEGER PRIMARY KEY, nom TEXT, role TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS controle_qualite (id INTEGER PRIMARY KEY, date TEXT, type TEXT, intervenant TEXT, resultat TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS pannes (id INTEGER PRIMARY KEY, date TEXT, description TEXT, intervenant TEXT, action TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS pieces_detachees (id INTEGER PRIMARY KEY, nom TEXT, ref TEXT, date_commande TEXT, fournisseur TEXT, date_reception TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, nom TEXT, type TEXT, fichier BLOB)''')
conn.commit()

# Email

def envoyer_email(destinataire, sujet, message):
    sender_email = "maryamabia14@gmail.com"
    app_password = "your_app_password_here"
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
    .section {
        padding: 80px 40px;
        margin-bottom: 60px;
        border-radius: 24px;
        background-size: cover;
        background-position: center;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        animation: fadeInUp 1.2s ease-in-out;
    }
    .title {
        text-align: center;
        font-size: 42px;
        margin-bottom: 40px;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4);
        animation: fadeIn 2s ease-in-out;
    }
    @keyframes fadeInUp {
        from {opacity: 0; transform: translateY(30px);}
        to {opacity: 1; transform: translateY(0);}
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
""", unsafe_allow_html=True)

# Section Helper

def section(title, bg_url, func):
    st.markdown(f"""
        <div class='section' style="background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('{bg_url}');">
        <div class='title'>{title}</div>
    """, unsafe_allow_html=True)
    func()
    st.markdown("</div>", unsafe_allow_html=True)

# Fonctions des sections

def gestion_utilisateurs():
    nom = st.text_input("Nom complet")
    role = st.selectbox("Rôle", ["Technicien", "Médecin", "Ingénieur", "Autre"])
    if st.button("Ajouter"):
        if nom:
            cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
            conn.commit()
            st.success("Ajouté")
    df = pd.read_sql("SELECT * FROM utilisateurs", conn)
    st.dataframe(df)

def suivi_qualite():
    users = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if users:
        date = st.date_input("Date", value=datetime.now())
        type_cq = st.selectbox("Type", ["Journalier", "Hebdomadaire", "Mensuel", "Annuel"])
        user = st.selectbox("Intervenant", users)
        result = st.text_area("Résultat")
        if st.button("Enregistrer contrôle"):
            cursor.execute("INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                           (date.strftime('%Y-%m-%d'), type_cq, user, result))
            conn.commit()
            st.success("Contrôle enregistré")
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    st.dataframe(df)

    st.markdown("---")
    st.subheader("🔔 Rappel de contrôle")
    df['date'] = pd.to_datetime(df['date']).dt.date
    today = datetime.now().date()
    for label, days in {"Journalier": 1, "Hebdomadaire": 7, "Mensuel": 30, "Annuel": 365}.items():
        filt = df[df['type'].str.contains(label)]
        if not filt.empty:
            delta = (today - max(filt['date'])).days
            if delta >= days:
                st.warning(f"❗ Contrôle {label.lower()} en retard depuis {delta} jours")
            else:
                st.success(f"✅ Contrôle {label.lower()} effectué il y a {delta} jours")
        else:
            st.error(f"❌ Aucun contrôle {label.lower()} enregistré")

    if st.button("✉️ Envoyer rappel par e-mail"):
        if envoyer_email("maryamabia01@gmail.com", "Rappel Gamma Caméra", "Merci de faire les contrôles qualité."):
            st.success("E-mail envoyé")
        else:
            st.error("Erreur lors de l'envoi")

def suivi_pannes():
    users = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    date = st.date_input("Date")
    desc = st.text_area("Description")
    user = st.selectbox("Intervenant", users)
    action = st.text_area("Action")
    if st.button("Enregistrer panne"):
        cursor.execute("INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                       (date.strftime('%Y-%m-%d'), desc, user, action))
        conn.commit()
        st.success("Panne enregistrée")
    df = pd.read_sql("SELECT * FROM pannes", conn)
    st.dataframe(df)

def gestion_pieces():
    nom = st.text_input("Nom pièce")
    ref = st.text_input("Référence")
    cmd = st.date_input("Date commande")
    fournisseur = st.text_input("Fournisseur")
    rec = st.date_input("Date réception")
    if st.button("Ajouter pièce"):
        cursor.execute("INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                       (nom, ref, cmd.strftime('%Y-%m-%d'), fournisseur, rec.strftime('%Y-%m-%d')))
        conn.commit()
        st.success("Pièce enregistrée")
    df = pd.read_sql("SELECT * FROM pieces_detachees", conn)
    st.dataframe(df)

def gestion_docs():
    nom = st.text_input("Nom document")
    type_doc = st.selectbox("Type", ["Protocole", "Rapport", "Notice"])
    fichier = st.file_uploader("Fichier")
    if fichier and st.button("Enregistrer doc"):
        cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)",
                       (nom, type_doc, fichier.read()))
        conn.commit()
        st.success("Document enregistré")
    df = pd.read_sql("SELECT id, nom, type FROM documents", conn)
    st.dataframe(df)

# Backgrounds
bg_utilisateurs = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Nuclear_medicine_imaging.jpg/1280px-Nuclear_medicine_imaging.jpg"
bg_qualite = "https://cdn.sanity.io/images/0vv8moc6/rd-website/674f25a916bc2fcff7bb7cf309f48cf889eeaf2f-1000x667.jpg"
bg_pannes = "https://www.sciencedirect.com/science/article/pii/S2212958821000114/fx1_lrg.jpg"
bg_pieces = "https://media.springernature.com/full/springer-static/image/art%3A10.1007%2Fs00259-019-04538-7/MediaObjects/259_2019_4538_Fig1_HTML.png"
bg_docs = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Technetium_generator.jpg/1200px-Technetium_generator.jpg"

# Affichage par section avec images mises à jour
section("👥 Gestion des intervenants", bg_utilisateurs, gestion_utilisateurs)
section("📋 Suivi des contrôles qualité", bg_qualite, suivi_qualite)
section("🛠️ Suivi des pannes", bg_pannes, suivi_pannes)
section("🔧 Pièces détachées", bg_pieces, gestion_pieces)
section("📂 Gestion des documents", bg_docs, gestion_docs)

st.markdown("""<hr style='border: none; height: 2px; background: #666; margin-top: 60px;'>
<p style='text-align:center;'>Développée par <strong>Maryam Abia</strong></p>""", unsafe_allow_html=True)
