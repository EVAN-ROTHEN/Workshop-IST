---
marp: true
title: "Vertex AI — Cheat sheet"
paginate: false
theme: cheatsheet-a4
---

# Google Vertex AI — Cheat sheet

<span class="meta">HEIG-VD IST 2025/26 · Auteurs : Essinger Benoît &amp; Rothen Evan · Plateforme ML/IA managée de Google Cloud · SDK `google-cloud-aiplatform` · réf. 2026</span>

**Ce que ça fait** — Plateforme **ML/IA unifiée et managée** sur tout le cycle de vie : *data → entraînement (**AutoML** no-code ou **Custom**) → éval → **serving** online/batch → monitoring*, **+ GenAI** (**Model Garden**, **Gemini**, RAG). **Intérêt** : d'un simple CSV à un **modèle déployé en ½ journée**, sans infra ni équipe MLOps. **Entrées** : CSV/Parquet (**GCS**), tables **BigQuery**, images/texte. **Sorties** : **endpoint REST** (temps réel) ou **batch** (→ GCS/BigQuery) + métriques & Explainable AI. **Interfaces** : SDK Python, CLI `gcloud ai`, API REST/gRPC, console, Terraform.

## Concepts à connaître

| Terme | Rôle |
|---|---|
| **Dataset** | Données managées (Tabular, Image, Text, Video) liées à GCS/BigQuery |
| **AutoML** | Entraîne un modèle **sans coder l'algo** — cœur de valeur PME |
| **Custom Training** | Ton code/conteneur (TF, PyTorch, sklearn) quand AutoML ne suffit pas |
| **Model / Registry** | Modèle entraîné, versionné et gouverné |
| **Endpoint** | Modèle déployé pour la prédiction **online** (REST, **facturé 24/7**) |
| **Batch prediction** | Job ponctuel de scoring de masse — **pas de coût permanent** |
| **Pipelines / Feature Store** | MLOps reproductible / features centralisées (avancé) |
| **Model Garden + Gemini** | Catalogue de modèles + API GenAI (pay-per-token) |

## Démarrer (setup, une fois)

```bash
gcloud auth login                                   # s'authentifier (humain)
gcloud auth application-default login               # ADC : credentials pour le SDK Python
gcloud config set project MON_PROJET                # projet par défaut
gcloud config set ai/region europe-west6            # région par défaut (Zurich, data residency)
gcloud services enable aiplatform.googleapis.com storage.googleapis.com bigquery.googleapis.com
gsutil mb -l europe-west6 gs://mon-bucket           # créer un bucket de staging
pip install google-cloud-aiplatform                 # SDK Python
```
<span class="meta">Prérequis : projet GCP avec **facturation activée** · Python 3.9+ · rôle IAM **Vertex AI User** · crédit d'essai **300 $ / 90 j**.</span>

## Workflow Python SDK — cas *churn* (AutoML Tabular)

```python
from google.cloud import aiplatform as aip
aip.init(project="MON_PROJET", location="europe-west6", staging_bucket="gs://mon-bucket")

# 1) Dataset tabulaire depuis un CSV (ou bq://projet.dataset.table)
ds = aip.TabularDataset.create(display_name="clients_churn",
                               gcs_source="gs://mon-bucket/clients.csv")
# 2) Entraînement AutoML (cible = colonne 'churned')
job = aip.AutoMLTabularTrainingJob(display_name="churn-automl",
        optimization_prediction_type="classification",
        optimization_objective="maximize-au-prc")          # classes déséquilibrées
model = job.run(dataset=ds, target_column="churned",
                budget_milli_node_hours=1000)              # 1 node-heure (~21 $)
# 3) Évaluation
for ev in model.list_model_evaluations(): print(dict(ev.metrics).get("auPrc"))
# 4a) Prédiction BATCH (recommandé hors temps réel → bien moins cher)
model.batch_predict(job_display_name="churn-batch", instances_format="csv",
        gcs_source="gs://mon-bucket/a_scorer.csv",
        gcs_destination_prefix="gs://mon-bucket/predictions/")
# 4b) Prédiction ONLINE (temps réel) — PENSE À UNDEPLOY ENSUITE
endpoint = model.deploy(machine_type="n1-standard-4")
endpoint.predict(instances=[{"anciennete_mois": "3", "type_contrat": "mensuel",
                             "facture_mensuelle": "99.9", "nb_tickets_support": "5"}])
endpoint.undeploy_all(); endpoint.delete()                 # 🔴 stoppe la facturation
```

---

## Référence CLI `gcloud ai` <span class="meta">(ajouter `--region=europe-west6` ou fixer `gcloud config set ai/region`)</span>

<div class="cols">
<div>

**Datasets**
| Commande | Effet |
|---|---|
| `gcloud ai datasets list` | lister |
| `gcloud ai datasets create --display-name=N …` | créer un dataset |
| `gcloud ai datasets describe ID` | détails |
| `gcloud ai datasets delete ID` | supprimer |

**Modèles & registry**
| Commande | Effet |
|---|---|
| `gcloud ai models list` | lister les modèles |
| `gcloud ai models describe ID` | détails / versions |
| `gcloud ai models upload --display-name=N …` | importer un modèle custom |
| `gcloud ai models delete ID` | supprimer |

**Prédiction batch & jobs**
| Commande | Effet |
|---|---|
| `gcloud ai batch-prediction-jobs create --model=ID …` | scoring batch |
| `gcloud ai batch-prediction-jobs list` | suivre les jobs batch |
| `gcloud ai custom-jobs create --worker-pool-spec=…` | entraînement custom |
| `gcloud ai custom-jobs stream-logs JOB` | logs d'un job en direct |

</div>
<div>

**Endpoints (serving online)**
| Commande | Effet |
|---|---|
| `gcloud ai endpoints list` | lister les endpoints |
| `gcloud ai endpoints create --display-name=N` | créer un endpoint |
| `gcloud ai endpoints deploy-model EP --model=ID --machine-type=…` | déployer un modèle |
| `gcloud ai endpoints predict EP --json-request=req.json` | prédire (temps réel) |
| `gcloud ai endpoints undeploy-model EP --deployed-model-id=ID` | **🔴 stoppe la facture** |
| `gcloud ai endpoints delete EP` | supprimer l'endpoint |

**Opérations & infos**
| Commande | Effet |
|---|---|
| `gcloud ai operations list` | opérations en cours |
| `gcloud ai operations describe OP` | suivre une opération longue |
| `gcloud ai endpoints describe EP` | modèles déployés sur un endpoint |

</div>
</div>

## GenAI / Gemini (Model Garden)

```python
import vertexai
from vertexai.generative_models import GenerativeModel
vertexai.init(project="MON_PROJET", location="europe-west6")
model = GenerativeModel("gemini-2.5-flash")          # ou gemini-2.5-pro
print(model.generate_content("Explique le churn en une phrase.").text)
# RAG / recherche sémantique : TextEmbeddingModel.from_pretrained("text-embedding-005")
```
<span class="meta">GenAI = **pay-per-token** : Gemini 2.5 Flash ≈ 0,30 $/1M in · Pro ≈ 1,25 $/1M in. Pas d'infra à gérer, pas d'always-on.</span>

## Maîtriser les coûts <span class="meta">(facturation à l'usage, à la seconde — pas d'abonnement)</span>

<div class="cols">
<div>

| Poste | Ordre de grandeur |
|---|---|
| Entraînement AutoML | **≈ 21 $/node-heure** |
| Endpoint online `n1-standard-4` | **≈ 0,22 $/h → ~160 $/mois** 24/7 |
| Prédiction batch | compute du job seulement |
| Gemini (token) | Flash ≈ 0,30 $/1M in |

</div>
<div>

```bash
gcloud ai endpoints list --region=europe-west6   # traquer les endpoints always-on
gcloud billing budgets create --billing-account=ACCT \
  --display-name="vertex" --budget-amount=100USD  # budget + alerte
```

</div>
</div>

<span class="tip">💡 <strong>Scénario PME (churn, ~50k clients, scoring mensuel)</strong> : endpoint online 24/7 ≈ <strong>217 $/mois (~CHF 195)</strong> · en <strong>batch</strong> ≈ <strong>65 $/mois (~CHF 60)</strong>. <strong>Batch vs online divise la facture par ~3</strong> ; un endpoint oublié est le piège n°1 → <code>undeploy</code> systématique.</span>

## Bonnes pratiques & quand l'utiliser

<div class="cols">
<div>

**Bonnes pratiques**
- <span class="pro">Batch par défaut</span> ; online seulement si temps réel requis.
- <span class="pro">`undeploy`/`delete`</span> les endpoints + **budgets/alertes**.
- <span class="pro">Région UE/CH</span> (`europe-west6`) pour la résidence des données.
- <span class="pro">Formats ouverts</span> (Parquet/SQL) → limite le **vendor lock-in**.

</div>
<div>

**Utiliser quand / éviter**
- <span class="pro">Utiliser</span> : déjà sur GCP/BigQuery, pas d'équipe MLOps, besoin d'aller vite, données tabulaires/images.
- <span class="con">Éviter</span> : besoin simple & stable (scikit + cron), trafic faible, exigence forte de portabilité.

</div>
</div>

<span class="meta">Réf. : cloud.google.com/vertex-ai · /docs · /pricing · /docs/tutorials/tabular-automl · SDK python/docs/reference/aiplatform · Model Garden</span>
