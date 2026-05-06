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

### Guide de démarrage rapide

**Prérequis avant de commencer :**
- PostgreSQL doit être en cours d'exécution
- La base de données `mexora_warehouse` doit être créée
- Le fichier `config/settings.py` doit être correctement configuré
- L'environnement virtuel doit être activé

**Étapes initiales de configuration :**

1. Vérifier que PostgreSQL fonctionne :
```bash
psql --version
psql -U postgres -c "SELECT version();"
```

2. Vérifier que les dépendances sont installées :
```bash
python3 -c "import pandas; import sqlalchemy; print('Dépendances OK')"
```

3. Vérifier la configuration de la base de données :
```bash
cat config/settings.py | grep DATABASE_URL
```

### Exécuter le pipeline complet

Cette commande exécute automatiquement les quatre étapes du pipeline ETL :

```bash
python3 main.py
```

Le pipeline complète les opérations suivantes dans cet ordre :
1. Extraction des données brutes depuis les sources
2. Transformation et nettoyage des données
3. Construction des dimensions
4. Chargement vers les tables de faits
5. Création des vues matérialisées

### Exécuter par étapes individuelles

Si vous souhaitez exécuter chaque étape séparément pour déboguer ou valider intermédiaires :

**Étape 1 : Extraction des données brutes**

Extrait les données depuis les sources CSV ou bases de données sources :

```bash
python3 -m extract.extractor
```

Après cette étape, vérifiez que les fichiers d'extraction ont été créés :
```bash
ls -la data/raw/
```

**Étape 2 : Nettoyage et transformation des données**

Exécutez ces commandes dans l'ordre. Chaque script valide et prépare un domaine spécifique :

```bash
# 2a. Construire les dimensions
python3 -m transform.build_dimensions
```

Vérifier les dimensions créées :
```bash
python3 -c "import pandas as pd; print(pd.read_sql('SELECT * FROM DIM_TEMPS LIMIT 5;', con))"
```

```bash
# 2b. Nettoyer les données produits
python3 -m transform.clean_produits
```

```bash
# 2c. Nettoyer les données clients
python3 -m transform.clean_clients
```

```bash
# 2d. Nettoyer les données de commandes
python3 -m transform.clean_commandes
```

**Étape 3 : Chargement des données vers le Data Warehouse**

Charge les données transformées dans les tables de faits :

```bash
python3 -m load.loader
```

Vérifier que les données ont été chargées :
```bash
psql -U $DB_USER -d mexora_warehouse -c "SELECT COUNT(*) FROM FACT_COMMANDES;"
```

**Étape 4 : Construire les vues matérialisées**

Crée les vues matérialisées pour l'analyse performante :

```bash
python3 scripts/create_materialized_views.py
```

Lister les vues matérialisées créées :
```bash
psql -U $DB_USER -d mexora_warehouse -c "SELECT matviewname FROM pg_matviews;"
```

### Consulter et analyser les logs

Le pipeline génère des logs détaillés pour chaque opération. Consultez-les en temps réel :

```bash
# Afficher les logs en continu
tail -f logs/etl.log
```

Ou consultez les logs après exécution :
```bash
# Voir tous les logs
cat logs/etl.log

# Voir les 50 dernières lignes
tail -50 logs/etl.log

# Voir les erreurs uniquement
grep "ERROR" logs/etl.log

# Voir les avertissements
grep "WARNING" logs/etl.log
```

### Étapes de validation du pipeline

Après chaque étape, validez les résultats :

```bash
# 1. Vérifier la connexion à la base de données
python3 << 'EOF'
from config.settings import DATABASE_URL
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema='public'")
    print(f"Nombre de tables : {result.fetchone()}")
EOF
```

```bash
# 2. Vérifier que les dimensions ont des données
python3 << 'EOF'
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    for table in ['DIM_TEMPS', 'DIM_PRODUIT', 'DIM_CLIENT', 'DIM_REGION', 'DIM_LIVREUR']:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        print(f"{table}: {result.scalar() or 0} lignes")
EOF
```

```bash
# 3. Vérifier que les tables de faits ont des données
python3 << 'EOF'
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    for table in ['FACT_COMMANDES', 'FACT_LIVRAISONS']:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar() or 0
        print(f"{table}: {count} lignes")
EOF
```

### Dépannage courant

**Problème : Erreur de connexion à PostgreSQL**

Solution :
```bash
# Vérifier que PostgreSQL est en cours d'exécution
sudo service postgresql status  # Linux
brew services list | grep postgres  # macOS

# Vérifier les paramètres de connexion dans config/settings.py
cat config/settings.py | grep DATABASE_URL

# Tester la connexion manuelle
psql -U postgres -d mexora_warehouse -c "SELECT 1";
```

**Problème : Erreur de données manquantes**

Vérifier :
```bash
# Vérifier que les fichiers source existent
ls -la data/raw/

# Vérifier que les données brutes ne sont pas vides
wc -l data/raw/*.csv
```

**Problème : La vie du pipeline échoue**

Étapes de déboggage :
```bash
# 1. Afficher un excédent de logs
python3 main.py --debug

# 2. Exécuter une étape individuelle
python3 -m extract.extractor 2>&1 | tee debug.log

# 3. Consulter les logs complets
tail -100 logs/etl.log
```

---

## Dashboard et requêtes analytiques

### Présentation des 5 questions métier

Le data warehouse est conçu pour répondre aux questions commerciales critiques suivantes :

1. **Quels produits génèrent le plus de revenus par trimestre ?**
   - Purpose : Identifier les produits phares et la saisonnalité
   - Data sources : FACT_COMMANDES + DIM_PRODUIT + DIM_TEMPS
   - Metric clé : revenu total par produit et trimestre

2. **Quel est le profil du client type par segment ?**
   - Purpose : Segmenter la clientèle pour des stratégies marketing ciblées
   - Data sources : DIM_CLIENT + FACT_COMMANDES
   - Metrics clés : nombre de clients, ticket moyen, fréquence d'achat par segment

3. **Quel est le taux de satisfaction par région et livreur ?**
   - Purpose : Évaluer la qualité du service de livraison
   - Data sources : FACT_LIVRAISONS + DIM_REGION + DIM_LIVREUR
   - Metric clé : délai de livraison moyen, taux de satisfaction

4. **Quels sont les produits saisonniers ?**
   - Purpose : Optimiser le stock et la logistique
   - Data sources : FACT_COMMANDES + DIM_PRODUIT + DIM_TEMPS
   - Metric clé : volume de ventes par mois/trimestre/année

5. **Quel est l'impact des promotions sur les ventes ?**
   - Purpose : Évaluer le ROI des promotions marketing
   - Data sources : FACT_COMMANDES + DIM_TEMPS
   - Metric clé : variation de ventes pré/post promotion

### Etapes pour créer le dashboard

**Étape 1 : Choisir un outil de visualisation**

Option A : Metabase (recommandé pour débutants, gratuit)
```bash
# Installer via Docker
docker run -d -p 3000:3000 --name metabase metabase/metabase

# Accéder à http://localhost:3000
```

Option B : Power BI Desktop (avancé)
```bash
# Télécharger depuis Microsoft Store
# Importé la base de données PostgreSQL via "Get Data"
```

Option C : Apache Superset
```bash
pip install apache-superset
superset db upgrade
superset fab create-admin
superset load_examples
superset run -p 8088
```

**Étape 2 : Se connecter à la base de données**

```bash
# Pour Metabase : Admin Panel > Databases > Add Database
# Paramètres :
# - Host: localhost
# - Port: 5432
# - Database: mexora_warehouse
# - Username: user
# - Password: password
```

**Étape 3 : Créer les requêtes SQL pour chaque question**

Voir la section "Requêtes SQL pour le dashboard" ci-dessous pour les SQL pour chaque question.

**Étape 4 : Créer les visualisations**

- Graphiques en barres pour les comparaisons (revenus par produit)
- Graphiques en ligne pour les tendances (saisonnalité)
- Heatmaps pour les matrices (région x livreur)
- Tableaux pour les détails clients

### Requêtes SQL pour le dashboard

**Question 1 : Revenus par produit et trimestre**

```sql
SELECT 
    dp.nom_produit,
    dt.trimestre,
    dt.annee,
    SUM(fc.montant_vente) as revenu_total,
    SUM(fc.quantite) as volume_total
FROM FACT_COMMANDES fc
JOIN DIM_PRODUIT dp ON fc.id_produit = dp.id_produit
JOIN DIM_TEMPS dt ON fc.id_date = dt.id_date
GROUP BY dp.nom_produit, dt.trimestre, dt.annee
ORDER BY dt.annee DESC, dt.trimestre DESC, revenu_total DESC;
```

**Question 2 : Profils clients par segment**

```sql
SELECT 
    dc.segment_client,
    COUNT(DISTINCT dc.id_client) as nombre_clients,
    ROUND(AVG(fc.montant_vente), 2) as ticket_moyen,
    COUNT(fc.id_commande) as total_commandes,
    ROUND(AVG(dc.tranche_age), 0) as age_moyen,
    MAX(dc.ville) as principal_ville
FROM DIM_CLIENT dc
LEFT JOIN FACT_COMMANDES fc ON dc.id_client = fc.id_client
GROUP BY dc.segment_client
ORDER BY nombre_clients DESC;
```

**Question 3 : Performance de livraison par région et livreur**

```sql
SELECT 
    dr.region_admin as region,
    dl.nom_livreur,
    ROUND(AVG(EXTRACT(DAY FROM fl.date_livraison - fl.date_commande)), 1) as delai_moyen_jours,
    COUNT(fl.id_livraison) as nombre_livraisons,
    ROUND(AVG(fl.cout_logistique), 2) as cout_moyen,
    ROUND(100.0 * SUM(CASE WHEN fl.statut = 'livrée' THEN 1 ELSE 0 END) / COUNT(*), 2) as taux_livraison_reussie
FROM FACT_LIVRAISONS fl
JOIN DIM_REGION dr ON fl.id_region = dr.id_region
JOIN DIM_LIVREUR dl ON fl.id_livreur = dl.id_livreur
GROUP BY dr.region_admin, dl.nom_livreur
ORDER BY delai_moyen_jours ASC;
```

**Question 4 : Produits saisonniers (variation mensuelle)**

```sql
SELECT 
    dp.nom_produit,
    dt.mois,
    dt.libelle_mois,
    SUM(fc.quantite) as volume_mensuel,
    ROUND(AVG(fc.montant_vente), 2) as revenu_moyen
FROM FACT_COMMANDES fc
JOIN DIM_PRODUIT dp ON fc.id_produit = dp.id_produit
JOIN DIM_TEMPS dt ON fc.id_date = dt.id_date
GROUP BY dp.nom_produit, dt.mois, dt.libelle_mois
ORDER BY dp.nom_produit, dt.mois;
```

**Question 5 : Impact des promotions sur les ventes**

```sql
SELECT 
    dt.annee,
    dt.trimestre,
    ROUND(AVG(fc.montant_vente), 2) as revenu_moyen,
    SUM(fc.quantite) as volume_total,
    COUNT(fc.id_commande) as nombre_commandes,
    CASE 
        WHEN dt.mois IN (11, 12, 3) THEN 'Période promotion'
        ELSE 'Hors promotion'
    END as periode
FROM FACT_COMMANDES fc
JOIN DIM_TEMPS dt ON fc.id_date = dt.id_date
GROUP BY dt.annee, dt.trimestre, periode
ORDER BY dt.annee DESC, dt.trimestre DESC;
```

### Vues matérialisées PostgreSQL

Les vues matérialisées stockent les résultats précalculés pour un accès plus rapide aux tableaux de bord :

**Vue 1 : Résumé ventes par produit et mois**

```sql
CREATE MATERIALIZED VIEW v_sales_by_product_month AS
SELECT 
    dp.id_produit,
    dp.nom_produit,
    dt.annee,
    dt.mois,
    dt.libelle_mois,
    COUNT(fc.id_commande) as nombre_commandes,
    SUM(fc.quantite) as quantite_vendue,
    SUM(fc.montant_vente) as revenu_total,
    ROUND(AVG(fc.montant_vente), 2) as panier_moyen
FROM FACT_COMMANDES fc
JOIN DIM_PRODUIT dp ON fc.id_produit = dp.id_produit
JOIN DIM_TEMPS dt ON fc.id_date = dt.id_date
GROUP BY dp.id_produit, dp.nom_produit, dt.annee, dt.mois, dt.libelle_mois
WITH DATA;

CREATE INDEX idx_v_sales_product_month ON v_sales_by_product_month(id_produit, annee, mois);
```

**Vue 2 : Performance livreurs par région**

```sql
CREATE MATERIALIZED VIEW v_delivery_performance AS
SELECT 
    dr.id_region,
    dr.region_admin,
    dl.id_livreur,
    dl.nom_livreur,
    COUNT(fl.id_livraison) as nombre_livraisons,
    ROUND(AVG(EXTRACT(DAY FROM fl.date_livraison - fl.date_commande)), 1) as delai_moyen_jours,
    ROUND(AVG(fl.cout_logistique), 2) as cout_moyen,
    ROUND(100.0 * SUM(CASE WHEN fl.statut = 'livrée' THEN 1 ELSE 0 END) / COUNT(*), 2) as taux_reussite
FROM FACT_LIVRAISONS fl
JOIN DIM_REGION dr ON fl.id_region = dr.id_region
JOIN DIM_LIVREUR dl ON fl.id_livreur = dl.id_livreur
GROUP BY dr.id_region, dr.region_admin, dl.id_livreur, dl.nom_livreur
WITH DATA;

CREATE INDEX idx_v_delivery_perf ON v_delivery_performance(id_region, id_livreur);
```

**Vue 3 : Segmentation clients et valeur**

```sql
CREATE MATERIALIZED VIEW v_customer_value_segmentation AS
SELECT 
    dc.id_client,
    dc.segment_client,
    dc.region,
    COUNT(DISTINCT fc.id_commande) as nombre_commandes,
    SUM(fc.montant_vente) as valeur_totale,
    ROUND(AVG(fc.montant_vente), 2) as panier_moyen,
    MAX(fc.date_commande) as derniere_commande,
    CASE 
        WHEN SUM(fc.montant_vente) > 10000 THEN 'VIP'
        WHEN SUM(fc.montant_vente) > 5000 THEN 'Premium'
        WHEN SUM(fc.montant_vente) > 1000 THEN 'Standard'
        ELSE 'Occasionnel'
    END as client_tier
FROM DIM_CLIENT dc
LEFT JOIN FACT_COMMANDES fc ON dc.id_client = fc.id_client
GROUP BY dc.id_client, dc.segment_client, dc.region
WITH DATA;

CREATE INDEX idx_v_customer_segment ON v_customer_value_segmentation(segment_client, client_tier);
```

### Rafraîchir les vues matérialisées

Les vues matérialisées doivent être mises à jour après chaque chargement de données complètes :

```bash
# Rafraîchir toutes les vues matérialisées
python3 << 'EOF'
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
views = [
    'v_sales_by_product_month',
    'v_delivery_performance',
    'v_customer_value_segmentation'
]

with engine.connect() as conn:
    for view in views:
        print(f"Rafraîchir {view}...")
        conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
        conn.commit()
        print(f"✓ {view} à jour")
EOF
```

---

## Gestion des changements dimensionnels (SCD)

Le projet implémente les trois stratégies principales de gestion des changements lents dimensionnels pour maintenir l'historique à long terme tout en permettant l'analyse correcte.

### SCD Type 1 : Écrasement (Overwrite)

Utilisé quand l'historique n'est pas nécessaire. Les anciennes valeurs sont écrasées sans conserver le passé.

Cas d'utilisation :
- Corrections d'erreurs non historiques
- Données de référence non analysables dans le temps
- Exemple : correction du nom d'une région

Implémentation :
```sql
-- Avant : "Tanger" → Après : "Tanger-Tétouan"
UPDATE DIM_REGION 
SET region_admin = 'Tanger-Tétouan' 
WHERE id_region = 5;
```

Code Python pour SCD Type 1 :
```python
def update_dimension_type1(engine, table_name, key_col, update_values):
    """Met à jour une dimension sans historique"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        for key, values in update_values.items():
            set_clause = ", ".join([f"{col} = '{val}'" for col, val in values.items()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {key_col} = {key}"
            conn.execute(text(query))
            conn.commit()
```

### SCD Type 2 : Historique complet (Slowly Changing Dimension)

Utilisé pour tracer tous les changements avec dates de validité. Chaque version d'un enregistrement est conservée.

Cas d'utilisation :
- Suivi de l'évolution des segments clients
- Historique des prix produits
- Changements de zone géographique
- Exemple : changement de segment client (Standard → Premium)

Implémentation :
```sql
-- Schéma avec colonnes de dates
CREATE TABLE DIM_CLIENT (
    surrogate_key SERIAL PRIMARY KEY,
    id_client INT,
    nom_client VARCHAR(255),
    segment_client VARCHAR(100),
    date_debut DATE,          -- Quand ce record s'applique
    date_fin DATE,            -- Quand ce record cesse de s'appliquer
    is_current BOOLEAN,       -- Marque le record actuel
    source_timestamp TIMESTAMP
);

-- Exemple d'historique pour le client 123
-- Record 1 : Standard (2023-01-01 à 2023-12-31)
-- Record 2 : Premium (2024-01-01 à aujourd'hui, is_current=true)
```

Code Python pour SCD Type 2 :
```python
def update_dimension_type2(engine, table_name, key_col, business_key, new_values, current_date):
    """Met à jour une dimension avec historique complet"""
    from sqlalchemy import text, DateTime
    
    with engine.connect() as conn:
        # 1. Clôturer l'enregistrement actuel
        conn.execute(text(f"""
            UPDATE {table_name} 
            SET date_fin = '{current_date}', is_current = false
            WHERE {business_key} = {new_values[business_key]} 
            AND is_current = true
        """))
        
        # 2. Insérer le nouveau record
        cols = ", ".join(new_values.keys() + ['date_debut', 'is_current'])
        vals = ", ".join([f"'{v}'" for v in new_values.values()] + [f"'{current_date}'", 'true'])
        conn.execute(text(f"""
            INSERT INTO {table_name} ({cols})
            VALUES ({vals})
        """))
        
        conn.commit()
```

Requête pour consulter l'historique Type 2 :
```sql
-- Afficher tout l'historique d'un client
SELECT * FROM DIM_CLIENT 
WHERE id_client = 123 
ORDER BY date_debut;

-- Afficher les valeurs actuelles uniquement
SELECT * FROM DIM_CLIENT 
WHERE is_current = true;

-- Afficher ce qu'était vrai à une date donnée
SELECT * FROM DIM_CLIENT 
WHERE id_client = 123 
AND date_debut <= '2023-06-15'::date 
AND date_fin > '2023-06-15'::date;
```

### SCD Type 3 : Historique limité (Parallel Columns)

Utilisé quand on veut conserver seulement l'ancienne et la nouvelle valeur sans chronologie complète.

Cas d'utilisation :
- Historique limité à 2 versions (avant/après)
- Changements peu fréquents
- Exemple : ancienne vs nouvelle catégorie produit

Implémentation :
```sql
-- Schéma avec colonnes parallèles
CREATE TABLE DIM_PRODUIT (
    id_produit INT PRIMARY KEY,
    nom_produit VARCHAR(255),
    categorie_actuelle VARCHAR(100),
    categorie_precedente VARCHAR(100),  -- La valeur précédente
    date_changement DATE                -- Quand le changement s'est produit
);
```

Code Python pour SCD Type 3 :
```python
def update_dimension_type3(engine, table_name, key_col, changing_col, new_value, current_date):
    """Met à jour une dimension avec historique limité (2 versions)"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # 1. Copier la valeur actuelle vers la colonne "précédente"
        conn.execute(text(f"""
            UPDATE {table_name} 
            SET {changing_col}_precedente = {changing_col}
            WHERE {key_col} = {key_col}
        """))
        
        # 2. Mettre à jour avec la nouvelle valeur
        conn.execute(text(f"""
            UPDATE {table_name}
            SET {changing_col} = '{new_value}',
                date_changement = '{current_date}'
            WHERE {key_col} = {key_col}
        """))
        
        conn.commit()
```

### Choix entre SCD Type 1, 2 et 3

Tableau de décision :

| Critère | Type 1 | Type 2 | Type 3 |
|---------|--------|--------|--------|
| Historique complet ? | Non | Oui | Dates partielle |
| Avant/Après ? | Non | Oui | Oui |
| Fréquence de changement | Rarement analysé | Souvent | Occasionnel |
| Complexité requête | Simple | Moyen | Simple |
| Taille table | Plus petite | Plus grande | Medium |
| Exemple | Correction de données | Segment client | Prix produit |

---

## Qualité et bonnes pratiques

### Architecture et design patterns

Le projet suit une architecture en couches stricte pour garantir la maintenabilité :

```
Données brutes → Extraction → Transformation → Chargement → Analyse
(CSV/DB)       (extract/)   (transform/)    (load/)      (dashboard)
```

Chaque couche est indépendante et réutilisable.

### Logging centralisé et détaillé

Utilisez le module logger pour tous les événements importants :

```python
# Importer le logger
from utils.logger import get_logger
logger = get_logger(__name__)

# Messages d'information
logger.info("Début traitement des clients")
logger.info(f"Nombre de lignes traitées : {count}")

# Messages d'avertissement
logger.warning("Valeur manquante détectée à la ligne 42")
logger.warning(f"Format de date inattendu : {date_value}")

# Messages d'erreur avec traceback
try:
    result = operation()
except Exception as e:
    logger.error(f"Erreur lors du traitement : {e}", exc_info=True)
```

Consulter les logs :
```bash
# Voir les 100 dernières lignes
tail -100 logs/etl.log

# Filtrer par niveau
grep "ERROR" logs/etl.log | head -20
grep "WARNING" logs/etl.log | wc -l

# Analyser les performances
grep "completed in" logs/etl.log
```

### Gestion robuste des erreurs

Implémenter des try-catch blocks pour toutes les opérations critiques :

```python
from sqlalchemy.exc import SQLAlchemyError
from utils.logger import get_logger

logger = get_logger(__name__)

def insert_data_safely(connection, table, data):
    """Insère des données avec gestion d'erreur"""
    try:
        # Opération métier
        connection.insert(table, data)
        connection.commit()
        logger.info(f"Insertion réussie de {len(data)} lignes dans {table}")
        return True
        
    except SQLAlchemyError as e:
        # Erreur base de données
        connection.rollback()
        logger.error(f"Erreur BD lors de l'insertion dans {table}: {e}", exc_info=True)
        return False
        
    except ValueError as e:
        # Erreur de validation
        logger.error(f"Erreur de validation des données : {e}", exc_info=True)
        return False
        
    except Exception as e:
        # Erreur générique
        logger.error(f"Erreur inattendue : {e}", exc_info=True)
        raise
```

Principes :
1. Rollback automatique en cas d'erreur
2. Logging détaillé pour le débogage
3. Messages clairs pour l'utilisateur
4. Documentation des cas d'exception
5. Tests unitaires pour les scénarios d'erreur

### Validation des données en entrée

Avant de charger les données, valider leur intégrité :

```python
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

def validate_data(df, table_name):
    """Valide un DataFrame avant chargement"""
    
    # 1. Vérifier les colonnes obligatoires
    required_cols = {
        'FACT_COMMANDES': ['id_commande', 'id_client', 'id_produit', 'montant_vente'],
        'DIM_CLIENT': ['id_client', 'nom_complet', 'email']
    }
    
    missing_cols = set(required_cols[table_name]) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Colonnes manquantes : {missing_cols}")
    
    # 2. Vérifier les doublons
    if df.duplicated().sum() > 0:
        logger.warning(f"Doublons détectés dans {table_name}: {df.duplicated().sum()}")
        df = df.drop_duplicates()
    
    # 3. Vérifier les valeurs nulles critiques
    for col in required_cols[table_name]:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            logger.warning(f"Valeurs nulles dans {col}: {null_count}")
            df = df[df[col].notna()]
    
    # 4. Vérifier les types de données
    if table_name == 'FACT_COMMANDES':
        if df['montant_vente'].dtype not in ['float64', 'int64']:
            df['montant_vente'] = pd.to_numeric(df['montant_vente'], errors='coerce')
    
    # 5. Vérifier les plages de valeurs
    if table_name == 'FACT_COMMANDES':
        if (df['montant_vente'] < 0).sum() > 0:
            logger.warning("Montants négatifs détectés et supprimés")
            df = df[df['montant_vente'] >= 0]
    
    logger.info(f"Validation complétée pour {table_name} : {len(df)} lignes valides")
    return df
```

Utilisation :
```python
# Avant d'insérer
df_validated = validate_data(df_raw, 'FACT_COMMANDES')
loader.insert_into_db(df_validated)
```

### Structure et conventions du code

Suivre les conventions pour une meilleure lisibilité :

**Nommage des variables et fonctions :**
```python
# Bon
def extract_customer_data(source_path: str) -> pd.DataFrame:
    """Extrait les données clients depuis le fichier source"""
    pass

customer_id = 123
total_sales = 5000.50

# Mauvais
def extract(p):
    pass

cid = 123
ts = 5000.50
```

**Docstrings obligatoires :**
```python
def calculate_customer_segment(annual_sales: float) -> str:
    """
    Détermine le segment client basé sur les ventes annuelles.
    
    Args:
        annual_sales: Total des ventes annuelles en MAD
        
    Returns:
        Segment ('VIP', 'Premium', 'Standard', 'Occasionnel')
        
    Raises:
        ValueError: Si annual_sales est négatif
        
    Examples:
        >>> calculate_customer_segment(15000)
        'VIP'
    """
    if annual_sales < 0:
        raise ValueError("annual_sales must be non-negative")
    
    if annual_sales > 10000:
        return 'VIP'
    elif annual_sales > 5000:
        return 'Premium'
    # ...
```

**Structuration modulaire :**
```python
# transformer.py - Un fichier par responsabilité

class ClientTransformer:
    """Transformations spécifiques aux clients"""
    
    @staticmethod
    def clean_email(email: str) -> str:
        """Valide et normalise une adresse email"""
        pass
    
    @staticmethod
    def extract_age_group(birth_date: datetime) -> str:
        """Catégorise par tranche d'âge"""
        pass

class ProductTransformer:
    """Transformations spécifiques aux produits"""
    
    @staticmethod
    def normalize_category(category: str) -> str:
        """Normalise les catégories de produits"""
        pass
```

### Développement et test itératif

Lors du développement, testez chaque étape séparément :

```bash
# 1. Tester l'extraction seule
python3 -m extract.extractor --sample 100

# 2. Tester une transformation seule avec des données d'exemple
python3 << 'EOF'
import pandas as pd
from transform.clean_clients import CleanClients

# Charger données test
df_test = pd.read_csv('data/test_clients.csv')

# Exécuter la transformation
cleaner = CleanClients()
df_cleaned = cleaner.transform(df_test)

# Valider les résultats
print(f"Avant : {len(df_test)} lignes")
print(f"Après : {len(df_cleaned)} lignes")
print(f"Colonnes : {df_cleaned.columns.tolist()}")
EOF

# 3. Vérifier les logs en temps réel
tail -f logs/etl.log
```

### Tests unitaires pour les transformations critiques

```python
# tests/test_transformers.py

import unittest
import pandas as pd
from datetime import datetime
from transform.clean_clients import CleanClients

class TestClientTransformer(unittest.TestCase):
    
    def setUp(self):
        """Préparer les données de test"""
        self.cleaner = CleanClients()
        self.test_data = pd.DataFrame({
            'id_client': [1, 2, 3],
            'nom_complet': ['Ahmed Mohamed', 'Fatima Abbas', None],
            'email': ['ahmed@mail.com', 'FATIMA@MAIL.COM', 'invalid-email'],
            'age': [25, 35, 20]
        })
    
    def test_normalize_email(self):
        """Test de normalisation d'email"""
        result = self.cleaner.normalize_email('TEST@MAIL.COM')
        self.assertEqual(result, 'test@mail.com')
    
    def test_remove_null_names(self):
        """Test suppression des noms vides"""
        result = self.cleaner.clean(self.test_data)
        self.assertEqual(len(result), 2)  # Un enregistrement supprimé
    
    def test_validate_email(self):
        """Test validation email"""
        self.assertTrue(self.cleaner.is_valid_email('test@example.com'))
        self.assertFalse(self.cleaner.is_valid_email('invalid-email'))

if __name__ == '__main__':
    unittest.main()
```

Exécuter les tests :
```bash
python3 -m pytest tests/test_transformers.py -v
```

### Documentation des règles de transformation

Pour chaque transformation, documenter clairement la logique métier :

```python
class CleanClients:
    """
    Module de nettoyage des données clients.
    
    Transformations appliquées :
    1. Normalisation des emails (minuscules, suppression espaces)
    2. Suppression des enregistrements sans nom
    3. Validation des tranches d'âge (min:18, max:120)
    4. Suppression des doublons basés sur (id_client, email)
    5. Mapping des villes vers les régions officielles
    
    Règles de exception :
    - Si email invalide : garder l'enregistrement, logger un warning
    - Si âge hors plage : remplacer par NULL et logger
    - Si ville inconnue : assigner 'Autre' et logger
    """
    pass
```

---

## Documentation complémentaire

- [Modélisation dimensionnelle : guide détaillé](./docs/modeling_guide.md)
- [Règles de transformation : dictionnaire des données](./docs/transformation_rules.md)
- [Schéma PostgreSQL : DDL complet](./docs/schema.sql)
- [Requêtes analytiques : SQL samples](./docs/analytics_queries.sql)

---

## Contribution et flux de développement

### Workflow Git recommandé

Suivez ce processus pour contribuer au projet :

**Étape 1 : Créer une branche pour votre feature**

```bash
# Mettre à jour main
git checkout main
git pull origin main

# Créer une branche feature avec un nom descriptif
git checkout -b feature/ajouter-nouvelle-dimension
# ou
git checkout -b bugfix/corriger-validation-email
# ou
git checkout -b docs/completer-guide-installation
```

Conventions de naming :
- `feature/description-courte` : nouvelles fonctionnalités
- `bugfix/description-courte` : corrections de bugs
- `docs/description-courte` : amélioration de documentation
- `refactor/description-courte` : refactoring de code

**Étape 2 : Développer et tester localement**

```bash
# Faire les modifications
# Tester le code
python3 -m pytest tests/
python3 main.py --test-mode

# Vérifier les logs
grep ERROR logs/etl.log
```

**Étape 3 : Committer avec des messages clairs**

```bash
# Ajouter les fichiers modifiés
git add transform/clean_clients.py
git add tests/test_cleaners.py

# Committer avec un message descriptif
git commit -m "Ajouter validation email pour clients

- Normaliser emails en minuscules
- Valider format email avec regex
- Logger les emails invalides comme avertissements
- Tests unitaires ajoutés pour 5 cas limites"

# Format recommandé :
# Ligne 1 : Titre court (50 caractères max)
# Ligne blanche
# Lignes suivantes : Description détaillée (70 caractères par ligne)
# - Point 1
# - Point 2
```

**Étape 4 : Soumettre une Pull Request**

```bash
# Pousser vers le serveur distant
git push origin feature/ajouter-nouvelle-dimension

# Sur GitHub : Créer une Pull Request avec :
```

Template de Pull Request :

```markdown
## Description
Ajout de validation email pour le nettoyage des données clients.

## Problème résolu
Corrige le bug où les emails invalides causaient un crash lors du chargement.

## Changes
- Normalisation des emails (minuscules, suppression espaces)
- Validation avec regex
- Tests pour 5 cas limites

## Type de changement
- [x] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing effectué
- Tests unitaires : 5/5 passent
- Test d'intégration : pipeline exécuté sans erreur
- Données de test : 10,000 clients

## Checklist
- [x] Code suit les conventions du projet
- [x] Logging ajouté pour les cas critiques
- [x] Docstring complétée
- [x] Tests unitaires ajoutés
- [x] Pas de hardcoded values
```

**Étape 5 : Code review et merge**

```bash
# Un pair examine le code
# Changes demandées ? Commits supplémentaires
git add .
git commit -m "Feedback de review : ajouter try-catch supplémentaire"
git push origin feature/ajouter-nouvelle-dimension

# Après approbation : merge sur main
git checkout main
git merge feature/ajouter-nouvelle-dimension
git push origin main

# Nettoyer la branche locale
git branch -d feature/ajouter-nouvelle-dimension
```

### Bonnes pratiques pour les commits

1. **Un commit = une logique** : Ne pas mélanger plusieurs changements distincts
2. **Message descriptif** : Expliquer le "pourquoi" pas le "quoi"
3. **Commits petits et fréquents** : Facilite le review et le revert si nécessaire
4. **Référencer les issues** : "fixes #42" pour lier au suivi de bug

### Standards de Pull Request

- Minimum 1 reviewer
- Pipeline CI doit passer
- Aucun conflit de merge
- Documentation mise à jour si applicable
- Tests ajoutés pour les bugs fixes

### Collaborer sur une feature complexe

Pour les features qui demandent plusieurs commits :

```bash
# Créer une branche feature
git checkout -b feature/grande-refactorisation

# Développer sur plusieurs commits
git commit -m "Étape 1 : extraire fonctions communes"
git commit -m "Étape 2 : créer classe générique"
git commit -m "Étape 3 : intégrer dans pipeline"

# Avant de merge : squash ou rebase ?
# Option A : Squash les commits
git rebase -i main

# Option B : Garder l'historique (recommandé)
# Laisser tous les commits

# Merge sur main
git push origin feature/grande-refactorisation
# Créer PR, faire review, puis merge
```

## Support, ressources et troubleshooting

### Déboggage du pipeline ETL

**Problème : Le pipeline s'exécute mais une étape échoue**

Démarche de diagnostic :

```bash
# 1. Vérifier les logs détaillés
tail -200 logs/etl.log | grep -A 5 "ERROR"

# 2. Tester cette étape seule
python3 -m extract.extractor --debug

# 3. Vérifier la base de données
python3 << 'EOF'
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
EOF

# 4. Vérifier les fichiers source
ls -lah data/raw/
file data/raw/clients.csv  # Voir l'encoding
head -5 data/raw/clients.csv
```

**Problème : Erreur de connexion PostgreSQL**

```bash
# 1. Vérifier que PostgreSQL fonctionne
sudo service postgresql status   # Linux
brew services list | grep postgres  # macOS

# 2. Tester la connection
psql -U postgres -d mexora_warehouse -c "SELECT COUNT(*) FROM information_schema.tables;"

# 3. Vérifier les paramètres dans config/settings.py
grep -E "USER|PASSWORD|HOST|PORT" config/settings.py

# 4. Tester la connexion SQLAlchemy
python3 << 'EOF'
from sqlalchemy import create_engine
DATABASE_URL = "postgresql://user:password@localhost:5432/mexora_warehouse"
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Connexion réussie!")
except Exception as e:
    print(f"Erreur : {e}")
EOF
```

**Problème : "Table doesn't exist"**

```bash
# 1. Vérifier que les schémas sont initialisés
psql -U postgres -d mexora_warehouse -c "\dt public.*"

# 2. Réinitialiser les schémas
python3 scripts/init_database.py

# 3. Vérifier les DDL
cat docs/schema.sql | head -50
```

**Problème : Lots de données manquantes après le chargement**

```bash
# 1. Comparer le nombre de lignes avant/après
wc -l data/raw/clients.csv
psql -U postgres -d mexora_warehouse -c "SELECT COUNT(*) FROM DIM_CLIENT;"

# 2. Vérifier les logs pour les suppressions
grep "filtered out\|dropped\|removed" logs/etl.log

# 3. Analyser les données brutes
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('data/raw/clients.csv')
print(f"Total : {len(df)}")
print(f"Doublons : {df.duplicated().sum()}")
print(f"Valeurs nulles : {df.isnull().sum()}")
print(f"Avant transformations : {len(df)}")

# Après transformations
from transform.clean_clients import CleanClients
cleaner = CleanClients()
df_cleaned = cleaner.transform(df)
print(f"Après transformations : {len(df_cleaned)}")
print(f"Supprimées : {len(df) - len(df_cleaned)}")
EOF
```

### Documentation complémentaire disponible

- [Guide de modélisation dimensionnelle](./docs/modeling_guide.md) - Explique les concepts d'étoiles et flocons
- [Dictionnaire des transformations](./docs/transformation_rules.md) - Détail de chaque règle métier
- [Schéma DDL complet](./docs/schema.sql) - Toutes les créations de tables
- [Requêtes analytiques exemples](./docs/analytics_queries.sql) - SQL pour le dashboard

### Exploration de la configuration

Fichier [config/settings.py](./config/settings.py) :

```python
# Connexion database
DATABASE_URL = "postgresql://user:password@localhost:5432/mexora_warehouse"

# Chemins
RAW_DATA_PATH = "./data/raw"
PROCESSED_DATA_PATH = "./data/processed"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/etl.log"

# Paramètres métier
SEGMENT_THRESHOLDS = {
    'VIP': 10000,
    'Premium': 5000,
    'Standard': 1000
}
```

Modifier les paramètres :
```bash
# Changer le niveau de log pour debug
sed -i 's/LOG_LEVEL = "INFO"/LOG_LEVEL = "DEBUG"/' config/settings.py

# Vérifier les changements
grep LOG_LEVEL config/settings.py
```

### Performance et optimisation

**Optimiser les requêtes lentes**

```bash
# 1. Identifier les requêtes lentes
psql -U postgres -d mexora_warehouse << 'EOF'
SELECT 
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
EOF

# 2. Analyser un requête avec EXPLAIN
psql -U postgres -d mexora_warehouse << 'EOF'
EXPLAIN ANALYZE
SELECT * FROM FACT_COMMANDES 
WHERE id_client = 123
ORDER BY date_commande DESC;
EOF

# 3. Ajouter les indexs appropriés
psql -U postgres -d mexora_warehouse << 'EOF'
CREATE INDEX idx_fact_commands_client ON FACT_COMMANDES(id_client);
CREATE INDEX idx_fact_commands_date ON FACT_COMMANDES(date_commande);
EOF
```

**Rafraîchir les vues matérialisées en arrière-plan**

```bash
# Planifier les rafraîchissements (cron job)
# Éditer le crontab
crontab -e

# Ajouter cette ligne : rafraîchir chaque nuit à 2h
0 2 * * * cd /home/farouk/Desktop/mexora_etl && python3 scripts/refresh_materialized_views.py
```

### Ressources d'apprentissage

Pour mieux comprendre les concepts :

1. **Data Warehouse Fundamentals**
   - Kimball's Dimensional Modeling
   - Star Schema vs Snowflake Schema
   - Fact Tables vs Dimension Tables

2. **ETL avec Python**
   - Pandas documentation : [pandas.pydata.org](https://pandas.pydata.org)
   - SQLAlchemy ORM : [sqlalchemy.org](https://www.sqlalchemy.org)
   - Python logging : [docs.python.org/logging](https://docs.python.org/3/library/logging.html)

3. **PostgreSQL**
   - Materialized Views : [postgresql.org/docs/materialized-views](https://www.postgresql.org/docs/current/sql-creatematerializedview.html)
   - Indexing : [postgresql.org/docs/indexing](https://www.postgresql.org/docs/current/sql-createindex.html)
   - Window Functions : [postgresql.org/docs/window-functions](https://www.postgresql.org/docs/current/functions-window.html)

4. **Git & GitHub**
   - Atlassian Git Tutorials : [atlassian.com/git](https://www.atlassian.com/git/tutorials)
   - Pro Git Book : [git-scm.com/book](https://git-scm.com/book/en/v2)

---

## Licence

Projet éducatif — Libre d'utilisation.

**Dernière mise à jour** : Mai 2026