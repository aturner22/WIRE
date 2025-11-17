#!/bin/bash

# SafetyWatch Deployment Verification Script
# Run this after deploying to verify everything works

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if URLs are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${YELLOW}Usage: ./verify-deployment.sh <frontend-url> <backend-url>${NC}"
    echo "Example: ./verify-deployment.sh https://safetywatch.vercel.app https://safetywatch-backend.up.railway.app"
    exit 1
fi

FRONTEND_URL=$1
BACKEND_URL=$2

echo "======================================"
echo "SafetyWatch Deployment Verification"
echo "======================================"
echo ""
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo ""

# Test 1: Backend Health Check
echo -e "${YELLOW}[1/8] Testing backend health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed (HTTP $HEALTH_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Backend health check failed (HTTP $HEALTH_RESPONSE)${NC}"
fi
echo ""

# Test 2: Backend API - Hazards Endpoint
echo -e "${YELLOW}[2/8] Testing hazards API endpoint...${NC}"
HAZARDS_RESPONSE=$(curl -s "$BACKEND_URL/api/v1/hazards?lat=51.5&lon=-0.1&name=London")
if echo "$HAZARDS_RESPONSE" | grep -q "heat_stress"; then
    echo -e "${GREEN}✓ Hazards API working (returned hazard data)${NC}"
else
    echo -e "${RED}✗ Hazards API failed${NC}"
    echo "Response: $HAZARDS_RESPONSE"
fi
echo ""

# Test 3: Backend API - Types Endpoint
echo -e "${YELLOW}[3/8] Testing types endpoint...${NC}"
TYPES_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/types")
if [ "$TYPES_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Types endpoint working (HTTP $TYPES_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Types endpoint failed (HTTP $TYPES_RESPONSE)${NC}"
fi
echo ""

# Test 4: Backend API - Methodologies Endpoint
echo -e "${YELLOW}[4/8] Testing methodologies endpoint...${NC}"
METHOD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/methodologies")
if [ "$METHOD_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Methodologies endpoint working (HTTP $METHOD_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Methodologies endpoint failed (HTTP $METHOD_RESPONSE)${NC}"
fi
echo ""

# Test 5: API Documentation
echo -e "${YELLOW}[5/8] Testing API documentation...${NC}"
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/docs")
if [ "$DOCS_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ API documentation accessible (HTTP $DOCS_RESPONSE)${NC}"
else
    echo -e "${RED}✗ API documentation failed (HTTP $DOCS_RESPONSE)${NC}"
fi
echo ""

# Test 6: Frontend Landing Page
echo -e "${YELLOW}[6/8] Testing frontend landing page...${NC}"
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Frontend accessible (HTTP $FRONTEND_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Frontend failed (HTTP $FRONTEND_RESPONSE)${NC}"
fi
echo ""

# Test 7: Frontend Dashboard Page
echo -e "${YELLOW}[7/8] Testing frontend dashboard page...${NC}"
DASHBOARD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/dashboard")
if [ "$DASHBOARD_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Dashboard page accessible (HTTP $DASHBOARD_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Dashboard page failed (HTTP $DASHBOARD_RESPONSE)${NC}"
fi
echo ""

# Test 8: Frontend Methodology Page
echo -e "${YELLOW}[8/8] Testing frontend methodology page...${NC}"
METHODOLOGY_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/methodology")
if [ "$METHODOLOGY_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Methodology page accessible (HTTP $METHODOLOGY_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Methodology page failed (HTTP $METHODOLOGY_RESPONSE)${NC}"
fi
echo ""

# Summary
echo "======================================"
echo "Verification Summary"
echo "======================================"
echo ""
echo "URLs to submit:"
echo "  Live Demo: $FRONTEND_URL"
echo "  API Docs: $BACKEND_URL/api/docs"
echo "  Health Check: $BACKEND_URL/health"
echo ""
echo -e "${GREEN}Manual Testing Checklist:${NC}"
echo "1. Visit $FRONTEND_URL and verify landing page"
echo "2. Go to Dashboard and search for 'London'"
echo "3. Verify all 8 hazards display"
echo "4. Check Forecast page (24h, 48h, 5-day)"
echo "5. Check Methodology page (all citations load)"
echo "6. Open browser console - check for errors (F12)"
echo "7. Test on mobile device"
echo "8. Test in different browsers (Chrome, Firefox, Safari)"
echo ""
echo -e "${YELLOW}Remember to update README.md with your live URLs!${NC}"
echo ""
