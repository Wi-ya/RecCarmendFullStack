"""
Main entry point for uploading listings to Supabase.
Uses SupabaseService to upload data.
"""
import argparse
from pathlib import Path

# Load .env from project root only (ReccarmendFullStack/.env)
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
except ImportError:
    pass

from supabase_service import SupabaseService

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload CSV to Supabase CarListings table.")
    parser.add_argument(
        "--no-reset-id",
        action="store_true",
        help="Skip resetting the ID sequence (use if reset step hangs or fails).",
    )
    args = parser.parse_args()

    supabase_service = SupabaseService()
    supabase_service.upload_all_listings(reset_id=not args.no_reset_id)