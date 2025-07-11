# app.py - Interface Streamlit professionnelle (par Maryam Abia)

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

# Connexion à la base de données
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# Création des tables si elles n'existent pas
cursor.execute('''CREATE TABLE IF NOT EXISTS controle_qualite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT, type TEXT, intervenant TEXT, resultat TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS pannes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT, description TEXT, intervenant TEXT, action TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS pieces_detachees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT, ref TEXT, date_commande TEXT, fournisseur TEXT, date_reception TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT, type TEXT, fichier BLOB
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT, role TEXT
)''')
conn.commit()

# ========================= DESIGN ===============================
st.set_page_config(page_title="Interface Gamma Caméra", layout="wide")
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(to bottom, #e0f0ff, #f7faff);
    scroll-behavior: smooth;
}
.header {
    display: flex;
    align-items: center;
    background-color: #ffffffdd;
    padding: 1rem 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}
.header img {
    height: 60px;
    margin-right: 20px;
}
.section {
    padding: 2rem;
    margin-bottom: 3rem;
    background: #ffffffdd;
    border-radius: 20px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.section h2 {
    color: #1f4e79;
    font-size: 28px;
    margin-bottom: 1rem;
}
.footer {
    text-align: center;
    font-size: 14px;
    color: #666;
    margin-top: 50px;
}
</style>
""", unsafe_allow_html=True)

# ======================== HEADER ===========================
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://i.imgur.com/wH3m6Qp.png", width=60)  # Logo FMPM
with col2:
    st.markdown("""
    <div class="header">
        <h1>🎛️ Interface de gestion - Gamma Caméra</h1>
    </div>
    """, unsafe_allow_html=True)

# ======================== ACCUEIL ===========================
with st.container():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown("""
    <h2>✨ Bienvenue dans l'interface de gestion de qualité de la Gamma Caméra</h2>
    <p>Cette application a été développée par <strong>Maryam Abia</strong> (Master Biomédical, FMPM Marrakech). Elle vous permet de gérer les contrôles qualité, les pannes, la maintenance, la documentation et plus encore.</p>
    """, unsafe_allow_html=True)
    st.image("https://cdn.pixabay.com/photo/2021/10/15/11/27/mri-6710645_1280.jpg", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================== UTILISATEURS ===========================
with st.container():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("👥 Gestion des intervenants")
    with st.form("form_user"):
        nom = st.text_input("Nom complet")
        role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"])
        submit = st.form_submit_button("Ajouter")
        if submit:
            if nom.strip() == "":
                st.error("Le nom ne peut pas être vide.")
            else:
                cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
                conn.commit()
                st.success("✅ Intervenant ajouté")
                st.experimental_rerun()
    st.dataframe(pd.read_sql_query("SELECT * FROM utilisateurs ORDER BY id DESC", conn))
    st.markdown('</div>', unsafe_allow_html=True)

# ======================== CONTRÔLES ===========================
with st.container():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🗕️ Suivi des contrôles de qualité")
    intervenants = pd.read_sql_query("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("Ajoutez d'abord des intervenants.")
    else:
        with st.form("form_cq"):
            date = st.date_input("Date du contrôle", value=datetime.now())
            type_cq = st.selectbox("Type de contrôle", [
                "Journalier: Résolution", "Hebdomadaire: Stabilité", "Mensuel: Linéarité", "Annuel: Complét"
            ])
            intervenant = st.selectbox("Intervenant", intervenants)
            resultat = st.text_area("Résultat ou observation")
            submit = st.form_submit_button("Enregistrer")
            if submit:
                cursor.execute("INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                               (date.strftime('%Y-%m-%d'), type_cq, intervenant, resultat))
                conn.commit()
                st.success("✅ Contrôle enregistré")
                st.experimental_rerun()
    df = pd.read_sql_query("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
    st.dataframe(df)
    st.download_button("📅 Télécharger CSV", data=df.to_csv(index=False), file_name="controle_qualite.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# ======================== FOOTER ===========================
st.markdown("""
<div class="footer">
    <hr>
    Développé par <strong>Maryam Abia</strong> - 2025 | FMPM Marrakech
</div>
""", unsafe_allow_html=True)
