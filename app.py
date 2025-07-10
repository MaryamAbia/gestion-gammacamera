import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Connexion à la base de données SQLite
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# Création des tables si elles n'existent pas
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
    app_password = "wyva itgr vrmu keet"  # ATTENTION: Mets ton vrai mot de passe d'application ici

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
        st.error(f"Erreur lors de l'envoi de l'email : {e}")
        return False

# CSS - Background app + styles sections + boutons
st.markdown("""
<style>
.stApp {
    background-image: url('https://st2.depositphotos.com/2890953/5471/i/600/depositphotos_54710477-stock-illustration-science-atom-globe-with-orbits.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: black;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.section-container {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 15px;
    padding: 25px 40px;
    margin-bottom: 30px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    color: #1f005c;
}

h2.section-title {
    color: #4b007a;
    margin-bottom: 10px;
}

button.section-toggle {
    background-color: #5b2a86;
    color: black;
    border-radius: 8px;
    padding: 8px 20px;
    border: none;
    font-weight: bold;
    cursor: pointer;
    margin-bottom: 15px;
    transition: background-color 0.3s ease;
    width: 100%;
    text-align: left;
    font-size: 18px;
}
button.section-toggle:hover {
    background-color: #7d4ba6;
}

input, select, textarea {
    border-radius: 6px;
    border: 1px solid #ccc;
    padding: 6px 12px;
    font-size: 16px;
    color: #333;
}

.stApp > main {
    overflow-y: auto;
    max-height: 90vh;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

st.title("Interface de gestion - Gamma Caméra")
st.markdown("Développée par **Maryam Abia** – Suivi du contrôle qualité en médecine nucléaire")

# Initialisation états toggle dans session_state
sections = ["gestion_intervenants", "controle_qualite", "suivi_pannes", "pieces_detachees", "gestion_documents", "rappels_controles"]
for sec in sections:
    if sec not in st.session_state:
        st.session_state[sec] = False

def toggle_button(label, key):
    if st.button(label, key=key):
        st.session_state[key] = not st.session_state[key]

def section_container(key, label, content_function):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    toggle_button(label, key)
    if st.session_state[key]:
        content_function()
    st.markdown('</div>', unsafe_allow_html=True)

# Contenus des sections

def contenu_gestion_intervenants():
    nom = st.text_input("Nom complet", key="nom_utilisateur")
    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"], key="role_utilisateur")
    if st.button("Ajouter l'intervenant", key="btn_ajouter_utilisateur"):
        if nom:
            cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
            conn.commit()
            st.success("Intervenant ajouté")
    df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df_users)

def contenu_controle_qualite():
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

def contenu_suivi_pannes():
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

def contenu_pieces_detachees():
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

def contenu_gestion_documents():
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

def contenu_rappels_controles():
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

# Affichage des sections avec toggle
section_container("gestion_intervenants", "👥 Gestion des intervenants", contenu_gestion_intervenants)
section_container("controle_qualite", "📅 Suivi des contrôles de qualité", contenu_controle_qualite)
section_container("suivi_pannes", "🛠️ Suivi des pannes", contenu_suivi_pannes)
section_container("pieces_detachees", "🔧 Pièces détachées", contenu_pieces_detachees)
section_container("gestion_documents", "📂 Gestion documentaire", contenu_gestion_documents)
section_container("rappels_controles", "🔔 Rappels des contrôles", contenu_rappels_controles)
