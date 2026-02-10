import pandas as pd
from pathlib import Path
from typing import List, Dict

class EventCompiler:
    """Manage curated geopolitical event dataset."""
    
    REQUIRED_COLUMNS = ['date', 'event_type', 'description', 'region']
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.events: pd.DataFrame = None
    
    def load(self) -> pd.DataFrame:
        """Load and validate event dataset."""
        self.events = pd.read_csv(self.filepath, parse_dates=['date'])
        
        # Validate schema
        missing_cols = set(self.REQUIRED_COLUMNS) - set(self.events.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Validate date range coverage
        min_date = self.events['date'].min()
        max_date = self.events['date'].max()
        print(f"✅ Loaded {len(self.events)} events from {min_date.date()} to {max_date.date()}")
        return self.events
    
    def get_events_in_window(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter events within date range."""
        mask = (self.events['date'] >= start_date) & (self.events['date'] <= end_date)
        return self.events.loc[mask].copy()