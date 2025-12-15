"""
Data Maintenance Module
Handles scheduled and automated data updates.
This module is responsible for running scrapers on a schedule (e.g., weekly).
Uses ScrapingController to perform the actual scraping operations.
After scraping, uploads data to Supabase with randomized order.
"""
import schedule
import time
import sys
from pathlib import Path
from datetime import datetime

# Import ScrapingController - works both as module and script
try:
    from .scraping_controller import ScrapingController
except ImportError:
    from scraping_controller import ScrapingController

# Import SupabaseService from Database_Model_Connection
import sys
_db_conn_path = Path(__file__).parent.parent / "Database_Model_Connection"
if _db_conn_path.exists():
    sys.path.insert(0, str(_db_conn_path.parent))
    from Database_Model_Connection import SupabaseService
else:
    raise ImportError(f"Could not find Database_Model_Connection at {_db_conn_path}")


class DataMaintenance:
    """
    Manages automated data maintenance tasks.
    Handles scheduling and execution of periodic scraping operations.
    """
    
    def __init__(self):
        """Initialize the data maintenance scheduler."""
        self.controller = ScrapingController()
        self.last_run: datetime | None = None
    
    def run_weekly_update(self, upload_to_supabase: bool = True) -> None:
        """
        Execute weekly data update by running all scrapers and uploading to Supabase.
        This method is called by the scheduler.
        
        Args:
            upload_to_supabase: If True, uploads scraped data to Supabase after scraping (default: True)
        """
        print(f"\n{'='*70}")
        print(f"🔄 Starting weekly data update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        try:
            # Step 1: Run all scrapers (saves to CSV files)
            print("📥 Step 1: Scraping websites...")
            self.controller.scrape_all_websites()
            print("\n✅ Scraping completed successfully")
            
            # Step 2: Upload to Supabase (with randomized order)
            if upload_to_supabase:
                print(f"\n{'='*70}")
                print("📤 Step 2: Uploading to Supabase...")
                print(f"{'='*70}\n")
                try:
                    supabase_service = SupabaseService()
                    rows_uploaded = supabase_service.upload_all_listings(
                        clear_table_flag=True,  # Clear existing data
                        reset_id=True  # Reset IDs to start from 1
                    )
                    print(f"\n✅ Upload completed: {rows_uploaded} rows uploaded to Supabase")
                except Exception as upload_error:
                    print(f"\n❌ Upload to Supabase failed: {upload_error}")
                    print("⚠️  Scraping completed, but data was not uploaded to database")
                    raise
            
            self.last_run = datetime.now()
            print(f"\n{'='*70}")
            print(f"✅ Weekly update completed successfully at {self.last_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}\n")
        except Exception as e:
            print(f"\n❌ Weekly update failed: {e}")
            raise
    
    def schedule_weekly_updates(self, day_of_week: str = "monday", time: str = "09:00") -> None:
        """
        Schedule weekly scraping updates.
        
        Args:
            day_of_week: Day of the week to run updates (e.g., "monday", "sunday")
            time: Time of day to run updates (e.g., "09:00", "14:30")
        """
        # Schedule weekly updates
        getattr(schedule.every(), day_of_week.lower()).at(time).do(self.run_weekly_update)
        print(f"📅 Scheduled weekly updates: Every {day_of_week} at {time}")
    
    def run_scheduler(self) -> None:
        """
        Run the scheduler continuously.
        This method blocks and runs the scheduled tasks.
        """
        print("🚀 Data maintenance scheduler started")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped by user")
    
    def run_manual_update(self, upload_to_supabase: bool = True) -> None:
        """
        Manually trigger a data update (useful for testing or on-demand updates).
        
        Args:
            upload_to_supabase: If True, uploads scraped data to Supabase after scraping (default: True)
        """
        print("🔧 Running manual data update...")
        self.run_weekly_update(upload_to_supabase=upload_to_supabase)


def main():
    """
    Main entry point for data maintenance.
    Can be run as a scheduled task or daemon.
    """
    maintenance = DataMaintenance()
    
    # Schedule weekly updates (every Monday at 9:00 AM)
    maintenance.schedule_weekly_updates(day_of_week="monday", time="09:00")
    
    # Option 1: Run scheduler continuously (for long-running processes)
    maintenance.run_scheduler()
    
    # Option 2: Run a one-time update (uncomment to use instead)
    # maintenance.run_manual_update()


if __name__ == "__main__":
    main()

