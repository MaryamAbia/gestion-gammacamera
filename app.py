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

# CSS style (simplifié ici, adapte selon حاجتك)
st.markdown("""
<style>
.stApp {
    padding: 0 40px 50px 40px !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 18px !important;
    background-color: #f7f7f7;
}
.banner {
    position: relative;
    width: 100%;
    height: 350px !important;
    border-radius: 12px;
    margin-bottom: 40px !important;
    overflow: hidden;
}
.banner img {
    width: 100%;
    height: 100% !important;
    object-fit: cover;
    border-radius: 12px;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 0;
}
.banner-text {
    position: relative;
    z-index: 1;
    background-color: rgba(255, 255, 255, 0.85);
    padding: 30px 50px;
    border-radius: 15px;
    color: #1f005c;
    text-align: center;
    font-size: 36px !important;
    font-weight: 700;
    animation: fadeIn 2s ease-in-out;
    max-width: 900px;
    margin: auto;
    top: 50%;
    transform: translateY(-50%);
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(-20px);}
    to {opacity: 1; transform: translateY(0);}
}
.section-container {
    border-radius: 30px;
    padding: 80px 60px 70px 60px !important;
    margin-bottom: 70px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    color: black;
    background-color: rgba(255, 255, 255, 0.9);
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center;
}
.section-title {
    font-size: 32px !important;
    margin-bottom: 25px !important;
    font-weight: 700;
    color: #1f005c;
    text-align: center;
}
.dataframe-container {
    margin-top: 30px !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")
st.markdown("""
<div class="banner">
    <img src="https://img.freepik.com/premium-photo/chemical-molecule-with-blue-background-3d-rendering_772449-4288.jpg" alt="banner" />
    <div class="banner-text">Bienvenue dans l'interface de gestion - Gamma Caméra</div>
</div>
""", unsafe_allow_html=True)
st.markdown("Développée par **Maryam Abia**")

# --- Fonctions générales pour afficher et modifier des enregistrements ---

def afficher_et_modifier_utilisateurs():
    st.subheader("Ajouter un intervenant")
    nom = st.text_input("Nom complet", key="nom_utilisateur")
    role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"], key="role_utilisateur")
    if st.button("Ajouter l'intervenant", key="btn_ajouter_utilisateur"):
        if nom:
            cursor.execute("INSERT INTO utilisateurs (nom, role) VALUES (?, ?)", (nom, role))
            conn.commit()
            st.success("Intervenant ajouté")

    st.subheader("Liste des intervenants")
    df_users = pd.read_sql("SELECT * FROM utilisateurs ORDER BY id DESC", conn)
    edited_id = None

    for index, row in df_users.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])
        with col1:
            st.write(row['nom'])
        with col2:
            st.write(row['role'])
        with col3:
            if st.button(f"Modifier {row['id']}", key=f"edit_user_{row['id']}"):
                edited_id = row['id']
        with col4:
            if st.button(f"Supprimer {row['id']}", key=f"del_user_{row['id']}"):
                cursor.execute("DELETE FROM utilisateurs WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()

    if edited_id:
        user = cursor.execute("SELECT * FROM utilisateurs WHERE id = ?", (edited_id,)).fetchone()
        if user:
            st.subheader(f"Modifier intervenant: {user[1]}")
            new_nom = st.text_input("Nom complet", value=user[1], key="edit_nom_utilisateur")
            new_role = st.selectbox("Rôle", ["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"], index=["Technicien", "Ingénieur", "Médecin", "Physicien Médical", "Autre"].index(user[2]), key="edit_role_utilisateur")
            if st.button("Enregistrer modifications", key="btn_save_user_edit"):
                cursor.execute("UPDATE utilisateurs SET nom = ?, role = ? WHERE id = ?", (new_nom, new_role, edited_id))
                conn.commit()
                st.success("Intervenant modifié")
                st.experimental_rerun()

def afficher_et_modifier_controles():
    st.subheader("Ajouter un contrôle qualité")
    intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
    if intervenants:
        date = st.date_input("Date du contrôle", value=datetime.now(), key="date_controle")
        type_cq = st.selectbox("Type de contrôle", [
            "Linéarité",
            "Uniformité intrinsèque",
            "Résolution spatiale intrinsèque",
            "Uniformité système avec collimateur",
            "Sensibilité",
            "Résolution énergétique",
            "Centre de rotation"
            ], key="type_controle")
        intervenant = st.selectbox("Intervenant", intervenants, key="intervenant_controle")
        resultat = st.text_area("Résultat ou observation", key="resultat_controle")
        if st.button("Enregistrer le contrôle", key="btn_enregistrer_controle"):
            cursor.execute("INSERT INTO controle_qualite (date, type, intervenant, resultat) VALUES (?, ?, ?, ?)",
                           (date.strftime('%Y-%m-%d'), type_cq, intervenant, resultat))
            conn.commit()
            st.success("Contrôle enregistré")
    else:
        st.warning("⚠️ Veuillez ajouter des intervenants d'abord.")

    st.subheader("Historique des contrôles qualité")
    df_cq = pd.read_sql("SELECT * FROM controle_qualite ORDER BY date DESC", conn)

    edited_id = None

    for index, row in df_cq.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2, 2, 3, 3, 1])
        with col1:
            st.write(row['date'])
        with col2:
            st.write(row['type'])
        with col3:
            st.write(row['intervenant'])
        with col4:
            st.write(row['resultat'])
        with col5:
            if st.button(f"Modifier {row['id']}", key=f"edit_cq_{row['id']}"):
                edited_id = row['id']
        with col6:
            if st.button(f"Supprimer {row['id']}", key=f"del_cq_{row['id']}"):
                cursor.execute("DELETE FROM controle_qualite WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()

    if edited_id:
        cq = cursor.execute("SELECT * FROM controle_qualite WHERE id = ?", (edited_id,)).fetchone()
        if cq:
            st.subheader(f"Modifier contrôle qualité - ID {edited_id}")
            new_date = st.date_input("Date", value=datetime.strptime(cq[1], '%Y-%m-%d'), key="edit_date_cq")
            new_type = st.selectbox("Type de contrôle", [
                "Linéarité",
                "Uniformité intrinsèque",
                "Résolution spatiale intrinsèque",
                "Uniformité système avec collimateur",
                "Sensibilité",
                "Résolution énergétique",
                "Centre de rotation"
                ], index=["Linéarité", "Uniformité intrinsèque", "Résolution spatiale intrinsèque", "Uniformité système avec collimateur", "Sensibilité", "Résolution énergétique", "Centre de rotation"].index(cq[2]), key="edit_type_cq")
            new_intervenant = st.selectbox("Intervenant", intervenants, index=intervenants.index(cq[3]), key="edit_intervenant_cq")
            new_resultat = st.text_area("Résultat / Observation", value=cq[4], key="edit_resultat_cq")
            if st.button("Enregistrer modifications", key="btn_save_cq_edit"):
                cursor.execute("UPDATE controle_qualite SET date = ?, type = ?, intervenant = ?, resultat = ? WHERE id = ?",
                               (new_date.strftime('%Y-%m-%d'), new_type, new_intervenant, new_resultat, edited_id))
                conn.commit()
                st.success("Contrôle qualité modifié")
                st.experimental_rerun()

def afficher_et_modifier_pannes():
    st.subheader("Ajouter une panne")
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

    st.subheader("Historique des pannes")
    df_pannes = pd.read_sql("SELECT * FROM pannes ORDER BY date DESC", conn)
    edited_id = None

    for index, row in df_pannes.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 3, 2, 3, 3, 1])
        with col1:
            st.write(row['date'])
        with col2:
            st.write(row['description'])
        with col3:
            st.write(row['intervenant'])
        with col4:
            st.write(row['action'])
        with col5:
            if st.button(f"Modifier {row['id']}", key=f"edit_panne_{row['id']}"):
                edited_id = row['id']
        with col6:
            if st.button(f"Supprimer {row['id']}", key=f"del_panne_{row['id']}"):
                cursor.execute("DELETE FROM pannes WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()

    if edited_id:
        panne = cursor.execute("SELECT * FROM pannes WHERE id = ?", (edited_id,)).fetchone()
        if panne:
            st.subheader(f"Modifier panne - ID {edited_id}")
            new_date = st.date_input("Date", value=datetime.strptime(panne[1], '%Y-%m-%d'), key="edit_date_panne")
            new_desc = st.text_area("Description", value=panne[2], key="edit_desc_panne")
            intervenants = pd.read_sql("SELECT nom FROM utilisateurs", conn)["nom"].tolist()
            new_intervenant = st.selectbox("Intervenant", intervenants, index=intervenants.index(panne[3]), key="edit_intervenant_panne")
            new_action = st.text_area("Action", value=panne[4], key="edit_action_panne")
            if st.button("Enregistrer modifications", key="btn_save_panne_edit"):
                cursor.execute("UPDATE pannes SET date = ?, description = ?, intervenant = ?, action = ? WHERE id = ?",
                               (new_date.strftime('%Y-%m-%d'), new_desc, new_intervenant, new_action, edited_id))
                conn.commit()
                st.success("Panne modifiée")
                st.experimental_rerun()

def afficher_et_modifier_pieces():
    st.subheader("Ajouter une pièce détachée")
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

    st.subheader("Historique des pièces")
    df_pieces = pd.read_sql("SELECT * FROM pieces_detachees ORDER BY date_commande DESC", conn)
    edited_id = None

    for index, row in df_pieces.iterrows():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,2,2,2,2,1])
        with col1:
            st.write(row['nom'])
        with col2:
            st.write(row['ref'])
        with col3:
            st.write(row['date_commande'])
        with col4:
            st.write(row['fournisseur'])
        with col5:
            st.write(row['date_reception'])
        with col6:
            if st.button(f"Modifier {row['id']}", key=f"edit_piece_{row['id']}"):
                edited_id = row['id']
        with col7:
            if st.button(f"Supprimer {row['id']}", key=f"del_piece_{row['id']}"):
                cursor.execute("DELETE FROM pieces_detachees WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()

    if edited_id:
        piece = cursor.execute("SELECT * FROM pieces_detachees WHERE id = ?", (edited_id,)).fetchone()
        if piece:
            st.subheader(f"Modifier pièce - ID {edited_id}")
            new_nom = st.text_input("Nom pièce", value=piece[1], key="edit_nom_piece")
            new_ref = st.text_input("Référence", value=piece[2], key="edit_ref_piece")
            new_date_cmd = st.date_input("Date commande", value=datetime.strptime(piece[3], '%Y-%m-%d'), key="edit_date_cmd_piece")
            new_fournisseur = st.text_input("Fournisseur", value=piece[4], key="edit_fournisseur_piece")
            new_date_rec = st.date_input("Date réception", value=datetime.strptime(piece[5], '%Y-%m-%d'), key="edit_date_rec_piece")
            if st.button("Enregistrer modifications", key="btn_save_piece_edit"):
                cursor.execute("UPDATE pieces_detachees SET nom = ?, ref = ?, date_commande = ?, fournisseur = ?, date_reception = ? WHERE id = ?",
                               (new_nom, new_ref, new_date_cmd.strftime('%Y-%m-%d'), new_fournisseur, new_date_rec.strftime('%Y-%m-%d'), edited_id))
                conn.commit()
                st.success("Pièce modifiée")
                st.experimental_rerun()

def afficher_et_modifier_documents():
    st.subheader("Ajouter un document")
    nom_doc = st.text_input("Nom du document", key="nom_doc")
    type_doc = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"], key="type_doc")
    fichier = st.file_uploader("Téléverser un fichier", key="file_uploader")
    if fichier and st.button("Enregistrer document", key="btn_enregistrer_doc"):
        blob = fichier.read()
        cursor.execute("INSERT INTO documents (nom, type, fichier) VALUES (?, ?, ?)", (nom_doc, type_doc, blob))
        conn.commit()
        st.success("Document enregistré")

    st.subheader("Liste des documents")
    df_docs = pd.read_sql("SELECT id, nom, type FROM documents ORDER BY id DESC", conn)
    edited_id = None

    for index, row in df_docs.iterrows():
        col1, col2, col3, col4, col5 = st.columns([3,2,2,1,1])
        with col1:
            st.write(row['nom'])
        with col2:
            st.write(row['type'])
        with col3:
            if st.button(f"Télécharger {row['id']}", key=f"download_doc_{row['id']}"):
                # Si besoin, ajouter fonction téléchargement
                st.info("Fonction téléchargement non implémentée.")
        with col4:
            if st.button(f"Modifier {row['id']}", key=f"edit_doc_{row['id']}"):
                edited_id = row['id']
        with col5:
            if st.button(f"Supprimer {row['id']}", key=f"del_doc_{row['id']}"):
                cursor.execute("DELETE FROM documents WHERE id = ?", (row['id'],))
                conn.commit()
                st.experimental_rerun()

    if edited_id:
        doc = cursor.execute("SELECT * FROM documents WHERE id = ?", (edited_id,)).fetchone()
        if doc:
            st.subheader(f"Modifier document - ID {edited_id}")
            new_nom = st.text_input("Nom du document", value=doc[1], key="edit_nom_doc")
            new_type = st.selectbox("Type", ["Protocole", "Contrat", "Notice", "Rapport"], index=["Protocole", "Contrat", "Notice", "Rapport"].index(doc[2]), key="edit_type_doc")
            if st.button("Enregistrer modifications", key="btn_save_doc_edit"):
                cursor.execute("UPDATE documents SET nom = ?, type = ? WHERE id = ?", (new_nom, new_type, edited_id))
                conn.commit()
                st.success("Document modifié")
                st.experimental_rerun()

def rappels_controles():
    st.subheader("Rappels des contrôles")
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

    check_due(df, "Linéarité", 30)
    check_due(df, "Uniformité intrinsèque", 7)
    check_due(df, "Résolution spatiale intrinsèque", 1)
    check_due(df, "Uniformité système avec collimateur", 7)
    check_due(df, "Sensibilité", 30)
    check_due(df, "Résolution énergétique", 365)
    check_due(df, "Centre de rotation", 365)

    if st.button("Envoyer un e-mail de rappel", key="btn_envoyer_rappel"):
        msg = "Bonjour, ceci est un rappel pour effectuer les contrôles Gamma Caméra."
        if envoyer_email("maryamabia01@gmail.com", "Rappel Gamma Caméra", msg):
            st.success("E-mail envoyé")
        else:
            st.error("Erreur lors de l'envoi")

# --- Affichage des sections dans la page unique ---

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">👥 Gestion des intervenants</h2>', unsafe_allow_html=True)
afficher_et_modifier_utilisateurs()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">🗕️ Suivi des contrôles qualité</h2>', unsafe_allow_html=True)
afficher_et_modifier_controles()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">🛠️ Suivi des pannes</h2>', unsafe_allow_html=True)
afficher_et_modifier_pannes()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">🔧 Pièces détachées</h2>', unsafe_allow_html=True)
afficher_et_modifier_pieces()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">📂 Gestion documentaire</h2>', unsafe_allow_html=True)
afficher_et_modifier_documents()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
rappels_controles()
st.markdown('</div>', unsafe_allow_html=True)
