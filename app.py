import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(layout="wide")

conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS controle_qualite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    intervenant TEXT,
    resultat TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    role TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS pannes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    description TEXT,
    intervenant TEXT,
    action TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    type TEXT,
    fichier BLOB
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS pieces_detachees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    ref TEXT,
    date_commande TEXT,
    fournisseur TEXT,
    date_reception TEXT
)''')

conn.commit()

st.markdown("""
    <style>
        .stApp { font-family: 'Segoe UI', sans-serif; background-color: #f4f6fa; }
        .banner {
            width: 100%; height: 200px; margin-bottom: 20px; position: relative;
            background: url('https://img.freepik.com/premium-photo/chemical-molecule-with-blue-background-3d-rendering_772449-4288.jpg') no-repeat center;
            background-size: cover; display: flex; align-items: center; justify-content: center;
            border-radius: 12px;
        }
        .banner h1 {
            background-color: rgba(255,255,255,0.9); padding: 20px 40px; border-radius: 8px;
            color: #003366; font-size: 36px;
        }
        .section-title {
            font-size: 26px; margin-top: 30px; color: #002244;
        }
        .divider {
            height: 2px; background-color: #ccc; margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
    <h1>Interface de Gestion - Gamma Caméra</h1>
</div>
""", unsafe_allow_html=True)

page = st.selectbox("Menu", [
    "Accueil", "Utilisateurs", "Contrôle Qualité", "Pannes",
    "Pièces Détachées", "Documents", "Statistiques", "Rappels"
])

if page == "Accueil":
    st.subheader("Bienvenue dans l'interface de gestion Gamma Caméra")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown("### [Utilisateurs]")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/4320/4320337.png", width=100)
        st.markdown("### [Contrôles Qualité]")
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/8375/8375938.png", width=100)
        st.markdown("### [Statistiques]")

elif page == "Utilisateurs":
    st.subheader("👥 Gestion des utilisateurs")
    with st.form("ajout_utilisateur"):
        nom = st.text_input("Nom")
        role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical"])
        if st.form_submit_button("Ajouter"):
            if nom:
                cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
                conn.commit()
                st.success("Utilisateur ajouté")
    df = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df)

elif page == "Contrôle Qualité":
    st.subheader("🧪 Enregistrement Contrôles Qualité")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    with st.form("form_cq"):
        date = st.date_input("Date", value=datetime.now())
        type_test = st.selectbox("Type", [
            "Journalier", "Hebdomadaire", "Mensuel", "Annuel"
        ])
        intervenant = st.selectbox("Intervenant", intervenants)
        resultat = st.text_area("Observation")
        if st.form_submit_button("Enregistrer"):
            cursor.execute("INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                           (date.strftime('%Y-%m-%d'), type_test, intervenant, resultat))
            conn.commit()
            st.success("Contrôle enregistré")
    st.markdown("### Historique")
    df = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
    st.dataframe(df)

elif page == "Pannes":
    st.subheader("🛠️ Suivi des pannes")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    with st.form("form_panne"):
        date = st.date_input("Date", value=datetime.now())
        desc = st.text_area("Description")
        inter = st.selectbox("Intervenant", intervenants)
        action = st.text_area("Action effectuée")
        if st.form_submit_button("Enregistrer"):
            cursor.execute("INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                           (date.strftime('%Y-%m-%d'), desc, inter, action))
            conn.commit()
            st.success("Panne enregistrée")
    df = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
    st.dataframe(df)

elif page == "Pièces Détachées":
    st.subheader("🔧 Gestion des pièces détachées")
    with st.form("form_piece"):
        nom = st.text_input("Nom pièce")
        ref = st.text_input("Référence")
        date_cmd = st.date_input("Date de commande")
        fournisseur = st.text_input("Fournisseur")
        date_rec = st.date_input("Date de réception")
        if st.form_submit_button("Enregistrer"):
            cursor.execute("INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                           (nom, ref, date_cmd.strftime('%Y-%m-%d'), fournisseur, date_rec.strftime('%Y-%m-%d')))
            conn.commit()
            st.success("Pièce enregistrée")
    df = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    st.dataframe(df)

elif page == "Documents":
    st.subheader("📁 Gestion documentaire")
    with st.form("form_doc"):
        nom = st.text_input("Nom document")
        type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice"])
        fichier = st.file_uploader("Fichier")
        if st.form_submit_button("Enregistrer") and fichier:
            blob = fichier.read()
            cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom, type_doc, blob))
            conn.commit()
            st.success("Document ajouté")
    df = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df)

elif page == "Statistiques":
    st.subheader("📊 Statistiques des contrôles")
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    summary = df['type'].value_counts().reset_index()
    summary.columns = ["Type de contrôle", "Nombre"]
    st.dataframe(summary)

elif page == "Rappels":
    st.subheader("🔔 Rappels")
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    df['date'] = pd.to_datetime(df['date']).dt.date
    today = datetime.now().date()
    freqs = {"Journalier": 1, "Hebdomadaire": 7, "Mensuel": 30, "Annuel": 365}
    for test, jours in freqs.items():
        filt = df[df['type'] == test]
        if not filt.empty:
            last = filt['date'].max()
            delta = (today - last).days
            if delta > jours:
                st.warning(f"⏰ {test} en retard ({delta} jours)")
            else:
                st.success(f"✅ {test} à jour ({delta} jours)")
        else:
            st.error(f"❌ Aucun {test} enregistré")
