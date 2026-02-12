import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib
matplotlib.use('Agg')  # Critical for Windows
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pymc')

class SingleChangePointModel:
    """
    Bayesian change point detection with CONTINUOUS tau approximation for speed.
    Avoids discrete sampling bottlenecks by modeling tau as float → enables full NUTS efficiency.
    """
    
    def __init__(self, data: np.ndarray, dates: pd.DatetimeIndex):
        """
        Initialize model with time series data.
        
        Args:
            data: 1D array of log returns (stationary series)
            dates: DatetimeIndex aligned with data
        """
        if len(data) != len(dates):
            raise ValueError(f"Data length ({len(data)}) must match dates length ({len(dates)})")
        self.data = np.asarray(data, dtype=np.float64)
        self.dates = pd.DatetimeIndex(dates)
        self.model = None
        self.trace = None
        self.tau_posterior = None
    
    def build_model(self) -> pm.Model:
        """Build model with CONTINUOUS tau (critical for sampling speed)."""
        n_obs = len(self.data)
        with pm.Model() as model:
            # CONTINUOUS tau (0.0 to n_obs) → enables efficient NUTS sampling
            tau_raw = pm.Uniform('tau_raw', lower=30, upper=n_obs-30)
            
            # Pre/post means (log returns typically near 0)
            mu1 = pm.Normal('mu1', mu=0, sigma=0.05)
            mu2 = pm.Normal('mu2', mu=0, sigma=0.05)
            
            # Pre/post volatilities
            sigma1 = pm.HalfNormal('sigma1', sigma=0.05)
            sigma2 = pm.HalfNormal('sigma2', sigma=0.05)
            
            # Vectorized switch using where (more efficient than pm.math.switch)
            idx = np.arange(n_obs)
            mu = pm.math.where(idx < tau_raw, mu1, mu2)
            sigma = pm.math.where(idx < tau_raw, sigma1, sigma2)
            
            # Likelihood
            pm.Normal('obs', mu=mu, sigma=sigma, observed=self.data)
            
            # Deterministic transformed variable for interpretation
            pm.Deterministic('tau', tau_raw)
            
        self.model = model
        return model
    
    def sample(self, draws: int = 500, tune: int = 500, chains: int = 2, 
               target_accept: float = 0.85) -> az.InferenceData:
        """Sample with Windows-safe settings (single core, no progress bar)."""
        if self.model is None:
            self.build_model()
        
        with self.model:
            self.trace = pm.sample(
                draws=draws,
                tune=tune,
                chains=chains,
                target_accept=target_accept,
                random_seed=42,
                return_inferencedata=True,
                progressbar=False,  # Prevents Windows console corruption
                cores=1             # Avoids Windows multiprocessing issues
            )
        return self.trace
    
    def diagnose_convergence(self) -> Dict:
        """Check convergence diagnostics."""
        summary = az.summary(self.trace, var_names=['tau', 'mu1', 'mu2', 'sigma1', 'sigma2'])
        r_hat_max = summary['r_hat'].max()
        ess_min = summary['ess_bulk'].min()
        
        return {
            'r_hat_max': r_hat_max,
            'ess_min': ess_min,
            'converged': (r_hat_max < 1.05) and (ess_min > 200),  # Lower ESS threshold for interim
            'summary': summary
        }
    
    def extract_change_point_date(self, credible_interval: float = 0.95) -> Dict:
        """Convert tau samples to calendar dates."""
        tau_samples = self.trace.posterior['tau'].values.flatten()
        tau_mode = int(np.round(np.median(tau_samples)))
        tau_date = self.dates[tau_mode]
        
        # 95% credible interval
        lower_idx = int(np.quantile(tau_samples, (1 - credible_interval) / 2))
        upper_idx = int(np.quantile(tau_samples, 1 - (1 - credible_interval) / 2))
        ci_start = self.dates[lower_idx]
        ci_end = self.dates[upper_idx]
        
        self.tau_posterior = tau_samples
        return {
            'mode_index': tau_mode,
            'mode_date': tau_date,
            'credible_interval': (ci_start, ci_end),
            'samples': tau_samples
        }
    
    def plot_posterior_tau(self, save_path: Optional[str] = None) -> None:
        """Visualize posterior distribution of change point."""
        if self.tau_posterior is None:
            raise ValueError("Run extract_change_point_date() first")
        
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.hist(self.tau_posterior, bins=40, color='steelblue', alpha=0.7, edgecolor='black')
        median_tau = np.median(self.tau_posterior)
        ax.axvline(median_tau, color='red', linestyle='--', linewidth=2,
                  label=f'Median τ: {self.dates[int(median_tau)].date()}')
        ax.set_title('Posterior Distribution of Change Point (τ)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time Index')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    
    def quantify_impact(self) -> Dict:
        """Compute probabilistic impact statements."""
        mu1_samples = self.trace.posterior['mu1'].values.flatten()
        mu2_samples = self.trace.posterior['mu2'].values.flatten()
        sigma1_samples = self.trace.posterior['sigma1'].values.flatten()
        sigma2_samples = self.trace.posterior['sigma2'].values.flatten()
        
        mean_shift = mu2_samples - mu1_samples
        vol_shift = sigma2_samples - sigma1_samples
        
        return {
            'mean_shift_median': np.median(mean_shift),
            'mean_shift_ci': np.percentile(mean_shift, [2.5, 97.5]),
            'prob_mean_increase': np.mean(mean_shift > 0.01),
            'prob_mean_decrease': np.mean(mean_shift < -0.01),
            'vol_shift_median': np.median(vol_shift),
            'vol_shift_ci': np.percentile(vol_shift, [2.5, 97.5]),
            'prob_vol_increase': np.mean(vol_shift > 0.005)
        }