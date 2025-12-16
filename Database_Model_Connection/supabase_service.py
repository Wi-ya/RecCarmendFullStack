"""
Supabase Service
Abstraction layer for database operations using Supabase.
"""

import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from supabase import create_client, Client

# Try to import psycopg2 for direct PostgreSQL connection
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Try to import pandas for CSV reading
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class SupabaseService:
    """
    Service class for interacting with Supabase database.
    Provides methods for querying car listings.
    """
    
    def __init__(self, db_url: Optional[str] = None, db_api_key: Optional[str] = None):
        """
        Initialize Supabase client.
        
        Args:
            db_url: Supabase project URL. If None, will try to get from environment.
            db_api_key: Supabase API key. If None, will try to get from environment.
        
        Raises:
            ValueError: If credentials are not provided or found in environment.
            ConnectionError: If connection to Supabase fails.
        """
        if db_url is None:
            db_url = os.getenv("DB_URL")
        if db_api_key is None:
            db_api_key = os.getenv("DB_API_KEY")
        
        if not db_url or not db_api_key:
            raise ValueError(
                "Missing Supabase credentials. "
                "Please provide DB_URL and DB_API_KEY or set them as environment variables."
            )
        
        try:
            print("Connecting to Supabase database...")
            self.client: Client = create_client(db_url, db_api_key)
            self.db_url = db_url
            print("✅ Connected to Supabase database")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")
    
    def search_cars(
        self,
        maximum_price: Optional[int] = None,
        maximum_mileage: Optional[int] = None,
        color: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        car_type: Optional[str] = None,
        limit: int = 10,
        return_has_more: bool = False,
        last_id: Optional[int] = None
    ):
        """
        Search for cars matching the specified criteria.
        
        Args:
            maximum_price: Maximum price filter
            maximum_mileage: Maximum mileage filter
            color: Color filter (case-insensitive partial match)
            make: Make filter (case-insensitive partial match)
            model: Model filter (case-insensitive partial match)
            min_year: Minimum year filter
            max_year: Maximum year filter
            car_type: Car type/body type filter (case-insensitive partial match)
            limit: Maximum number of results to return (default: 10)
            return_has_more: If True, returns tuple with has_more and total_count
            last_id: ID of the last car from previous page (for pagination)
        
        Returns:
            If return_has_more is False: List of car dictionaries
            If return_has_more is True: Tuple of (results, has_more, total_count)
        """
        # Normalize input values
        color = color.lower() if color and color.lower() not in ["null", "", None] else None
        make = make.lower() if make and make.lower() not in ["null", "", None] else None
        model = model.lower() if model and model.lower() not in ["null", "", None] else None
        car_type = car_type.lower() if car_type and car_type.lower() not in ["null", "", None] else None
        
        # Build the query with filters
        query = self.client.table('CarListings').select('*', count='exact')
        
        # Apply pagination: skip cars with ID <= last_id
        if last_id is not None:
            query = query.gt('id', last_id)
        
        # Apply numeric filters
        if maximum_price and maximum_price > 0:
            query = query.lte('price', maximum_price)
        if maximum_mileage and maximum_mileage > 0:
            query = query.lte('mileage', maximum_mileage)
        if min_year and min_year > 0:
            query = query.gte('year', min_year)
        if max_year and max_year > 0:
            query = query.lte('year', max_year)
        
        # Apply text filters (case-insensitive search)
        if color:
            query = query.ilike('color', f'%{color}%')
        if make:
            # Use exact match for make (case-insensitive)
            query = query.ilike('make', make)
        if model:
            # Use partial match for model (case-insensitive)
            query = query.ilike('model', f'%{model}%')
        
        # Handle carType - try both possible column names
        if car_type:
            try:
                query_with_cartype = query.ilike('body_type', f'%{car_type}%').order('id', desc=False)
                response = query_with_cartype.limit(limit).execute()
                if response.data and len(response.data) > 0:
                    results = response.data
                    if return_has_more:
                        total_count = response.count if hasattr(response, 'count') else len(results)
                        has_more = len(results) == limit
                        return results, has_more, total_count
                    return results
            except Exception as e:
                # If body_type fails, try carType column
                try:
                    query_with_cartype = query.ilike('carType', f'%{car_type}%').order('id', desc=False)
                    response = query_with_cartype.limit(limit).execute()
                    if response.data and len(response.data) > 0:
                        results = response.data
                        if return_has_more:
                            total_count = response.count if hasattr(response, 'count') else len(results)
                            has_more = len(results) == limit
                            return results, has_more, total_count
                        return results
                except Exception as e2:
                    # If both fail, continue without carType filter
                    print(f"Warning: Could not filter by car type '{car_type}', showing all types")
        
        # Execute query (either no carType filter, or carType filter failed)
        try:
            response = query.order('id', desc=False).limit(limit).execute()
            results = response.data if response.data else []
            
            if return_has_more:
                total_count = response.count if hasattr(response, 'count') else len(results)
                has_more = len(results) == limit
                return results, has_more, total_count
            
            return results
        except Exception as e:
            print(f"Error querying database: {e}")
            if return_has_more:
                return [], False, 0
            return []
    
    def get_all_cars(self, limit: int = 10) -> List[Dict]:
        """
        Get all cars from the database (for testing/debugging).
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of car dictionaries
        """
        try:
            response = self.client.table('CarListings').select('*').limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting all cars: {e}")
            return []
    
    def sortDB(
        self,
        maximum_price: Optional[int] = None,
        maximum_mileage: Optional[int] = None,
        color: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        car_type: Optional[str] = None,
        return_has_more: bool = False
    ):
        """
        Alias method for search_cars() to match sequence diagram naming.
        This method calls search_cars() internally.
        
        Args:
            maximum_price: Maximum price filter
            maximum_mileage: Maximum mileage filter
            color: Color filter
            make: Make filter
            model: Model filter
            min_year: Minimum year filter
            max_year: Maximum year filter
            car_type: Car type/body type filter
            return_has_more: If True, returns tuple with has_more and total_count
        
        Returns:
            If return_has_more is False: List of car dictionaries
            If return_has_more is True: Tuple of (results, has_more, total_count)
        """
        return self.search_cars(
            maximum_price=maximum_price,
            maximum_mileage=maximum_mileage,
            color=color,
            make=make,
            model=model,
            min_year=min_year,
            max_year=max_year,
            car_type=car_type,
            limit=10,
            return_has_more=return_has_more
        )
    
    def clear_table(self, table_name: str = 'CarListings') -> None:
        """
        Clear all data from the specified table.
        
        Args:
            table_name: Name of the table to clear (default: 'CarListings')
        """
        print(f"Clearing table '{table_name}'...")
        self.client.table(table_name).delete().neq('id', -1).execute()
        print("✅ Table cleared")
    
    def reset_id_sequence(self, table_name: str = 'CarListings') -> None:
        """
        Reset the ID identity column to start from 1.
        
        Args:
            table_name: Name of the table (default: 'CarListings')
        
        Raises:
            ValueError: If DATABASE_URL not found or psycopg2 not available
        """
        print(f"Resetting ID sequence for '{table_name}'...")
        
        db_connection_string = os.getenv("DATABASE_URL")
        if not db_connection_string:
            raise ValueError("DATABASE_URL not found in .env - required for ID reset")
        
        if not PSYCOPG2_AVAILABLE:
            raise ValueError("psycopg2 not available - install with: pip install psycopg2-binary")
        
        # Add SSL if not present
        if 'sslmode=' not in db_connection_string:
            separator = '&' if '?' in db_connection_string else '?'
            db_connection_string = f"{db_connection_string}{separator}sslmode=require"
        
        # Connect and reset
        conn = psycopg2.connect(db_connection_string)
        cursor = conn.cursor()
        
        # Try identity column reset
        cursor.execute(f'ALTER TABLE "{table_name}" ALTER COLUMN id RESTART WITH 1;')
        conn.commit()
        
        cursor.close()
        conn.close()
        print("✅ ID sequence reset to start from 1")
    
    def _prepare_data(self, file_path: Path) -> list:
        """
        Read CSV, clean data, and return records ready for upload.
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            List of records ready for upload
        
        Raises:
            ImportError: If pandas is not available
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas not available - install with: pip install pandas")
        
        print(f"Reading {file_path}...")
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows")
        
        # Clean data: replace "CALL" with 0
        print("Cleaning data...")
        if 'price' in df.columns:
            df['price'] = df['price'].astype(str).str.upper().str.replace('CALL', '0', regex=False)
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
        if 'mileage' in df.columns:
            df['mileage'] = df['mileage'].astype(str).str.upper().str.replace('CALL', '0', regex=False)
            df['mileage'] = pd.to_numeric(df['mileage'], errors='coerce').fillna(0).astype(int)
        
        # Handle NULLs
        df = df.where(pd.notnull(df), None)
        
        # Remove auto-generated columns
        auto_generated_columns = ['id', 'created_at', 'updated_at']
        columns_to_drop = [col for col in auto_generated_columns if col in df.columns]
        if columns_to_drop:
            df = df.drop(columns=columns_to_drop)
        
        # Convert to records and randomize
        records = df.to_dict(orient="records")
        print("Randomizing record order...")
        random.shuffle(records)
        
        return records
    
    def upload_data(self, table_name: str, records: list, chunk_size: int = 1000) -> int:
        """
        Upload records to Supabase in chunks.
        
        Args:
            table_name: Name of the table to upload to
            records: List of records to upload
            chunk_size: Number of records per chunk (default: 1000)
        
        Returns:
            Number of rows uploaded
        """
        total_rows = len(records)
        print(f"Uploading {total_rows} rows to '{table_name}' (chunks of {chunk_size})...")
        
        uploaded = 0
        for i in range(0, total_rows, chunk_size):
            chunk = records[i:i + chunk_size]
            self.client.table(table_name).insert(chunk).execute()
            uploaded += len(chunk)
            print(f"  Uploaded {uploaded}/{total_rows} rows...", end='\r')
        
        print(f"\n✅ Successfully uploaded {uploaded} rows")
        return uploaded
    
    def upload_all_listings(
        self, 
        csv_file_path: Optional[Path] = None,
        clear_table_flag: bool = True, 
        reset_id: bool = True
    ) -> int:
        """
        Main upload function: Clear → Reset ID → Upload.
        Uploads data from all_listings.csv to CarListings table.
        
        Args:
            csv_file_path: Path to CSV file. If None, uses default location (data/all_listings.csv)
            clear_table_flag: Clear table before uploading (default: True)
            reset_id: Reset ID sequence to start from 1 (default: True)
        
        Returns:
            Number of rows uploaded
        
        Raises:
            FileNotFoundError: If CSV file not found
            ImportError: If pandas not available
        """
        # Determine file path
        if csv_file_path is None:
            # Default: look for data/all_listings.csv relative to project root
            current_script_path = Path(__file__).resolve()
            data_folder = current_script_path.parent.parent / "data"
            csv_file_path = data_folder / "all_listings.csv"
        
        if not csv_file_path.exists():
            raise FileNotFoundError(f"Could not find CSV file at: {csv_file_path}")
        
        table_name = 'CarListings'
        
        # Prepare data
        records = self._prepare_data(csv_file_path)
        
        # Step 1: Clear table
        if clear_table_flag:
            self.clear_table(table_name)
        
        # Step 2: Reset ID sequence
        if reset_id:
            self.reset_id_sequence(table_name)
        
        # Step 3: Upload data
        uploaded = self.upload_data(table_name, records)
        
        return uploaded

