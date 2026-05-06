"""
Transform phase: Build dimension and fact tables
Creates normalized dimensional model for data warehouse
"""

import pandas as pd
from datetime import date, timedelta
from config.settings import (
    SEUIL_CA_GOLD, SEUIL_CA_SILVER, JOURS_FERIES_MAROC, RAMADAN_PERIODES,
    DATE_DEBUT_TEMPS, DATE_FIN_TEMPS
)
from utils.logger import get_logger

logger = get_logger(__name__)


def build_dim_temps(date_debut: str = None, date_fin: str = None) -> pd.DataFrame:
    """
    Build time dimension with Moroccan holidays and Ramadan periods.
    
    Args:
        date_debut: Start date (default from settings)
        date_fin: End date (default from settings)
        
    Returns:
        Complete time dimension DataFrame with all attributes
    """
    date_debut = date_debut or DATE_DEBUT_TEMPS
    date_fin = date_fin or DATE_FIN_TEMPS
    
    logger.info(f"[BUILD] DIM_TEMPS: construction pour période {date_debut} à {date_fin}")
    
    dates = pd.date_range(start=date_debut, end=date_fin, freq='D')
    
    df = pd.DataFrame({
        'id_date': dates.strftime('%Y%m%d').astype(int),
        'date_complete': dates,
        'jour': dates.day,
        'mois': dates.month,
        'trimestre': dates.quarter,
        'annee': dates.year,
        'semaine': dates.isocalendar().week,
        'libelle_jour': dates.strftime('%A'),
        'libelle_mois': dates.strftime('%B'),
        'libelle_trimestre': 'Q' + dates.quarter.astype(str) + ' ' + dates.year.astype(str),
        'est_weekend': dates.dayofweek >= 5,
    })
    
    # Add Moroccan holidays
    df['est_ferie_maroc'] = df['date_complete'].dt.strftime('%Y-%m-%d').isin(JOURS_FERIES_MAROC)
    
    # Add Ramadan periods
    df['periode_ramadan'] = False
    for debut, fin in RAMADAN_PERIODES:
        masque = (df['date_complete'] >= debut) & (df['date_complete'] <= fin)
        df.loc[masque, 'periode_ramadan'] = True
    
    # Select final columns
    df = df[['id_date', 'jour', 'mois', 'trimestre', 'annee', 'semaine',
             'libelle_jour', 'libelle_mois', 'libelle_trimestre',
             'est_weekend', 'est_ferie_maroc', 'periode_ramadan']]
    
    logger.info(f"[BUILD] DIM_TEMPS: {len(df)} jours créés")
    return df


def build_dim_region(df_regions: pd.DataFrame) -> pd.DataFrame:
    """
    Build region dimension from reference data.
    
    Args:
        df_regions: Raw regions DataFrame
        
    Returns:
        Region dimension table
    """
    logger.info(f"[BUILD] DIM_REGION: construction avec {len(df_regions)} régions")
    
    df = df_regions.copy()
    
    # Ensure required columns, add ID if missing
    if 'id_region' not in df.columns:
        df.insert(0, 'id_region', range(1, len(df) + 1))
    
    # Normalize column names
    columns_map = {
        'nom_ville_standard': 'nom_region',
        'code_ville': 'code_region',
        'province': 'province',
        'region_admin': 'region_admin',
    }
    
    for old, new in columns_map.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]
    
    # Select relevant columns
    available_cols = [c for c in ['id_region', 'nom_region', 'code_region', 
                                   'province', 'region_admin'] if c in df.columns]
    df = df[available_cols].drop_duplicates()
    
    logger.info(f"[BUILD] DIM_REGION: {len(df)} régions créées")
    return df


def build_dim_client(df_clients: pd.DataFrame, df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Build customer dimension with segmentation.
    
    Args:
        df_clients: Cleaned clients DataFrame
        df_commandes: Cleaned orders DataFrame (for segmentation)
        
    Returns:
        Customer dimension with segments
    """
    logger.info(f"[BUILD] DIM_CLIENT: construction depuis {len(df_clients)} clients")
    
    df = df_clients.copy()
    
    # Ensure required columns
    if 'id_client' not in df.columns:
        df.insert(0, 'id_client', range(1, len(df) + 1))
    
    # Calculate customer segments based on order history
    segments = calculer_segments_clients(df_commandes)
    df = df.merge(segments, on='id_client', how='left')
    df['segment_client'] = df['segment_client'].fillna('Bronze')
    df['ca_12m'] = df['ca_12m'].fillna(0)
    
    # Select dimension columns
    dim_cols = ['id_client', 'nom', 'prenom', 'email', 'date_naissance', 'age',
                'tranche_age', 'sexe', 'ville', 'telephone', 'date_inscription',
                'canal_acquisition', 'segment_client', 'ca_12m']
    available_cols = [c for c in dim_cols if c in df.columns]
    df = df[available_cols].drop_duplicates(subset=['id_client'])
    
    logger.info(f"[BUILD] DIM_CLIENT: {len(df)} clients créés avec segments")
    return df


def build_dim_produit(df_produits: pd.DataFrame) -> pd.DataFrame:
    """
    Build product dimension.
    
    Args:
        df_produits: Cleaned products DataFrame
        
    Returns:
        Product dimension table
    """
    logger.info(f"[BUILD] DIM_PRODUIT: construction depuis {len(df_produits)} produits")
    
    df = df_produits.copy()
    
    # Ensure ID column
    if 'id_produit' not in df.columns and 'product_id' not in df.columns:
        df.insert(0, 'id_produit', range(1, len(df) + 1))
    elif 'product_id' in df.columns and 'id_produit' not in df.columns:
        df.rename(columns={'product_id': 'id_produit'}, inplace=True)
    
    # Select relevant columns
    possible_cols = ['id_produit', 'nom', 'description', 'categorie', 'prix_unitaire',
                     'poids', 'stock', 'actif', 'date_creation']
    available_cols = [c for c in possible_cols if c in df.columns]
    df = df[available_cols].drop_duplicates(subset=['id_produit'])
    
    logger.info(f"[BUILD] DIM_PRODUIT: {len(df)} produits créés")
    return df


def build_dim_livreur(df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Build delivery partner dimension from orders.
    
    Args:
        df_commandes: Cleaned orders DataFrame
        
    Returns:
        Delivery partner dimension
    """
    logger.info(f"[BUILD] DIM_LIVREUR: construction")
    
    # Extract unique drivers from orders
    df = df_commandes[['id_livreur']].drop_duplicates().copy()
    df = df[df['id_livreur'] != '-1']  # Exclude unknown drivers
    
    # Add default information
    df['nom_livreur'] = 'Livreur_' + df['id_livreur'].astype(str)
    df['statut'] = 'actif'
    
    # Add unknown driver entry
    df_unknown = pd.DataFrame({
        'id_livreur': ['-1'],
        'nom_livreur': ['Livreur Inconnu'],
        'statut': ['inactif']
    })
    df = pd.concat([df, df_unknown], ignore_index=True)
    
    logger.info(f"[BUILD] DIM_LIVREUR: {len(df)} livreurs créés")
    return df


def calculer_segments_clients(df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate customer segments based on 12-month revenue.
    
    Business rules:
      Gold   : Revenue 12 months >= 15,000 MAD
      Silver : Revenue 12 months >= 5,000 MAD
      Bronze : Revenue 12 months < 5,000 MAD
    
    Args:
        df_commandes: Orders DataFrame with financial data
        
    Returns:
        DataFrame with customer IDs and segments
    """
    date_limite = pd.Timestamp(date.today() - timedelta(days=365))
    
    # Filter recent delivered orders
    df_recents = df_commandes[
        (df_commandes['date_commande'] >= date_limite) &
        (df_commandes['statut'] == 'livré')
    ].copy()
    
    if len(df_recents) == 0:
        logger.warning("[BUILD] Aucune commande livrée récente pour segmentation")
        return pd.DataFrame(columns=['id_client', 'segment_client', 'ca_12m'])
    
    try:
        # Calculate revenue per customer
        df_recents['quantite'] = df_recents['quantite'].astype(float)
        df_recents['prix_unitaire'] = df_recents['prix_unitaire'].astype(float)
        df_recents['montant_ttc'] = df_recents['quantite'] * df_recents['prix_unitaire']
        
        ca_par_client = df_recents.groupby('id_client')['montant_ttc'].sum().reset_index()
        ca_par_client.columns = ['id_client', 'ca_12m']
        
        # Apply segmentation rules
        def segmenter(ca):
            if ca >= SEUIL_CA_GOLD:
                return 'Gold'
            elif ca >= SEUIL_CA_SILVER:
                return 'Silver'
            else:
                return 'Bronze'
        
        ca_par_client['segment_client'] = ca_par_client['ca_12m'].apply(segmenter)
        
        logger.info(f"[BUILD] Segments: {len(ca_par_client)} clients segmentés " +
                   f"(Gold: {(ca_par_client['segment_client'] == 'Gold').sum()}, " +
                   f"Silver: {(ca_par_client['segment_client'] == 'Silver').sum()}, " +
                   f"Bronze: {(ca_par_client['segment_client'] == 'Bronze').sum()})")
        
        return ca_par_client
    except Exception as e:
        logger.warning(f"[BUILD] Erreur segmentation clients: {str(e)}")
        return pd.DataFrame(columns=['id_client', 'segment_client', 'ca_12m'])


def build_fait_ventes(df_commandes: pd.DataFrame, 
                     dim_temps: pd.DataFrame,
                     dim_client: pd.DataFrame = None,
                     dim_produit: pd.DataFrame = None,
                     dim_region: pd.DataFrame = None,
                     dim_livreur: pd.DataFrame = None) -> pd.DataFrame:
    """
    Build fact table for sales.
    
    Args:
        df_commandes: Clean orders data
        dim_temps: Time dimension (required for date keys)
        dim_client: Customer dimension (optional, for enrichment)
        dim_produit: Product dimension (optional, for enrichment)
        dim_region: Region dimension (optional, for enrichment)
        dim_livreur: Delivery dimension (optional, for enrichment)
        
    Returns:
        Fact table with measures and keys
    """
    logger.info(f"[BUILD] FAIT_VENTES: construction depuis {len(df_commandes)} commandes")
    
    df = df_commandes.copy()
    
    # Convert to numeric
    df['quantite'] = df['quantite'].astype(float)
    df['prix_unitaire'] = df['prix_unitaire'].astype(float)
    
    # Calculate measures
    df['montant_ht'] = df['quantite'] * df['prix_unitaire']
    df['montant_ttc'] = df['montant_ht'] * 1.2  # Assuming 20% VAT for Morocco
    df['marge_estimee'] = df['montant_ht'] * 0.3  # Estimated margin 30%
    
    # Create date keys
    df['date_commande'] = pd.to_datetime(df['date_commande'], format='mixed', dayfirst=True, errors='coerce')
    df['id_date_commande'] = df['date_commande'].dt.strftime('%Y%m%d').astype(int)
    
    # Handle date_livraison with fallback to date_commande
    if 'date_livraison' in df.columns:
        df['date_livraison'] = pd.to_datetime(df['date_livraison'], format='mixed', dayfirst=True, errors='coerce')
        df['id_date_livraison'] = df['date_livraison'].fillna(df['date_commande']).dt.strftime('%Y%m%d').astype(int)
    else:
        df['id_date_livraison'] = df['id_date_commande']
    
    # Ensure dimension keys
    if 'id_client' not in df.columns:
        df['id_client'] = 0
    if 'id_produit' not in df.columns:
        df['id_produit'] = 0
    if 'id_region' not in df.columns:
        df['id_region'] = 0
    
    # Select fact columns
    fact_cols = [
        'id_commande', 'id_client', 'id_produit', 'id_region', 'id_livreur',
        'id_date_commande', 'id_date_livraison',
        'quantite', 'prix_unitaire', 'montant_ht', 'montant_ttc', 'marge_estimee',
        'statut'
    ]
    available_cols = [c for c in fact_cols if c in df.columns]
    df = df[available_cols]
    
    logger.info(f"[BUILD] FAIT_VENTES: {len(df)} lignes créées")
    logger.info(f"[BUILD] Montant total: {df['montant_ttc'].sum():,.0f} MAD")
    
    return df
