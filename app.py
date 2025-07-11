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

# Envoi d'e-mails
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

# Menu
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Medical_Symbol.svg/2048px-Medical_Symbol.svg.png", width=80)
st.sidebar.title("📋 Menu")
page = st.sidebar.radio("Aller vers :", [
    "Accueil", "Utilisateurs", "Contrôles de qualité", "Pannes et Maintenance",
    "Pièces détachées", "Documents", "Analyse", "Téléchargement des données", "Rappels de contrôles"
])

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

if page == "Analyse":
    st.title("📊 Analyse des données")

    df_cq = pd.read_sql_query("SELECT * FROM controle_qualite", conn)
    if not df_cq.empty:
        fig_cq = px.histogram(df_cq, x="type", color="type", title="Nombre de contrôles par type")
        st.plotly_chart(fig_cq)

    df_pannes = pd.read_sql_query("SELECT * FROM pannes", conn)
    if not df_pannes.empty:
        df_pannes['date'] = pd.to_datetime(df_pannes['date'])
        pannes_par_mois = df_pannes.groupby(df_pannes['date'].dt.to_period('M')).size().reset_index(name='Nombre')
        pannes_par_mois['date'] = pannes_par_mois['date'].astype(str)
        fig_pannes = px.bar(pannes_par_mois, x='date', y='Nombre', title="Fréquence des pannes par mois")
        st.plotly_chart(fig_pannes)

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
        st.download_button("📥 Télécharger CSV", data=df.to_csv(index=False), file_name="pannes.csv", mime="text/csv")

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
    st.download_button("📥 Télécharger CSV", data=df.to_csv(index=False), file_name="pieces_detachees.csv", mime="text/csv")

elif page == "Documents":
    st.title("📂 Gestion documentaire")

    with st.form("form_doc"):
        nom = st.text_input("Nom du document")
        type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"])
        fichier = st.file_uploader("Téléverser un fichier", type=["pdf", "docx", "png", "jpg"])
        submit = st.form_submit_button("Enregistrer")
        if submit and fichier is not None:
            blob = fichier.read()
            cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom, type_doc, blob))
            conn.commit()
            st.success("✅ Document enregistré")
            st.experimental_rerun()

    st.subheader("Liste des documents")
    df = pd.read_sql_query("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df)

elif page == "Téléchargement des données":
    st.title("📥 Exportation globale des données")

    tables = {
        "Contrôles de qualité": "controle_qualite",
        "Pannes": "pannes",
        "Pièces détachées": "pieces_detachees",
        "Utilisateurs": "utilisateurs"
    }

    for label, table in tables.items():
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        st.download_button(f"📁 Télécharger - {label}", data=df.to_csv(index=False), file_name=f"{table}.csv", mime="text/csv")

st.markdown('</div>', unsafe_allow_html=True)
