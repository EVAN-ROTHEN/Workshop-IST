# Notes de recherche — Google Vertex AI

> Document de travail interne (non rendu). Sert de base factuelle aux slides + cheat sheet
> et de fiche de révision pour les 6 minutes de questions.
> Sources et chiffres : Google Cloud + comparatifs publics, état ~mai 2026.

## 1. Qu'est-ce que Vertex AI ?

Plateforme **ML/IA managée et unifiée** de Google Cloud (lancée en mai 2021, fusion d'AI Platform
+ AutoML). Couvre **tout le cycle de vie** d'un modèle dans une seule console / un seul SDK :

```
Data → Feature Eng. → Train (AutoML / Custom) → Évaluer → Déployer → Servir → Monitorer → Réentraîner
```

Depuis 2023-2024, fort virage **GenAI** : **Model Garden** (catalogue de modèles : Gemini, Llama,
Claude via partenariat, modèles open source), **Vertex AI Studio**, **RAG Engine**, **Agent Builder**.
=> Vertex AI = à la fois plateforme "MLOps classique" ET plateforme "GenAI d'entreprise".

### Composants — lecture critique (important vs secondaire)

| Brique | Rôle | Importance pour une PME |
|---|---|---|
| **AutoML** (Tabular, Image, Text, Video) | Entraîne un modèle sans coder le modèle | ⭐⭐⭐ Cœur de valeur pour PME sans data scientists |
| **Custom Training** | Entraînement de code perso (conteneur), TF/PyTorch/sklearn | ⭐⭐ Quand AutoML ne suffit pas |
| **Prediction / Endpoints** | Servir le modèle : online (REST temps réel) ou batch | ⭐⭐⭐ Mais piège de coût (always-on) |
| **Model Registry** | Versionner / gouverner les modèles | ⭐⭐ Gouvernance |
| **Pipelines** (Kubeflow/TFX) | Orchestration MLOps reproductible | ⭐⭐ Utile à maturité, complexe au début |
| **Feature Store** | Centraliser/servir les features | ⭐ Souvent surdimensionné pour une PME |
| **Model Garden + Gemini** | Catalogue + API GenAI | ⭐⭐⭐ Très actuel, mais surtout du pay-per-token |
| **Workbench** | Notebooks managés (JupyterLab) | ⭐⭐ Dev/exploration |
| **Model Monitoring** | Détection de dérive (drift/skew) | ⭐⭐ Important en prod |
| **Vizier** | Optimisation d'hyperparamètres | ⭐ Avancé |
| **Explainable AI** | Importance des features / attributions | ⭐⭐ Confiance & conformité |

### Comment ça interagit avec le monde extérieur
- **Entrées** : CSV/Parquet sur **Cloud Storage**, tables **BigQuery**, images/textes ; via console,
  **SDK Python** (`google-cloud-aiplatform`), **`gcloud`**, **API REST/gRPC**, Terraform.
- **Sorties** : **endpoint REST** (online), fichiers de prédictions (batch, vers GCS/BigQuery),
  modèle exporté (selon le type), métriques d'évaluation, attributions Explainable AI.

## 2. Tarifs (référence 2026, USD ; ~1 USD ≈ 0.90 CHF)

> Principe : pas d'abonnement, **paiement à l'usage**, facturation à la seconde (incréments 30 s)
> pour train/predict. La plateforme elle-même est gratuite, on paie le **compute + stockage**.

- **AutoML Tabular — entraînement** : **21,252 $ / node-heure**. Coût = budget de node-heures × prix.
  Pas facturé si l'entraînement échoue (sauf annulation utilisateur).
- **Prédiction online (endpoint)** : on paie la **VM tant que le modèle est déployé**, même sans trafic.
  Ex. `n1-standard-4` ≈ **0,219 $/h** → **~160 $/mois en 24/7**. Il faut **undeploy** pour stopper la facture.
- **Prédiction batch** : facturée au compute du job (quelques node-heures), **pas de coût permanent**.
- **Gemini sur Vertex AI** (pay-per-token, par M de tokens) :
  - Gemini 2.5 Pro : ~1,25 $ in / 10,00 $ out
  - Gemini 2.5 Flash : ~0,30 $ in / 2,50 $ out
  - Gemini 2.5 Flash-Lite : ~0,10 $ in / 0,40 $ out
- **Stockage** : Cloud Storage / BigQuery facturés à part (faible pour une PME, ~quelques $/mois).
- **Crédit gratuit** : essai Google Cloud **300 $ / 90 jours** (couvre largement la démo).

### Scénario de coût — PME "churn" (inventé, réaliste)
Hypothèses : ~50 000 clients, **réentraînement mensuel**, scoring **mensuel**, 1 dev occasionnel.

| Poste | Online endpoint 24/7 | Batch mensuel |
|---|---|---|
| Entraînement AutoML (~2 node-h/mois) | ~42 $ | ~42 $ |
| Servir le modèle | endpoint n1-std-4 24/7 ≈ **160 $** | batch ~1-3 node-h ≈ **8 $** |
| Stockage (GCS+BigQuery) | ~5 $ | ~5 $ |
| Workbench (dev, éteint la plupart du temps) | ~10 $ | ~10 $ |
| **Total / mois** | **≈ 217 $ ≈ CHF ~195** | **≈ 65 $ ≈ CHF ~60** |

**Enseignement clé** : pour un scoring **mensuel**, l'endpoint online **quadruple** la facture.
Choisir **batch** quand on n'a pas besoin de temps réel = principal levier d'économie.

## 3. Bénéfices (vrais)
- **Time-to-model** très court avec AutoML : un CSV → modèle déployable sans écrire de modèle.
- **Managé de bout en bout** : pas d'infra/MLOps à maintenir ; scaling automatique.
- **Unifié** : data (BigQuery), train, serve, monitor, GenAI dans une seule plateforme/SDK.
- **Intégration GCP native** : BigQuery, Cloud Storage, IAM, logging.
- **GenAI d'entreprise** : accès Gemini + Model Garden avec contrôle, data residency, MLOps.
- **Qualité AutoML** souvent compétitive face à un modèle "fait maison" non optimisé.

## 4. Limites / faiblesses (critique honnête)
- **Coût peu prévisible** : endpoints always-on, node-heures, tokens → factures qui dérapent vite.
- **Boîte noire AutoML** : peu de contrôle sur l'algo ; Explainable AI atténue mais ne supprime pas.
- **Vendor lock-in** (voir §5).
- **Courbe d'apprentissage** sur les briques avancées (Pipelines, Feature Store) ; doc dense.
- **Renommages/réorganisations fréquents** des produits Google → confusion, tutos périmés.
- **Quotas & régions** : tout n'est pas disponible partout ; data residency à vérifier (Suisse/UE).
- **Overkill pour petits besoins** : un scikit-learn + cron peut suffire et coûter ~0.

## 5. Vendor lock-in
| Niveau | Élément |
|---|---|
| 🔴 Fort | AutoML (modèle non exportable de façon réutilisable hors GCP), Feature Store, Pipelines spécifiques, APIs Gemini propriétaires |
| 🟠 Moyen | Endpoints, format des datasets, SDK `aiplatform` |
| 🟢 Faible | Custom training (ton code/conteneur), données dans GCS/BigQuery (exportables), modèles open source du Model Garden |

**Mitigations** : garder données + features en formats ouverts (Parquet/SQL) ; privilégier
**custom training** + conteneurs portables si la portabilité compte ; isoler les appels Vertex
derrière une **couche d'abstraction** ; éviter les services les plus propriétaires pour le cœur métier.

## 6. Alternatives & positionnement
| Solution | Positionnement vs Vertex AI |
|---|---|
| **AWS SageMaker** | Équivalent direct, écosystème AWS, plus de briques mais plus complexe |
| **Azure Machine Learning** | Équivalent direct, fort en intégration entreprise Microsoft |
| **Databricks (MLflow)** | Orienté data+ML lakehouse, multi-cloud, moins "no-code" |
| **Open source** (scikit-learn, MLflow, FastAPI, Airflow) | Coût infra minimal, contrôle total, mais tout à construire/maintenir |
| **Hugging Face / OpenAI / Anthropic API** | Pour la GenAI pure sans plateforme MLOps complète |

## 7. Quand utiliser / quand éviter
**Utiliser quand** : déjà sur GCP/BigQuery ; pas (ou peu) d'équipe MLOps ; besoin d'aller vite ;
données tabulaires/images standard ; besoin GenAI d'entreprise gouvernée ; charge variable.

**Éviter quand** : besoin simple et stable (scikit + cron suffit) ; budget serré et trafic faible
(endpoint = piège) ; exigence forte de portabilité/souveraineté ; besoin de contrôle fin sur l'algo ;
multi-cloud imposé.

## 8. Références (à mettre sur les slides)
- Vertex AI — site officiel : https://cloud.google.com/vertex-ai
- Documentation : https://cloud.google.com/vertex-ai/docs
- Tarifs : https://cloud.google.com/vertex-ai/pricing
- Tuto AutoML Tabular : https://cloud.google.com/vertex-ai/docs/tutorials/tabular-automl
- SDK Python : https://cloud.google.com/python/docs/reference/aiplatform/latest
- Model Garden : https://cloud.google.com/model-garden
