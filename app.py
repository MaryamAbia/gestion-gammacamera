import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import numpy as np

# ------------------------------------------------------------------
#  CONFIGURATION DE LA PAGE
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Gestion Gamma Caméra",
    page_icon="🔬",
    layout="wide"
)

# ------------------------------------------------------------------
#  CONNEXION À LA BASE DE DONNÉES
# ------------------------------------------------------------------
@st.cache_resource
def init_connection():
    return sqlite3.connect("gamma_camera.db", check_same_thread=False)

conn = init_connection()
cursor = conn.cursor()

# ------------------------------------------------------------------
#  CRÉATION DES TABLES
# ------------------------------------------------------------------
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
        id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, type TEXT, fichier BLOB, nom_fichier_original TEXT
    )''')
    conn.commit()

create_tables()

# ------------------------------------------------------------------
#  STYLE CSS PERSONNALISÉ
# ------------------------------------------------------------------
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
        height: 150px;
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

# ------------------------------------------------------------------
#  FONCTIONS UTILITAIRES
# ------------------------------------------------------------------
def envoyer_email(destinataire, sujet, message):
    """Envoi d'un email simple via SMTP Gmail."""
    SENDER_EMAIL = "maryamabia14@gmail.com"
    APP_PASSWORD = "wyva itgr vrmu keet"  # À sécuriser!

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

def update_record(table, record_id, data_dict):
    """Met à jour un enregistrement dans une table."""
    if not data_dict:
        return
    set_clause = ", ".join([f"{col}=?" for col in data_dict.keys()])
    values = list(data_dict.values()) + [record_id]
    cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id=?", values)
    conn.commit()

def delete_record(table, record_id):
    """Supprime un enregistrement par id."""
    cursor.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
    conn.commit()

# ------------------------------------------------------------------
#  MENU LATÉRAL
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<img src="https://fmpm.uca.ma/wp-content/uploads/2024/04/logofm-1.png" class="sidebar-logo">',
        unsafe_allow_html=True
    )
    st.markdown("## 🧭 Navigation")
    menu = st.radio(
        "Choisissez une section :",
        [
            "Accueil", "Utilisateurs", "Contrôle Qualité", "Types de Tests",
            "Pannes", "Pièces Détachées", "Documents", "Statistiques",
            "Prédiction des pannes", "Rappels"
        ]
    )
    st.markdown("---")
    st.info("**Développé par Maryam Abia**\n\nMaster Instrumentation et Analyse Biomédicale")

# ------------------------------------------------------------------
#  CORPS PRINCIPAL
# ------------------------------------------------------------------
main_container = st.container()

if menu == "Accueil":
    with main_container:
        st.markdown('<div class="banner"><h1>Interface de Gestion - Gamma Caméra</h1></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Bienvenue dans le futur de la gestion biomédicale")
            st.write("""
            Cette plateforme centralise toutes les opérations essentielles pour la maintenance et le contrôle qualité de votre Gamma Caméra. 
            De la gestion des pannes au suivi des pièces détachées, en passant par l'archivage des documents, tout est conçu pour optimiser votre flux de travail.
            **Explorez les différentes sections via le menu latéral pour commencer.**
            """)
        with col2:
            st.image("https://png.pngtree.com/png-clipart/20250130/original/pngtree-ai-nurse-revolutionizing-healthcare-png-image_20358481.png")

        st.markdown("---")

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

elif menu == "Utilisateurs":
    with main_container:
        st.header(f"📊 {menu}")
        with st.expander("➕ Ajouter un nouvel utilisateur"):
            with st.form("new_user_form", clear_on_submit=True):
                nom = st.text_input("Nom complet")
                role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Responsable", "Autre"])
                submitted = st.form_submit_button("Ajouter")
                if submitted:
                    if nom.strip() == "":
                        st.error("Le nom ne peut pas être vide.")
                    else:
                        cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
                        conn.commit()
                        st.success(f"Utilisateur {nom} ajouté avec succès.")

        # Affichage des utilisateurs existants
        df_users = pd.read_sql("SELECT * FROM utilisateurs", conn)
        if df_users.empty:
            st.info("Aucun utilisateur enregistré.")
        else:
            st.dataframe(df_users)

        # Option suppression utilisateur
        id_del = st.number_input("Entrez l'ID pour supprimer un utilisateur", min_value=0, step=1)
        if st.button("Supprimer utilisateur"):
            cursor.execute("DELETE FROM utilisateurs WHERE id=?", (id_del,))
            conn.commit()
            st.success(f"Utilisateur avec ID {id_del} supprimé.")

elif menu == "Contrôle Qualité":
    with main_container:
        st.header("📋 Gestion du Contrôle Qualité")
        with st.expander("➕ Ajouter un nouveau contrôle qualité"):
            with st.form("form_cq", clear_on_submit=True):
                date_cq = st.date_input("Date du contrôle", datetime.today())
                type_cq = st.selectbox("Type de contrôle", ["Intrinsèque", "Extrinsèque", "SPECT"])
                test_cq = st.text_input("Nom du test")
                intervenant_cq = st.text_input("Intervenant")
                resultat_cq = st.selectbox("Résultat", ["OK", "Non OK"])
                submitted_cq = st.form_submit_button("Enregistrer")
                if submitted_cq:
                    cursor.execute("""
                    INSERT INTO controle_qualite (date, type, test, intervenant, resultat)
                    VALUES (?, ?, ?, ?, ?)
                    """, (date_cq.strftime("%Y-%m-%d"), type_cq, test_cq, intervenant_cq, resultat_cq))
                    conn.commit()
                    st.success("Contrôle qualité enregistré avec succès.")

        # Affichage des contrôles qualité
        df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
        if df_cq.empty:
            st.info("Aucun contrôle qualité enregistré.")
        else:
            st.dataframe(df_cq)

elif menu == "Types de Tests":
    with main_container:
        st.header("🧪 Types de Tests de Contrôle Qualité")
        tests = [
            {"Nom": "Test Intrinsèque", "Description": "Vérification des composants internes de la caméra."},
            {"Nom": "Test Extrinsèque", "Description": "Contrôle de la performance globale avec source externe."},
            {"Nom": "Test SPECT", "Description": "Analyse des images tomographiques obtenues."},
        ]
        df_tests = pd.DataFrame(tests)
        st.table(df_tests)

elif menu == "Pannes":
    with main_container:
        st.header("⚠️ Gestion des Pannes")
        with st.expander("➕ Ajouter une nouvelle panne"):
            with st.form("form_pannes", clear_on_submit=True):
                date_panne = st.date_input("Date de la panne", datetime.today())
                desc_panne = st.text_area("Description de la panne")
                intervenant_panne = st.text_input("Intervenant")
                action_panne = st.text_area("Action corrective réalisée")
                submitted_panne = st.form_submit_button("Enregistrer")
                if submitted_panne:
                    cursor.execute("""
                    INSERT INTO pannes (date, description, intervenant, action)
                    VALUES (?, ?, ?, ?)
                    """, (date_panne.strftime("%Y-%m-%d"), desc_panne, intervenant_panne, action_panne))
                    conn.commit()
                    st.success("Panne enregistrée avec succès.")

        df_pannes = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
        if df_pannes.empty:
            st.info("Aucune panne enregistrée.")
        else:
            st.dataframe(df_pannes)

elif menu == "Pièces Détachées":
    with main_container:
        st.header("🔧 Gestion des Pièces Détachées")
        with st.expander("➕ Ajouter une nouvelle pièce"):
            with st.form("form_pieces", clear_on_submit=True):
                nom_piece = st.text_input("Nom de la pièce")
                ref_piece = st.text_input("Référence")
                date_commande = st.date_input("Date de commande")
                fournisseur = st.text_input("Fournisseur")
                date_reception = st.date_input("Date de réception")
                submitted_piece = st.form_submit_button("Enregistrer")
                if submitted_piece:
                    cursor.execute("""
                    INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception)
                    VALUES (?, ?, ?, ?, ?)
                    """, (
                        nom_piece, ref_piece,
                        date_commande.strftime("%Y-%m-%d"),
                        fournisseur,
                        date_reception.strftime("%Y-%m-%d")
                    ))
                    conn.commit()
                    st.success("Pièce détachée enregistrée avec succès.")

        df_pieces = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
        if df_pieces.empty:
            st.info("Aucune pièce détachée enregistrée.")
        else:
            st.dataframe(df_pieces)

elif menu == "Documents":
    with main_container:
        st.header("📁 Gestion des Documents")
        with st.expander("➕ Ajouter un nouveau document"):
            with st.form("form_documents", clear_on_submit=True):
                nom_doc = st.text_input("Nom du document")
                type_doc = st.selectbox("Type de document", ["Rapport", "Manuel", "Certificat", "Autre"])
                fichier = st.file_uploader("Télécharger le fichier", type=["pdf", "docx", "xlsx", "png", "jpg"])
                submitted_doc = st.form_submit_button("Enregistrer")
                if submitted_doc:
                    if fichier is not None:
                        blob = fichier.read()
                        cursor.execute("""
                        INSERT INTO documents (nom, type, fichier, nom_fichier_original)
                        VALUES (?, ?, ?, ?)
                        """, (nom_doc, type_doc, blob, fichier.name))
                        conn.commit()
                        st.success("Document enregistré avec succès.")
                    else:
                        st.error("Veuillez télécharger un fichier.")

        df_docs = pd.read_sql("SELECT id, nom, type, nom_fichier_original FROM documents ORDER BY id DESC", conn)
        if df_docs.empty:
            st.info("Aucun document enregistré.")
        else:
            st.dataframe(df_docs)

        # Option pour télécharger un document
        id_download = st.number_input("Entrez l'ID du document à télécharger", min_value=0, step=1)
        if st.button("Télécharger le document"):
            cursor.execute("SELECT fichier, nom_fichier_original FROM documents WHERE id=?", (id_download,))
            res = cursor.fetchone()
            if res:
                fichier_blob, nom_fichier = res
                st.download_button(
                    label="Télécharger",
                    data=fichier_blob,
                    file_name=nom_fichier
                )
            else:
                st.error("Document introuvable.")

elif menu == "Statistiques":
    with main_container:
        st.header("📈 Statistiques et Visualisations")
        df_pannes = pd.read_sql("SELECT * FROM pannes", conn)
        if df_pannes.empty:
            st.info("Pas de données de panne pour afficher les statistiques.")
        else:
            df_pannes["date"] = pd.to_datetime(df_pannes["date"])
            df_pannes["mois"] = df_pannes["date"].dt.to_period("M").astype(str)

            pannes_par_mois = df_pannes.groupby("mois").size().reset_index(name="Nombre de pannes")

            fig = px.bar(pannes_par_mois, x="mois", y="Nombre de pannes", title="Nombre de pannes par mois")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Tableau des pannes")
            st.dataframe(df_pannes)

elif menu == "Prédiction des pannes":
    with main_container:
        st.subheader("🔮 Prédiction des pannes (Machine Learning)")

        df_pannes = pd.read_sql("SELECT * FROM pannes", conn)
        if df_pannes.empty:
            st.warning("⚠️ Pas assez de données de pannes pour entraîner un modèle.")
        else:
            df_pannes["date"] = pd.to_datetime(df_pannes["date"])
            df_pannes["jour"] = df_pannes["date"].dt.day
            df_pannes["mois"] = df_pannes["date"].dt.month
            df_pannes["année"] = df_pannes["date"].dt.year

            # Encodage des descriptions
            le_desc = LabelEncoder()
            df_pannes["desc_code"] = le_desc.fit_transform(df_pannes["description"].astype(str))

            # Variables d'entrée et cible (ici, juste présence de panne = 1)
            X = df_pannes[["jour", "mois", "année", "desc_code"]]
            y = np.ones(len(X))  # Toutes lignes = panne (car on analyse les pannes)

            # Division en train/test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

            # Modèle simple
            model = LogisticRegression()
            model.fit(X_train, y_train)

            # Évaluation
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            st.info(f"Précision du modèle : {acc*100:.1f}%")

            # Prédiction sur une date future
            future_date = st.date_input("Choisir une date future")
            future_desc = st.text_input("Description prévue (ex: problème caméra)")

            if st.button("Prédire la probabilité de panne"):
                if future_desc in le_desc.classes_:
                    desc_code = le_desc.transform([future_desc])[0]
                else:
                    desc_code = 0  # Valeur par défaut si description inconnue

                future_data = pd.DataFrame([{
                    "jour": future_date.day,
                    "mois": future_date.month,
                    "année": future_date.year,
                    "desc_code": desc_code
                }])

                prob = model.predict_proba(future_data)[:, 1][0]
                st.success(f"Probabilité estimée de panne : {prob*100:.2f}%")

elif menu == "Rappels":
    with main_container:
        st.subheader("📧 Envoyer un rappel par Email")
        with st.form("email_form"):
            dest = st.text_input("Email du destinataire")
            sujet = st.text_input("Sujet", "Rappel: Contrôle Qualité Gamma Caméra")
            message = st.text_area("Message", "Bonjour,\n\nCeci est un rappel concernant le contrôle qualité de la Gamma Caméra.")
            submitted = st.form_submit_button("Envoyer le rappel")
            if submitted:
                if dest.strip() == "":
                    st.error("Veuillez entrer un email valide.")
                else:
                    if envoyer_email(dest, sujet, message):
                        st.success(f"Email envoyé avec succès à {dest}.")

# ------------------------------------------------------------------
#  PIED DE PAGE
# ------------------------------------------------------------------
st.markdown('<div class="footer">&copy; 2025 Maryam Abia – Tous droits réservés</div>', unsafe_allow_html=True)
