"""
Legacy main.py - Now just calls upload_listings.py
This file is kept for backward compatibility.
For new code, use upload_listings.py directly.
"""
from upload_listings import upload_all_listings

if __name__ == "__main__":
    # Simply call the upload function
    # This maintains backward compatibility while using the cleaner implementation
    upload_all_listings()