import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Connexion à la base de données
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# Création des tables si n'existent pas
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

# Fonction d'envoi d'email
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

# --- CSS Style Propre et Moderne ---
st.markdown("""
<style>
    /* Corps de la page */
    .main {
        background-color: #f9f9fb;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sidebar */
    .css-1d391kg .css-1d391kg {
        background-color: #1f005c;
    }

    /* Titres */
    .title {
        color: #1f005c;
        font-weight: 700;
        font-size: 2.4rem;
        margin-bottom: 0;
    }

    /* Cards container */
    .cards-container {
        display: flex;
        flex-wrap: wrap;
        gap: 25px;
        justify-content: center;
        margin-top: 40px;
    }

    /* Each card */
    .card {
        background: white;
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        width: 280px;
        height: 180px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #1f005c;
        font-weight: 600;
        font-size: 1.25rem;
        text-align: center;
    }
    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(31, 0, 92, 0.3);
    }

    /* Image header */
    .header-img {
        width: 100%;
        max-height: 320px;
        border-radius: 18px;
        object-fit: cover;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(31, 0, 92, 0.2);
    }

    /* Footer texte */
    .footer-text {
        text-align: center;
        color: #555;
        margin-top: 40px;
        font-size: 0.9rem;
    }

</style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(page_title="Gamma Caméra - Gestion", layout="wide")

# Sidebar navigation
menu = st.sidebar.selectbox("Navigation", [
    "Accueil",
    "Gestion des utilisateurs",
    "Contrôles qualité",
    "Suivi des pannes",
    "Pièces détachées",
    "Gestion documentaire",
    "Rappels contrôles"
])

# --- Fonctions de contenu ---

def accueil():
    st.markdown('<h1 class="title">Bienvenue sur l\'interface de gestion - Gamma Caméra</h1>', unsafe_allow_html=True)
    st.image("https://img.freepik.com/premium-photo/chemical-molecule-with-blue-background-3d-rendering_772449-4288.jpg", use_column_width=True, clamp=True, output_format='auto', caption="Gamma Caméra - Radioprotection")
    st.write("""
        Cette interface vous permet de gérer facilement tous les aspects liés à la Gamma Caméra :
        - Gestion des utilisateurs
        - Contrôles qualité
        - Suivi des pannes
        - Gestion des pièces détachées
        - Gestion documentaire
        - Rappels automatiques pour les contrôles qualité
        
        Utilisez le menu latéral pour naviguer entre les sections.
    """)
    st.markdown('<p class="footer-text">Développé par <b>Maryam Abia</b></p>', unsafe_allow_html=True)

def gestion_utilisateurs():
    st.header("👥 Gestion des intervenants")
    nom = st.text_input("Nom complet")
    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"])
    if st.button("Ajouter l'intervenant"):
        if nom.strip():
            cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom.strip(), role))
            conn.commit()
            st.success("Intervenant ajouté avec succès")
        else:
            st.warning("Veuillez entrer un nom valide")
    df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df_users)

def controles_qualite():
    st.header("🗕 Contrôles qualité")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if intervenants:
        date = st.date_input("Date du contrôle", value=datetime.now())
        types_cq = [
            "Linéarité", "Uniformité intrinsèque", "Résolution spatiale intrinsèque",
            "Uniformité système avec collimateur", "Sensibilité", "Résolution énergétique", "Centre de rotation"
        ]
        type_cq = st.selectbox("Type de contrôle", types_cq)
        intervenant = st.selectbox("Intervenant", intervenants)
        resultat = st.text_area("Résultat / Observations")
        if st.button("Enregistrer le contrôle"):
            cursor.execute(
                "INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                (date.strftime('%Y-%m-%d'), type_cq, intervenant, resultat)
            )
            conn.commit()
            st.success("Contrôle qualité enregistré")
    else:
        st.warning("Ajoutez d'abord des intervenants dans la section correspondante.")
    df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
    st.dataframe(df_cq)

def suivi_pannes():
    st.header("🛠️ Suivi des pannes")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if intervenants:
        date = st.date_input("Date de la panne", value=datetime.now())
        description = st.text_area("Description de la panne")
        intervenant = st.selectbox("Intervenant responsable", intervenants)
        action = st.text_area("Action réalisée")
        if st.button("Enregistrer la panne"):
            cursor.execute(
                "INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                (date.strftime('%Y-%m-%d'), description, intervenant, action)
            )
            conn.commit()
            st.success("Panne enregistrée")
    else:
        st.warning("Ajoutez d'abord des intervenants.")
    df_pannes = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
    st.dataframe(df_pannes)

def pieces_detachees():
    st.header("🔧 Gestion des pièces détachées")
    nom_piece = st.text_input("Nom de la pièce")
    ref = st.text_input("Référence")
    date_cmd = st.date_input("Date de commande", value=datetime.now())
    fournisseur = st.text_input("Fournisseur")
    date_rec = st.date_input("Date de réception", value=datetime.now())
    if st.button("Ajouter la pièce"):
        cursor.execute(
            "INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
            (nom_piece, ref, date_cmd.strftime('%Y-%m-%d'), fournisseur, date_rec.strftime('%Y-%m-%d'))
        )
        conn.commit()
        st.success("Pièce détachée ajoutée")
    df_pieces = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    st.dataframe(df_pieces)

def gestion_documents():
    st.header("📂 Gestion documentaire")
    nom_doc = st.text_input("Nom du document")
    type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"])
    fichier = st.file_uploader("Téléverser un fichier", type=["pdf", "docx", "png", "jpg"])
    if fichier and st.button("Enregistrer le document"):
        blob = fichier.read()
        cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom_doc, type_doc, blob))
        conn.commit()
        st.success("Document enregistré")
    df_docs = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df_docs)

def rappels_controles():
    st.header("🔔 Rappels des contrôles qualité")
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    if df.empty:
        st.warning("Aucun contrôle qualité enregistré.")
        return
    today = datetime.now().date()
    df['date'] = pd.to_datetime(df['date']).dt.date

    freq_map = {
        "Linéarité": 7,
        "Uniformité intrinsèque": 7,
        "Résolution spatiale intrinsèque": 30,
        "Uniformité système avec collimateur": 7,
        "Sensibilité": 365,
        "Résolution énergétique": 365,
        "Centre de rotation": 180
    }

    for test_type, days in freq_map.items():
        subset = df[df['type'] == test_type]
        if not subset.empty:
            last_date = subset['date'].max()
            delta = (today - last_date).days
            if delta > days:
                st.warning(f"⏰ Le contrôle {test_type} est en retard ({delta} jours)")
            else:
                st.success(f"✅ Le contrôle {test_type} est à jour ({delta} jours)")

        else:
            st.error(f"❌ Aucun contrôle {test_type} enregistré")

    if st.button("Envoyer un e-mail de rappel"):
        msg = "Bonjour, ceci est un rappel automatique pour les contrôles qualité de la Gamma Caméra."
        if envoyer_email("maryamabia01@gmail.com", "Rappel Gamma Caméra", msg):
            st.success("E-mail de rappel envoyé avec succès")
        else:
            st.error("Erreur lors de l'envoi de l'e-mail")

# --- Affichage pages selon sélection ---

if menu == "Accueil":
    accueil()
elif menu == "Gestion des utilisateurs":
    gestion_utilisateurs()
elif menu == "Contrôles qualité":
    controles_qualite()
elif menu == "Suivi des pannes":
    suivi_pannes()
elif menu == "Pièces détachées":
    pieces_detachees()
elif menu == "Gestion documentaire":
    gestion_documents()
elif menu == "Rappels contrôles":
    rappels_controles()
