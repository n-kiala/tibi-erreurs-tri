import streamlit as st

st.set_page_config(page_title="Tibi — Erreurs de tri", layout="wide", page_icon="logo_tibi.png")


def check_login():
    """Retourne True si l'utilisateur est authentifié."""

    if st.session_state.get("connecte"):
        return True

    col_gauche, col_centre, col_droite = st.columns([1, 1, 1])
    with col_centre:
        st.image("logo_tibi.png", width=120)
        st.title("Accès client")
        st.caption("Portail Tibi — Suivi des erreurs de tri du Recyparc de Ransart")

        with st.form("login_form"):
            nom_utilisateur = st.text_input("Nom d'utilisateur")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)

            if submit:
                if (
                    nom_utilisateur == st.secrets["tibi_username"]
                    and mot_de_passe == st.secrets["tibi_password"]
                ):
                    st.session_state["connecte"] = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects ❌")

    return False


if check_login():
    with st.sidebar:
        st.image("logo_neurogreen.png", width=140)
        st.markdown("---")
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state["connecte"] = False
            st.rerun()

    page_accueil = st.Page("page_files/accueil.py", title="Vue d'ensemble", icon=":material/home:")
    page_analyse = st.Page("page_files/analyse.py", title="Analyse des erreurs", icon=":material/monitoring:")
    page_galerie = st.Page("page_files/galerie.py", title="Galerie photos", icon=":material/photo_library:")

    pg = st.navigation([page_accueil, page_analyse, page_galerie])
    pg.run()
