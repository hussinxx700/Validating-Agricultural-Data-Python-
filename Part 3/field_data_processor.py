"""
Module: field_data_processor

This module provides a class for processing field data including ingestion, column renaming, applying corrections,
and weather station mapping.

Author: Elhussin sobhy
Date: 24/02/2024

"""

import pandas as pd
from data_ingestion import create_db_engine, query_data, read_from_web_CSV
import logging


class FieldDataProcessor:
    
    """
    A class for processing field data including ingestion, column renaming, applying corrections,
    and weather station mapping.

    Parameters:
    - config_params (dict): Configuration parameters including database path, SQL query, columns to rename,
      values to rename, and weather mapping CSV.
    - logging_level (str, optional): Logging level for the class. Defaults to "INFO".

    Attributes:
    - db_path (str): The path to the SQLite database file.
    - sql_query (str): SQL query to execute for data ingestion.
    - columns_to_rename (dict): Mapping of columns to rename.
    - values_to_rename (dict): Mapping of values to rename.
    - weather_map_data (str): URL or path to the weather mapping CSV.
    - logger (Logger): Logger object for logging messages.
    - df (DataFrame): DataFrame to store the processed data.
    - engine: SQLAlchemy engine object for database connection.
    """

    def __init__(self, config_params, logging_level="INFO"):

        """
        Initialize a FieldDataProcessor instance.

        Parameters:
        - config_params (dict): A dictionary containing configuration parameters including:
        - db_path (str): The path to the SQLite database file.
        - sql_query (str): The SQL query to execute for data ingestion.
        - columns_to_rename (dict): A dictionary mapping columns to rename.
        - values_to_rename (dict): A dictionary mapping values to rename.
        - weather_mapping_csv (str): The URL or path to the weather mapping CSV.
        - logging_level (str, optional): The logging level for the class. Defaults to "INFO".

        Attributes:
        - db_path (str): The path to the SQLite database file.
        - sql_query (str): The SQL query to execute for data ingestion.
        - columns_to_rename (dict): A dictionary mapping columns to rename.
        - values_to_rename (dict): A dictionary mapping values to rename.
        - weather_map_data (str): The URL or path to the weather mapping CSV.
        - logger (Logger): The Logger object for logging messages.
        - df (DataFrame): The DataFrame to store the processed data.
        - engine (Engine): The SQLAlchemy engine object for database connection.
        
        """

        self.db_path = config_params["db_path"]
        self.sql_query = config_params["sql_query"]
        self.columns_to_rename = config_params["columns_to_rename"]
        self.values_to_rename = config_params["values_to_rename"]
        self.weather_map_data = config_params["weather_mapping_csv"]

        self.initialize_logging(logging_level)

        # We create empty objects to store the DataFrame and engine in
        self.df = None
        self.engine = None

    def initialize_logging(self, logging_level):

        """
        Sets up logging for this instance of FieldDataProcessor.
        
        Parameters:
        - logging_level (str): Logging level for the class.
        """
        logger_name = __name__ + ".FieldDataProcessor"
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False  # Prevents log messages from being propagated to the root logger

        # Set logging level
        if logging_level.upper() == "DEBUG":
            log_level = logging.DEBUG

        elif logging_level.upper() == "INFO":
            log_level = logging.INFO

        elif logging_level.upper() == "NONE":  # Option to disable logging
            self.logger.disabled = True
            return
        else:
            log_level = logging.INFO  # Default to INFO

        self.logger.setLevel(log_level)

        # Only add handler if not already added to avoid duplicate messages
        if not self.logger.handlers:

            ch = logging.StreamHandler()  # Create console handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def ingest_sql_data(self):

        """
        Ingests data from an SQL database using the provided SQL query.
        
        Returns:
        - DataFrame: Processed DataFrame containing the ingested data.
        """
        self.engine = create_db_engine(self.db_path)
        self.df = query_data(self.engine, self.sql_query)
        self.logger.info("Successfully loaded data.")
        return self.df

    def rename_columns(self):

        """
        Renames columns in the DataFrame according to the specified mapping.
        """
        column1, column2 = list(self.columns_to_rename.keys())[0], list(self.columns_to_rename.values())[0]
        temp_name = "__temp_name_for_swap__"

        while temp_name in self.df.columns:
            temp_name += "_"

        self.df = self.df.rename(columns={column1: temp_name, column2: column1})
        self.df = self.df.rename(columns={temp_name: column2})
        self.logger.info(f"Swapped columns: {column1} with {column2}")

    def apply_corrections(self, column_name='Crop_type', abs_column='Elevation'):

        """
        Applies corrections to specified columns in the DataFrame.
        
        Parameters:
        - column_name (str, optional): Name of the column to apply corrections to. Defaults to 'Crop_type'.
        - abs_column (str, optional): Name of the column to take absolute values. Defaults to 'Elevation'.
        """
        self.df['Elevation'] = self.df['Elevation'].abs()
        self.df['Crop_type'] = self.df['Crop_type'].apply(lambda crop: self.values_to_rename.get(crop, crop))
        self.df['Crop_type'] = self.df['Crop_type'].str.strip()
        self.logger.info(f"Applied corrections successfully on: {column_name} and {abs_column}")

    def weather_station_mapping(self):

        """
        Maps weather station data to field data based on the Field_ID.
        
        Returns:
        - DataFrame: Processed DataFrame with weather station data mapped.
        """
        weather_map_df = read_from_web_CSV(self.weather_map_data)
        self.df = self.df.merge(weather_map_df, on='Field_ID', how='left')
        self.df = self.df.drop(columns="Unnamed: 0")
        return self.df

    def process(self):

        """
        Processes field data including ingestion, column renaming, applying corrections, and weather station mapping.
        """
        self.ingest_sql_data()
        self.rename_columns()
        self.apply_corrections()
        self.weather_station_mapping()
