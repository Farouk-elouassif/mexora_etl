"""
Transform phase: Clean and standardize products data
Applies product-specific transformation rules
"""

import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)


def transform_produits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning rules to products data.
    
    Transformation rules:
      R1 - Standardize category names (consistent casing)
      R2 - Handle missing prices
      R3 - Standardize product status (actif/inactif)
      R4 - Validate numeric fields
      R5 - Remove duplicate products
    
    Args:
        df: Raw products DataFrame
        
    Returns:
        Cleaned products DataFrame
    """
    initial_count = len(df)
    logger.info(f"[TRANSFORM] Produits: démarrage avec {initial_count} lignes")
    
    df = df.copy()
    
    # R1 - Standardize category casing
    if 'categorie' in df.columns or 'category' in df.columns:
        cat_col = 'categorie' if 'categorie' in df.columns else 'category'
        df[cat_col] = df[cat_col].str.lower().str.strip().str.title()
        logger.info(f"[TRANSFORM] R1 Catégories: standardisées")
    
    # R2 - Handle missing prices
    price_col = 'prix_unitaire' if 'prix_unitaire' in df.columns else 'prix' if 'prix' in df.columns else None
    if price_col:
        df_before = len(df)
        try:
            df[price_col] = df[price_col].astype(float)
            missing_prices = df[price_col].isna().sum()
            # Option: Set missing prices to 0 or remove rows
            df = df[df[price_col] > 0]
            removed_prices = df_before - len(df)
            logger.info(f"[TRANSFORM] R2 Prix: {missing_prices} manquants, {removed_prices} prix <= 0 supprimés")
        except (ValueError, TypeError):
            logger.warning("[TRANSFORM] R2 Prix: erreur conversion")
    
    # R3 - Standardize product status
    if 'actif' in df.columns or 'status' in df.columns:
        status_col = 'actif' if 'actif' in df.columns else 'status'
        mapping_status = {
            '1': 'actif', 'true': 'actif', 'yes': 'actif', 'o': 'actif', 'oui': 'actif',
            '0': 'inactif', 'false': 'inactif', 'no': 'inactif', 'non': 'inactif',
            'actif': 'actif', 'inactif': 'inactif', 'archive': 'inactif'
        }
        df[status_col] = df[status_col].astype(str).str.lower().str.strip().map(mapping_status).fillna('actif')
        logger.info(f"[TRANSFORM] R3 Statut: standardisé")
    
    # R4 - Validate numeric fields (quantity if exists)
    numeric_fields = ['poids', 'stock', 'quantite_min', 'quantite_max']
    for field in numeric_fields:
        if field in df.columns:
            try:
                df[field] = df[field].astype(float)
                df[field] = df[field].fillna(0)
                logger.info(f"[TRANSFORM] R4 {field}: validé")
            except (ValueError, TypeError):
                logger.warning(f"[TRANSFORM] R4 {field}: erreur conversion, remplissage par 0")
                df[field] = 0
    
    # R5 - Remove duplicate products
    if 'id_produit' in df.columns or 'product_id' in df.columns:
        id_col = 'id_produit' if 'id_produit' in df.columns else 'product_id'
        df_before = len(df)
        df = df.drop_duplicates(subset=[id_col], keep='first')
        duplicates = df_before - len(df)
        logger.info(f"[TRANSFORM] R5 Doublons: {duplicates} produits en doublon supprimés")
    
    # Fill missing values
    text_cols = df.select_dtypes(include=['object']).columns
    for col in text_cols:
        df[col] = df[col].fillna('Non renseigné')
    
    final_count = len(df)
    total_removed = initial_count - final_count
    logger.info(f"[TRANSFORM] Produits: {initial_count} → {final_count} lignes ({total_removed} supprimées au total)")
    
    return df
