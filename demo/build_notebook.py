"""Construit churn_vertex_ai.ipynb (Colab-ready) à partir de cellules définies ici.

Lance : python build_notebook.py  ->  écrit churn_vertex_ai.ipynb
"""
import json
import os

def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": list(lines)}

def code(*lines):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": list(lines)}

cells = [
    md(
        "# 🎯 Démo Vertex AI — Prédiction de churn (AutoML Tabular)\n",
        "\n",
        "**Workshop IST 2025/26 — HEIG-VD.** Plateforme : Google Vertex AI.\n",
        "\n",
        "On part d'un **CSV de clients** et on obtient un **modèle de churn déployé**, "
        "**sans écrire une seule ligne de modèle ML** — uniquement de la configuration.\n",
        "\n",
        "**Étapes :** 1) Dataset → 2) Entraînement AutoML → 3) Évaluation & importance des features "
        "→ 4) Prédiction (batch *recommandé*, ou endpoint online).\n",
        "\n",
        "> ⚠️ **Coût & durée.** L'entraînement AutoML Tabular dure **~1 à 2 h** et coûte **~21 $/node-heure** "
        "(≈ 20–40 $ ici). Couvert par le **crédit gratuit (300 $)**. **Lancez l'entraînement AVANT la présentation** "
        "et gardez les captures : en live, on montre surtout l'évaluation et la prédiction.\n"
    ),
    md("## 0. Installation & authentification *(Colab)*"),
    code(
        "# Sur Colab uniquement (déjà présent sur Vertex AI Workbench)\n",
        "!pip install -q --upgrade google-cloud-aiplatform google-cloud-storage\n"
    ),
    code(
        "# Authentification\n",
        "import sys\n",
        "if 'google.colab' in sys.modules:\n",
        "    from google.colab import auth\n",
        "    auth.authenticate_user()\n",
        "    print('Authentifié via Colab.')\n",
        "else:\n",
        "    # En local : `gcloud auth application-default login` au préalable\n",
        "    print('Hors Colab : utiliser Application Default Credentials.')\n"
    ),
    md(
        "## 1. Configuration\n",
        "Renseignez votre **ID de projet** et un **bucket** Cloud Storage. Région `europe-west6` "
        "(**Zurich**) pour garder les données en Suisse."
    ),
    code(
        "PROJECT_ID = 'mon-projet-gcp'        # <-- À MODIFIER\n",
        "REGION     = 'europe-west6'          # Zurich\n",
        "BUCKET     = 'gs://mon-bucket-churn' # <-- À MODIFIER (doit exister)\n",
        "\n",
        "from google.cloud import aiplatform as aip\n",
        "aip.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET)\n",
        "print('Vertex AI initialisé sur', PROJECT_ID, REGION)\n"
    ),
    code(
        "# (Optionnel) Activer les APIs et créer le bucket si besoin\n",
        "# !gcloud services enable aiplatform.googleapis.com storage.googleapis.com --project $PROJECT_ID\n",
        "# !gsutil mb -l europe-west6 $BUCKET\n",
        "\n",
        "# Uploader les CSV générés (generate_dataset.py) vers le bucket\n",
        "!gsutil cp data/clients.csv $BUCKET/clients.csv\n",
        "!gsutil cp data/clients_a_scorer.csv $BUCKET/clients_a_scorer.csv\n"
    ),
    md(
        "## 2. Créer le Dataset tabulaire\n",
        "Vertex AI peut lire un CSV sur GCS **ou** une table BigQuery (`bq://projet.dataset.table`)."
    ),
    code(
        "dataset = aip.TabularDataset.create(\n",
        "    display_name='clients_churn',\n",
        "    gcs_source=f'{BUCKET}/clients.csv',\n",
        ")\n",
        "print('Dataset créé :', dataset.resource_name)\n"
    ),
    md(
        "## 3. Entraîner un modèle AutoML Tabular\n",
        "On indique simplement la **colonne cible** (`churned`). Vertex teste plusieurs algos, "
        "fait le feature engineering et sélectionne le meilleur modèle.\n",
        "\n",
        "`budget_milli_node_hours=1000` = **1 node-heure** (minimum, suffisant pour la démo).\n",
        "⏳ **~1–2 h** d'exécution."
    ),
    code(
        "job = aip.AutoMLTabularTrainingJob(\n",
        "    display_name='churn-automl',\n",
        "    optimization_prediction_type='classification',\n",
        "    optimization_objective='maximize-au-prc',  # bon pour classes déséquilibrées\n",
        ")\n",
        "\n",
        "model = job.run(\n",
        "    dataset=dataset,\n",
        "    target_column='churned',\n",
        "    budget_milli_node_hours=1000,      # 1 node-heure (~21 $)\n",
        "    column_transformations=None,        # auto-détection des types\n",
        "    model_display_name='churn-model',\n",
        "    disable_early_stopping=False,\n",
        ")\n",
        "print('Modèle entraîné :', model.resource_name)\n"
    ),
    md(
        "## 4. Évaluation & importance des features\n",
        "C'est ce qui parle au **métier** : quelles variables expliquent le départ des clients ?"
    ),
    code(
        "# Métriques d'évaluation (AUC PR/ROC, précision, rappel, matrice de confusion)\n",
        "for ev in model.list_model_evaluations():\n",
        "    m = dict(ev.metrics)\n",
        "    print('auPrc :', round(m.get('auPrc', 0), 3),\n",
        "          '| auRoc :', round(m.get('auRoc', 0), 3),\n",
        "          '| logLoss :', round(m.get('logLoss', 0), 3))\n",
        "\n",
        "# Importance globale des features (sur la console : onglet 'Feature importance')\n",
        "# Disponible aussi via l'API d'explication selon le type de modèle.\n"
    ),
    md(
        "## 5a. Prédiction BATCH *(recommandée — pas de coût permanent)*\n",
        "Idéal pour un **scoring mensuel** : on lance le job, il écrit les résultats sur GCS, puis s'arrête."
    ),
    code(
        "batch = model.batch_predict(\n",
        "    job_display_name='churn-batch',\n",
        "    gcs_source=f'{BUCKET}/clients_a_scorer.csv',\n",
        "    gcs_destination_prefix=f'{BUCKET}/predictions/',\n",
        "    instances_format='csv',\n",
        "    predictions_format='jsonl',\n",
        "    machine_type='n1-standard-4',\n",
        ")\n",
        "print('Prédictions écrites dans', f'{BUCKET}/predictions/')\n",
        "# -> chaque ligne contient la proba de churn ; trier pour obtenir la liste 'à risque'.\n"
    ),
    md(
        "## 5b. Endpoint ONLINE *(optionnel — temps réel, mais coûteux)*\n",
        "⚠️ Un endpoint est **facturé 24/7 tant qu'il est déployé**, **même sans trafic**. "
        "Toujours **`undeploy`** après la démo."
    ),
    code(
        "endpoint = model.deploy(machine_type='n1-standard-4')\n",
        "\n",
        "pred = endpoint.predict(instances=[{\n",
        "    'anciennete_mois': '3', 'type_contrat': 'mensuel',\n",
        "    'facture_mensuelle': '99.9', 'facture_totale': '299.7',\n",
        "    'nb_tickets_support': '5', 'moyen_paiement': 'cheque',\n",
        "    'support_premium': '0', 'age': '29',\n",
        "}])\n",
        "print('Prédiction :', pred.predictions)\n"
    ),
    code(
        "# 🔴 IMPORTANT : stopper la facturation de l'endpoint\n",
        "endpoint.undeploy_all()\n",
        "endpoint.delete()\n",
        "print('Endpoint déployé puis nettoyé.')\n"
    ),
    md(
        "## 6. Nettoyage & rappel coût\n",
        "```python\n",
        "# model.delete(); dataset.delete()\n",
        "```\n",
        "**Récapitulatif coût (scoring mensuel) :** endpoint 24/7 ≈ **CHF ~195/mois** vs **batch ≈ CHF ~60/mois**.\n",
        "👉 En l'absence de besoin temps réel, **le batch divise la facture par ~3**.\n"
    ),
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, "churn_vertex_ai.ipynb")
with open(out, "w") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Notebook écrit :", out, "—", len(cells), "cellules")
