"""
Load phase: Load dimensions and facts into PostgreSQL
"""

import pandas as pd
from sqlalchemy import text, MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert
from config.settings import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, 
    POSTGRES_USER, POSTGRES_PASSWORD, DWH_SCHEMA, CHUNK_SIZE
)
from utils.db_connection import get_db_connection
from utils.logger import get_logger

logger = get_logger(__name__)


def get_connection_string() -> str:
    """
    Generate PostgreSQL connection string.
    
    Returns:
        Connection string for SQLAlchemy
    """
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


def create_schema(engine):
    """
    Create data warehouse schema if it doesn't exist.
    
    Args:
        engine: SQLAlchemy engine
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DWH_SCHEMA}"))
            conn.commit()
            logger.info(f"[LOAD] Schéma {DWH_SCHEMA} créé/vérifié")
    except Exception as e:
        logger.warning(f"[LOAD] Erreur création schéma: {str(e)}")


def charger_dimension(df: pd.DataFrame, 
                     table_name: str, 
                     engine,
                     if_exists: str = 'replace') -> int:
    """
    Load dimension table into PostgreSQL.
    Strategy: replace (truncate + reload) for dimensions.
    
    Args:
        df: DataFrame to load
        table_name: Target table name
        engine: SQLAlchemy engine
        if_exists: 'replace', 'append', or 'fail'
        
    Returns:
        Number of rows loaded
    """
    try:
        if len(df) == 0:
            logger.warning(f"[LOAD] {table_name}: DataFrame vide, chargement ignoré")
            return 0
        
        # Load data
        rows = df.to_sql(
            name=table_name,
            con=engine,
            schema=DWH_SCHEMA,
            if_exists=if_exists,
            index=False,
            method='multi',
            chunksize=CHUNK_SIZE
        )
        
        logger.info(f"[LOAD] {table_name}: {len(df)} lignes chargées (stratégie: {if_exists})")
        return len(df)
        
    except Exception as e:
        logger.error(f"[LOAD] Erreur chargement {table_name}: {str(e)}")
        raise


def charger_faits(df: pd.DataFrame, 
                 table_name: str,
                 engine,
                 key_column: str = 'id_commande',
                 strategy: str = 'replace') -> int:
    """
    Load fact table into PostgreSQL.
    Supports UPSERT for incremental loads.
    
    Args:
        df: Fact table DataFrame
        table_name: Target table name
        engine: SQLAlchemy engine
        key_column: Primary key for upsert
        strategy: 'replace' (truncate+load) or 'upsert' (update on conflict)
        
    Returns:
        Number of rows loaded/updated
    """
    try:
        if len(df) == 0:
            logger.warning(f"[LOAD] {table_name}: DataFrame vide, chargement ignoré")
            return 0
        
        if strategy == 'replace':
            # Simple replace strategy
            rows = df.to_sql(
                name=table_name,
                con=engine,
                schema=DWH_SCHEMA,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=CHUNK_SIZE
            )
            logger.info(f"[LOAD] {table_name}: {len(df)} lignes chargées (replace)")
            
        elif strategy == 'upsert':
            # UPSERT strategy using PostgreSQL ON CONFLICT
            logger.info(f"[LOAD] {table_name}: début upsert pour {len(df)} lignes")
            
            with engine.begin() as conn:
                # First ensure table exists
                df.head(0).to_sql(
                    name=table_name,
                    con=conn,
                    schema=DWH_SCHEMA,
                    if_exists='append',
                    index=False
                )
                
                # Process in chunks
                for chunk in [df[i:i+CHUNK_SIZE] for i in range(0, len(df), CHUNK_SIZE)]:
                    records = chunk.to_dict('records')
                    
                    # Build column list for UPDATE clause
                    update_cols = [c for c in chunk.columns if c != key_column]
                    
                    # Execute upsert using raw SQL
                    insert_stmt = f"""
                    INSERT INTO {DWH_SCHEMA}.{table_name} ({', '.join(chunk.columns)})
                    VALUES ({', '.join(['%s'] * len(chunk.columns))})
                    ON CONFLICT ({key_column}) DO UPDATE SET
                    {', '.join([f"{c} = EXCLUDED.{c}" for c in update_cols])}
                    """
                    
                    for record in records:
                        values = [record[c] for c in chunk.columns]
                        conn.execute(text(insert_stmt), values)
                
            logger.info(f"[LOAD] {table_name}: {len(df)} lignes upsertées")
        
        else:
            raise ValueError(f"Stratégie inconnue: {strategy}")
        
        return len(df)
        
    except Exception as e:
        logger.error(f"[LOAD] Erreur chargement {table_name} ({strategy}): {str(e)}")
        raise


def verifier_chargement(engine) -> dict:
    """
    Verify that all dimension and fact tables are loaded.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        Dictionary with table names and record counts
    """
    try:
        stats = {}
        tables = [
            'dim_temps', 'dim_region', 'dim_client', 
            'dim_produit', 'dim_livreur', 'fait_ventes'
        ]
        
        with engine.connect() as conn:
            for table in tables:
                try:
                    result = conn.execute(
                        text(f"SELECT COUNT(*) FROM {DWH_SCHEMA}.{table}")
                    )
                    count = result.scalar()
                    stats[table] = count
                    logger.info(f"[VERIFY] {table}: {count} lignes")
                except:
                    stats[table] = 0
                    logger.warning(f"[VERIFY] {table}: table non trouvée")
        
        return stats
        
    except Exception as e:
        logger.error(f"[VERIFY] Erreur vérification: {str(e)}")
        return {}
