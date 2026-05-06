"""
Configuration settings for Mexora ETL Pipeline
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
LOGS_DIR = PROJECT_ROOT / 'logs'

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Database configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_DB = os.getenv('POSTGRES_DB', 'mexora_etl')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'etl_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'etl_password_secure')

# Data warehouse schema
DWH_SCHEMA = 'dwh_mexora'

# Source files
SOURCE_COMMANDES = DATA_DIR / 'commandes_mexora.csv'
SOURCE_CLIENTS = DATA_DIR / 'clients_mexora.csv'
SOURCE_PRODUITS = DATA_DIR / 'produits_mexora.json'
SOURCE_REGIONS = DATA_DIR / 'regions_maroc.csv'

# Date ranges
DATE_DEBUT_TEMPS = '2020-01-01'
DATE_FIN_TEMPS = '2025-12-31'

# Business rules
SEUIL_CA_GOLD = 15000  # MAD
SEUIL_CA_SILVER = 5000  # MAD

# Age validation
AGE_MIN = 16
AGE_MAX = 100

# ETL settings
CHUNK_SIZE = 1000
BATCH_SIZE = 5000

# Statuts de commande valides
STATUTS_VALIDES = ['livré', 'annulé', 'en_cours', 'retourné', 'inconnu']

# Mapping villes Maroc
VILLES_MAROC = {
    'casablanca': 'Casablanca',
    'casa': 'Casablanca',
    'fes': 'Fès',
    'fez': 'Fès',
    'marrakech': 'Marrakech',
    'tanger': 'Tanger',
    'tangier': 'Tanger',
    'rabat': 'Rabat',
    'benali': 'Ben Ali',
    'ben ali': 'Ben Ali',
    'agadir': 'Agadir',
    'meknes': 'Meknès',
    'oujda': 'Oujda',
}

# Jours fériés marocains
JOURS_FERIES_MAROC = [
    '2020-01-01', '2020-01-11', '2020-05-01', '2020-07-30', '2020-08-14', '2020-11-06', '2020-11-18',
    '2021-01-01', '2021-01-11', '2021-05-01', '2021-07-30', '2021-08-14', '2021-11-06', '2021-11-18',
    '2022-01-01', '2022-01-11', '2022-05-01', '2022-07-30', '2022-08-14', '2022-11-06', '2022-11-18',
    '2023-01-01', '2023-01-11', '2023-05-01', '2023-07-30', '2023-08-14', '2023-11-06', '2023-11-18',
    '2024-01-01', '2024-01-11', '2024-05-01', '2024-07-30', '2024-08-14', '2024-11-06', '2024-11-18',
    '2025-01-01', '2025-01-11', '2025-05-01', '2025-07-30', '2025-08-14', '2025-11-06', '2025-11-18',
]

# Périodes Ramadan approximatives
RAMADAN_PERIODES = [
    ('2020-04-24', '2020-05-23'),
    ('2021-04-13', '2021-05-12'),
    ('2022-04-02', '2022-05-01'),
    ('2023-03-22', '2023-04-20'),
    ('2024-03-10', '2024-04-09'),
    ('2025-02-28', '2025-03-30'),
]
