"""
Database connection utilities for Mexora ETL
Handles PostgreSQL connections using SQLAlchemy
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections"""

    def __init__(self, host=None, port=None, database=None, user=None, password=None):
        """
        Initialize database connection parameters
        
        Args:
            host: PostgreSQL host (default: localhost)
            port: PostgreSQL port (default: 5432)
            database: Database name (default: mexora_etl)
            user: Database user (default: etl_user)
            password: Database password (default: etl_password_secure)
        """
        self.host = host or os.getenv('POSTGRES_HOST', 'localhost')
        self.port = port or os.getenv('POSTGRES_PORT', '5432')
        self.database = database or os.getenv('POSTGRES_DB', 'mexora_etl')
        self.user = user or os.getenv('POSTGRES_USER', 'etl_user')
        self.password = password or os.getenv('POSTGRES_PASSWORD', 'etl_password_secure')
        
        self.engine = None
        self.session_factory = None

    def get_connection_string(self):
        """Generate PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def connect(self):
        """
        Establish database connection
        
        Returns:
            SQLAlchemy engine object
        """
        try:
            connection_string = self.get_connection_string()
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Test connections before using
                echo=False
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✓ Database connection successful")
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            
            return self.engine
        
        except Exception as e:
            logger.error(f"✗ Failed to connect to database: {str(e)}")
            raise

    def get_session(self):
        """
        Get a new database session
        
        Returns:
            SQLAlchemy session object
        """
        if not self.session_factory:
            self.connect()
        return self.session_factory()

    def test_connection(self):
        """Test database connection and return status"""
        try:
            if not self.engine:
                self.connect()
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                db_version = result.fetchone()
                logger.info(f"Connected to: {db_version[0]}")
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def close(self):
        """Close database connection pool"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global connection instance
_db_connection = None


def get_db_connection(host=None, port=None, database=None, user=None, password=None):
    """
    Get or create global database connection
    
    Returns:
        DatabaseConnection instance
    """
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection(host, port, database, user, password)
        _db_connection.connect()
    
    return _db_connection


def close_db_connection():
    """Close global database connection"""
    global _db_connection
    if _db_connection:
        _db_connection.close()
        _db_connection = None


if __name__ == "__main__":
    # Test connection
    print("Testing database connection...")
    db = get_db_connection()
    
    if db.test_connection():
        print("✓ All systems operational")
    else:
        print("✗ Connection failed")
    
    close_db_connection()
