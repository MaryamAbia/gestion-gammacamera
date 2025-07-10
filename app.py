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

# Création tables si non existantes
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

st.App {
    background-image: url('https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.freepik.com%2Fpremium-ai-image%2Fclear-nuclear-medicine-image-showing-distribution-radiotracer-within-body-highlighting-areas-high-uptake-set-specialized-imaging-center-with-advanced-technology_267592288.htm&psig=AOvVaw2-Q9eywj3K6ocud-cVbQpT&ust=1752247411104000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCLi3zL3Mso4DFQAAAAAdAAAAABAE');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: black;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}




# Fonction d'envoi email (modifie avec ton email / mdp)
def envoyer_email(destinataire, sujet, message):
    sender_email = "maryamabia14@gmail.com"
    app_password = "wyva itgr vrmu keet"  # mets ton mdp d'application Gmail

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

# CSS avec backgrounds spécifiques par section, animation et styles
st.markdown("""
<style>
/* Reset global */
.stApp {
    background-color: #f9f9f9;
    color: black;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Animation fade in + slide down */
@keyframes fadeInSlideDown {
    0% {
        opacity: 0;
        transform: translateY(-30px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Bienvenu animé */
.animated-bienvenu {
    animation-name: fadeInSlideDown;
    animation-duration: 1.2s;
    animation-fill-mode: forwards;
    opacity: 0;
    animation-delay: 0.2s;
    font-size: 30px;
    font-weight: 700;
    color: #5b2a86;
    margin-bottom: 5px;
    text-align: center;
}

/* Titre animé */
.animated-title {
    animation-name: fadeInSlideDown;
    animation-duration: 1.2s;
    animation-fill-mode: forwards;
    opacity: 0;
    animation-delay: 0.8s;
    font-size: 36px;
    font-weight: 900;
    color: #4b007a;
    margin-bottom: 40px;
    text-align: center;
}

/* Styles de base des sections */
.section-container {
    border-radius: 15px;
    padding: 30px 40px;
    margin-bottom: 30px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    color: black !important;
    background-repeat: no-repeat;
    background-position: center;
    background-size: 150px 150px;
    background-blend-mode: lighten;
}

/* Sections avec images de fond différentes */
/* Remplace les URLs par les tiennes */

.section-container-gestion_intervenants {
    background-color: #e6e6fa; /* lavande clair */
    background-image: url('https://depositphotos.com/fr/photo/atomic-particle-3d-illustration-282758078.html');
    background-position: right bottom;
    background-size: 120px 120px;
}

.section-container-controle_qualite {
    background-color: #fff0f6; /* rose pale */
    background-image: url('https://cdn-icons-png.flaticon.com/512/889/889392.png');
    background-position: left top;
    background-size: 100px 100px;
}

.section-container-suivi_pannes {
    background-color: #f0fff0; /* vert pâle */
    background-image: url('https://cdn-icons-png.flaticon.com/512/564/564619.png');
    background-position: center right;
    background-size: 100px 100px;
}

.section-container-pieces_detachees {
    background-color: #f5f5dc; /* beige */
    background-image: url('https://cdn-icons-png.flaticon.com/512/2983/2983462.png');
    background-position: left center;
    background-size: 120px 120px;
}

.section-container-gestion_documents {
    background-color: #e0ffff; /* cyan pâle */
    background-image: url('https://cdn-icons-png.flaticon.com/512/3221/3221823.png');
    background-position: center;
    background-size: 130px 130px;
}

.section-container-rappels_controles {
    background-color: #fffacd; /* jaune pâle */
    background-image: url('https://cdn-icons-png.flaticon.com/512/597/597177.png');
    background-position: right center;
    background-size: 120px 120px;
}

/* Styles inputs et boutons */
input, select, textarea {
    border-radius: 6px;
    border: 1px solid #ccc;
    padding: 8px 12px;
    font-size: 16px;
    color: #333;
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 12px;
}

div.stButton > button:first-child {
    background-color: #5b2a86;
    color: white;
    border-radius: 8px;
    padding: 10px 22px;
    border: none;
    font-weight: bold;
    transition: background-color 0.3s ease;
    margin-top: 10px;
    width: 100%;
}

div.stButton > button:first-child:hover {
    background-color: #7d4ba6;
    cursor: pointer;
}

.stCheckbox > label {
    color: #4b007a;
    font-weight: 600;
    font-size: 18px;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

# Affichage Bienvenu + Titre avec animation
st.markdown('<div class="animated-bienvenu">BIENVENU</div>', unsafe_allow_html=True)
st.markdown('<div class="animated-title">Interface de gestion - Gamma Caméra</div>', unsafe_allow_html=True)
st.markdown("Développée par **Maryam Abia** – Suivi du contrôle qualité en médecine nucléaire")

# Init état des sections dans session_state
sections = [
    "gestion_intervenants",
    "controle_qualite",
    "suivi_pannes",
    "pieces_detachees",
    "gestion_documents",
    "rappels_controles"
]

for sec in sections:
    if sec not in st.session_state:
        st.session_state[sec] = False

# Fonction section avec checkbox et fond image
def section_container_checkbox(key, label, content_function):
    css_class = f"section-container section-container-{key}"
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    show = st.checkbox(label, value=st.session_state[key], key=f"chk_{key}")
    st.session_state[key] = show
    if show:
        content_function()
    st.markdown('</div>', unsafe_allow_html=True)

# Contenus des sections (identiques à ta version, ici en résumé)

def contenu_gestion_intervenants():
    st.header("👥 Gestion des intervenants")
    nom = st.text_input("Nom complet", key="nom_utilisateur")
    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"], key="role_utilisateur")
    if st.button("Ajouter l'intervenant", key="btn_ajouter_utilisateur"):
        if nom.strip() == "":
            st.warning("Veuillez saisir un nom.")
        else:
            cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
            conn.commit()
            st.success("Intervenant ajouté")
    df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df_users)

def contenu_controle_qualite():
    st.header("📅 Suivi des contrôles de qualité")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("Veuillez ajouter des intervenants d'abord.")
        return
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
    st.header("🛠️ Suivi des pannes")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("Veuillez ajouter des intervenants d'abord.")
        return
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
    st.header("🔧 Pièces détachées")
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
    st.header("📂 Gestion documentaire")
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
    st.header("🔔 Rappels des contrôles")
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    if df.empty:
        st.info("Aucun contrôle qualité enregistré.")
        return
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

# Affichage des sections avec checkbox et fond images
section_container_checkbox("gestion_intervenants", "👥 Gestion des intervenants", contenu_gestion_intervenants)
section_container_checkbox("controle_qualite", "📅 Suivi des contrôles de qualité", contenu_controle_qualite)
section_container_checkbox("suivi_pannes", "🛠️ Suivi des pannes", contenu_suivi_pannes)
section_container_checkbox("pieces_detachees", "🔧 Pièces détachées", contenu_pieces_detachees)
section_container_checkbox("gestion_documents", "📂 Gestion documentaire", contenu_gestion_documents)
section_container_checkbox("rappels_controles", "🔔 Rappels des contrôles", contenu_rappels_controles)
