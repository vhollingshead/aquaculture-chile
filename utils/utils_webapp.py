import plotly.figure_factory as ff
import streamlit as st
from numpy.random import default_rng as rng
import pandas as pd
import geopandas as gpd
import re
from typing import Optional, Tuple
import numpy as np
import plotly.express as px

# Coordinate String Parser - Extract First Pair and Convert to Decimal Degrees
# This script extracts the first coordinate pair from a multi-line coordinate string and converts to decimal degrees

def extract_first_coordinate_pair(coord_string: str) -> Optional[str]:
    """
    Extract the first coordinate pair from a multi-line coordinate string.
    
    Args:
        coord_string: String containing multiple coordinate pairs separated by newlines
        
    Returns:
        First coordinate pair as string, or None if not found
    """
    if pd.isna(coord_string) or coord_string == '':
        return None
    
    try:
        # Split by newline and get the first non-empty line
        lines = coord_string.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ',' in line:
                return line
        
        return None
    
    except Exception as e:
        print(f"Error extracting first coordinate pair: {e}")
        return None

def parse_dms_coordinate(dms_string: str) -> Optional[Tuple[float, float]]:
    """
    Parse DMS (Degrees, Minutes, Seconds) coordinate string to decimal degrees.
    
    Args:
        dms_string: String like "S 41°35´14.4850, W 73°37´45.1614"
    
    Returns:
        Tuple of (latitude, longitude) in decimal degrees, or None if parsing fails
    """
    if pd.isna(dms_string) or dms_string == '':
        return None
    
    try:
        # Split by comma to separate lat and lon
        parts = dms_string.split(',')
        if len(parts) != 2:
            return None
        
        lat_str, lon_str = parts[0].strip(), parts[1].strip()
        
        # Parse latitude - format: S 41°35´14.4850
        lat_match = re.search(r'([NS])\s*(\d+)°(\d+)´([\d.]+)', lat_str)
        if not lat_match:
            return None
        
        lat_dir, lat_deg, lat_min, lat_sec = lat_match.groups()
        lat_decimal = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600
        if lat_dir == 'S':
            lat_decimal = -lat_decimal
        
        # Parse longitude - format: W 73°37´45.1614
        lon_match = re.search(r'([EW])\s*(\d+)°(\d+)´([\d.]+)', lon_str)
        if not lon_match:
            return None
        
        lon_dir, lon_deg, lon_min, lon_sec = lon_match.groups()
        lon_decimal = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600
        if lon_dir == 'W':
            lon_decimal = -lon_decimal
        
        return (lat_decimal, lon_decimal)
    
    except Exception as e:
        print(f"Error parsing coordinate: {dms_string} - {e}")
        return None

def process_coordinate_string(coord_string: str) -> dict:
    """
    Process a coordinate string to extract first pair and convert to decimal degrees.
    
    Args:
        coord_string: Multi-line coordinate string
        
    Returns:
        Dictionary with original string, first pair, and decimal coordinates
    """
    result = {
        'original_string': coord_string,
        'first_pair': None,
        'latitude': None,
        'longitude': None,
        'success': False,
        'error': None
    }
    
    try:
        # Extract first coordinate pair
        first_pair = extract_first_coordinate_pair(coord_string)
        result['first_pair'] = first_pair
        
        if first_pair is None:
            result['error'] = "No valid coordinate pair found"
            return result
        
        # Convert to decimal degrees
        coords = parse_dms_coordinate(first_pair)
        
        if coords is not None:
            result['latitude'] = coords[0]
            result['longitude'] = coords[1]
            result['success'] = True
        else:
            result['error'] = "Failed to parse coordinate pair"
    
    except Exception as e:
        result['error'] = str(e)
    
    return result

def process_dataframe_coordinates(df: pd.DataFrame, coord_column: str, 
                                output_lat_col: str = 'latitude', 
                                output_lon_col: str = 'longitude') -> pd.DataFrame:
    """
    Process coordinate strings in a DataFrame column.
    
    Args:
        df: DataFrame containing coordinate strings
        coord_column: Name of the column containing coordinate strings
        output_lat_col: Name for the output latitude column
        output_lon_col: Name for the output longitude column
    
    Returns:
        DataFrame with added latitude and longitude columns
    """
    df = df.copy()
    
    # Initialize coordinate columns
    df[output_lat_col] = np.nan
    df[output_lon_col] = np.nan
    
    # Process each coordinate string
    success_count = 0
    total_count = len(df)
    
    for idx, coord_str in enumerate(df[coord_column]):
        result = process_coordinate_string(coord_str)
        
        if result['success']:
            df.loc[idx, output_lat_col] = result['latitude']
            df.loc[idx, output_lon_col] = result['longitude']
            success_count += 1
    
    print(f"Successfully processed {success_count}/{total_count} coordinate strings ({success_count/total_count*100:.1f}%)")
    
    return df

# Example usage and testing
if __name__ == "__main__":
    
    # Test with the provided coordinate string
    test_coord_string = 'S 41°35´14.4850, W 73°37´45.1614\nS 41°35´14.6624, W 73°37´44.7895\nS 41°35´22.7008, W 73°37´52.0099\nS 41°35´22.5292, W 73°37´52.3697\n'
    
    print("=== Coordinate String Parser Test ===")
    print(f"Original string:\n{test_coord_string}")
    
    # Process the coordinate string
    result = process_coordinate_string(test_coord_string)
    
    print(f"\nFirst coordinate pair: {result['first_pair']}")
    print(f"Latitude: {result['latitude']}")
    print(f"Longitude: {result['longitude']}")
    print(f"Success: {result['success']}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    # Test with DataFrame
    print("\n=== DataFrame Processing Test ===")
    
    # Create sample DataFrame
    sample_data = {
        'ID': [1, 2, 3],
        'COORDENADA': [
            'S 41°35´14.4850, W 73°37´45.1614\nS 41°35´14.6624, W 73°37´44.7895',
            'S 42°10´20.5000, W 72°50´30.2500\nS 42°10´21.0000, W 72°50´31.0000',
            'S 40°45´15.7500, W 74°15´45.5000\nS 40°45´16.0000, W 74°15´46.0000'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    print("Sample DataFrame:")
    print(df)
    
    # Process coordinates
    df_processed = process_dataframe_coordinates(df, 'COORDENADA')
    
    print("\nProcessed DataFrame:")
    print(df_processed[['ID', 'COORDENADA', 'latitude', 'longitude']])
    
    # Additional test cases
    print("\n=== Additional Test Cases ===")
    
    test_cases = [
        'S 41°35´14.4850, W 73°37´45.1614\nS 41°35´14.6624, W 73°37´44.7895',
        'N 40°45´15.7500, E 74°15´45.5000\nN 40°45´16.0000, E 74°15´46.0000',
        'S 33°26´16.0000, W 70°39´01.0000',  # Single coordinate
        '',  # Empty string
        'Invalid coordinate string',  # Invalid format
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_case}")
        result = process_coordinate_string(test_case)
        print(f"First pair: {result['first_pair']}")
        print(f"Latitude: {result['latitude']}")
        print(f"Longitude: {result['longitude']}")
        print(f"Success: {result['success']}")
        if result['error']:
            print(f"Error: {result['error']}")
    
    print("\n=== Script Complete ===")
    print("Use process_coordinate_string() for single strings")
    print("Use process_dataframe_coordinates() for DataFrame processing")


    import logging
import sshtunnel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from pyprojroot import here
import os
import yaml

import logging
logger = logging.getLogger(__name__)

def db_connect(secrets):
    db_params = secrets['db']

    if db_params.get('use_tunnel'):
        tunnel = sshtunnel.SSHTunnelForwarder(db_params['ssh_host'],
                    ssh_username=db_params['ssh_user'],
                    ssh_password=db_params['ssh_pass'],
                    remote_bind_address = (db_params['host'], db_params['port']),
                    local_bind_address=('localhost', db_params['local_port']),
                    ssh_port = db_params['ssh_port']
                )
        tunnel.start()
        eng = create_engine("postgresql+psycopg2://{sql_user}:{sql_pass}@0.0.0.0:{local_port}/{dbname}?sslmode=allow".format(
                sql_user=db_params['user'],
                sql_pass=db_params['pass'],
                local_port=db_params['local_port'],
                dbname=db_params['dbname']
            ))
        # Testing out db connection
        try:
            with eng.connect() as conn:
                result = conn.execute(text("select * from information_schema.tables limit 10;"))
                if result.rowcount > 0:
                    logging.debug("Database connection successful.")
                else:
                    logging.error("Database connected but no data retrieved. Check the database structure and connection")
        except SQLAlchemyError as err:
            logging.error("Error in connecting to database, because of the following cause: ", err.__cause__)
    else:
        tunnel = None
        eng = create_engine('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
                host=db_params['host'],
                port=db_params['port'],
                dbname=db_params['dbname'],
                user=db_params['user'],
                password=db_params['pass']
            ))
        try:
            with eng.connect() as conn:
                result = conn.execute(text("select * from information_schema.tables limit 10;"))
                if result.rowcount > 0:
                    logging.debug("Database connection successful.")
                else:
                    logging.error("Database connected but no data retrieved. Check the database structure and connection")
        except SQLAlchemyError as err:
            logging.error("Error in connecting to database, because of the following cause: ", err.__cause__)
    
    return eng, tunnel

def load_secrets(secrets_path=os.path.join(here(),'config/secrets.yaml')):
    """Load secrets configuration"""
    with open(secrets_path, 'r') as f:
        return yaml.safe_load(f)