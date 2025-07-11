import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Config page
st.set_page_config(page_title="Gestion Gamma Caméra", layout="wide")

# Connexion DB
conn = sqlite3.connect("gamma_camera.db", check_same_thread=False)
cursor = conn.cursor()

# Création tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    role TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS controle_qualite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    test TEXT,
    intervenant TEXT,
    resultat TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS pannes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    description TEXT,
    intervenant TEXT,
    action TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS pieces_detachees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    ref TEXT,
    date_commande TEXT,
    fournisseur TEXT,
    date_reception TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    type TEXT,
    fichier BLOB
)
''')
conn.commit()

# === Configuration email (intégrée depuis ton code ancien) ===
SENDER_EMAIL = "maryamabia14@gmail.com"
APP_PASSWORD = "wyva itgr vrmu keet"  # Remplace par ton vrai password app Gmail

def envoyer_email(destinataire, sujet, message):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = destinataire
    msg["Subject"] = sujet
    msg.attach(MIMEText(message, "plain"))
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinataire, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur email : {e}")
        return False

# === CSS Styling ===
st.markdown("""
<style>
    .stApp { font-family: 'Segoe UI', sans-serif; background-color: #f4f6fa; }
    .banner {
        width: 100%; height: 200px; margin-bottom: 20px; position: relative;
        background: url('https://img.freepik.com/premium-photo/chemical-molecule-with-blue-background-3d-rendering_772449-4288.jpg') no-repeat center;
        background-size: cover; display: flex; align-items: center; justify-content: center;
        border-radius: 12px;
    }
    .banner h1 {
        background-color: rgba(255,255,255,0.9); padding: 20px 40px; border-radius: 8px;
        color: #003366; font-size: 36px;
    }
    .section-title {
        font-size: 26px; margin-top: 30px; color: #002244;
    }
    .divider {
        height: 2px; background-color: #ccc; margin: 20px 0;
    }
    .img-block {
        width: 100%; border-radius: 10px; margin-top: 10px;
    }
    .footer {
        margin-top: 50px; font-size: 14px; color: #555; text-align: center;
    }
    .btn-del {
        background-color: #ff4b4b; color: white; border-radius: 6px; padding: 6px 12px;
        border: none; cursor: pointer; margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Bandeau principal
st.markdown("""
<div class="banner">
    <h1>Interface de Gestion - Gamma Caméra</h1>
</div>
""", unsafe_allow_html=True)

# Menu latéral
menu = st.sidebar.selectbox("Navigation", [
    "Accueil",
    "Utilisateurs",
    "Contrôle Qualité",
    "Types de Tests",
    "Pannes",
    "Pièces Détachées",
    "Documents",
    "Statistiques",
    "Rappels"
])

# --- Page Accueil ---
if menu == "Accueil":
    st.subheader("Bienvenue dans l'interface de gestion Gamma Caméra")

    st.markdown("""
    ### 🧬 Qu'est-ce que la Médecine Nucléaire ?
    La médecine nucléaire est une spécialité médicale utilisant des substances radioactives pour le diagnostic et le traitement.
    Elle permet de visualiser la fonction des organes grâce à l'émission de rayonnements gamma captés par une gamma caméra.
    """)
    st.image("https://media.springernature.com/w580h326/nature-cms/uploads/collections/7e9b9309-f848-4071-8004-3dfde0e14fa7/NM_S02_hero.jpg", use_column_width=True)

    st.markdown("""
    ### 📸 La Gamma Caméra
    Dispositif détectant les rayonnements gamma émis par le patient après injection d’un radio-isotope.
    Elle fournit des images fonctionnelles essentielles pour le diagnostic médical.
    """)
    st.image("https://www.siemens-healthineers.com/fr-fr/molecular-imaging/gamma-cameras/spect-systems/symbia-evo-excel/images/_jcr_content/root/responsivegrid/image.coreimg.jpeg/1624351381990/symbia-evo-teaser.jpeg", use_column_width=True)

    st.markdown("""
    ### 🧪 Le Contrôle de Qualité
    Garantit la fiabilité des images par plusieurs tests (uniformité, résolution, linéarité...).
    Ce suivi assure des performances optimales et la sécurité du patient.
    """)
    st.image("https://img.freepik.com/free-photo/medical-technologist-checking-machine-hospital-laboratory_342744-1310.jpg", use_column_width=True)

    st.markdown("---")
    st.markdown("**Développée par Maryam Abia – Master Instrumentation et Analyse Biomédicale**")

# --- Page Utilisateurs ---
elif menu == "Utilisateurs":
    st.header("Gestion des Utilisateurs")

    with st.expander("Ajouter un nouvel utilisateur"):
        nom = st.text_input("Nom complet", key="nom_utilisateur")
        role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"], key="role_utilisateur")
        if st.button("Ajouter", key="btn_ajouter_utilisateur"):
            if nom.strip() == "":
                st.error("Le nom ne peut pas être vide.")
            else:
                cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom.strip(), role))
                conn.commit()
                st.success(f"Utilisateur '{nom}' ajouté.")

    st.markdown("---")
    st.subheader("Liste des utilisateurs")
    df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    edited_users = st.data_editor(df_users, num_rows="dynamic", use_container_width=True)

    if st.button("Enregistrer les modifications utilisateurs"):
        for i, row in edited_users.iterrows():
            cursor.execute("UPDATE utilisateurs SET nom = ?, role = ? WHERE id = ?", (row['nom'], row['role'], row['id']))
        conn.commit()
        st.success("Modifications enregistrées.")

# --- Page Contrôle Qualité ---
elif menu == "Contrôle Qualité":
    st.header("Suivi des Contrôles Qualité")

    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("Ajoutez des utilisateurs/intervenants dans la page 'Utilisateurs' avant de continuer.")
    else:
        with st.expander("Ajouter un nouveau contrôle"):
            date_cq = st.date_input("Date du contrôle", datetime.now())
            type_cq = st.selectbox("Type de contrôle", [
                "Journalier: Résolution",
                "Hebdomadaire: Stabilisé",
                "Mensuel: Linéarité",
                "Annuel: Complèt"
            ])
            tests_possibles = {
                "Journalier: Résolution": ["Résolution spatiale intrinsèque", "Uniformité intrinsèque"],
                "Hebdomadaire: Stabilisé": ["Uniformité extrinsèque", "Test de sensibilité"],
                "Mensuel: Linéarité": ["Test de linéarité", "Uniformité du système avec collimateur"],
                "Annuel: Complèt": ["Test complet annuel", "Mesure résolution énergétique"]
            }
            test_cq = st.selectbox("Test effectué", tests_possibles[type_cq])
            intervenant_cq = st.selectbox("Intervenant", intervenants)
            resultat_cq = st.text_area("Résultat / Observation")

            if st.button("Ajouter contrôle"):
                cursor.execute(
                    "INSERT INTO controle_qualite (date, type, test, intervenant, resultat) VALUES (?, ?, ?, ?, ?)",
                    (date_cq.strftime('%Y-%m-%d'), type_cq, test_cq, intervenant_cq, resultat_cq)
                )
                conn.commit()
                st.success("Contrôle ajouté.")

        st.markdown("---")
        st.subheader("Historique des contrôles")
        df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)
        edited_cq = st.data_editor(df_cq, num_rows="dynamic", use_container_width=True)

        if st.button("Enregistrer modifications contrôles"):
            for i, row in edited_cq.iterrows():
                cursor.execute(
                    "UPDATE controle_qualite SET date = ?, type = ?, test = ?, intervenant = ?, resultat = ? WHERE id = ?",
                    (row['date'], row['type'], row['test'], row['intervenant'], row['resultat'], row['id'])
                )
            conn.commit()
            st.success("Modifications sauvegardées.")

# --- Page Types de Tests ---
elif menu == "Types de Tests":
    st.header("Descriptions des Tests de Contrôle Qualité")

    tests_info = {
        "Test de linéarité": """
        Le test de linéarité est un contrôle de routine hebdomadaire, complété par une vérification quantitative semestrielle.
        Il permet de s’assurer que la gamma caméra restitue correctement les formes sans distorsion.
        """,
        "Test d’uniformité intrinsèque": """
        Vérifie la capacité de la gamma caméra à produire une image homogène à partir d’une source uniforme.
        Test de réception, puis effectué hebdomadairement (10 × 10⁶ coups) et mensuellement (200 × 10⁶ coups).
        """,
        "Test de résolution spatiale intrinsèque": """
        Évalue la capacité de la gamma caméra à distinguer les détails fins sans collimateur.
        Test de réception, ensuite réalisé mensuellement.
        """,
        "Test d’uniformité du système avec collimateur": """
        Vérifie l’homogénéité de l’image produite avec collimateur.
        Test initial de référence, puis répété hebdomadairement (contrôle visuel) et semestriellement (contrôle visuel et quantitatif).
        """,
        "Test de sensibilité": """
        Évalue la réponse du système à un radionucléide d’activité connue.
        Contrôle effectué à la réception comme test de référence, puis annuellement.
        """,
        "Mesure de la résolution énergétique (RE)": """
        Réalisée avec la même source que le test de sensibilité.
        Mesure la largeur à mi-hauteur (LMH) du pic photoélectrique.
        Valeur typique d’environ 10 % à 140 keV, indiquant la capacité à distinguer les photons proches en énergie.
        """
    }

    for nom_test, description in tests_info.items():
        st.subheader(nom_test)
        st.write(description)
        st.image("https://img.freepik.com/free-photo/technology-background-with-glowing-particles_1048-8033.jpg?w=740&t=st=1689288281~exp=1689288881~hmac=8e9241f9aa3eecb8a5e57e746e2491adce3a99b3b4d909c405a6a2d974d7b1c4", width=600)
        st.markdown("---")

# --- Page Pannes ---
elif menu == "Pannes":
    st.header("Suivi des Pannes")

    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if not intervenants:
        st.warning("Ajoutez des utilisateurs dans la page 'Utilisateurs' avant de continuer.")
    else:
        with st.expander("Ajouter une nouvelle panne"):
            date_panne = st.date_input("Date de la panne", datetime.now())
            desc = st.text_area("Description")
            intervenant_panne = st.selectbox("Intervenant", intervenants)
            action = st.text_area("Action réalisée")

            if st.button("Ajouter panne"):
                cursor.execute(
                    "INSERT INTO pannes (date, description, intervenant, action) VALUES (?, ?, ?, ?)",
                    (date_panne.strftime('%Y-%m-%d'), desc, intervenant_panne, action)
                )
                conn.commit()
                st.success("Panne ajoutée.")

        st.markdown("---")
        st.subheader("Historique des pannes")
        df_pannes = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
        edited_pannes = st.data_editor(df_pannes, num_rows="dynamic", use_container_width=True)

        if st.button("Enregistrer modifications pannes"):
            for i, row in edited_pannes.iterrows():
                cursor.execute(
                    "UPDATE pannes SET date = ?, description = ?, intervenant = ?, action = ? WHERE id = ?",
                    (row['date'], row['description'], row['intervenant'], row['action'], row['id'])
                )
            conn.commit()
            st.success("Modifications sauvegardées.")

# --- Page Pièces Détachées ---
elif menu == "Pièces Détachées":
    st.header("Gestion des Pièces Détachées")

    with st.expander("Ajouter une nouvelle pièce"):
        nom_piece = st.text_input("Nom de la pièce")
        ref_piece = st.text_input("Référence")
        date_cmd = st.date_input("Date de commande")
        fournisseur = st.text_input("Fournisseur")
        date_rec = st.date_input("Date de réception")

        if st.button("Ajouter la pièce"):
            cursor.execute(
                "INSERT INTO pieces_detachees (nom, ref, date_commande, fournisseur, date_reception) VALUES (?, ?, ?, ?, ?)",
                (nom_piece, ref_piece, date_cmd.strftime('%Y-%m-%d'), fournisseur, date_rec.strftime('%Y-%m-%d'))
            )
            conn.commit()
            st.success("Pièce ajoutée.")

    st.markdown("---")
    st.subheader("Liste des pièces")
    df_pieces = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    edited_pieces = st.data_editor(df_pieces, num_rows="dynamic", use_container_width=True)

    if st.button("Enregistrer modifications pièces"):
        for i, row in edited_pieces.iterrows():
            cursor.execute(
                "UPDATE pieces_detachees SET nom = ?, ref = ?, date_commande = ?, fournisseur = ?, date_reception = ? WHERE id = ?",
                (row['nom'], row['ref'], row['date_commande'], row['fournisseur'], row['date_reception'], row['id'])
            )
        conn.commit()
        st.success("Modifications sauvegardées.")

# --- Page Documents ---
elif menu == "Documents":
    st.header("Gestion des Documents")

    with st.expander("Ajouter un document"):
        nom_doc = st.text_input("Nom du document")
        type_doc = st.selectbox("Type de document", ["Manuel", "Procédure", "Rapport", "Autre"])
        fichier = st.file_uploader("Charger le fichier")

        if st.button("Ajouter document"):
            if fichier is not None and nom_doc.strip() != "":
                blob = fichier.read()
                cursor.execute(
                    "INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)",
                    (nom_doc.strip(), type_doc, blob)
                )
                conn.commit()
                st.success("Document ajouté.")
            else:
                st.error("Veuillez renseigner un nom et choisir un fichier.")

    st.markdown("---")
    st.subheader("Liste des documents")
    df_docs = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    st.dataframe(df_docs)

# --- Page Statistiques ---
elif menu == "Statistiques":
    st.header("Statistiques des Contrôles Qualité")

    df_cq = pd.read_sql("SELECT * FROM controle_qualite", conn)
    if df_cq.empty:
        st.info("Aucun contrôle qualité enregistré.")
    else:
        # Filtrage par type
        types_dispo = df_cq['type'].unique()
        type_sel = st.selectbox("Filtrer par type", options=types_dispo, index=0)
        df_filtre = df_cq[df_cq['type'] == type_sel]

        # Histogramme mensuel
        df_filtre['date'] = pd.to_datetime(df_filtre['date'])
        hist_data = df_filtre.groupby(df_filtre['date'].dt.to_period("M")).size().reset_index(name='Nombre')
        hist_data['date'] = hist_data['date'].dt.to_timestamp()

        fig = px.bar(hist_data, x='date', y='Nombre', title=f"Nombre de contrôles qualité ({type_sel}) par mois")
        st.plotly_chart(fig, use_container_width=True)

# --- Page Rappels ---
elif menu == "Rappels":
    st.header("Envoi de Rappels par Email")

    dest = st.text_input("Email destinataire")
    sujet = st.text_input("Sujet", value="Rappel Contrôle Qualité Gamma Caméra")
    message = st.text_area("Message", value="Bonjour,\n\nCeci est un rappel automatique pour effectuer un contrôle qualité.\n\nCordialement,\nMaryam Abia")

    if st.button("Envoyer le rappel"):
        if dest.strip() == "" or sujet.strip() == "" or message.strip() == "":
            st.error("Tous les champs doivent être remplis.")
        else:
            if envoyer_email(dest, sujet, message):
                st.success("Email envoyé avec succès.")

# Footer
st.markdown("""
<div class="footer">
    &copy; 2025 Maryam Abia – Master Instrumentation et Analyse Biomédicale
</div>
""", unsafe_allow_html=True)
