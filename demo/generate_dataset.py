"""
Génère un jeu de données de churn synthétique mais réaliste pour la démo Vertex AI.

PME par abonnement (~télécom / SaaS). La cible `churned` (0/1) dépend de façon
plausible des features (ancienneté faible, contrat mensuel, beaucoup de tickets
support, charges élevées => churn plus probable), avec du bruit.

Usage :
    python generate_dataset.py            # -> data/clients.csv (train, avec label)
                                          # -> data/clients_a_scorer.csv (à prédire, sans label)
"""
import csv
import os
import random

random.seed(42)
N_TRAIN = 4000          # >= 1000 requis par AutoML Tabular
N_SCORE = 500           # clients actuels à scorer (sans label)

CONTRATS = ["mensuel", "annuel", "biennal"]
PAIEMENTS = ["carte", "prelevement", "virement", "cheque"]

def make_client(i, with_label=True):
    anciennete = random.randint(1, 72)                      # mois
    contrat = random.choices(CONTRATS, weights=[0.55, 0.30, 0.15])[0]
    facture = round(random.uniform(20, 110), 2)             # CHF / mois
    total = round(facture * anciennete * random.uniform(0.9, 1.1), 2)
    tickets = random.choices([0, 1, 2, 3, 4, 5, 8], weights=[40, 25, 15, 8, 5, 4, 3])[0]
    paiement = random.choice(PAIEMENTS)
    support_premium = random.choices([0, 1], weights=[0.7, 0.3])[0]
    age = random.randint(18, 80)

    row = {
        "customer_id": f"C{100000 + i}",
        "anciennete_mois": anciennete,
        "type_contrat": contrat,
        "facture_mensuelle": facture,
        "facture_totale": total,
        "nb_tickets_support": tickets,
        "moyen_paiement": paiement,
        "support_premium": support_premium,
        "age": age,
    }

    if with_label:
        # Probabilité de churn "métier" + bruit
        p = 0.06
        if contrat == "mensuel":            p += 0.22
        if anciennete < 6:                  p += 0.20
        elif anciennete < 12:               p += 0.08
        if tickets >= 4:                    p += 0.18
        elif tickets >= 2:                  p += 0.06
        if facture > 90:                    p += 0.10
        if support_premium == 1:            p -= 0.08
        if paiement == "cheque":            p += 0.05
        p += random.uniform(-0.05, 0.05)
        p = min(max(p, 0.01), 0.95)
        row["churned"] = 1 if random.random() < p else 0
    return row

def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(here, "data")
    os.makedirs(data_dir, exist_ok=True)

    train = [make_client(i, with_label=True) for i in range(N_TRAIN)]
    fields_train = list(train[0].keys())
    write_csv(os.path.join(data_dir, "clients.csv"), train, fields_train)

    score = [make_client(N_TRAIN + i, with_label=False) for i in range(N_SCORE)]
    fields_score = list(score[0].keys())
    write_csv(os.path.join(data_dir, "clients_a_scorer.csv"), score, fields_score)

    churn_rate = sum(r["churned"] for r in train) / len(train)
    print(f"OK : {N_TRAIN} clients (train), churn = {churn_rate:.1%}")
    print(f"OK : {N_SCORE} clients à scorer (sans label)")
    print(f"Fichiers : {data_dir}/clients.csv , {data_dir}/clients_a_scorer.csv")
