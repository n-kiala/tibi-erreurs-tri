import streamlit as st

from common import CATEGORIES, CATEGORY_LABELS, assign_sequence_id, load_erreurs, signed_url

st.set_page_config(page_title="Changement comportemental", layout="wide")
st.title("Changement comportemental")

st.markdown(
    """
    Cette page permettra, à terme, de mesurer si une alerte modifie réellement
    le geste de tri de l'usager. Pour chaque alerte, la caméra capture une
    **séquence de plusieurs images rapprochées** : en les visionnant dans
    l'ordre, on peut observer si la personne corrige son geste (ex. repose
    l'objet dans le bon conteneur) ou non.

    Aucun suivi comportemental n'est encore quantifié — cette étape nécessite
    une relecture (manuelle ou automatisée) de chaque séquence. La visionneuse
    ci-dessous sert de première brique pour cette relecture : elle permet de
    parcourir, alerte par alerte, la séquence d'images correspondante. Une fois
    les séquences codées (comportement corrigé ou non), les indicateurs de
    pertinence de l'outil (taux de correction, évolution dans le temps, etc.)
    pourront être calculés et affichés ici.
    """
)

try:
    df = load_erreurs()
except Exception as e:
    st.error(f"Erreur de connexion au stockage cloud : {e}")
    st.stop()

if df.empty:
    st.warning("Aucune erreur trouvée dans le stockage cloud.")
    st.stop()

df = assign_sequence_id(df, max_gap=20)

st.markdown("---")
st.sidebar.header("Filtres")

categorie_choisie = st.sidebar.selectbox(
    "Type de déchet",
    options=CATEGORIES,
    format_func=lambda c: CATEGORY_LABELS[c],
)
df_categorie = df[df["categorie"] == categorie_choisie]

jours_disponibles = sorted(df_categorie["date"].unique(), reverse=True)
if not jours_disponibles:
    st.info("Aucune séquence disponible pour cette catégorie.")
    st.stop()

jour_choisi = st.sidebar.selectbox(
    "Jour",
    options=jours_disponibles,
    format_func=lambda d: d.strftime("%d/%m/%Y"),
)
df_jour = df_categorie[df_categorie["date"] == jour_choisi]

sequences = df_jour.groupby("sequence_id").agg(
    nb_images=("frame", "count"),
    premiere_frame=("frame", "min"),
    derniere_frame=("frame", "max"),
)
sequences = sequences.sort_values("premiere_frame")

if sequences.empty:
    st.info("Aucune séquence disponible pour ce jour.")
    st.stop()

options_sequence = list(sequences.index)
sequence_choisie = st.selectbox(
    "Alerte à visionner",
    options=options_sequence,
    format_func=lambda sid: (
        f"Frames {sequences.loc[sid, 'premiere_frame']}–{sequences.loc[sid, 'derniere_frame']} "
        f"({sequences.loc[sid, 'nb_images']} image(s))"
    ),
)

df_sequence = df_jour[df_jour["sequence_id"] == sequence_choisie].sort_values("frame")

st.write(
    f"**{len(df_sequence)} image(s)** dans cette séquence, du "
    f"{jour_choisi.strftime('%d/%m/%Y')}."
)

if len(df_sequence) == 1:
    st.info(
        "Cette alerte ne contient qu'une seule image : impossible d'observer "
        "une évolution du comportement sur cette séquence."
    )

st.write("---")

colonnes = st.columns(min(len(df_sequence), 5))
for index, (_, row) in enumerate(df_sequence.iterrows()):
    with colonnes[index % len(colonnes)]:
        with st.container(border=True):
            try:
                st.image(signed_url(row["blob_name"]), use_container_width=True)
            except Exception:
                st.warning("Image indisponible")
            st.caption(f"Frame {row['frame']}")
