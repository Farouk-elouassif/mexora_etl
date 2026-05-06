"""
Transform phase: Clean and standardize clients data
Applies 5 transformation rules for customer data quality
"""

import pandas as pd
import re
from datetime import date, timedelta
from config.settings import AGE_MIN, AGE_MAX
from utils.logger import get_logger

logger = get_logger(__name__)


def transform_clients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning rules to clients data.
    
    Transformation rules:
      R1 - Deduplicate on normalized email (keep most recent registration)
      R2 - Standardize gender field (target: 'm' / 'f' / 'inconnu')
      R3 - Validate birth dates (age between 16 and 100 years)
      R4 - Validate email format using regex
      R5 - Calculate age and age group for segmentation
    
    Args:
        df: Raw clients DataFrame
        
    Returns:
        Cleaned clients DataFrame
    """
    initial_count = len(df)
    logger.info(f"[TRANSFORM] Clients: démarrage avec {initial_count} lignes")
    
    df = df.copy()
    
    # R1 - Deduplicate on normalized email
    df['email_norm'] = df['email'].str.lower().str.strip()
    df_before = len(df)
    df = df.sort_values('date_inscription').drop_duplicates(
        subset=['email_norm'], 
        keep='last'
    )
    dedup_removed = df_before - len(df)
    logger.info(f"[TRANSFORM] R1 Doublons: {dedup_removed} clients dédoublonnés (email)")
    
    # R2 - Standardize gender
    mapping_sexe = {
        'm': 'm', 'f': 'f',
        '1': 'm', '0': 'f',
        'homme': 'm', 'femme': 'f',
        'male': 'm', 'female': 'f',
        'h': 'm', 'm.': 'm', 'f.': 'f',
        'mr': 'm', 'mme': 'f', 'mlle': 'f',
    }
    df['sexe'] = df['sexe'].str.lower().str.strip().map(mapping_sexe).fillna('inconnu')
    invalid_sexe = (df['sexe'] == 'inconnu').sum()
    logger.info(f"[TRANSFORM] R2 Sexe: standardisé, {invalid_sexe} valeurs 'inconnu'")
    
    # R3 - Validate birth dates and calculate age
    df['date_naissance'] = pd.to_datetime(df['date_naissance'], errors='coerce')
    today = pd.Timestamp(date.today())
    
    # Calculate age
    df['age'] = ((today - df['date_naissance']).dt.days / 365.25).astype(int)
    
    # Remove invalid ages (outside 16-100 range)
    invalid_ages = ((df['age'] < AGE_MIN) | (df['age'] > AGE_MAX)).sum()
    df.loc[(df['age'] < AGE_MIN) | (df['age'] > AGE_MAX), 'date_naissance'] = pd.NaT
    df.loc[(df['age'] < AGE_MIN) | (df['age'] > AGE_MAX), 'age'] = None
    logger.info(f"[TRANSFORM] R3 Dates: {invalid_ages} dates invalides (âge hors limites)")
    
    # Create age group
    df['tranche_age'] = pd.cut(
        df['age'].fillna(0),
        bins=[0, 18, 25, 35, 45, 55, 65, 200],
        labels=['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    )
    
    # R4 - Validate email format
    pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    invalid_emails = (~df['email'].str.match(pattern_email, na=False)).sum()
    df.loc[~df['email'].str.match(pattern_email, na=False), 'email'] = None
    logger.info(f"[TRANSFORM] R4 Emails: {invalid_emails} format invalide")
    
    # R5 - Additional data quality checks
    # Check for null critical fields
    df['nom'] = df['nom'].fillna('Inconnu')
    df['prenom'] = df['prenom'].fillna('Inconnu')
    df['ville'] = df['ville'].fillna('Non renseignée')
    
    final_count = len(df)
    total_removed = initial_count - final_count
    logger.info(f"[TRANSFORM] Clients: {initial_count} → {final_count} lignes ({total_removed} supprimées au total)")
    
    return df
