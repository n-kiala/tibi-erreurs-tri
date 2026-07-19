import re
import datetime
from dataclasses import dataclass

import pandas as pd
import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account

BUCKET_NAME = "tibilevel"
PREFIX = "erreurs_tri/"

CATEGORIES = ["DEEE", "DSM", "plastique_dur"]

CATEGORY_LABELS = {
    "DEEE": "DEEE (déchets électriques et électroniques)",
    "DSM": "DSM (déchets spéciaux ménagers)",
    "plastique_dur": "Plastique dur",
}

VERT_PRINCIPAL = "#4CAF50"
VERT_CLAIR = "#81C784"
PALETTE = [VERT_PRINCIPAL, "#2E7D32", VERT_CLAIR]

# Décalage d'affichage : les dates réelles (capturées en 2025) sont translatées
# pour que la plus récente tombe sur cette date, en conservant l'écart entre elles.
DATE_ANCHOR = datetime.date(2026, 7, 17)

FILENAME_RE = re.compile(
    r"^surveillance_(?P<date>\d{4}-\d{2}-\d{2})"
    r"_frame(?P<frame>\d+)"
    r"_conf(?P<conf>\d+)"
    r"_(?P<ts>\d+)"
    r"_(?P<hash>[0-9a-f]+)"
    r"(?:_\d{6})?"
    r"(?:_valide-(?P<validator>[^.]+))?"
    r"\.jpg$",
    re.IGNORECASE,
)


@st.cache_resource
def get_storage_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    return storage.Client(credentials=credentials, project=creds_dict["project_id"])


@dataclass
class Erreur:
    categorie: str
    date: datetime.date
    frame: int
    confiance: int
    validateur: str | None
    blob_name: str


@st.cache_data(ttl=300)
def load_erreurs() -> pd.DataFrame:
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)

    rows = []
    for categorie in CATEGORIES:
        blobs = bucket.list_blobs(prefix=f"{PREFIX}{categorie}/")
        for blob in blobs:
            filename = blob.name.split("/")[-1]
            match = FILENAME_RE.match(filename)
            if not match:
                continue
            rows.append(
                {
                    "categorie": categorie,
                    "date": datetime.date.fromisoformat(match.group("date")),
                    "frame": int(match.group("frame")),
                    "confiance": int(match.group("conf")),
                    "validateur": match.group("validator"),
                    "valide": match.group("validator") is not None,
                    "blob_name": blob.name,
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        offset = DATE_ANCHOR - df["date"].max()
        df["date"] = df["date"] + offset

    return df


def assign_sequence_id(df: pd.DataFrame, max_gap: int = 20) -> pd.DataFrame:
    """Regroupe en une même séquence les frames rapprochées (même jour, même
    catégorie) : elles correspondent probablement à une seule et même alerte."""
    if df.empty:
        df = df.copy()
        df["sequence_id"] = pd.Series(dtype=int)
        return df

    df = df.sort_values(["categorie", "date", "frame"]).copy()
    sequence_ids = []
    compteur = 0
    cle_precedente = None
    frame_precedente = None
    for _, row in df.iterrows():
        cle = (row["categorie"], row["date"])
        if cle != cle_precedente or row["frame"] - frame_precedente >= max_gap:
            compteur += 1
        sequence_ids.append(compteur)
        cle_precedente = cle
        frame_precedente = row["frame"]

    df["sequence_id"] = sequence_ids
    return df


def dedupe_by_frame_gap(df: pd.DataFrame, min_gap: int = 20) -> pd.DataFrame:
    """Ne garde que la première image de chaque séquence rapprochée."""
    if df.empty:
        return df

    df = assign_sequence_id(df, max_gap=min_gap)
    return df.groupby("sequence_id", as_index=False).first()


@st.cache_data(ttl=3000)
def signed_url(blob_name: str) -> str:
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(hours=1),
        method="GET",
    )
