import pandas as pd
from pathlib import Path
from typing import Union

class BrentDataLoader:
    """Load and validate Brent oil price data with robust datetime handling."""
    
    def __init__(self, filepath: Union[str, Path]):
        self.filepath = Path(filepath)
        self.df: pd.DataFrame = None
    
    def load(self) -> pd.DataFrame:
        """Load data with robust datetime parsing (pandas >=2.0 compatible)."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Data file not found: {self.filepath}")
        
        try:
            # Step 1: Read raw CSV without date parsing
            self.df = pd.read_csv(self.filepath)
            
            # Step 2: Standardize column names
            self.df.columns = ['Date', 'Price']
            # Step 3: Parse dates with mixed format handling (pandas >=2.0)
            self.df['Date'] = pd.to_datetime(
                self.df['Date'], 
                format='mixed',  # Handles "20-May-87", "01-Jan-90", etc.
                dayfirst=True,   # Critical: "01/02/2023" = 1 Feb, not 2 Jan
                errors='coerce'  # Convert unparseable dates to NaT (for debugging)
            )
            
            # Step 4: Drop rows with invalid dates
            invalid_dates = self.df['Date'].isna().sum()
            if invalid_dates > 0:
                print(f"⚠️ Warning: Dropped {invalid_dates} rows with invalid dates")
                self.df = self.df.dropna(subset=['Date'])
            
            # Step 5: Sort chronologically and reset index
            self.df = self.df.sort_values('Date').reset_index(drop=True)
            
            self._validate()
            return self.df
            
        except KeyError as e:
            raise ValueError("CSV must contain 'Date' and 'Price' columns") from e
    
    def _validate(self) -> None:
        """Check for abnormal date gaps and missing prices."""
        gaps = self.df['Date'].diff().dt.days
        large_gaps = gaps[gaps > 3]
        if len(large_gaps) > 0:
            print(f"⚠️ Warning: {len(large_gaps)} gaps >3 days detected")
        
        missing_prices = self.df['Price'].isna().sum()
        if missing_prices > 0:
            print(f"⚠️ Warning: {missing_prices} missing price values (forward-filled)")
            self.df['Price'] = self.df['Price'].fillna(method='ffill')