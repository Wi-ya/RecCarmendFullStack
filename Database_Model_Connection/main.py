"""
Main entry point for uploading listings to Supabase.
Uses SupabaseService to upload data.
"""
from supabase_service import SupabaseService

if __name__ == "__main__":
    # Create SupabaseService instance
    supabase_service = SupabaseService()
    
    # Upload all listings
    supabase_service.upload_all_listings()