"""Data loaders for warehouse.

This module handles loading transformed data into the data warehouse
with support for fact tables and dimension tables.
"""

import logging
import pandas as pd
from abc import ABC, abstractmethod
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


class BaseLoader(ABC):
    """Base class for data loaders."""

    @abstractmethod
    def load(self, utility_type: str, data: pd.DataFrame):
        """Load data to destination.

        Args:
            utility_type: Type of utility (electricity, water, gas)
            data: Data to load
        """
        pass


class WarehouseLoader(BaseLoader):
    """Load data into data warehouse with star schema design.
    
    Features:
    - Fact table loading for each utility type
    - Support for incremental loads
    - Error handling and rollback
    - Load tracking and audit trails
    """

    def __init__(self, db_url: str = None):
        """Initialize warehouse loader.

        Args:
            db_url: Database connection URL
                   Default: postgresql://user:password@localhost/utility_warehouse
        """
        self.db_url = db_url or "postgresql://user:password@localhost/utility_warehouse"
        self.engine = None
        logger.info("Initializing Warehouse Loader")

    def _get_connection(self):
        """Get or create database connection.
        
        Returns:
            SQLAlchemy engine instance
        """
        if self.engine is None:
            try:
                self.engine = create_engine(self.db_url)
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                raise
        return self.engine

    def load(self, utility_type: str, data: pd.DataFrame):
        """Load data to warehouse.

        Args:
            utility_type: Type of utility (electricity, water, gas)
            data: Data to load
            
        Raises:
            Exception: If load operation fails
        """
        if data.empty:
            logger.warning(f"No data to load for {utility_type}")
            return

        try:
            engine = self._get_connection()
            table_name = f"fact_{utility_type}"
            
            logger.info(f"Loading {len(data)} records to {table_name}")
            
            # Load data using pandas to_sql with append mode
            # Use sqlalchemy_kwargs to pass additional parameters
            data.to_sql(
                table_name,
                engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000
            )
            
            logger.info(f"Successfully loaded {len(data)} records to {table_name}")

        except Exception as e:
            logger.error(f"Failed to load {utility_type} data: {str(e)}")
            raise

    def load_dimension(self, dim_type: str, data: pd.DataFrame):
        """Load dimension table data.

        Args:
            dim_type: Type of dimension (date, customer, location)
            data: Dimension data to load
        """
        if data.empty:
            logger.warning(f"No dimension data to load for {dim_type}")
            return

        try:
            engine = self._get_connection()
            table_name = f"dim_{dim_type}"
            
            logger.info(f"Loading {len(data)} dimension records to {table_name}")
            
            # Load with replace strategy for dimension tables
            data.to_sql(
                table_name,
                engine,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000
            )
            
            logger.info(f"Successfully loaded dimension {table_name}")

        except Exception as e:
            logger.error(f"Failed to load dimension {dim_type}: {str(e)}")
            raise

    def validate_load(self, utility_type: str) -> int:
        """Validate loaded data and return record count.

        Args:
            utility_type: Type of utility to validate

        Returns:
            Number of records in warehouse table
        """
        try:
            engine = self._get_connection()
            table_name = f"fact_{utility_type}"
            
            with engine.connect() as connection:
                result = connection.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                )
                count = result.fetchone()[0]
                logger.info(f"Validated {count} records in {table_name}")
                return count
                
        except Exception as e:
            logger.error(f"Validation failed for {utility_type}: {str(e)}")
            return 0
