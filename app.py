import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Gestion Gamma Caméra",
    page_icon="🔬",
    layout="wide"
)

# --- CONNEXION À LA BASE DE DONNÉES ---
@st.cache_resource
def init_connection():
    return sqlite3.connect("gamma_camera.db", check_same_thread=False)

conn = init_connection()
cursor = conn.cursor()

# --- CRÉATION DES TABLES (si elles n'existent pas) ---
def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, role TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS controle_qualite (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, test TEXT, intervenant TEXT, resultat TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pannes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, description TEXT, intervenant TEXT, action TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pieces_detachees (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, ref TEXT, date_commande TEXT, fournisseur TEXT, date_reception TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, type TEXT, fichier BLOB
    )''')
    conn.commit()

create_tables()

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
<style>
    /* --- Général --- */
    .stApp {
        background-color: #f0f2f6;
        font-family: 'Segoe UI', sans-serif;
    }

    /* --- Logo dans la barre latérale --- */
    [data-testid="stSidebar"] {
        padding-top: 1rem;
    }
    .sidebar-logo {
        width: 80px;
        display: block;
        margin: 0 auto 1rem auto;
    }

    /* --- Titres et Textes --- */
    h1, h2, h3 {
        color: #0d3d56;
    }

    /* --- Conteneurs et Cartes --- */
    .main-container {
        padding: 2rem;
    }
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .stExpander {
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
    }

    /* --- Bannière --- */
    .banner {
        padding: 3rem;
        background: linear-gradient(135deg, #0d3d56 0%, #1a6a9c 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .banner h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 600;
    }

    /* --- Images fines et allongées --- */
    .slim-image img {
        border-radius: 10px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        width: 100%;
        object-fit: cover;
        height: 150px; /* Hauteur fixe pour un effet allongé */
    }

    /* --- Pied de page --- */
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 40px;
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def envoyer_email(destinataire, sujet, message):
    SENDER_EMAIL = "maryamabia14@gmail.com"
    APP_PASSWORD = "wyva itgr vrmu keet"
    
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = destinataire
    msg["Subject"] = sujet
    msg.attach(MIMEText(message, "plain"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, destinataire, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email : {e}")
        return False

# --- MENU LATÉRAL ---
with st.sidebar:
    st.markdown(
        f'<img src="https://fmpm.uca.ma/wp-content/uploads/2024/04/logofm-1.png" class="sidebar-logo">',
        unsafe_allow_html=True
     )
    
    st.markdown("## 🧭 Navigation")
    menu = st.radio(
        "Choisissez une section :",
        [
            "Accueil", "Utilisateurs", "Contrôle Qualité", "Types de Tests",
            "Pannes", "Pièces Détachées", "Documents", "Statistiques", "Rappels"
        ],
        captions=[
            "Page de bienvenue", "Gérer les intervenants", "Suivi des tests", "Infos sur les tests",
            "Historique des pannes", "Gestion du stock", "Manuels et rapports", "Visualisation des données", "Envoyer des alertes"
        ]
    )
    st.markdown("---")
    st.info("**Développé par Maryam Abia**\n\nMaster Instrumentation et Analyse Biomédicale")

# --- CORPS PRINCIPAL DE L'APPLICATION ---
main_container = st.container()

if menu == "Accueil":
    with main_container:
        st.markdown('<div class="banner"><h1>Interface de Gestion - Gamma Caméra</h1></div>', unsafe_allow_html=True)
        
        # --- SECTION D'INTRODUCTION AVEC LE ROBOT ---
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Bienvenue dans le futur de la gestion biomédicale")
            st.write("""
            Cette plateforme centralise toutes les opérations essentielles pour la maintenance et le contrôle qualité de votre Gamma Caméra. 
            De la gestion des pannes au suivi des pièces détachées, en passant par l'archivage des documents, tout est conçu pour optimiser votre flux de travail.
            
            **Explorez les différentes sections via le menu latéral pour commencer.**
            """)
        with col2:
            st.image("https://png.pngtree.com/png-clipart/20250130/original/pngtree-ai-nurse-revolutionizing-healthcare-png-image_20358481.png" )

        st.markdown("---")

        # --- SECTION AVEC LES CONCEPTS CLÉS ---
        st.subheader("Concepts Clés en Médecine Nucléaire")
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("##### Radiotraceurs et Sécurité")
            st.write("Les radiotraceurs, comme le Technétium-99m, sont des substances radioactives qui, une fois injectées, se fixent sur un organe cible. Leur gestion sécurisée est primordiale.")
            st.markdown('<div class="slim-image"><img src="https://www.ehs.washington.edu/sites/default/files/Radiation-becky-yost_0.png"></div>', unsafe_allow_html=True )
        with col4:
            st.markdown("##### Technologie Gamma Caméra")
            st.write("La gamma caméra est un détecteur qui capte les rayonnements gamma émis par les radiotraceurs pour créer une image fonctionnelle (scintigraphie) de l'organe étudié.")
            st.markdown('<div class="slim-image"><img src="https://marketing.webassets.siemens-healthineers.com/2c2b0aa34ea22838/2e0bbcc28c19/v/9b9d3e5cf4b4/siemens-healthineers-mi-symbia-evo-excel.jpg"></div>', unsafe_allow_html=True )


# --- AUTRES PAGES ---
else:
    with main_container:
        st.header(f"📊 {menu}")

        if menu == "Utilisateurs":
            with st.expander("➕ Ajouter un nouvel utilisateur"):
                with st.form("new_user_form", clear_on_submit=True):
                    nom = st.text_input("Nom complet")
                    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"])
                    submitted = st.form_submit_button("Ajouter l'utilisateur")
                    if submitted and nom.strip() != "":
                        cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom.strip(), role))
                        conn.commit()
                        st.success(f"Utilisateur '{nom}' ajouté.")
                        st.rerun()
                    elif submitted:
                        st.error("Le nom ne peut pas être vide.")

            st.markdown("---")
            st.subheader("Liste des utilisateurs")
            df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
            st.dataframe(df_users, use_container_width=True)

        elif menu == "Contrôle Qualité":
            intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
            if not intervenants:
                st.warning("Veuillez d'abord ajouter des utilisateurs dans la section 'Utilisateurs'.")
            else:
                with st.expander("➕ Ajouter un nouveau contrôle"):
                    with st.form("new_cq_form", clear_on_submit=True):
                        date_cq = st.date_input("Date du contrôle", datetime.now())
                        type_cq = st.selectbox("Type de contrôle", ["Journalier", "Hebdomadaire", "Mensuel", "Annuel"])
                        test_cq = st.text_input("Test effectué")
                        intervenant_cq = st.selectbox("Intervenant", intervenants)
                        resultat_cq = st.text_area("Résultat / Observation")
                        submitted = st.form_submit_button("Ajouter le contrôle")
                        if submitted:
                            cursor.execute(
                                "INSERT INTO controle_qualite (date, type, test, intervenant, resultat) VALUES (?, ?, ?, ?, ?)",
                                (date_cq.strftime('%Y-%m-%d'), type_cq, test_cq, intervenant_cq, resultat_cq)
                            )
                            conn.commit()
                            st.success("Contrôle ajouté avec succès.")
                            st.rerun()
                
                st.markdown("---")
                st.subheader("Historique des contrôles")
                df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
                st.dataframe(df_cq, use_container_width=True)

        elif menu == "Types de Tests":
            tests_info = {
                "Test de linéarité": "S'assure que la caméra restitue les formes sans distorsion.",
                "Test d’uniformité intrinsèque": "Vérifie la production d'une image homogène à partir d’une source uniforme.",
                "Test de résolution spatiale intrinsèque": "Évalue la capacité à distinguer les détails fins sans collimateur.",
                "Test d’uniformité du système avec collimateur": "Vérifie l’homogénéité de l’image avec le collimateur.",
                "Test de sensibilité": "Évalue la réponse du système à un radionucléide d’activité connue.",
                "Mesure de la résolution énergétique (RE)": "Mesure la capacité à distinguer les photons d'énergies proches."
            }
            
            for i, (nom_test, description) in enumerate(tests_info.items()):
                with st.container():
                    st.markdown(f'<div class="card"><h3>{nom_test}</h3><p>{description}</p></div>', unsafe_allow_html=True)

        elif menu == "Pannes":
            intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
            if not intervenants:
                st.warning("Veuillez d'abord ajouter des utilisateurs.")
            else:
                with st.expander("➕ Ajouter une nouvelle panne"):
                    with st.form("new_panne_form", clear_on_submit=True):
                        date_panne = st.date_input("Date de la panne", datetime.now())
                        desc = st.text_area("Description de la panne")
                        intervenant_panne = st.selectbox("Intervenant", intervenants)
                        action = st.text_area("Action corrective réalisée")
                        submitted = st.form_submit_button("Ajouter la panne")
                        if submitted:
                            cursor.execute(
                                "INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                                (date_panne.strftime('%Y-%m-%d'), desc, intervenant_panne, action)
                            )
                            conn.commit()
                            st.success("Panne enregistrée.")
                            st.rerun()

                st.markdown("---")
                st.subheader("Historique des pannes")
                df_pannes = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
                st.dataframe(df_pannes, use_container_width=True)

        elif menu == "Pièces Détachées":
            with st.expander("➕ Ajouter une nouvelle pièce"):
                with st.form("new_piece_form", clear_on_submit=True):
                    nom_piece = st.text_input("Nom de la pièce")
                    ref_piece = st.text_input("Référence")
                    date_cmd = st.date_input("Date de commande")
                    fournisseur = st.text_input("Fournisseur")
                    date_rec = st.date_input("Date de réception")
                    submitted = st.form_submit_button("Ajouter la pièce")
                    if submitted and nom_piece:
                        cursor.execute(
                            "INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                            (nom_piece, ref_piece, date_cmd.strftime('%Y-%m-%d'), fournisseur, date_rec.strftime('%Y-%m-%d'))
                        )
                        conn.commit()
                        st.success("Pièce ajoutée au stock.")
                        st.rerun()

            st.markdown("---")
            st.subheader("Inventaire des pièces")
            df_pieces = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
            st.dataframe(df_pieces, use_container_width=True)

        elif menu == "Documents":
            with st.expander("➕ Ajouter un nouveau document"):
                with st.form("new_doc_form", clear_on_submit=True):
                    nom_doc = st.text_input("Nom du document")
                    type_doc = st.selectbox("Type", ["Manuel", "Procédure", "Rapport", "Autre"])
                    fichier = st.file_uploader("Charger le fichier (PDF, TXT, etc.)")
                    submitted = st.form_submit_button("Ajouter le document")
                    if submitted and fichier and nom_doc:
                        blob = fichier.read()
                        cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom_doc, type_doc, blob))
                        conn.commit()
                        st.success("Document ajouté.")
                        st.rerun()
                    elif submitted:
                        st.error("Veuillez renseigner un nom et choisir un fichier.")

            st.markdown("---")
            st.subheader("Liste des documents")
            df_docs = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
            st.dataframe(df_docs, use_container_width=True)

        elif menu == "Statistiques":
            df_cq = pd.read_sql("SELECT * FROM controle_qualite", conn)
            if df_cq.empty:
                st.info("Aucune donnée de contrôle qualité disponible pour générer des statistiques.")
            else:
                st.subheader("Analyse des Contrôles Qualité")
                df_cq['date'] = pd.to_datetime(df_cq['date'])
                
                fig1 = px.pie(df_cq, names='type', title='Répartition des contrôles par type')
                st.plotly_chart(fig1, use_container_width=True)

                df_cq['mois'] = df_cq['date'].dt.to_period("M").astype(str)
                count_by_month = df_cq.groupby('mois').size().reset_index(name='nombre')
                fig2 = px.bar(count_by_month, x='mois', y='nombre', title='Nombre de contrôles effectués par mois', labels={'mois': 'Mois', 'nombre': 'Nombre de contrôles'})
                st.plotly_chart(fig2, use_container_width=True)

        elif menu == "Rappels":
            st.subheader("Envoyer un rappel par Email")
            with st.form("email_form"):
                dest = st.text_input("Email du destinataire")
                sujet = st.text_input("Sujet", "Rappel: Contrôle Qualité Gamma Caméra")
                message = st.text_area("Message", "Bonjour,\n\nCeci est un rappel pour effectuer le contrôle qualité périodique de la gamma caméra.\n\nCordialement,\nL'équipe de maintenance.")
                submitted = st.form_submit_button("📧 Envoyer le rappel")
                if submitted:
                    if dest and sujet and message:
                        if envoyer_email(dest, sujet, message):
                            st.success(f"Email envoyé avec succès à {dest}.")
                    else:
                        st.error("Veuillez remplir tous les champs.")

# --- PIED DE PAGE ---
st.markdown(
    '<div class="footer">&copy; 2025 Maryam Abia – Tous droits réservés</div>',
    unsafe_allow_html=True
)
