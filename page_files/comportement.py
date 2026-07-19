import streamlit as st

st.set_page_config(page_title="Changement comportemental", layout="wide")
st.title("Changement comportemental")

st.markdown(
    """
    Cette page permettra, à terme, de mesurer si une alerte modifie réellement
    le geste de tri de l'usager.

    Pour chaque alerte, la caméra capture une **séquence de plusieurs images
    rapprochées**. En les visionnant dans l'ordre, il sera possible d'observer
    si la personne corrige son geste (par exemple en reposant l'objet dans le
    bon conteneur) ou non.

    Aucun suivi comportemental n'est encore disponible : cette fonctionnalité
    nécessite au préalable une relecture, manuelle ou automatisée, de chaque
    séquence d'images. Une fois cette relecture réalisée, les indicateurs de
    pertinence de l'outil — taux de correction, évolution dans le temps, etc. —
    pourront être calculés et affichés ici.
    """
)
