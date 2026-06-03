# Démo — Prédiction de churn avec Vertex AI (AutoML Tabular)

Objectif : montrer qu'on passe d'un **CSV clients** à un **modèle de churn déployé**
**sans coder de modèle ML**, et illustrer au passage forces *et* faiblesses de Vertex AI.

## Contenu
| Fichier | Rôle |
|---|---|
| `generate_dataset.py` | Génère un dataset churn synthétique réaliste |
| `data/clients.csv` | 4 000 clients **avec** label `churned` (entraînement) |
| `data/clients_a_scorer.csv` | 500 clients **sans** label (à prédire) |
| `churn_vertex_ai.ipynb` | Notebook Colab : dataset → AutoML → éval → prédiction |
| `build_notebook.py` | Régénère le notebook si besoin |

## Prérequis
- Projet Google Cloud avec **facturation activée** (crédit gratuit 300 $ suffit).
- APIs activées : `aiplatform.googleapis.com`, `storage.googleapis.com`.
- Un **bucket** Cloud Storage en `europe-west6` (Zurich).
- Au choix : **Google Colab** (le plus simple) ou Vertex AI Workbench.

## Marche à suivre
```bash
# 1. (local) générer les données
python generate_dataset.py

# 2. ouvrir churn_vertex_ai.ipynb dans Colab
#    - renseigner PROJECT_ID et BUCKET
#    - exécuter les cellules dans l'ordre
```

## ⏱️ Timing & coût — À LIRE AVANT LA PRÉSENTATION
- L'entraînement AutoML dure **~1 à 2 h** → **à lancer la veille**, pas en live.
- Coût indicatif : entraînement ~20–40 $, batch quelques $, **endpoint ≈ 0,22 $/h** (à supprimer après).
- **Toujours** exécuter `endpoint.undeploy_all()` / `endpoint.delete()` après la démo.
- Mettre un **budget + alerte** de facturation sur le projet par sécurité.

## Plan de secours (si pas de live / Wi-Fi capricieux)
Préparer des **captures d'écran** de la console Vertex AI :
1. le **Dataset** tabulaire (colonnes détectées),
2. l'écran d'**entraînement terminé**,
3. l'onglet **Évaluation** (auPRC/auROC, matrice de confusion),
4. l'onglet **Feature importance** (variables explicatives),
5. le résultat de la **prédiction batch** (proba de churn par client).

> Conseil démo : montrer surtout **(3) évaluation**, **(4) importance des features** (ça parle au métier)
> et **(5) prédiction**. L'entraînement, on l'a déjà lancé.

## Script de démo (~2,5 min, à insérer après la slide « 🎬 Démo »)
1. « Voici nos données : un simple CSV de 4 000 clients. » *(montrer 3-4 lignes)*
2. « On crée un Dataset Vertex et on lance AutoML en lui disant juste : la cible, c'est `churned`. » *(montrer la cellule + la console)*
3. « Une heure plus tard, voici le modèle. Regardez l'évaluation : auPRC ~0.8x. » *(onglet Évaluation)*
4. « Et surtout, les features qui expliquent le churn : ancienneté faible, contrat mensuel, tickets support. » *(Feature importance)* → **insight métier**
5. « On score les clients actuels en **batch** → liste des clients à risque pour l'équipe rétention. »
6. « Bilan : zéro code de modèle, ~½ journée. Le revers : ce modèle vit dans Vertex (lock-in) et l'endpoint coûte cher si on le laisse tourner. »
