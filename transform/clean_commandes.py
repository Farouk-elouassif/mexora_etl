"""
Transform phase: Clean and standardize orders data
Applies 7 transformation rules as per Mexora business requirements
"""

import pandas as pd
import logging
from config.settings import STATUTS_VALIDES, VILLES_MAROC
from extract.extractor import charger_referentiel_villes
from utils.logger import get_logger

logger = get_logger(__name__)


def transform_commandes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning rules to orders data.
    
    Transformation rules:
      R1 - Remove duplicate order IDs (keep last occurrence)
      R2 - Standardize date format to YYYY-MM-DD
      R3 - Normalize city names using regions reference
      R4 - Standardize order status values
      R5 - Remove rows with quantity <= 0
      R6 - Remove rows with price = 0 (test orders)
      R7 - Replace missing delivery IDs with -1 (unknown driver)
    
    Args:
        df: Raw orders DataFrame
        
    Returns:
        Cleaned orders DataFrame
    """
    initial_count = len(df)
    logger.info(f"[TRANSFORM] Commandes: démarrage avec {initial_count} lignes")
    
    df = df.copy()
    
    # R1 - Remove duplicates on id_commande (keep last)
    df_before = len(df)
    df = df.drop_duplicates(subset=['id_commande'], keep='last')
    duplicates_removed = df_before - len(df)
    logger.info(f"[TRANSFORM] R1 Doublons: {duplicates_removed} lignes supprimées")
    
    # R2 - Standardize dates
    before_dates = len(df)
    df['date_commande'] = pd.to_datetime(
        df['date_commande'], format='mixed', dayfirst=True, errors='coerce'
    )
    dates_invalides = df['date_commande'].isna().sum()
    if dates_invalides > 0:
        df = df.dropna(subset=['date_commande'])
    logger.info(f"[TRANSFORM] R2 Dates: {dates_invalides} dates invalides supprimées")
    
    # R3 - Normalize cities using reference
    try:
        mapping_villes = charger_referentiel_villes()
        df['ville_livraison'] = df['ville_livraison'].str.strip().str.lower()
        df['ville_livraison'] = df['ville_livraison'].map(mapping_villes).fillna('Non renseignée')
    except Exception as e:
        logger.warning(f"[TRANSFORM] R3 Villes: erreur lors du mapping (utilisation directe) - {str(e)}")
        df['ville_livraison'] = df['ville_livraison'].str.strip().str.title()
    
    # R4 - Standardize order status
    mapping_statuts = {
        'livré': 'livré', 'livre': 'livré', 'LIVRE': 'livré', 'DONE': 'livré',
        'annulé': 'annulé', 'annule': 'annulé', 'KO': 'annulé',
        'en_cours': 'en_cours', 'OK': 'en_cours', 'PENDING': 'en_cours',
        'retourné': 'retourné', 'retourne': 'retourné',
    }
    df['statut'] = df['statut'].str.lower().str.strip().map(mapping_statuts).fillna('inconnu')
    invalides_statut = ~df['statut'].isin(STATUTS_VALIDES)
    logger.warning(f"[TRANSFORM] R4 Statuts: {invalides_statut.sum()} valeurs non reconnues → 'inconnu'")
    df.loc[invalides_statut, 'statut'] = 'inconnu'
    
    # R5 - Remove negative/zero quantities
    before_qty = len(df)
    try:
        df['quantite'] = df['quantite'].astype(float)
        df = df[df['quantite'] > 0]
    except (ValueError, TypeError):
        logger.warning("[TRANSFORM] R5 Quantités: erreur conversion, suppression lignes invalides")
        df = df[df['quantite'].astype(str).str.replace('.', '', 1).str.isdigit()]
        df['quantite'] = df['quantite'].astype(float)
        df = df[df['quantite'] > 0]
    qty_removed = before_qty - len(df)
    logger.info(f"[TRANSFORM] R5 Quantités: {qty_removed} lignes supprimées (quantité <= 0)")
    
    # R6 - Remove zero-price test orders
    before_price = len(df)
    try:
        df['prix_unitaire'] = df['prix_unitaire'].astype(float)
        df = df[df['prix_unitaire'] > 0]
    except (ValueError, TypeError):
        logger.warning("[TRANSFORM] R6 Prix: erreur conversion")
    price_removed = before_price - len(df)
    logger.info(f"[TRANSFORM] R6 Prix: {price_removed} commandes test supprimées (prix = 0)")
    
    # R7 - Replace missing driver IDs with -1
    nb_livreur_missing = df['id_livreur'].isna().sum()
    df['id_livreur'] = df['id_livreur'].fillna('-1')
    logger.info(f"[TRANSFORM] R7 Livreurs: {nb_livreur_missing} valeurs manquantes remplacées par -1")
    
    final_count = len(df)
    total_removed = initial_count - final_count
    logger.info(f"[TRANSFORM] Commandes: {initial_count} → {final_count} lignes ({total_removed} supprimées au total)")
    
    return df
