import pandas as pd
import plotly.express as px
import streamlit as st

from common import CATEGORIES, CATEGORY_LABELS, load_erreurs

st.set_page_config(page_title="Analyse des erreurs de tri", layout="wide")

CATEGORY_COLORS = {
    "DEEE": "#2a78d6",
    "DSM": "#008300",
    "plastique_dur": "#e87ba4",
}

try:
    df = load_erreurs()
except Exception as e:
    st.error(f"Erreur de connexion au stockage cloud : {e}")
    st.stop()

if df.empty:
    st.warning("Aucune erreur trouvée dans le stockage cloud.")
    st.stop()

col_titre, col_date = st.columns([3, 1])
with col_titre:
    st.title("Analyse des erreurs de tri")

min_date, max_date = df["date"].min(), df["date"].max()
with col_date:
    date_range = st.date_input(
        "Sélectionnez la période",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
else:
    df_filtered = df

col_filtre, _, _ = st.columns([1, 1, 2])
with col_filtre:
    categories_selectionnees = st.multiselect(
        "Type de déchet",
        options=CATEGORIES,
        default=CATEGORIES,
        format_func=lambda c: CATEGORY_LABELS[c],
    )

if categories_selectionnees:
    df_filtered = df_filtered[df_filtered["categorie"].isin(categories_selectionnees)]

st.markdown("---")
cols = st.columns(len(CATEGORIES) + 1)
with cols[0]:
    st.metric("Total (période sélectionnée)", len(df_filtered))
for col, categorie in zip(cols[1:], CATEGORIES):
    with col:
        st.metric(categorie, int((df_filtered["categorie"] == categorie).sum()))

st.markdown("---")

# ==========================================
# Évolution du nombre d'erreurs dans le temps
# ==========================================
st.subheader("Évolution du nombre d'erreurs détectées")

df_tendance = (
    df_filtered.groupby(["date", "categorie"]).size().reset_index(name="Nombre d'erreurs")
)

if not df_tendance.empty:
    fig1 = px.line(
        df_tendance,
        x="date",
        y="Nombre d'erreurs",
        color="categorie",
        category_orders={"categorie": CATEGORIES},
        color_discrete_map=CATEGORY_COLORS,
        markers=True,
        labels={"date": "", "categorie": "Type de déchet"},
    )
    fig1.update_traces(line_width=2, marker_size=8)
    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        legend_title_text="Type de déchet",
        hovermode="x unified",
    )
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("Voir les données sous forme de tableau"):
        st.dataframe(
            df_tendance.pivot(index="date", columns="categorie", values="Nombre d'erreurs").fillna(0).astype(int),
            use_container_width=True,
        )
else:
    st.info("Aucune donnée disponible pour ce graphique.")

st.markdown("---")

# ==========================================
# Répartition par flux + statut de validation
# ==========================================
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("Répartition par flux")
    df_repartition = df_filtered.groupby("categorie").size().reset_index(name="Nombre d'erreurs")
    if not df_repartition.empty:
        fig2 = px.bar(
            df_repartition,
            x="categorie",
            y="Nombre d'erreurs",
            color="categorie",
            category_orders={"categorie": CATEGORIES},
            color_discrete_map=CATEGORY_COLORS,
            labels={"categorie": ""},
        )
        fig2.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Aucune donnée disponible.")

with col_graph2:
    st.subheader("Détections relues par un opérateur")
    df_filtered = df_filtered.copy()
    df_filtered["Statut"] = df_filtered["valide"].map({True: "Validée", False: "Non relue"})
    df_statut = df_filtered.groupby(["categorie", "Statut"]).size().reset_index(name="Nombre")
    if not df_statut.empty:
        fig3 = px.bar(
            df_statut,
            x="categorie",
            y="Nombre",
            color="Statut",
            category_orders={"categorie": CATEGORIES},
            color_discrete_map={"Validée": "#008300", "Non relue": "#c3c2b7"},
            barmode="stack",
            labels={"categorie": ""},
        )
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            legend_title_text="Statut",
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Aucune donnée disponible.")
