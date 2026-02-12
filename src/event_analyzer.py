import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List, Tuple, Dict

class EventImpactAnalyzer:
    """Associate detected change points with geopolitical events and quantify impacts."""
    
    def __init__(self, events_df: pd.DataFrame):
        self.events = events_df.copy()
        self.events['date'] = pd.to_datetime(self.events['date'])
    
    def associate_change_points(
        self, 
        change_point_date: pd.Timestamp, 
        window_days: int = 7
    ) -> List[Dict]:
        """
        Find events within ±window_days of detected change point.
        
        Returns list of matching events with temporal proximity score.
        """
        window_start = change_point_date - timedelta(days=window_days)
        window_end = change_point_date + timedelta(days=window_days)
        
        matches = self.events[
            (self.events['date'] >= window_start) & 
            (self.events['date'] <= window_end)
        ].copy()
        
        if len(matches) == 0:
            return []
        
        # Calculate proximity score (1.0 = exact match, 0.0 = edge of window)
        matches['days_from_cp'] = (matches['date'] - change_point_date).dt.days.abs()
        matches['proximity_score'] = 1 - (matches['days_from_cp'] / window_days)
        
        return matches.sort_values('proximity_score', ascending=False).to_dict('records')
    
    def quantify_event_impact(
        self,
        event: Dict,
        impact_results: Dict,
        price_level_before: float,
        price_level_after: float
    ) -> str:
        """
        Generate human-readable impact statement with probabilistic quantification.
        
        Example: "Following Russia-Ukraine invasion (Feb 24, 2022), 
                  95% credible interval for price increase: +$28 to +$38 (32% rise)"
        """
        event_date = pd.Timestamp(event['date'])
        event_desc = event['description']
        event_type = event['event_type']
        
        # Convert log return shift to price percentage change
        mean_shift = impact_results['mean_shift_median']
        price_change_pct = (np.exp(mean_shift) - 1) * 100
        
        # Directional statement
        if impact_results['prob_mean_increase'] > 0.9:
            direction = "increase"
            magnitude = f"+{price_change_pct:.1f}%"
        elif impact_results['prob_mean_decrease'] > 0.9:
            direction = "decrease"
            magnitude = f"{price_change_pct:.1f}%"
        else:
            direction = "shift"
            magnitude = f"{price_change_pct:.1f}%"
        
        # Volatility statement
        vol_shift = impact_results['vol_shift_median']
        vol_change_pct = (np.exp(vol_shift) - 1) * 100
        vol_statement = f"Volatility {'increased' if vol_shift > 0 else 'decreased'} by {abs(vol_change_pct):.0f}%"
        
        return (
            f"Following {event_type} event '{event_desc}' ({event_date.date()}), "
            f"Bayesian analysis detects structural break with {direction} of {magnitude} "
            f"({impact_results['prob_mean_increase']*100:.0f}% probability). "
            f"{vol_statement}."
        )