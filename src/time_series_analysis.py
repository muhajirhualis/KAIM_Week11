import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Dict

class TimeSeriesAnalyzer:
    """Analyze time series properties: trend, stationarity, volatility."""

    def __init__(self, df: pd.DataFrame):
        # Validate input
        if not {'Date', 'Price'}.issubset(df.columns):
            raise ValueError("DataFrame must contain 'Date' and 'Price' columns")
        if df['Date'].dtype != 'datetime64[us]':
            raise TypeError("'Date' column must be datetime type")
        
        # Store copy with reset index for safe operations
        self.df = df[['Date', 'Price']].copy().reset_index(drop=True)
        self.log_returns: pd.Series = None
    
    def compute_log_returns(self) -> pd.Series:
        """Calculate log returns while PRESERVING datetime index."""
        
        log_returns = np.log(self.df['Price'] / self.df['Price'].shift(1)).dropna()
        # Explicitly reassign index to be safe
        log_returns.index = self.df['Date'].iloc[1:]  # Align with shifted series
        self.log_returns = log_returns
        return log_returns
    
    def adf_test(self, series: pd.Series, label: str = "Series") -> Dict:
        """Perform Augmented Dickey-Fuller test with NaN handling."""
        clean_series = series.dropna()
        if len(clean_series) < 10:
            raise ValueError(f"Series '{label}' too short for ADF test after NaN removal")
        
        result = adfuller(clean_series, autolag='AIC')
        return {
            'statistic': result[0],
            'p_value': result[1],
            'stationary': result[1] < 0.05,
            'interpretation': f"{label} is {'STATIONARY' if result[1] < 0.05 else 'NON-STATIONARY'} (p={result[1]:.4f})"
        }
    
    def analyze_stationarity(self) -> Tuple[Dict, Dict]:
        """Compare stationarity of raw prices vs log returns."""
        if self.log_returns is None:
            self.compute_log_returns()
        
        price_adf = self.adf_test(self.df['Price'], "Raw Prices")
        returns_adf = self.adf_test(self.log_returns, "Log Returns")
        return price_adf, returns_adf
    
    def plot_trend_and_volatility(self, save_path: str = None) -> None:
        """Visualize price trend and volatility clustering with robust index handling."""
        # Ensure log returns computed
        if self.log_returns is None:
            self.compute_log_returns()
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        
        # === TREND ANALYSIS ===
        ax1.plot(self.df['Date'], self.df['Price'], 
                alpha=0.4, color='gray', label='Daily Price', linewidth=0.8)
        
        # Add rolling means (handle edge cases)
        for window, label, color in [(30, '30-day', 'blue'), (90, '90-day', 'red')]:
            rolling_mean = self.df['Price'].rolling(window=window, min_periods=1).mean()
            ax1.plot(self.df['Date'], rolling_mean, 
                    label=f'{label} rolling mean', linewidth=2, color=color)
        
        ax1.set_title('Brent Oil Price Trend Analysis (1987–2022)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price (USD/barrel)', fontsize=11)
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # === VOLATILITY ANALYSIS ===
        # Compute volatility on log returns (skip first NaN)
        volatility = self.log_returns.rolling(window=30, min_periods=1).std()
        
        # Plot only where volatility is defined (avoid index mismatch)
        valid_mask = ~volatility.isna()
        ax2.plot(self.df.loc[valid_mask, 'Date'], 
                volatility.loc[valid_mask], 
                color='purple', linewidth=1.2)
        
        ax2.set_title('Volatility Clustering (30-day rolling std of log returns)', 
                     fontsize=14, fontweight='bold')
        ax2.set_ylabel('Volatility', fontsize=11)
        ax2.set_xlabel('Date', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=volatility.mean(), color='red', linestyle='--', 
                   alpha=0.7, label=f'Mean: {volatility.mean():.4f}')
        ax2.legend(fontsize=9)
        
        plt.tight_layout()
        
        # Save if path provided (create directory if needed)
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved to: {save_path}")
        
        plt.show()