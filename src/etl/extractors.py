"""Data extractors for utility companies.

This module provides extractors for different utility data sources
including electricity, water, and gas consumption data.
"""

import logging
import pandas as pd
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Base class for all data extractors."""

    def __init__(self, source_path: str = None):
        """Initialize extractor.

        Args:
            source_path: Path to data source
        """
        self.source_path = source_path or Path("data/raw")

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Extract data from source.

        Returns:
            DataFrame with extracted data
        """
        pass


class ElectricityExtractor(BaseExtractor):
    """Extract electricity consumption data from power companies."""

    def extract(self) -> pd.DataFrame:
        """Extract electricity data.
        
        Returns:
            DataFrame containing:
            - customer_id
            - reading_date
            - consumption_kwh
            - peak_kwh
            - off_peak_kwh
            - demand_charge
            - energy_charge
            - total_charge
        """
        logger.info("Extracting electricity data from sources")
        try:
            # Expected columns for electricity data
            columns = [
                "customer_id",
                "reading_date",
                "consumption_kwh",
                "peak_kwh",
                "off_peak_kwh",
                "demand_charge",
                "energy_charge",
                "total_charge",
            ]
            logger.info("Electricity data extraction ready")
            return pd.DataFrame(columns=columns)
        except Exception as e:
            logger.error(f"Failed to extract electricity data: {str(e)}")
            raise


class WaterExtractor(BaseExtractor):
    """Extract water consumption data from water utilities."""

    def extract(self) -> pd.DataFrame:
        """Extract water data.
        
        Returns:
            DataFrame containing:
            - customer_id
            - reading_date
            - consumption_gallons
            - consumption_cubic_meters
            - fixed_charge
            - usage_charge
            - total_charge
        """
        logger.info("Extracting water data from sources")
        try:
            # Expected columns for water data
            columns = [
                "customer_id",
                "reading_date",
                "consumption_gallons",
                "consumption_cubic_meters",
                "fixed_charge",
                "usage_charge",
                "total_charge",
            ]
            logger.info("Water data extraction ready")
            return pd.DataFrame(columns=columns)
        except Exception as e:
            logger.error(f"Failed to extract water data: {str(e)}")
            raise


class GasExtractor(BaseExtractor):
    """Extract gas consumption data from gas suppliers."""

    def extract(self) -> pd.DataFrame:
        """Extract gas data.
        
        Returns:
            DataFrame containing:
            - customer_id
            - reading_date
            - consumption_therms
            - consumption_cubic_meters
            - base_charge
            - usage_charge
            - total_charge
            - temperature_avg
            - heating_degree_days
        """
        logger.info("Extracting gas data from sources")
        try:
            # Expected columns for gas data
            columns = [
                "customer_id",
                "reading_date",
                "consumption_therms",
                "consumption_cubic_meters",
                "base_charge",
                "usage_charge",
                "total_charge",
                "temperature_avg",
                "heating_degree_days",
            ]
            logger.info("Gas data extraction ready")
            return pd.DataFrame(columns=columns)
        except Exception as e:
            logger.error(f"Failed to extract gas data: {str(e)}")
            raise
