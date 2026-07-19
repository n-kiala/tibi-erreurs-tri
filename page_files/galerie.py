import streamlit as st

from common import CATEGORIES, CATEGORY_LABELS, load_erreurs, signed_url

st.set_page_config(page_title="Galerie des erreurs", layout="wide")
st.title("Galerie des erreurs détectées")
st.caption("Consultez les photos prises par la caméra de surveillance pour chaque erreur de tri.")

try:
    df = load_erreurs()
except Exception as e:
    st.error(f"Erreur de connexion au stockage cloud : {e}")
    st.stop()

if df.empty:
    st.warning("Aucune erreur trouvée dans le stockage cloud.")
    st.stop()

PAGE_SIZE = 24

st.sidebar.header("Filtres")

categorie_choisie = st.sidebar.selectbox(
    "Type de déchet",
    options=CATEGORIES,
    format_func=lambda c: CATEGORY_LABELS[c],
)

df_categorie = df[df["categorie"] == categorie_choisie]

jours_disponibles = sorted(df_categorie["date"].unique(), reverse=True)
jour_choisi = st.sidebar.selectbox(
    "Jour",
    options=["Tous les jours"] + list(jours_disponibles),
    format_func=lambda d: d if isinstance(d, str) else d.strftime("%d/%m/%Y"),
)

if jour_choisi != "Tous les jours":
    df_categorie = df_categorie[df_categorie["date"] == jour_choisi]

confiance_min = st.sidebar.slider("Confiance minimale (%)", 0, 100, 0)
df_categorie = df_categorie[df_categorie["confiance"] >= confiance_min]

statut_choisi = st.sidebar.radio(
    "Statut",
    options=["Toutes", "Validées uniquement", "Non relues uniquement"],
)
if statut_choisi == "Validées uniquement":
    df_categorie = df_categorie[df_categorie["valide"]]
elif statut_choisi == "Non relues uniquement":
    df_categorie = df_categorie[~df_categorie["valide"]]

df_categorie = df_categorie.sort_values("date", ascending=False)

st.markdown("---")
st.write(f"**{len(df_categorie)} photo(s)** trouvée(s) pour *{CATEGORY_LABELS[categorie_choisie]}*.")

if df_categorie.empty:
    st.info("Aucune photo ne correspond aux filtres sélectionnés.")
    st.stop()

if "galerie_page" not in st.session_state:
    st.session_state["galerie_page"] = 0

nb_pages = max(1, (len(df_categorie) - 1) // PAGE_SIZE + 1)
st.session_state["galerie_page"] = min(st.session_state["galerie_page"], nb_pages - 1)

col_prev, col_page, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("← Précédent", disabled=st.session_state["galerie_page"] == 0):
        st.session_state["galerie_page"] -= 1
        st.rerun()
with col_page:
    st.markdown(
        f"<div style='text-align:center;'>Page {st.session_state['galerie_page'] + 1} / {nb_pages}</div>",
        unsafe_allow_html=True,
    )
with col_next:
    if st.button("Suivant →", disabled=st.session_state["galerie_page"] >= nb_pages - 1):
        st.session_state["galerie_page"] += 1
        st.rerun()

debut = st.session_state["galerie_page"] * PAGE_SIZE
page_df = df_categorie.iloc[debut : debut + PAGE_SIZE]

st.write("---")

colonnes = st.columns(4)
for index, (_, row) in enumerate(page_df.iterrows()):
    with colonnes[index % 4]:
        with st.container(border=True):
            try:
                st.image(signed_url(row["blob_name"]), use_container_width=True)
            except Exception:
                st.warning("Image indisponible")

            st.markdown(f"**📅 {row['date'].strftime('%d/%m/%Y')}** · frame {row['frame']}")
            st.markdown(f"🎯 Confiance : {row['confiance']}%")
            if row["valide"]:
                st.markdown(f"✅ Validée par **{row['validateur']}**")
            else:
                st.markdown("⏳ Non relue par un opérateur")
