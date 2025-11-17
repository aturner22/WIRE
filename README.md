# WIRE: Weather-Induced Risk Exposure

Weather-based hazard assessment system for care institutions.

## Overview

WIRE transforms meteorological data into risk assessments for institutions with a duty of care. The modular system monitors eight weather-related hazards with thresholds calibrated for elderly, children, and medically vulnerable individuals.

Each hazard calculation is based on cited academic research.

## Features

- Real-time and 5-day forecast hazard monitoring
- Eight comprehensive hazard assessments with 1-5 risk scoring
- Academic methodology with citations
- Risk thresholds calibrated for vulnerable populations
- Global coverage via OpenWeather API
- Clean, professional interface

## Hazard Modules

### 1. Heat Stress
Uses NOAA Heat Index methodology to assess heat-related illness risk from temperature and humidity.
- Citation: Rothfusz (1990), NWS Technical Attachment SR 90-23

### 2. Cold Exposure
Applies Wind Chill Index to evaluate hypothermia and frostbite risk.
- Citation: Environment Canada Wind Chill Model

### 3. Respiratory Risk
Monitors air quality using EPA AQI standards for PM2.5, PM10, NO2, O3, SO2, and CO.
- Citation: Hoek et al. (2013), Environmental Health

### 4. Slip/Fall Risk
Assesses surface conditions for ice, frost, and wet surface hazards.
- Citation: Gao et al. (2004), Ergonomics

### 5. Storm Risk
Composite assessment of wind speed, pressure, and precipitation intensity.
- Citation: WMO Guidelines (WMO-No. 1150, 2015)

### 6. Flood Risk
Evaluates flooding potential from rainfall intensity and accumulation.
- Citation: Versini et al. (2010), Journal of Hydrology

### 7. Dehydration Risk
Elderly-specific dehydration risk based on heat index and environmental factors.
- Citation: WHO Heat-Health Action Plan Guidance (2011)

### 8. Travel/Visibility Risk
Assesses transport safety from visibility, precipitation, and wind conditions.
- Citation: Edwards (1999), Journal of Safety Research

## Technology Stack

**Backend:**
- FastAPI (Python 3.11)
- Pydantic for validation
- OpenWeather API integration

**Frontend:**
- Next.js 14 with TypeScript
- Tailwind CSS

## Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- OpenWeather API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd openweather-health-watch
```

2. Configure environment variables:
```bash
cp .env.example .env
# Add your OPENWEATHER_API_KEY to .env
```

3. Install backend dependencies:
```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Running Locally

Start the backend server:
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

Start the frontend development server:
```bash
cd frontend
npm run dev
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
./
├── backend/
│   ├── app/
│   │   ├── api/routes/              # REST endpoints
│   │   ├── services/
│   │   │   ├── weather_service.py   # OpenWeather client
│   │   │   ├── hazard_calculator.py # Orchestrator
│   │   │   └── hazards/             # Hazard modules
│   │   ├── schemas/                 # Pydantic models
│   │   └── main.py                  # FastAPI application
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Landing page
│   │   ├── dashboard/               # Dashboard view
│   │   ├── forecast/                # Forecast view
│   │   └── methodology/             # Citations
│   ├── lib/
│   │   └── api.ts                   # API client
│   └── package.json
└── README.md
```

## API Endpoints

### Hazard Assessment
- `GET /api/v1/hazards?lat={lat}&lon={lon}&name={name}` - Current conditions
- `GET /api/v1/hazards/forecast?lat={lat}&lon={lon}&hours={120}` - Forecast

### Location Management
- `POST /api/v1/locations` - Create location
- `GET /api/v1/locations` - List locations
- `GET /api/v1/locations/search?q={query}` - Geocode search

### Metadata
- `GET /api/v1/methodologies` - Academic methodologies
- `GET /api/v1/methodologies/{hazard_type}` - Specific methodology
- `GET /health` - Health check

## Testing

Run the backend integration test:
```bash
cd backend
uv run test_api.py
```

Test a specific location:
```bash
curl "http://localhost:8000/api/v1/hazards?lat=51.5074&lon=-0.1278&name=London"
```

## Environment Variables

Environment variables in `.env`:

```bash
# Required
OPENWEATHER_API_KEY=your_api_key_here

# Optional
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

Ensure `OPENWEATHER_API_KEY` is set in backend environment variables, and `NEXT_PUBLIC_API_URL` points to the deployed backend URL in frontend environment variables.

## Copyright

Copyright 2025 Ashley Turner. All rights reserved.
