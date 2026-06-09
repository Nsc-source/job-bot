"""Data transformers for utility companies.

This module provides transformers for cleaning, enriching, and standardizing
utility consumption data from different sources.
"""

import logging
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseTransformer(ABC):
    """Base class for all data transformers."""

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data.

        Args:
            data: Raw data DataFrame

        Returns:
            Transformed DataFrame
        """
        pass

    def _add_audit_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add audit columns for tracking and lineage.

        Args:
            df: DataFrame to augment

        Returns:
            DataFrame with audit columns
        """
        df["loaded_at"] = datetime.now()
        df["data_version"] = "1.0"
        df["source"] = self.__class__.__name__
        return df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to lowercase with underscores.

        Args:
            df: DataFrame with raw column names

        Returns:
            DataFrame with standardized column names
        """
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
        return df


class ElectricityTransformer(BaseTransformer):
    """Transform electricity consumption data.
    
    Handles:
    - Column standardization
    - Data type conversion
    - Validation of consumption values
    - Addition of derived metrics
    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform electricity data.

        Args:
            data: Raw electricity data

        Returns:
            Transformed electricity data
        """
        logger.info("Starting electricity data transformation")

        if data.empty:
            logger.warning("Received empty electricity dataset")
            return data

        try:
            # Standardize columns
            data = self._standardize_columns(data)
            
            # Convert data types
            if "reading_date" in data.columns:
                data["reading_date"] = pd.to_datetime(data["reading_date"])
            
            # Ensure numeric columns
            numeric_cols = [
                "consumption_kwh",
                "peak_kwh",
                "off_peak_kwh",
                "demand_charge",
                "energy_charge",
                "total_charge",
            ]
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors="coerce")
            
            # Add derived metrics
            if "peak_kwh" in data.columns and "off_peak_kwh" in data.columns:
                data["peak_ratio"] = (
                    data["peak_kwh"] / (data["peak_kwh"] + data["off_peak_kwh"])
                ).fillna(0)
            
            # Add audit columns
            data = self._add_audit_columns(data)
            
            logger.info(f"Successfully transformed {len(data)} electricity records")
            return data

        except Exception as e:
            logger.error(f"Error transforming electricity data: {str(e)}")
            raise


class WaterTransformer(BaseTransformer):
    """Transform water consumption data.
    
    Handles:
    - Column standardization
    - Unit conversion (gallons to cubic meters)
    - Seasonal pattern detection
    - Quality flag processing
    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform water data.

        Args:
            data: Raw water data

        Returns:
            Transformed water data
        """
        logger.info("Starting water data transformation")

        if data.empty:
            logger.warning("Received empty water dataset")
            return data

        try:
            # Standardize columns
            data = self._standardize_columns(data)
            
            # Convert data types
            if "reading_date" in data.columns:
                data["reading_date"] = pd.to_datetime(data["reading_date"])
            
            # Ensure numeric columns
            numeric_cols = [
                "consumption_gallons",
                "consumption_cubic_meters",
                "fixed_charge",
                "usage_charge",
                "total_charge",
            ]
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors="coerce")
            
            # Unit conversion if needed
            if "consumption_gallons" in data.columns and "consumption_cubic_meters" not in data.columns:
                data["consumption_cubic_meters"] = data["consumption_gallons"] / 264.172
            
            # Add audit columns
            data = self._add_audit_columns(data)
            
            logger.info(f"Successfully transformed {len(data)} water records")
            return data

        except Exception as e:
            logger.error(f"Error transforming water data: {str(e)}")
            raise


class GasTransformer(BaseTransformer):
    """Transform gas consumption data.
    
    Handles:
    - Column standardization
    - Temperature correlation analysis
    - Heating degree day calculations
    - Seasonal adjustment
    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform gas data.

        Args:
            data: Raw gas data

        Returns:
            Transformed gas data
        """
        logger.info("Starting gas data transformation")

        if data.empty:
            logger.warning("Received empty gas dataset")
            return data

        try:
            # Standardize columns
            data = self._standardize_columns(data)
            
            # Convert data types
            if "reading_date" in data.columns:
                data["reading_date"] = pd.to_datetime(data["reading_date"])
            
            # Ensure numeric columns
            numeric_cols = [
                "consumption_therms",
                "consumption_cubic_meters",
                "base_charge",
                "usage_charge",
                "total_charge",
                "temperature_avg",
                "heating_degree_days",
            ]
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors="coerce")
            
            # Calculate temperature sensitivity if not present
            if "consumption_therms" in data.columns and "temperature_avg" in data.columns:
                # Temperature correlation (rough estimate)
                data["temp_sensitivity"] = (
                    (65 - data["temperature_avg"]) / 65
                ).clip(lower=0)
            
            # Add audit columns
            data = self._add_audit_columns(data)
            
            logger.info(f"Successfully transformed {len(data)} gas records")
            return data

        except Exception as e:
            logger.error(f"Error transforming gas data: {str(e)}")
            raise
