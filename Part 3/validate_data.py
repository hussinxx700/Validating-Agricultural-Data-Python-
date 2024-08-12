import unittest
import pandas as pd
from field_data_processor import FieldDataProcessor
from weather_data_processor import WeatherDataProcessor

config_params =    {
    
    "sql_query": """
                    SELECT *
                        FROM geographic_features
                        LEFT JOIN weather_features USING (Field_ID)
                        LEFT JOIN soil_and_crop_features USING (Field_ID)
                        LEFT JOIN farm_management_features USING (Field_ID)
                """,
    "db_path": 'sqlite:///Maji_Ndogo_farm_survey_small.db',
    "columns_to_rename": {'Annual_yield': 'Crop_type', 'Crop_type': 'Annual_yield'}, 
    "values_to_rename": {'cassaval': 'cassava', 'wheatn': 'wheat', 'teaa': 'tea'},
    "weather_csv_path": "https://raw.githubusercontent.com/Explore-AI/Public-Data/master/Maji_Ndogo/Weather_station_data.csv",
    "weather_mapping_csv": "https://raw.githubusercontent.com/Explore-AI/Public-Data/master/Maji_Ndogo/Weather_data_field_mapping.csv" ,
    "regex_patterns" : {
                        'Rainfall': r'(\d+(\.\d+)?)\s?mm',
                         'Temperature': r'(\d+(\.\d+)?)\s?C',
                        'Pollution_level': r'=\s*(-?\d+(\.\d+)?)|Pollution at \s*(-?\d+(\.\d+)?)'
    }
}

class TestDataIngestion(unittest.TestCase):

    def test_read_weather_DataFrame_shape(self):
        # Test shape of weather DataFrame after reading
        weather_processor = WeatherDataProcessor(config_params)
        weather_df = weather_processor.process()
        weather_df = weather_processor.weather_df
        self.assertEqual(weather_df.shape, (1843, 4))

    def test_read_field_DataFrame_shape(self):
        # Test shape of field DataFrame after reading
        field_processor = FieldDataProcessor(config_params)
        field_df = field_processor.process()
        field_df = field_processor.df
        self.assertEqual(field_df.shape, (5654, 19))

    def test_weather_DataFrame_columns(self):
        # Test columns of weather DataFrame
        weather_processor = WeatherDataProcessor(config_params)
        weather_df = weather_processor.process()
        weather_df = weather_processor.weather_df
        self.assertListEqual(weather_df.columns.tolist(), ['Weather_station_ID',
                                                            'Message',
                                                            'Measurement',
                                                            'Value'])

    def test_field_DataFrame_columns(self):
        # Test columns of field DataFrame
        field_processor = FieldDataProcessor(config_params)
        field_df = field_processor.process()
        field_df = field_processor.df
        self.assertListEqual(field_df.columns.tolist(), ['Field_ID',
                                                        'Elevation',
                                                        'Latitude',
                                                        'Longitude',
                                                        'Location',
                                                        'Slope',
                                                        'Rainfall',
                                                        'Min_temperature_C',
                                                        'Max_temperature_C',
                                                        'Ave_temps',
                                                        'Soil_fertility',
                                                        'Soil_type',
                                                        'pH',
                                                        'Pollution_level',
                                                        'Plot_size',
                                                        'Annual_yield',
                                                        'Crop_type',
                                                        'Standard_yield',
                                                        'Weather_station']
)

    def test_field_DataFrame_non_negative_elevation(self):
        # Test if all elevation values in field DataFrame are non-negative
        field_processor = FieldDataProcessor(config_params)
        field_df = field_processor.process()
        field_df = field_processor.df
        self.assertTrue((field_df['Elevation'] >= 0).all())

    def test_crop_types_are_valid(self):
        # Test if all crop types in field DataFrame are valid
        field_processor = FieldDataProcessor(config_params)
        field_df = field_processor.process()
        field_df = field_processor.df
        valid_crop_types = ['cassava', 'tea', 'wheat', 'potato', 'banana', 
                            'coffee', 'rice','maize']  # Define valid crop types
        self.assertTrue(field_df['Crop_type'].isin(valid_crop_types).all())

    def test_positive_rainfall_values(self):
        # Test if all rainfall values in weather DataFrame are positive
        field_processor = FieldDataProcessor(config_params)
        field_df = field_processor.process()
        field_df = field_processor.df
        self.assertTrue((field_df['Rainfall'] > 0).all())

if __name__ == '__main__':
    unittest.main()
