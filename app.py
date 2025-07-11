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

# Configuration Streamlit
st.set_page_config(layout="wide")
st.title("📡 Interface de gestion - Gamma Caméra")

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
        return False

# Menu principal
menu = st.sidebar.radio("Navigation", [
    "Accueil",
    "Utilisateurs",
    "Contrôles de qualité",
    "Descriptions des tests",
    "Pannes",
    "Pièces détachées",
    "Documents",
    "Analyse",
    "Rappels automatiques"
])

if menu == "Accueil":
    st.markdown("""
    ## Bienvenue 👋
    Interface complète de gestion de la gamma caméra : utilisateurs, contrôles qualité, pannes, documents, pièces détachées, rappels automatiques, et plus encore.
    Utilisez le menu à gauche pour naviguer entre les sections.
    """)

elif menu == "Utilisateurs":
    st.header("👥 Gestion des intervenants")
    with st.form("form_user"):
        nom = st.text_input("Nom complet")
        role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"])
        submit = st.form_submit_button("Ajouter")
        if submit:
            if nom.strip() != "":
                cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
                conn.commit()
                st.success("✅ Intervenant ajouté")
            else:
                st.warning("Veuillez entrer un nom.")

    st.subheader("Liste des intervenants")
    df = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df)

elif menu == "Contrôles de qualité":
    st.header("📅 Enregistrement des contrôles de qualité")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    types_tests = [
        "Linéarité",
        "Uniformité intrinsèque",
        "Résolution spatiale intrinsèque",
        "Uniformité système avec collimateur",
        "Sensibilité",
        "Résolution énergétique",
        "Centre de rotation"
    ]
    if intervenants:
        with st.form("form_cq"):
            date = st.date_input("Date", value=datetime.now())
            type_test = st.selectbox("Type de test", types_tests)
            intervenant = st.selectbox("Intervenant", intervenants)
            resultat = st.text_area("Observation / Résultat")
            submit = st.form_submit_button("Enregistrer")
            if submit:
                cursor.execute("""
                    INSERT INTO controle_qualite (date, type, intervenant, resultat)
                    VALUES (?, ?, ?, ?)
                """, (date.strftime('%Y-%m-%d'), type_test, intervenant, resultat))
                conn.commit()
                st.success("✅ Contrôle enregistré")
    else:
        st.warning("⚠️ Veuillez ajouter d'abord des intervenants.")

    st.subheader("Historique des contrôles")
    df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
    st.dataframe(df_cq)

elif menu == "Descriptions des tests":
    st.header("📖 Descriptions des tests de la gamma caméra")
    tests_info = {
        "Linéarité": {
            "fréquence": "Hebdomadaire et Semestrielle",
            "description": "Vérifie que la gamma caméra restitue correctement les formes sans distorsion."
        },
        "Uniformité intrinsèque": {
            "fréquence": "Hebdomadaire (10×10⁶ coups) et Mensuelle (200×10⁶ coups)",
            "description": "Contrôle la capacité de la gamma caméra à produire une image homogène à partir d'une source uniforme."
        },
        "Résolution spatiale intrinsèque": {
            "fréquence": "Mensuelle",
            "description": "Évalue la capacité de la gamma caméra à distinguer les détails fins (sans collimateur)."
        },
        "Uniformité système avec collimateur": {
            "fréquence": "Hebdomadaire (visuel) et Semestrielle (quantitatif)",
            "description": "Vérifie l’homogénéité de l’image produite avec collimateur."
        },
        "Sensibilité": {
            "fréquence": "Annuelle",
            "description": "Évalue la réponse du système à un radionucléide d’activité connue."
        },
        "Résolution énergétique": {
            "fréquence": "Annuelle",
            "description": "Mesure la capacité du système à distinguer les photons d’énergie proche (typiquement 10 % à 140 keV)."
        },
        "Centre de rotation": {
            "fréquence": "Tomographique (réception + périodique)",
            "description": "Évalue l’alignement correct du système lors de l’acquisition tomographique."
        }
    }
    for test, infos in tests_info.items():
        with st.container():
            st.subheader(f"🔬 {test}")
            st.markdown(f"**Fréquence :** {infos['fréquence']}")
            st.markdown(f"**Description :** {infos['description']}")
            st.markdown("---")

elif menu == "Pannes":
    st.header("🛠️ Suivi des pannes")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if intervenants:
        with st.form("form_panne"):
            date = st.date_input("Date", value=datetime.now())
            description = st.text_area("Description de la panne")
            intervenant = st.selectbox("Intervenant", intervenants)
            action = st.text_area("Action effectuée")
            submit = st.form_submit_button("Enregistrer")
            if submit:
                cursor.execute("INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                               (date.strftime('%Y-%m-%d'), description, intervenant, action))
                conn.commit()
                st.success("✅ Panne enregistrée")
    else:
        st.warning("Ajoutez d'abord des intervenants.")

    st.subheader("Historique des pannes")
    df = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
    st.dataframe(df)

elif menu == "Pièces détachées":
    st.header("🔧 Gestion des pièces détachées")
    with st.form("form_piece"):
        nom = st.text_input("Nom de la pièce")
        ref = st.text_input("Référence")
        date_commande = st.date_input("Date de commande")
        fournisseur = st.text_input("Fournisseur")
        date_reception = st.date_input("Date de réception")
        submit = st.form_submit_button("Enregistrer")
        if submit:
            cursor.execute("INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                           (nom, ref, date_commande.strftime('%Y-%m-%d'), fournisseur, date_reception.strftime('%Y-%m-%d')))
            conn.commit()
            st.success("✅ Pièce enregistrée")

    st.subheader("Historique des pièces")
    df = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    st.dataframe(df)

elif menu == "Documents":
    st.header("📂 Gestion des documents")
    with st.form("form_doc"):
        nom = st.text_input("Nom du document")
        type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"])
        fichier = st.file_uploader("Fichier", type=["pdf", "docx", "png", "jpg"])
        submit = st.form_submit_button("Enregistrer")
        if submit and fichier:
            blob = fichier.read()
            cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom, type_doc, blob))
            conn.commit()
            st.success("✅ Document enregistré")

    st.subheader("Liste des documents")
    df = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df)

elif menu == "Analyse":
    st.header("📊 Analyse des données")
    df_cq = pd.read_sql("SELECT * FROM controle_qualite", conn)
    if not df_cq.empty:
        fig = px.histogram(df_cq, x="type", color="type", title="Nombre de contrôles par type")
        st.plotly_chart(fig)

    df_pannes = pd.read_sql("SELECT * FROM pannes", conn)
    if not df_pannes.empty:
        df_pannes['date'] = pd.to_datetime(df_pannes['date'])
        freq = df_pannes.groupby(df_pannes['date'].dt.to_period('M')).size().reset_index(name='Nombre')
        freq['date'] = freq['date'].astype(str)
        fig = px.bar(freq, x='date', y='Nombre', title="Fréquence des pannes par mois")
        st.plotly_chart(fig)

elif menu == "Rappels automatiques":
    st.header("🔔 Rappels des contrôles qualité")
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    if df.empty:
        st.warning("Aucun contrôle enregistré.")
    else:
        df['date'] = pd.to_datetime(df['date']).dt.date
        today = datetime.now().date()

        freqs = {
            "Linéarité": 7,
            "Uniformité intrinsèque": 7,
            "Résolution spatiale intrinsèque": 30,
            "Uniformité système avec collimateur": 7,
            "Sensibilité": 365,
            "Résolution énergétique": 365,
            "Centre de rotation": 180
        }

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

        if st.button("📧 Envoyer rappel par e-mail"):
            msg = "Ceci est un rappel automatique pour effectuer les contrôles qualité de la gamma caméra."
            sent = envoyer_email("maryamabia01@gmail.com", "Rappel des contrôles qualité", msg)
            if sent:
                st.success("📨 E-mail envoyé avec succès !")
            else:
                st.error("Erreur lors de l'envoi de l'e-mail.")
