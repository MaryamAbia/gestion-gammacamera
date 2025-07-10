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

# CSS pour chaque section avec image
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f7f7;
        font-family: 'Segoe UI', sans-serif;
    }
    .section-container {
        border-radius: 15px;
        padding: 30px 40px;
        margin-bottom: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        color: black;
        background-color: rgba(255, 255, 255, 0.88);
        background-repeat: no-repeat;
        background-size: 120px 120px;
        background-position: right bottom;
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
st.title("Interface de gestion - Gamma Caméra")
st.markdown("Développée par **Maryam Abia**")

# Fonction générique pour section avec image

def section_container(key, label, content_func):
    css = f"section-container section-container-{key}"
    st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
    st.header(label)
    content_func()
    st.markdown('</div>', unsafe_allow_html=True)

# Contenus des sections

def contenu_gestion_intervenants():
    nom = st.text_input("Nom complet")
    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien", "Autre"])
    if st.button("Ajouter"):
        cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
        conn.commit()
        st.success("Ajouté")
    df = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df)

def contenu_controle_qualite():
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if intervenants:
        date = st.date_input("Date", value=datetime.now())
        type_cq = st.selectbox("Type", ["Journalier", "Hebdomadaire", "Mensuel", "Annuel"])
        intervenant = st.selectbox("Intervenant", intervenants)
        resultat = st.text_area("Résultat")
        if st.button("Enregistrer CQ"):
            cursor.execute("INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                           (date.strftime('%Y-%m-%d'), type_cq, intervenant, resultat))
            conn.commit()
            st.success("Contrôle enregistré")
    st.dataframe(pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn))

def contenu_suivi_pannes():
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    date = st.date_input("Date panne")
    desc = st.text_area("Description")
    inter = st.selectbox("Intervenant", intervenants)
    action = st.text_area("Action réalisée")
    if st.button("Ajouter panne"):
        cursor.execute("INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                       (date.strftime('%Y-%m-%d'), desc, inter, action))
        conn.commit()
        st.success("Panne ajoutée")
    st.dataframe(pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn))

def contenu_pieces_detachees():
    nom = st.text_input("Nom pièce")
    ref = st.text_input("Référence")
    date_cmd = st.date_input("Date commande")
    fournisseur = st.text_input("Fournisseur")
    date_rec = st.date_input("Date réception")
    if st.button("Ajouter pièce"):
        cursor.execute("INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                       (nom, ref, date_cmd.strftime('%Y-%m-%d'), fournisseur, date_rec.strftime('%Y-%m-%d')))
        conn.commit()
        st.success("Pièce ajoutée")
    st.dataframe(pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn))

def contenu_gestion_documents():
    nom_doc = st.text_input("Nom document")
    type_doc = st.selectbox("Type", ["Protocole", "Rapport", "Notice"])
    fichier = st.file_uploader("Téléverser")
    if fichier and st.button("Enregistrer doc"):
        blob = fichier.read()
        cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom_doc, type_doc, blob))
        conn.commit()
        st.success("Document enregistré")
    st.dataframe(pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn))

def contenu_rappels_controles():
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    if df.empty:
        st.info("Aucun contrôle enregistré.")
        return
    today = datetime.now().date()
    df['date'] = pd.to_datetime(df['date']).dt.date
    def check(type_label, freq):
        rows = df[df['type'].str.contains(type_label)]
        if not rows.empty:
            last_date = rows['date'].max()
            delta = (today - last_date).days
            if delta >= freq:
                st.warning(f"{type_label} en retard de {delta} jours")
            else:
                st.success(f"{type_label} réalisé il y a {delta} jours")
        else:
            st.error(f"Aucun {type_label} trouvé")
    check("Journalier", 1)
    check("Hebdomadaire", 7)
    check("Mensuel", 30)
    check("Annuel", 365)
    if st.button("Envoyer rappel"):
        msg = "Bonjour, ceci est un rappel pour les contrôles Gamma Caméra."
        envoyer_email("maryamabia01@gmail.com", "Rappel CQ Gamma Caméra", msg)

# Appel des sections
section_container("gestion_intervenants", "👥 Gestion des intervenants", contenu_gestion_intervenants)
section_container("controle_qualite", "🗕️ Suivi des contrôles", contenu_controle_qualite)
section_container("suivi_pannes", "🛠️ Suivi des pannes", contenu_suivi_pannes)
section_container("pieces_detachees", "🔧 Pièces détachées", contenu_pieces_detachees)
section_container("gestion_documents", "📂 Gestion documentaire", contenu_gestion_documents)
section_container("rappels_controles", "🔔 Rappels des contrôles", contenu_rappels_controles)
