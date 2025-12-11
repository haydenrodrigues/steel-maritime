# Maritime Demurrage Optimizer

A statistical and ontology-based maritime demurrage minimization system designed to help ship operators save millions by predicting and reducing port delays.

## Overview

This application provides ship operators with intelligent tools to:
- Predict demurrage costs before voyages begin
- Optimize arrival times to minimize port waiting
- Analyze historical demurrage patterns
- Leverage maritime domain knowledge through an ontology system

## Project Architecture

```
/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── ontology.py            # Maritime domain ontology
├── demurrage_model.py     # Statistical prediction model
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base layout
│   ├── dashboard.html     # Main dashboard
│   ├── voyage_planning.html  # Voyage planning & predictions
│   ├── analytics.html     # Historical analytics
│   ├── fleet.html         # Fleet management
│   ├── ports.html         # Port database
│   └── ontology.html      # Ontology viewer
└── static/                # Static assets
```

## Key Components

### 1. Demurrage Prediction Model
Uses statistical analysis to predict port delays based on:
- Port congestion levels
- Cargo handling complexity
- Weather patterns
- Port efficiency metrics
- Vessel-cargo compatibility

### 2. Maritime Ontology
Encodes domain knowledge about:
- Vessel types (Bulk Carriers, Tankers, Container Ships, General Cargo)
- Cargo categories and handling requirements
- Port terminal capabilities
- Delay causes and mitigation strategies

### 3. Database Models
- **Vessel**: Fleet vessels with specs and demurrage rates
- **Port**: Global ports with congestion and handling data
- **CargoType**: Cargo categories and handling complexity
- **Voyage**: Planned and completed voyages
- **DemurrageRecord**: Historical demurrage incidents

## Tech Stack

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Statistical**: NumPy, SciPy, Pandas
- **Frontend**: Bootstrap 5, Jinja2 templates

## Running the Application

The application runs on port 5000:
```bash
python app.py
```

## Features

1. **Dashboard**: Overview of fleet, demurrage costs, and recent voyages
2. **Voyage Planning**: Get predictions with risk factors and recommendations
3. **Analytics**: Historical analysis by port, vessel, and time
4. **Fleet Management**: View and manage vessel details
5. **Port Database**: Port profiles with congestion metrics
6. **Ontology Viewer**: Explore maritime domain relationships
