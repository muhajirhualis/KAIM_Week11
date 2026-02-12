# Brent Oil Price Change Point Analysis

Detect structural breaks in Brent oil prices linked to geopolitical events using Bayesian change point models.

## Project Overview

- **Objective**: Identify statistically significant regime shifts in Brent oil prices (1987–2022) and correlate with major geopolitical/economic events
- **Core Method**: Bayesian change point detection with PyMC
- **Key Output**: Probabilistic event impact assessment with uncertainty quantification

## ⚙️ Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
## Brent Oil Price Dashboard

Interactive dashboard for analyzing geopolitical event impacts on Brent oil prices.

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```
API runs on: http://localhost:5000

Frontend Setup
```bash
cd frontend
npm install
npm start
```
Dashboard runs on: http://localhost:3000
