import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --------------------------------------
# Connexion à la base de données SQLite
# Cette base contient toutes les données de l'application (contrôles, pannes, utilisateurs, etc.)
# --------------------------------------
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# --------------------------------------
# Création des tables SQLite si elles n'existent pas encore
# Chaque table correspond à une fonctionnalité de gestion
# --------------------------------------

# Table des contrôles de qualité (date, type, intervenant, résultat)
cursor.execute('''CREATE TABLE IF NOT EXISTS controle_qualite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    intervenant TEXT,
    resultat TEXT
)''')

# Table des pannes et maintenance (date, description, intervenant, action réalisée)
cursor.execute('''CREATE TABLE IF NOT EXISTS pannes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    description TEXT,
    intervenant TEXT,
    action TEXT
)''')

# Table des pièces détachées (nom, référence, dates commande et réception, fournisseur)
cursor.execute('''CREATE TABLE IF NOT EXISTS pieces_detachees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    ref TEXT,
    date_commande TEXT,
    fournisseur TEXT,
    date_reception TEXT
)''')

# Table des documents (nom, type, fichier stocké en BLOB)
cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    type TEXT,
    fichier BLOB
)''')

# Table des utilisateurs / intervenants (nom, rôle)
cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    role TEXT
)''')

conn.commit()  # Enregistrer toutes les modifications dans la base

# --------------------------------------
# Fonction pour envoyer des emails via SMTP Gmail
# --------------------------------------
def envoyer_email(destinataire, sujet, message):
    sender_email = "maryamabia14@gmail.com"  # Adresse email de l'expéditeur
    app_password = "wyva itgr vrmu keet"  # Mot de passe d'application Gmail (App Password)

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = destinataire
    msg["Subject"] = sujet
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # Connexion sécurisée au serveur SMTP Gmail
        server.login(sender_email, app_password)  # Connexion avec l'adresse et mot de passe d'application
        server.sendmail(sender_email, destinataire, msg.as_string())  # Envoi de l'email
        server.quit()  # Fermeture de la connexion SMTP
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        return False

# --------------------------------------
# Fonction simple de connexion (login)
# Ici, c'est un login statique avec username="admin" et password="1234"
# Vous pouvez améliorer pour gérer plusieurs utilisateurs plus tard
# --------------------------------------
def login():
    st.title("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

# --------------------------------------
# Vérification de l'état de connexion dans la session
# Si l'utilisateur n'est pas connecté, afficher le formulaire de login et stopper l'app
# --------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# --------------------------------------
# Barre latérale (Sidebar) : menu de navigation
# Affichage du logo et choix de la page à afficher
# --------------------------------------
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Medical_Symbol.svg/2048px-Medical_Symbol.svg.png",
    width=80
)
st.sidebar.title("📋 Menu")
page = st.sidebar.radio("Aller vers :", [
    "Accueil",
    "Utilisateurs",
    "Contrôles de qualité",
    "Pannes et Maintenance",
    "Pièces détachées",
    "Documents",
    "Analyse",
    "Téléchargement des données",
    "Rappels de contrôles"
])

# --------------------------------------
# Style CSS simple pour la zone principale (fond gris clair + arrondi + police)
# --------------------------------------
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        font-family: Arial, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main">', unsafe_allow_html=True)

# --------------------------------------
# PAGE D'ACCUEIL
# --------------------------------------
if page == "Accueil":
    st.title("📡 Interface de gestion - Gamma Caméra")
    st.markdown("""
    Bienvenue dans l'interface de gestion dédiée au suivi de la gamma caméra.  
    Utilisez le menu à gauche pour naviguer entre les différentes fonctionnalités.
    """)

# --------------------------------------
# PAGE GESTION DES UTILISATEURS / INTERVENANTS
# --------------------------------------
elif page == "Utilisateurs":
    st.title("👥 Gestion des intervenants")

    # Formulaire pour ajouter un nouvel intervenant
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
                st.experimental_rerun()  # Rafraîchir la page pour afficher la liste mise à jour

    # Affichage de la liste des intervenants existants
    st.subheader("Liste des intervenants")
    df = pd.read_sql_query("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df)

# --------------------------------------
# PAGE CONTRÔLES DE QUALITÉ
# --------------------------------------
elif page == "Contrôles de qualité":
    st.title("📅 Suivi des contrôles de qualité")

    # Récupérer la liste des intervenants pour les proposer dans la liste déroulante
    intervenants = pd.read_sql_query("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("⚠️ Ajoutez d'abord des intervenants dans la section 'Utilisateurs'.")
    else:
        with st.form("form_cq"):
            date = st.date_input("Date du contrôle", value=datetime.now())
            type_cq = st.selectbox("Type de contrôle", [
                "Journalier: Résolution",
                "Hebdomadaire: Stabilisé",
                "Mensuel: Linéarité",
                "Annuel: Complèt"
            ])
            intervenant = st.selectbox("Intervenant", intervenants)
            resultat = st.text_area("Résultat ou observation")
            submit = st.form_submit_button("Enregistrer")
            if submit:
                cursor.execute(
                    "INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                    (date.strftime('%Y-%m-%d'), type_cq, intervenant, resultat)
                )
                conn.commit()
                st.success("✅ Contrôle enregistré")
                st.experimental_rerun()

        # Affichage de l'historique des contrôles
        st.subheader("Historique des contrôles")
        df = pd.read_sql_query("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
        st.dataframe(df)
        st.download_button(
            "📥 Télécharger CSV",
            data=df.to_csv(index=False),
            file_name="controle_qualite.csv",
            mime="text/csv"
        )

# --------------------------------------
# PAGE PANNES ET MAINTENANCE
# --------------------------------------
elif page == "Pannes et Maintenance":
    st.title("🛠️ Suivi des pannes et maintenance")

    intervenants = pd.read_sql_query("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("⚠️ Ajoutez d'abord des intervenants dans la section 'Utilisateurs'.")
    else:
        with st.form("form_panne"):
            date = st.date_input("Date de l'incident", value=datetime.now())
            description = st.text_area("Description de la panne")
            intervenant = st.selectbox("Intervenant", intervenants)
            action = st.text_area("Action ou réparation effectuée")
            submit = st.form_submit_button("Enregistrer")
            if submit:
                cursor.execute(
                    "INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                    (date.strftime('%Y-%m-%d'), description, intervenant, action)
                )
                conn.commit()
                st.success("✅ Panne enregistrée")
                st.experimental_rerun()

        st.subheader("Historique des pannes")
        df = pd.read_sql_query("SELECT * FROM pannes ORDER BY date DESC", conn)
        st.dataframe(df)
        st.download_button(
            "📥 Télécharger CSV",
            data=df.to_csv(index=False),
            file_name="pannes.csv",
            mime="text/csv"
        )

# --------------------------------------
# PAGE PIÈCES DÉTACHÉES
# --------------------------------------
elif page == "Pièces détachées":
    st.title("🔧 Suivi des pièces détachées")

    with st.form("form_piece"):
        nom = st.text_input("Nom de la pièce")
        ref = st.text_input("Référence")
        date_commande = st.date_input("Date de commande")
        fournisseur = st.text_input("Fournisseur")
        date_reception = st.date_input("Date de réception (prévue ou réelle)")
        submit = st.form_submit_button("Enregistrer")
        if submit:
            cursor.execute(
                "INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                (nom, ref, date_commande.strftime('%Y-%m-%d'), fournisseur, date_reception.strftime('%Y-%m-%d'))
            )
            conn.commit()
            st.success("✅ Pièce enregistrée")
            st.experimental_rerun()

    st.subheader("Historique des pièces détachées")
    df = pd.read_sql_query("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    st.dataframe(df)
    st.download_button(
        "📥 Télécharger CSV",
        data=df.to_csv(index=False),
        file_name="pieces_detachees.csv",
        mime="text/csv"
    )


# PAGE DOCUMENTS

elif page == "Documents":
    st.title("📂 Gestion documentaire")

    with st.form("form_doc"):
        nom = st.text_input("Nom du document")
        type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"])
        fichier = st.file_uploader("Téléverser un fichier", type=["pdf", "docx", "png", "jpg"])
        submit = st.form_submit_button("Enregistrer")
        if submit and fichier is not None:
            blob = fichier.read()
            cursor.execute(
                "INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)",
                (nom, type_doc, blob)
            )
            conn.commit()
            st.success("✅ Document enregistré")
            st.experimental_rerun()

    st.subheader("Liste des documents")
    df = pd.read_sql_query("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df)

# --------------------------------------
# PAGE ANALYSE
# --------------------------------------
elif page == "Analyse":
    st.title("📊 Analyse des données")

    # Analyse des contrôles de qualité par type
    df_cq = pd.read_sql_query("SELECT * FROM controle_qualite", conn)
    if not df_cq.empty:
        fig_cq = px.histogram(df_cq, x="type", color="type", title="Nombre de contrôles par type")
        st.plotly_chart(fig_cq)

    # Analyse des pannes par mois
    df_pannes = pd.read_sql_query("SELECT * FROM pannes", conn)
    if not df_pannes.empty:
        df_pannes['date'] = pd.to_datetime(df_pannes['date'])
        pannes_par_mois = df_pannes.groupby(df_pannes['date'].dt.to_period('M')).size().reset_index(name='Nombre')
        pannes_par_mois['date'] = pannes_par_mois['date'].astype(str)
        fig_pannes = px.bar(pannes_par_mois, x='date', y='Nombre', title="Fréquence des pannes par mois")
        st.plotly_chart(fig_pannes)

# --------------------------------------
# PAGE TÉLÉCHARGEMENT GLOBAL DES DONNÉES
# --------------------------------------
elif page == "Téléchargement des données":
    st.title("📥 Exportation globale des données")
    tables = {
        "Contrôles de qualité": "controle_qualite",
        "Pannes": "pannes",
        "Pièces détachées": "pieces_detachees",
        "Utilisateurs": "utilisateurs"
    }

    # Pour chaque table, permettre le téléchargement au format CSV
    for label, table in tables.items():
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        csv = df.to_csv(index=False)
        st.download_button(f"📁 Télécharger - {label}", data=csv, file_name=f"{table}.csv", mime="text/csv")

# --------------------------------------
# PAGE RAPPELS DE CONTRÔLES
# Vérifie les derniers contrôles effectués par type
# Alerte si un contrôle est en retard selon sa fréquence (ex: journalier = 1 jour max)

elif page == "Rappels de contrôles":
    st.title("🔔 Rappels des contrôles")

    today = datetime.now().date()
    df = pd.read_sql_query("SELECT * FROM controle_qualite", conn)
    if df.empty:
        st.warning("⚠️ Aucun contrôle enregistré pour le moment.")
    else:
        df['date'] = pd.to_datetime(df['date']).dt.date

        # Fonction pour vérifier si un contrôle est en retard
        def check_due(df, type_label, freq_days):
            filt = df[df['type'].str.contains(type_label)]
            if not filt.empty:
                last_date = filt['date'].max()
                delta = (today - last_date).days
                if delta >= freq_days:
                    st.warning(f"⏰ Contrôle {type_label.lower()} en retard ({delta} jours depuis le dernier)")
                else:
                    st.success(f"✅ Contrôle {type_label.lower()} fait il y a {delta} jours")
            else:
                st.error(f"❌ Aucun enregistrement pour contrôle {type_label.lower()}")

        # Vérification selon fréquence en jours
        check_due(df, "Journalier", 1)
        check_due(df, "Hebdomadaire", 7)
        check_due(df, "Mensuel", 30)
        check_due(df, "Annuel", 365)

        st.info("Les rappels sont calculés par rapport à la dernière date enregistrée dans chaque type de contrôle.")

        # Bouton pour envoyer un email de rappel automatique
        if st.button("Envoyer un e-mail de rappel"):
            sujet = "Rappel des contrôles Gamma Caméra"
            message = (
                "Bonjour,\n\n"
                "Ceci est un rappel automatique pour effectuer les contrôles nécessaires sur la gamma caméra.\n\n"
                "Merci.\n\n"
                "Cordialement,\n"
                "Interface de gestion Gamma Caméra"
            )
            success = envoyer_email("maryamabia01@gmail.com", sujet, message)
            if success:
                st.success("E-mail envoyé avec succès !")
            else:
                st.error("Erreur lors de l'envoi de l'e-mail.")

# Fin du bloc principal HTML (div)
st.markdown('</div>', unsafe_allow_html=True)
#logo fmpm 
import os  

st.markdown('<div class="main">', unsafe_allow_html=True)
# Affichage du logo + titre alignés à gauche avec un style propre
st.markdown("""
    <style>
    .header-container {
        display: flex;
        align-items: center;
        background-color: #ffffff;
        padding: 10px 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .header-container img {
        width: 70px;
        margin-right: 15px;
    }
    .header-container h1 {
        font-size: 24px;
        margin: 0;
        color: #1f4e79;
    }
    </style>

    <div class="header-container">
       
