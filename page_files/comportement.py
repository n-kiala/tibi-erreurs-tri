import streamlit as st

st.set_page_config(page_title="Changement comportemental", layout="wide")
st.title("Changement comportemental")

st.markdown(
    """
    Cette page permettra, à terme, de mesurer si une alerte modifie réellement
    le geste de tri de l'usager.

    Pour chaque alerte, la caméra capture une **séquence de plusieurs images
    rapprochées**. En les visionnant dans l'ordre, il sera possible d'observer
    si la personne corrige son geste  ou non.

   
    """
)
