import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
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

# Email function
def envoyer_email(destinataire, sujet, message):
    sender_email = "maryamabia14@gmail.com"
    app_password = "wyva itgr vrmu keet"  # Your app password here
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

# CSS Styling and backgrounds
st.markdown("""
<style>
.stApp {
    background-color: #f7f7f7;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #1f005c;
    padding: 0 30px 30px 30px;
}
.banner {
    position: relative;
    width: 100%;
    height: 250px;
    border-radius: 12px;
    margin-bottom: 40px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.banner img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0.6);
    position: absolute;
    top: 0; left: 0;
}
.banner-text {
    position: relative;
    z-index: 1;
    color: white;
    font-size: 36px;
    font-weight: 700;
    text-align: center;
    padding: 70px 30px;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
}
.section-container {
    border-radius: 25px;
    padding: 60px 50px 50px 50px;
    margin-bottom: 50px;
    background-color: rgba(255, 255, 255, 0.9);
    box-shadow: 0 12px 40px rgba(0,0,0,0.1);
}
.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 15px;
    color: #4b0082;
}
.section-image {
    width: 100%;
    max-height: 250px;
    border-radius: 15px;
    margin-bottom: 25px;
    object-fit: cover;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
input, textarea, select, button {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

# Banner with image and title
st.markdown("""
<div class="banner">
    <img src="https://img.freepik.com/premium-photo/chemical-molecule-with-blue-background-3d-rendering_772449-4288.jpg" alt="Banner"/>
    <div class="banner-text">Interface de gestion complète - Gamma Caméra</div>
</div>
""", unsafe_allow_html=True)

st.markdown("Développée par **Maryam Abia**")

# --- Sections with images and content ---

def gestion_intervenants():
    st.markdown('<h2 class="section-title">👥 Gestion des intervenants</h2>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1532619675605-f717f4d5d7d8?auto=format&fit=crop&w=800&q=60", use_column_width=True)
    nom = st.text_input("Nom complet", key="nom_utilisateur")
    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"], key="role_utilisateur")
    if st.button("Ajouter l'intervenant", key="btn_ajouter_utilisateur"):
        if nom.strip() != "":
            cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
            conn.commit()
            st.success("Intervenant ajouté avec succès.")
        else:
            st.warning("Veuillez entrer un nom valide.")
    df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    st.dataframe(df_users)

def controle_qualite():
    st.markdown('<h2 class="section-title">🗕️ Suivi des contrôles qualité</h2>', unsafe_allow_html=True)
    st.image("https://marketing.webassets.siemens-healthineers.com/2c2b0aa34ea22838/2e0bbcc28c19/v/9b9d3e5cf4b4/siemens-healthineers-mi-symbia-evo-excel.jpg", use_column_width=True)
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("⚠️ Ajoutez d'abord des intervenants dans la section précédente.")
        return
    date = st.date_input("Date du contrôle", value=datetime.now(), key="date_controle")
    types_controles = [
        "Journalier: Résolution",
        "Hebdomadaire: Stabilisé",
        "Mensuel: Linéarité",
        "Annuel: Complèt"
    ]
    type_cq = st.selectbox("Type de contrôle", types_controles, key="type_controle")
    intervenant = st.selectbox("Intervenant", intervenants, key="intervenant_controle")
    resultat = st.text_area("Résultat ou observation", key="resultat_controle")
    if st.button("Enregistrer le contrôle", key="btn_enregistrer_controle"):
        cursor.execute("INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                       (date.strftime('%Y-%m-%d'), type_cq, intervenant, resultat))
        conn.commit()
        st.success("Contrôle enregistré avec succès.")
    df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
    st.dataframe(df_cq)

def suivi_pannes():
    st.markdown('<h2 class="section-title">🛠️ Suivi des pannes</h2>', unsafe_allow_html=True)
    st.image("https://st.depositphotos.com/1471096/58879/i/450/depositphotos_588797742-stock-photo-rendering-cryptocurrency-proton-coin-colorful.jpg", use_column_width=True)
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("⚠️ Ajoutez d'abord des intervenants dans la section Gestion des intervenants.")
        return
    date = st.date_input("Date panne", key="date_panne")
    description = st.text_area("Description de la panne", key="desc_panne")
    intervenant = st.selectbox("Intervenant", intervenants, key="intervenant_panne")
    action = st.text_area("Action réalisée", key="action_panne")
    if st.button("Enregistrer panne", key="btn_enregistrer_panne"):
        cursor.execute("INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                       (date.strftime('%Y-%m-%d'), description, intervenant, action))
        conn.commit()
        st.success("Panne enregistrée avec succès.")
    df_pannes = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
    st.dataframe(df_pannes)

def pieces_detachees():
    st.markdown('<h2 class="section-title">🔧 Gestion des pièces détachées</h2>', unsafe_allow_html=True)
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcREoTgwglu38D65SXA4vIFu-42VfzZRL0aU9g&s", use_column_width=True)
    nom_piece = st.text_input("Nom de la pièce", key="nom_piece")
    ref = st.text_input("Référence", key="ref_piece")
    date_commande = st.date_input("Date de commande", key="date_cmd_piece")
    fournisseur = st.text_input("Fournisseur", key="fournisseur_piece")
    date_reception = st.date_input("Date de réception", key="date_rec_piece")
    if st.button("Ajouter pièce", key="btn_ajouter_piece"):
        if nom_piece.strip() != "":
            cursor.execute("INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                           (nom_piece, ref, date_commande.strftime('%Y-%m-%d'), fournisseur, date_reception.strftime('%Y-%m-%d')))
            conn.commit()
            st.success("Pièce détachée ajoutée.")
        else:
            st.warning("Veuillez entrer un nom de pièce valide.")
    df_pieces = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    st.dataframe(df_pieces)

def gestion_documents():
    st.markdown('<h2 class="section-title">📂 Gestion des documents</h2>', unsafe_allow_html=True)
    st.image("https://t4.ftcdn.net/jpg/01/99/88/39/360_F_199883901_zBkNX4DJZngAegnUwvWgtuD1ESvCCRd2.jpg", use_column_width=True)
    nom_doc = st.text_input("Nom du document", key="nom_doc")
    type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"], key="type_doc")
    fichier = st.file_uploader("Téléverser un fichier", key="file_uploader")
    if fichier and st.button("Enregistrer document", key="btn_enregistrer_doc"):
        blob = fichier.read()
        cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom_doc, type_doc, blob))
        conn.commit()
        st.success("Document enregistré.")
    df_docs = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df_docs)

def rappels_controles():
    st.markdown('<h2 class="section-title">🔔 Rappels des contrôles qualité</h2>', unsafe_allow_html=True)
    st.image("https://img.freepik.com/free-photo/modern-hospital-machinery-illuminates-blue-mri-scanner-generated-by-ai_188544-44420.jpg", use_column_width=True)
    df = pd.read_sql("SELECT * FROM controle_qualite", conn)
    today = datetime.now().date()
    if df.empty:
        st.warning("Aucun contrôle enregistré.")
        return
    df['date'] = pd.to_datetime(df['date']).dt.date

    def check_due(df, type_label, freq_days):
        filt = df[df['type'].str.contains(type_label)]
        if not filt.empty:
            last_date = filt['date'].max()
            delta = (today - last_date).days
            if delta >= freq_days:
                st.warning(f"⏰ Contrôle {type_label.lower()} en retard ({delta} jours)")
            else:
                st.success(f"✅ Contrôle {type_label.lower()} effectué il y a {delta} jours")
        else:
            st.error(f"❌ Aucun contrôle {type_label.lower()} trouvé")

    check_due(df, "Journalier", 1)
    check_due(df, "Hebdomadaire", 7)
    check_due(df, "Mensuel", 30)
    check_due(df, "Annuel", 365)

    if st.button("Envoyer un e-mail de rappel", key="btn_envoyer_rappel"):
        msg = "Bonjour, ceci est un rappel automatique pour effectuer les contrôles Gamma Caméra."
        if envoyer_email("maryamabia01@gmail.com", "Rappel Gamma Caméra", msg):
            st.success("E-mail envoyé avec succès.")
        else:
            st.error("Erreur lors de l'envoi de l'e-mail.")

# Display all sections in one page with spacing
gestion_intervenants()
st.markdown("<hr>", unsafe_allow_html=True)
controle_qualite()
st.markdown("<hr>", unsafe_allow_html=True)
suivi_pannes()
st.markdown("<hr>", unsafe_allow_html=True)
pieces_detachees()
st.markdown("<hr>", unsafe_allow_html=True)
gestion_documents()
st.markdown("<hr>", unsafe_allow_html=True)
rappels_controles()
