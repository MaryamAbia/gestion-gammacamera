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

# Configuration de la page
st.set_page_config(layout="wide")

# Style CSS avec image de fond
st.markdown("""
    <style>
    body {
        background-image: url('https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.cmn-lescedres.com%2Fexamens%2Fosseuse%2F&psig=AOvVaw0CAMwJ_J-oqaKvMnD5xHdM&ust=1752237053807000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCKCnopmmso4DFQAAAAAdAAAAABAT');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
    }

    .block-container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 3rem 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    h1 {
        color: #0d47a1;
        font-weight: 700;
        font-size: 2.8rem;
    }

    h2, h3 {
        color: #1565c0;
    }

    div.stButton > button {
        background-color: #1565c0;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        font-size: 1rem;
        border: none;
        transition: 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #003c8f;
        transform: scale(1.02);
        cursor: pointer;
    }

    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

# Titre principal
st.title("🎛️ Interface de gestion - Gamma Caméra")
st.markdown("Développée par **Maryam Abia** – Suivi du contrôle qualité en médecine nucléaire")

# --- Accueil ---
with st.expander("🏠 Accueil", expanded=True):
    st.image("https://cdn-icons-png.flaticon.com/512/2872/2872613.png", width=100)
    st.write("""
    Cette interface innovante a été développée dans le cadre d’un projet de fin d’études pour suivre le contrôle de qualité de la gamma caméra.
    ☢️ Radioprotection | ⚛️ Imagerie nucléaire | 🧪 Suivi qualité
    """)

# --- Utilisateurs ---
with st.expander("👥 Gestion des intervenants"):
    nom = st.text_input("Nom complet", key="nom_utilisateur")
    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"], key="role_utilisateur")
    if st.button("Ajouter l'intervenant", key="btn_ajouter_utilisateur"):
        if nom:
            cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
            conn.commit()
            st.success("Intervenant ajouté")
    df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df_users)

# --- Contrôles qualité ---
with st.expander("📅 Suivi des contrôles de qualité"):
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if intervenants:
        date = st.date_input("Date du contrôle", value=datetime.now(), key="date_controle")
        type_cq = st.selectbox("Type de contrôle", ["Journalier: Résolution", "Hebdomadaire: Stabilisé", "Mensuel: Linéarité", "Annuel: Complèt"], key="type_controle")
        intervenant = st.selectbox("Intervenant", intervenants, key="intervenant_controle")
        resultat = st.text_area("Résultat ou observation", key="resultat_controle")
        if st.button("Enregistrer le contrôle", key="btn_enregistrer_controle"):
            cursor.execute("INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                           (date.strftime('%Y-%m-%d'), type_cq, intervenant, resultat))
            conn.commit()
            st.success("Contrôle enregistré")
    df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
    st.dataframe(df_cq)

# --- Pannes ---
with st.expander("🛠️ Suivi des pannes"):
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    date = st.date_input("Date panne", key="date_panne")
    desc = st.text_area("Description", key="desc_panne")
    inter = st.selectbox("Intervenant", intervenants, key="intervenant_panne")
    action = st.text_area("Action réalisée", key="action_panne")
    if st.button("Enregistrer panne", key="btn_enregistrer_panne"):
        cursor.execute("INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                       (date.strftime('%Y-%m-%d'), desc, inter, action))
        conn.commit()
        st.success("Panne enregistrée")
    df_pannes = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
    st.dataframe(df_pannes)

# --- Pièces détachées ---
with st.expander("🔧 Pièces détachées"):
    nom_piece = st.text_input("Nom pièce", key="nom_piece")
    ref = st.text_input("Référence", key="ref_piece")
    date_cmd = st.date_input("Date commande", key="date_cmd_piece")
    fournisseur = st.text_input("Fournisseur", key="fournisseur_piece")
    date_rec = st.date_input("Date réception", key="date_rec_piece")
    if st.button("Ajouter pièce", key="btn_ajouter_piece"):
        cursor.execute("INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                       (nom_piece, ref, date_cmd.strftime('%Y-%m-%d'), fournisseur, date_rec.strftime('%Y-%m-%d')))
        conn.commit()
        st.success("Pièce ajoutée")
    df_pieces = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    st.dataframe(df_pieces)

# --- Documents ---
with st.expander("📂 Gestion documentaire"):
    nom_doc = st.text_input("Nom du document", key="nom_doc")
    type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"], key="type_doc")
    fichier = st.file_uploader("Téléverser un fichier", key="file_uploader")
    if fichier and st.button("Enregistrer document", key="btn_enregistrer_doc"):
        blob = fichier.read()
        cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom_doc, type_doc, blob))
        conn.commit()
        st.success("Document enregistré")
    df_docs = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df_docs)

# --- Analyse ---
with st.expander("📊 Analyse"):
    df_cq = pd.read_sql("SELECT * FROM controle_qualite", conn)
    if not df_cq.empty:
        fig1 = px.histogram(df_cq, x="type", color="type", title="Nombre de contrôles par type")
        st.plotly_chart(fig1)

    df_p = pd.read_sql("SELECT * FROM pannes", conn)
    if not df_p.empty:
        df_p['date'] = pd.to_datetime(df_p['date'])
        grouped = df_p.groupby(df_p['date'].dt.to_period("M")).size().reset_index(name="Nombre")
        grouped['date'] = grouped['date'].astype(str)
        fig2 = px.bar(grouped, x="date", y="Nombre", title="Pannes par mois")
        st.plotly_chart(fig2)

# --- Rappels ---
with st.expander("🔔 Rappels des contrôles"):
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    today = datetime.now().date()
    df['date'] = pd.to_datetime(df['date']).dt.date
    def check_due(df, type_label, freq_days):
        filt = df[df['type'].str.contains(type_label)]
        if not filt.empty:
            last_date = filt['date'].max()
            delta = (today - last_date).days
            if delta >= freq_days:
                st.warning(f"⏰ Contrôle {type_label.lower()} en retard ({delta} jours)")
            else:
                st.success(f"✅ Contrôle {type_label.lower()} fait il y a {delta} jours")
        else:
            st.error(f"❌ Aucun contrôle {type_label.lower()}")
    check_due(df, "Journalier", 1)
    check_due(df, "Hebdomadaire", 7)
    check_due(df, "Mensuel", 30)
    check_due(df, "Annuel", 365)

    if st.button("Envoyer un e-mail de rappel", key="btn_envoyer_rappel"):
        msg = "Bonjour, ceci est un rappel pour effectuer les contrôles Gamma Caméra."
        if envoyer_email("maryamabia01@gmail.com", "Rappel Gamma Caméra", msg):
            st.success("E-mail envoyé")
        else:
            st.error("Erreur lors de l'envoi")
