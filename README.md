# Tibi — Erreurs de tri (Recyparc de Ransart)

Dashboard client dédié au suivi des erreurs de tri détectées par la caméra de
surveillance : DEEE, DSM et plastique dur. Connexion : `tibi` /
`tibineurogreen#2026` (stockés dans les secrets Streamlit, pas dans le code).

## Architecture

- **Stockage** : bucket GCS `tibilevel`, préfixe `erreurs_tri/<categorie>/`.
  Réutilise le bucket déjà connecté à `TIBI_Smart_Totem`, avec un compte de
  service dédié en **lecture seule** (`tibi-erreurs-dashboard@fastai-cours`).
- **Métadonnées** : pas de base de données séparée — tout est encodé dans le
  nom du fichier (`common.py` fait le parsing) :
  `surveillance_<date>_frame<N>_conf<confiance>_<timestamp>_<hash>[_valide-<Nom>].jpg`
- **Pages** : `page_files/accueil.py` (vue d'ensemble), `analyse.py`
  (graphiques date × catégorie), `galerie.py` (photos filtrables avec URL
  signées, 1h de validité).

## Ajouter une nouvelle catégorie

Ajouter le nom du dossier GCS dans `CATEGORIES` et son libellé dans
`CATEGORY_LABELS` (`common.py`), puis uploader les images sous
`gs://tibilevel/erreurs_tri/<nouvelle_categorie>/`.

## Brancher les alertes live du Raspberry Pi

Le Pi écrit déjà dans `gs://tibi-recyparc-ransart/` (frames brutes) et a accès
en écriture à `tibilevel`. Pour que ce dashboard affiche les alertes en temps
réel plutôt que le dataset historique :

1. Faire écrire au pipeline de classification les nouvelles détections
   directement sous `gs://tibilevel/erreurs_tri/<categorie>/` avec le même
   format de nom de fichier — aucune modification du dashboard n'est
   nécessaire, `load_erreurs()` les listera automatiquement (cache de 5 min).
2. Si le format de nom change (ex: ajout de métadonnées), mettre à jour
   `FILENAME_RE` dans `common.py`.

## Déploiement (Streamlit Community Cloud)

1. Pousser ce dossier sur GitHub.
2. Sur [share.streamlit.io](https://share.streamlit.io), "New app" → choisir
   le repo, branche, et `TIBI_Erreurs_Tri/dashboard.py` comme fichier
   principal.
3. Dans les "Secrets" de l'app, coller le contenu de
   `.streamlit/secrets.toml.example` complété avec la vraie clé du compte de
   service (fournie séparément, jamais commitée).
