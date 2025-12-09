"""
Upload all_listings.csv to Supabase CarListings table.
Clears table, resets ID sequence, and uploads data.
"""
import os
import random
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Try to import psycopg2 for direct PostgreSQL connection
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Load environment variables
load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_API_KEY = os.getenv("DB_API_KEY")

if not DB_URL or not DB_API_KEY:
    raise ValueError(
        "Missing Supabase credentials. Create a .env file with:\n"
        "DB_URL=https://your-project.supabase.co\n"
        "DB_API_KEY=your-service-role-key"
    )


def clear_table(supabase: Client, table_name: str) -> None:
    """Clear all data from the table."""
    print(f"Step 1: Clearing table '{table_name}'...")
    supabase.table(table_name).delete().neq('id', -1).execute()
    print("✅ Table cleared")


def reset_id_sequence(table_name: str) -> None:
    """Reset the ID identity column to start from 1."""
    print(f"Step 2: Resetting ID sequence for '{table_name}'...")
    
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


def prepare_data(file_path: Path) -> list:
    """Read CSV, clean data, and return records ready for upload."""
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


def upload_data(supabase: Client, table_name: str, records: list, chunk_size: int = 1000) -> int:
    """Upload records to Supabase in chunks."""
    total_rows = len(records)
    print(f"Step 3: Uploading {total_rows} rows to '{table_name}' (chunks of {chunk_size})...")
    
    uploaded = 0
    for i in range(0, total_rows, chunk_size):
        chunk = records[i:i + chunk_size]
        supabase.table(table_name).insert(chunk).execute()
        uploaded += len(chunk)
        print(f"  Uploaded {uploaded}/{total_rows} rows...", end='\r')
    
    print(f"\n✅ Successfully uploaded {uploaded} rows")
    return uploaded


def upload_all_listings(clear_table_flag: bool = True, reset_id: bool = True) -> int:
    """
    Main upload function: Clear → Reset ID → Upload
    
    Args:
        clear_table_flag: Clear table before uploading (default: True)
        reset_id: Reset ID sequence to start from 1 (default: True)
    
    Returns:
        int: Number of rows uploaded
    """
    # Setup
    current_script_path = Path(__file__).resolve()
    data_folder = current_script_path.parent.parent / "data"
    file_path = data_folder / "all_listings.csv"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find all_listings.csv at: {file_path}")
    
    supabase: Client = create_client(DB_URL, DB_API_KEY)
    table_name = 'CarListings'
    
    # Prepare data
    records = prepare_data(file_path)
    
    # Step 1: Clear table
    if clear_table_flag:
        clear_table(supabase, table_name)
    
    # Step 2: Reset ID sequence
    if reset_id:
        reset_id_sequence(table_name)
    
    # Step 3: Upload data
    uploaded = upload_data(supabase, table_name, records)
    
    return uploaded


if __name__ == "__main__":
    upload_all_listings()

