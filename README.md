# Workshop IST 2025/26 — Google Vertex AI

Évaluation critique de **Google Vertex AI** (plateforme ML/IA managée) pour une PME suisse,
avec démo d'un cas d'usage **prédiction de churn** (AutoML Tabular).

## Livrables (à rendre le 12 juin 2026, 16:15)
| Livrable | Source | PDF |
|---|---|---|
| Slides de présentation (~12 min) | `slides/presentation.md` | `slides/presentation.pdf` |
| Cheat sheet (max 2 pages) | `cheatsheet/cheatsheet.md` | `cheatsheet/cheatsheet.pdf` |

## Structure
```
slides/          présentation Marp (Markdown -> PDF)
cheatsheet/      cheat sheet Marp (Markdown -> PDF, A4 portrait)
demo/            notebook de démo churn + dataset synthétique
assets/          schémas (SVG)
research/        notes de recherche (factuel, prix, alternatives) — non rendu
```

## Générer les PDF
Nécessite Node + un Chrome/Chromium (téléchargeable via puppeteer).
```bash
# Chromium (une fois)
npx -y puppeteer browsers install chrome

# Export (le Makefile gère le chemin de Chrome automatiquement)
make pdf          # slides + cheat sheet
make slides       # slides uniquement
make cheatsheet   # cheat sheet uniquement
```

## Préparer la démo
Voir `demo/README.md` (timing, coûts, plan de secours, script de démo).
