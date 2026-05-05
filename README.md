# Mexora ETL — Pipeline ETL & Data Warehouse

**Pipeline ETL complet et Data Warehouse** construit avec Python, PostgreSQL et visualisations interactives pour l'analyse de données e-commerce.

## Vue d'ensemble du projet

Mexora ETL est un **miniprojet de modélisation dimensionnelle** qui implémente un pipeline ETL complet pour transformer des données brutes en un data warehouse optimisé pour l'analyse. Le projet couvre la **modélisation en étoile**, l'**extraction/transformation/chargement** avec Python, la **persistance** PostgreSQL, et des **dashboards** analytiques.

### Objectifs pédagogiques
- Maîtriser la modélisation dimensionnelle (schéma en étoile)
- Construire un pipeline ETL robuste et maintenable
- Gérer les changements dimensionnels (SCD)
- Optimiser les performances avec PostgreSQL
- Créer des visualisations métier pertinentes

---

## Architecture et Structure

### Dimensions du Data Warehouse

| Dimension | Description | Attributs minimum requis |
|-----------|-------------|------------------------|
| **DIM_TEMPS** | Référentiel calendaire | `id_date`, `jour`, `mois`, `trimestre`, `annee`, `libelle_mois`, `est_weekend`, `est_ferie_maroc`, `periode_ramadan` |
| **DIM_PRODUIT** | Catalogue produits | `id_produit`, `nom_produit`, `categorie`, `sous_categorie`, `marque`, `fournisseur`, `prix_standard`, `origine_pays` |
| **DIM_CLIENT** | Segmentation clients | `id_client`, `nom_complet`, `tranche_age`, `sexe`, `ville`, `region`, `segment_client`, `canal_acquisition` |
| **DIM_REGION** | Zone géographique | `id_region`, `ville`, `province`, `region_admin`, `zone_geo` |
| **DIM_LIVREUR** | Livraison | `id_livreur`, `nom_livreur`, `type_transport`, `zone_couverture` |

### Tables de faits
- **FACT_COMMANDES** : mesures de ventes (quantité, montant, marges)
- **FACT_LIVRAISONS** : mesures logistiques (délai, coût)

### Structure des répertoires
```
mexora_etl/
├── main.py                 # Point d'entrée principal
├── config/
│   └── settings.py         # Configuration (BD, chemins, paramètres)
├── extract/
│   └── extractor.py        # Lecteurs de sources de données
├── transform/
│   ├── build_dimensions.py # Construction des dimensions
│   ├── clean_clients.py    # Nettoyage données clients
│   ├── clean_commandes.py  # Nettoyage commandes
│   └── clean_produits.py   # Nettoyage produits
├── load/
│   └── loader.py           # Chargement vers PostgreSQL
├── utils/
│   └── logger.py           # Logging centralisé
└── README.md               # Ce fichier
```

---

## Critères d'évaluation

### Étape 1 — Modélisation (25 points)
| Critère | Points |
|---------|--------|
| Schéma correct et complet | 5 |
| Granularité justifiée | 5 |
| Additivité des mesures | 5 |
| SCD correctement identifiés et justifiés | 10 |

### Étape 2 — ETL Python (40 points)
| Critère | Points |
|---------|--------|
| Qualité du code (lisibilité, structure) | 10 |
| Exhaustivité des transformations | 15 |
| Logging et documentation des règles | 10 |
| Gestion des erreurs | 5 |

### Étape 3 — PostgreSQL (20 points)
| Critère | Points |
|---------|--------|
| Schéma SQL correct | 5 |
| Indexation appropriée | 5 |
| 3 vues matérialisées fonctionnelles | 10 |

### Étape 4 — Dashboard (15 points)
| Critère | Points |
|---------|--------|
| 5 questions répondues visuellement | 10 |
| Qualité de la visualisation | 5 |
| Insights métier identifiés | 5 |

**Total : 100 points**

---

## Outils requis

| Outil | Usage | Installation |
|-------|-------|--------------|
| **Python 3.11+** | ETL | `brew install python` / [python.org](https://www.python.org) |
| **pandas** | Transformation données | `pip install pandas` |
| **SQLAlchemy** | Connexion PostgreSQL | `pip install sqlalchemy psycopg2` |
| **PostgreSQL 15+** | Data Warehouse | [postgresql.org](https://www.postgresql.org) |
| **DBeaver** | Interface SQL | [dbeaver.io](https://dbeaver.io) (gratuit) |
| **Metabase** | Dashboard (option 1) | [metabase.com](https://metabase.com) (gratuit, docker) |
| **Power BI Desktop** | Dashboard (option 2) | Microsoft Store (gratuit) |
| **Git + GitHub** | Versioning | [git-scm.com](https://git-scm.com) |

---

## Installation et configuration

### 1. **Prérequis système**
```bash
# Vérifier Python
python3 --version  # ≥ 3.11

# Vérifier PostgreSQL
psql --version     # ≥ 15
```

### 2. **Cloner le projet**
```bash
git clone https://github.com/username/mexora_etl.git
cd mexora_etl
```

### 3. **Créer un environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows
```

### 4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

### 5. **Configurer la base de données**
```bash
# Créer la base PostgreSQL
createdb mexora_warehouse

# Configurer dans config/settings.py
DATABASE_URL = "postgresql://user:password@localhost:5432/mexora_warehouse"
```

### 6. **Initialiser les schémas**
```bash
python3 scripts/init_database.py
```

---

## Utilisation

### Exécuter le pipeline complet
```bash
python3 main.py
```

### Exécuter par étapes
```bash
# Étape 1 : Extraction
python3 -m extract.extractor

# Étape 2 : Transformation
python3 -m transform.build_dimensions
python3 -m transform.clean_clients
python3 -m transform.clean_commandes
python3 -m transform.clean_produits

# Étape 3 : Chargement
python3 -m load.loader

# Étape 4 : Construire les vues matérialisées
python3 scripts/create_materialized_views.py
```

### Consulter les logs
```bash
tail -f logs/etl.log
```

---

## Dashboard et requêtes analytiques

### 5 questions métier à répondre

1. **Quels produits génèrent le plus de revenus par trimestre ?**
2. **Quel est le profil du client type par segment ?**
3. **Quel est le taux de satisfaction par région et livreur ?**
4. **Quels sont les produits saisonniers ?**
5. **Quel est l'impact des promotions sur les ventes ?**

### Vues matérialisées PostgreSQL
```sql
-- Vue 1 : Résumé ventes par produit et mois
CREATE MATERIALIZED VIEW v_sales_by_product_month AS ...

-- Vue 2 : Performance livreurs par région
CREATE MATERIALIZED VIEW v_delivery_performance AS ...

-- Vue 3 : Segmentation clients et valeur
CREATE MATERIALIZED VIEW v_customer_value_segmentation AS ...
```

---

## Gestion des changements dimensionnels (SCD)

Le projet implémente les stratégies de gestion des changements lents :

### **SCD Type 1** : Écrasement
- Utilisé pour : corrections d'erreurs non historiques
- Exemple : correction du nom d'une région

### **SCD Type 2** : Historique complet
- Utilisé pour : suivi de l'évolution des charges
- Exemple : changement de segment client
- Implémentation : colonnes `date_debut`, `date_fin`, `is_current`

### **SCD Type 3** : Colonnes parallèles
- Utilisé pour : historique limité
- Exemple : ancienne vs nouvelle catégorie

---

## Qualité et bonnes pratiques

### Logging
```python
# Utiliser le module logger centralisé
from utils.logger import get_logger
logger = get_logger(__name__)

logger.info("Début traitement...")
logger.warning("Valeur manquante détectée")
logger.error("Erreur critique", exc_info=True)
```

### Gestion des erreurs
- Try-catch sur opérations BD
- Validation des données en entrée
- Rollback en cas d'erreur
- Documentation des cas d'exception

### Structure du code
- Séparation des couches (extract → transform → load)
- Fonctions réutilisables
- Docstrings pour chaque module
- Tests unitaires pour les transformations critiques

---

## Documentation complémentaire

- [Modélisation dimensionnelle : guide détaillé](./docs/modeling_guide.md)
- [Règles de transformation : dictionnaire des données](./docs/transformation_rules.md)
- [Schéma PostgreSQL : DDL complet](./docs/schema.sql)
- [Requêtes analytiques : SQL samples](./docs/analytics_queries.sql)

---

## Contribution

1. Créer une branche `feature/ma-feature`
2. Committer avec messages clairs
3. Soumettre une pull request avec documentation
4. Valider que le pipeline s'exécute sans erreurs

---

## Support et ressources

- **Logs** : `logs/etl.log` pour debugging
- **Configuration** : [config/settings.py](./config/settings.py)
- **Questions** : Vérifier les docstrings et commentaires du code

---

## Licence

Projet éducatif — Libre d'utilisation.

**Dernière mise à jour** : Mai 2026