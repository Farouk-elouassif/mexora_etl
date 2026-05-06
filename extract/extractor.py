"""
Extract phase: Load raw data from source files
"""

import pandas as pd
import json
from config.settings import SOURCE_COMMANDES, SOURCE_CLIENTS, SOURCE_PRODUITS, SOURCE_REGIONS
from utils.logger import get_logger

logger = get_logger(__name__)


def extract_commandes(filepath: str = None) -> pd.DataFrame:
    """
    Extract orders from CSV file.
    
    Args:
        filepath: Path to commandes_mexora.csv
        
    Returns:
        Raw DataFrame with all columns as strings to avoid implicit conversions
    """
    filepath = filepath or str(SOURCE_COMMANDES)
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8', dtype=str)
        logger.info(f"[EXTRACT] Commandes: {len(df)} lignes extraites depuis {filepath}")
        return df
    except Exception as e:
        logger.error(f"[EXTRACT] Erreur extraction commandes: {str(e)}")
        raise


def extract_clients(filepath: str = None) -> pd.DataFrame:
    """
    Extract clients from CSV file.
    
    Args:
        filepath: Path to clients_mexora.csv
        
    Returns:
        Raw DataFrame with all columns as strings
    """
    filepath = filepath or str(SOURCE_CLIENTS)
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8', dtype=str)
        logger.info(f"[EXTRACT] Clients: {len(df)} lignes extraites depuis {filepath}")
        return df
    except Exception as e:
        logger.error(f"[EXTRACT] Erreur extraction clients: {str(e)}")
        raise


def extract_produits(filepath: str = None) -> pd.DataFrame:
    """
    Extract products from JSON file.
    
    Args:
        filepath: Path to produits_mexora.json
        
    Returns:
        Flattened DataFrame with product information
    """
    filepath = filepath or str(SOURCE_PRODUITS)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle nested products array
        produits_list = data.get('produits', data) if isinstance(data, dict) else data
        df = pd.DataFrame(produits_list)
        
        logger.info(f"[EXTRACT] Produits: {len(df)} lignes extraites depuis {filepath}")
        return df
    except Exception as e:
        logger.error(f"[EXTRACT] Erreur extraction produits: {str(e)}")
        raise


def extract_regions(filepath: str = None) -> pd.DataFrame:
    """
    Extract reference regions from CSV file.
    
    Args:
        filepath: Path to regions_maroc.csv
        
    Returns:
        DataFrame with normalized region/city names
    """
    filepath = filepath or str(SOURCE_REGIONS)
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8', dtype=str)
        logger.info(f"[EXTRACT] Régions: {len(df)} lignes extraites depuis {filepath}")
        return df
    except Exception as e:
        logger.error(f"[EXTRACT] Erreur extraction régions: {str(e)}")
        raise


def charger_referentiel_villes(filepath: str = None) -> dict:
    """
    Load city reference mapping from regions file.
    
    Args:
        filepath: Path to regions_maroc.csv
        
    Returns:
        Dictionary mapping normalized city names to standard names
    """
    filepath = filepath or str(SOURCE_REGIONS)
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        
        # Create mapping from various city formats
        mapping = {}
        if 'nom_ville_standard' in df.columns:
            for idx, row in df.iterrows():
                standard_name = row['nom_ville_standard'].lower().strip()
                # Map various formats to standard name
                mapping[standard_name] = row['nom_ville_standard']
                
                # Add alternative mappings
                if 'code_ville' in df.columns:
                    mapping[row['code_ville'].lower().strip()] = row['nom_ville_standard']
        
        logger.info(f"[EXTRACT] Référentiel villes: {len(mapping)} entités chargées")
        return mapping
    except Exception as e:
        logger.error(f"[EXTRACT] Erreur chargement référentiel villes: {str(e)}")
        raise
