# Brent Oil Price Analysis: Task 1 Workflow Plan

## Analysis Workflow (Data → Insights)

1. **Data Loading & Validation**
   - Load `brent_daily.csv` with `pd.read_csv(parse_dates=['Date'])`
   - Validate date continuity (check for gaps >1 business day)
   - Handle missing values via forward-fill (market closure days)

2. **Exploratory Time Series Analysis**
   - Plot raw prices (1987–2022) with annotated volatility regimes
   - Compute 30/90-day rolling means to isolate trend component
   - Calculate log returns: `np.log(price) - np.log(price.shift(1))`
   - Analyze volatility clustering via rolling 30-day standard deviation

3. **Stationarity Assessment**
   - Augmented Dickey-Fuller (ADF) test on prices vs. log returns
   - KPSS test for trend-stationarity confirmation
   - Decision rule: Model log returns if ADF p-value < 0.05

4. **Event Dataset Integration**
   - Merge curated geopolitical events (see `data/events.csv`)
   - Align event dates with price series (±3-day window for market reaction)

5. **Bayesian Change Point Modeling**
   - Single-change-point model: `price ~ N(μ₁, σ₁)` for `t < τ`, `N(μ₂, σ₂)` for `t ≥ τ`
   - MCMC sampling via PyMC (2,000 draws, 2 chains)
   - Extract posterior distribution of τ, Δμ = μ₂ - μ₁

6. **Causal Interpretation Framework**
   - Map detected τ to event dates within 7-day window
   - Quantify impact magnitude with 95% credible intervals
   - **Critical limitation**: Temporal correlation ≠ causation (see §3)

7. **Stakeholder Communication**
   - Investors: Interactive Plotly dashboard showing event-price alignment
   - Policymakers: PDF report with policy efficacy assessment tables
   - Energy companies: CSV export of high-volatility windows for risk planning

## Assumptions & Limitations

### Key Assumptions

- Oil price reactions to events occur within 7 business days
- Single dominant structural break per analysis window (simplification)
- Log returns approximately Gaussian (violated during extreme shocks)

### Critical Limitation: Correlation ≠ Causation
>
> **A statistically significant change point coinciding with an event date establishes temporal association—not causal impact.** Confounding factors include:
>
> - **Anticipatory pricing**: Markets react *before* official announcements (e.g., OPEC meeting leaks)
> - **Simultaneous shocks**: Multiple events cluster (e.g., Mar 2020: pandemic + Saudi-Russia price war)
> - **Omitted variables**: Global GDP, USD strength, and inventory levels co-vary with prices
> - **Reverse causality**: Price spikes may *trigger* policy responses (e.g., SPR releases)
>
> **Causal claims require**: (a) counterfactual modeling ("what if event hadn't occurred?"), (b) controlling for confounders via multivariate analysis, and (c) domain validation. This analysis identifies *candidate structural breaks*—causal attribution remains a hypothesis requiring external validation.

## Communication Channels

| Stakeholder      | Channel               | Format                          | Key Metric                     |
|------------------|-----------------------|---------------------------------|--------------------------------|
| Investors        | Web dashboard         | Plotly/Dash interactive chart   | % price change ±7 days         |
| Policymakers     | Formal report         | PDF with executive summary      | Policy efficacy score (1–5)    |
| Energy Companies | Operational briefing  | Annotated volatility timeline   | High-risk date windows         |
| Public           | Data story            | Medium article with visuals     | Plain-language event context   |


## Change Point Model: Purpose & Expected Outputs

**Purpose**: Detect *structural breaks* where statistical properties (mean, variance) of the time series shift abruptly—indicating regime changes potentially triggered by external shocks.

**Expected Outputs**:

- **Posterior distribution of τ**: Probability density over time showing most likely change point date(s)
- **Parameter shifts**: Posterior distributions of μ₁, μ₂ (and σ₁, σ₂) with credible intervals
- **Impact magnitude**: Probabilistic statement like *"P(μ₂ > μ₁ + $5) = 0.94"*
- **Uncertainty quantification**: 95% credible interval for change date (e.g., "Sep 12–28, 2019")

**Limitations**:

- Cannot identify *cause*—only statistical discontinuity
- Struggles with gradual transitions (designed for abrupt shifts)
- Single-change-point models miss complex multi-regime dynamics
- Sensitive to prior specification when data evidence is weak