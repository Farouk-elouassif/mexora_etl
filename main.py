"""
Main ETL pipeline orchestration
Coordinates Extract → Transform → Load phases
"""

import sys
import argparse
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

from config.settings import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, 
    POSTGRES_USER, POSTGRES_PASSWORD, DWH_SCHEMA, DATA_DIR
)
from extract.extractor import (
    extract_commandes, extract_clients, extract_produits, 
    extract_regions, charger_referentiel_villes
)
from transform.clean_commandes import transform_commandes
from transform.clean_clients import transform_clients
from transform.clean_produits import transform_produits
from transform.build_dimensions import (
    build_dim_temps, build_dim_region, build_dim_client,
    build_dim_produit, build_dim_livreur, build_fait_ventes,
    calculer_segments_clients
)
from load.loader import (
    create_schema, charger_dimension, charger_faits, verifier_chargement
)
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='ETL Pipeline pour Mexora Data Warehouse'
    )
    parser.add_argument(
        '--date-debut',
        type=str,
        default='2020-01-01',
        help='Date de début (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--date-fin',
        type=str,
        default=(datetime.today()).strftime('%Y-%m-%d'),
        help='Date de fin (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--phase',
        type=str,
        choices=['extract', 'transform', 'load', 'full'],
        default='full',
        help='Phase à exécuter'
    )
    parser.add_argument(
        '--no-load',
        action='store_true',
        help='Exécuter E-T mais ne pas charger (test mode)'
    )
    
    return parser.parse_args()


def phase_extraction():
    """Phase 1: Extract raw data from sources."""
    logger.info("=" * 80)
    logger.info("[PHASE 1] EXTRACTION - Début")
    logger.info("=" * 80)
    
    try:
        # Extract all sources
        logger.info("[EXTRACT] Chargement des données sources...")
        df_commandes = extract_commandes()
        df_clients = extract_clients()
        df_produits = extract_produits()
        df_regions = extract_regions()
        
        logger.info(f"[EXTRACT] Commandes: {len(df_commandes)} lignes")
        logger.info(f"[EXTRACT] Clients: {len(df_clients)} lignes")
        logger.info(f"[EXTRACT] Produits: {len(df_produits)} lignes")
        logger.info(f"[EXTRACT] Régions: {len(df_regions)} lignes")
        
        # Load city reference
        referentiel_villes = charger_referentiel_villes()
        logger.info(f"[EXTRACT] Référentiel villes: {len(referentiel_villes)} villes normalisées")
        
        logger.info("[PHASE 1] EXTRACTION - Succès ✓")
        
        return {
            'commandes': df_commandes,
            'clients': df_clients,
            'produits': df_produits,
            'regions': df_regions,
            'referentiel_villes': referentiel_villes
        }
        
    except Exception as e:
        logger.error(f"[PHASE 1] EXTRACTION - Erreur: {str(e)}")
        raise


def phase_transformation(extracted_data):
    """Phase 2: Transform and clean data."""
    logger.info("=" * 80)
    logger.info("[PHASE 2] TRANSFORMATION - Début")
    logger.info("=" * 80)
    
    try:
        df_commandes = extracted_data['commandes']
        df_clients = extracted_data['clients']
        df_produits = extracted_data['produits']
        df_regions = extracted_data['regions']
        
        # Transform each dataset
        logger.info("[TRANSFORM] Nettoyage commandes...")
        df_commandes_clean = transform_commandes(df_commandes)
        logger.info(f"[TRANSFORM] Commandes nettoyées: {len(df_commandes_clean)} lignes (réduit de {len(df_commandes) - len(df_commandes_clean)})")
        
        logger.info("[TRANSFORM] Nettoyage clients...")
        df_clients_clean = transform_clients(df_clients)
        logger.info(f"[TRANSFORM] Clients nettoyés: {len(df_clients_clean)} lignes (réduit de {len(df_clients) - len(df_clients_clean)})")
        
        logger.info("[TRANSFORM] Nettoyage produits...")
        df_produits_clean = transform_produits(df_produits)
        logger.info(f"[TRANSFORM] Produits nettoyés: {len(df_produits_clean)} lignes (réduit de {len(df_produits) - len(df_produits_clean)})")
        
        logger.info("[PHASE 2] TRANSFORMATION - Succès ✓")
        
        return {
            'commandes': df_commandes_clean,
            'clients': df_clients_clean,
            'produits': df_produits_clean,
            'regions': df_regions
        }
        
    except Exception as e:
        logger.error(f"[PHASE 2] TRANSFORMATION - Erreur: {str(e)}")
        raise


def phase_modelisation(transformed_data, date_debut, date_fin):
    """Phase 3: Build dimensional model."""
    logger.info("=" * 80)
    logger.info("[PHASE 3] MODÉLISATION DIMENSIONNELLE - Début")
    logger.info("=" * 80)
    
    try:
        df_commandes = transformed_data['commandes']
        df_clients = transformed_data['clients']
        df_produits = transformed_data['produits']
        df_regions = transformed_data['regions']
        
        # Build dimensions
        logger.info("[MODEL] Construction DIM_TEMPS...")
        dim_temps = build_dim_temps(date_debut, date_fin)
        logger.info(f"[MODEL] DIM_TEMPS: {len(dim_temps)} lignes")
        
        logger.info("[MODEL] Construction DIM_REGION...")
        dim_region = build_dim_region(df_regions)
        logger.info(f"[MODEL] DIM_REGION: {len(dim_region)} lignes")
        
        logger.info("[MODEL] Construction DIM_PRODUIT...")
        dim_produit = build_dim_produit(df_produits)
        logger.info(f"[MODEL] DIM_PRODUIT: {len(dim_produit)} lignes")
        
        logger.info("[MODEL] Construction DIM_LIVREUR...")
        dim_livreur = build_dim_livreur(df_commandes)
        logger.info(f"[MODEL] DIM_LIVREUR: {len(dim_livreur)} lignes")
        
        logger.info("[MODEL] Calcul segmentation clients...")
        segments = calculer_segments_clients(df_commandes)
        
        logger.info("[MODEL] Construction DIM_CLIENT...")
        dim_client = build_dim_client(df_clients, df_commandes)
        logger.info(f"[MODEL] DIM_CLIENT: {len(dim_client)} lignes")
        
        logger.info("[MODEL] Construction FAIT_VENTES...")
        fait_ventes = build_fait_ventes(
            df_commandes, 
            dim_temps, 
            dim_region, 
            dim_client, 
            dim_produit, 
            dim_livreur
        )
        logger.info(f"[MODEL] FAIT_VENTES: {len(fait_ventes)} lignes")
        
        if len(fait_ventes) > 0:
            revenue_total = fait_ventes['montant_ttc'].sum()
            logger.info(f"[MODEL] Montant TTC total: {revenue_total:,.2f} MAD")
        
        logger.info("[PHASE 3] MODÉLISATION - Succès ✓")
        
        return {
            'dim_temps': dim_temps,
            'dim_region': dim_region,
            'dim_client': dim_client,
            'dim_produit': dim_produit,
            'dim_livreur': dim_livreur,
            'fait_ventes': fait_ventes
        }
        
    except Exception as e:
        logger.error(f"[PHASE 3] MODÉLISATION - Erreur: {str(e)}")
        raise


def phase_chargement(model_data):
    """Phase 4: Load into PostgreSQL."""
    logger.info("=" * 80)
    logger.info("[PHASE 4] CHARGEMENT - Début")
    logger.info("=" * 80)
    
    try:
        # Create engine and schema
        connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(connection_string)
        
        logger.info("[LOAD] Création schéma...")
        create_schema(engine)
        
        # Load dimensions
        logger.info("[LOAD] Chargement dimensions...")
        
        charger_dimension(model_data['dim_temps'], 'dim_temps', engine, if_exists='replace')
        charger_dimension(model_data['dim_region'], 'dim_region', engine, if_exists='replace')
        charger_dimension(model_data['dim_produit'], 'dim_produit', engine, if_exists='replace')
        charger_dimension(model_data['dim_livreur'], 'dim_livreur', engine, if_exists='replace')
        charger_dimension(model_data['dim_client'], 'dim_client', engine, if_exists='replace')
        
        # Load fact table
        logger.info("[LOAD] Chargement table de faits...")
        charger_faits(
            model_data['fait_ventes'], 
            'fait_ventes', 
            engine,
            strategy='replace'
        )
        
        # Verify load
        logger.info("[LOAD] Vérification chargement...")
        stats = verifier_chargement(engine)
        
        logger.info("[PHASE 4] CHARGEMENT - Succès ✓")
        
        return stats
        
    except Exception as e:
        logger.error(f"[PHASE 4] CHARGEMENT - Erreur: {str(e)}")
        raise


def generer_rapport(stats):
    """Generate ETL execution report."""
    logger.info("=" * 80)
    logger.info("[RAPPORT] ETL Pipeline - Résumé exécution")
    logger.info("=" * 80)
    
    for table, count in stats.items():
        logger.info(f"  ✓ {table.upper()}: {count:,} lignes")
    
    logger.info("=" * 80)
    logger.info("[SUCCÈS] Pipeline complété avec succès")
    logger.info("=" * 80)


def main():
    """Main ETL orchestration."""
    
    # Parse arguments
    args = parse_arguments()
    logger.info(f"[START] Pipeline lancé à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"[START] Paramètres: phase={args.phase}, dates=[{args.date_debut}, {args.date_fin}]")
    
    time_start = datetime.now()
    
    try:
        # Phase 1: Extract
        if args.phase in ['extract', 'full']:
            extracted = phase_extraction()
        else:
            raise ValueError("Phase extract requise")
        
        # Phase 2: Transform
        if args.phase in ['transform', 'full']:
            transformed = phase_transformation(extracted)
        else:
            raise ValueError("Phase transform requise")
        
        # Phase 3: Model
        if args.phase in ['full']:
            model = phase_modelisation(transformed, args.date_debut, args.date_fin)
        else:
            raise ValueError("Phase modelisation requise")
        
        # Phase 4: Load
        if args.phase in ['full'] and not args.no_load:
            stats = phase_chargement(model)
            generer_rapport(stats)
        else:
            logger.info("[LOAD] Chargement ignoré (mode test ou args.no_load=True)")
        
        # Calculate elapsed time
        time_elapsed = (datetime.now() - time_start).total_seconds()
        logger.info(f"[END] Pipeline complété en {time_elapsed:.2f} secondes")
        
        return 0
        
    except Exception as e:
        logger.error(f"[FATAL] Erreur pipeline: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
