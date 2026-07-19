import streamlit as st

from common import CATEGORIES, CATEGORY_LABELS, load_erreurs

col_logo1, col_vide, col_logo2 = st.columns([1, 2, 1])

with col_logo1:
    st.image("logo_neurogreen.png", width=150)

with col_logo2:
    st.image("logo_tibi.png", width=150)

st.markdown("---")

st.markdown(
    "<h1 style='text-align: center;'>Erreurs de tri — Recyparc de Ransart</h1>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

col_gauche, col_texte, col_droite = st.columns([1, 6, 1])
with col_texte:
    st.markdown(
        """
        <div style="text-align: justify; line-height: 1.6; font-size: 1.1em;">
        Ce dashboard présente les erreurs de tri détectées par le système de surveillance
        du Recyparc de Ransart, dans le cadre du partenariat entre Tibi et Neurogreen.
        Trois flux sont suivis ici : les DEEE (déchets électriques et électroniques),
        les DSM (déchets spéciaux ménagers) et le plastique dur. Chaque détection peut être
        consultée avec sa date, son niveau de confiance et, lorsqu'elle a été relue par un
        opérateur, le nom de la personne l'ayant validée.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

try:
    df = load_erreurs()
except Exception as e:
    st.error(f"Erreur de connexion au stockage cloud : {e}")
    st.stop()

st.subheader("Vue d'ensemble")
cols = st.columns(len(CATEGORIES) + 1)

with cols[0]:
    st.metric("Total des erreurs", len(df))

for col, categorie in zip(cols[1:], CATEGORIES):
    with col:
        st.metric(CATEGORY_LABELS[categorie], int((df["categorie"] == categorie).sum()))

if not df.empty:
    st.caption(
        f"Période couverte : du {df['date'].min().strftime('%d/%m/%Y')} "
        f"au {df['date'].max().strftime('%d/%m/%Y')}."
    )
