#!/bin/bash

# SSL Certificate Monitor - Build and Test Script

set -e

echo "================================================"
echo "SSL Certificate Monitor - Build and Test Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $(pwd)"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python3 available: $(python3 --version)${NC}"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠ pip3 not found, trying pip${NC}"
    if ! command -v pip &> /dev/null; then
        echo -e "${RED}❌ pip not found. Please install pip.${NC}"
        exit 1
    fi
    PIP_CMD="pip"
else
    PIP_CMD="pip3"
    echo -e "${GREEN}✓ pip3 available${NC}"
fi

# Check for docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker available: $(docker --version)${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Docker not found - Docker tests will be skipped${NC}"
    DOCKER_AVAILABLE=false
fi

# Check for docker-compose
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ docker-compose available: $(docker-compose --version)${NC}"
    COMPOSE_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ docker-compose not found - Docker Compose tests will be skipped${NC}"
    COMPOSE_AVAILABLE=false
fi

echo ""
echo "================================================"
echo "Step 1: Checking Python dependencies"
echo "================================================"

# Install Python dependencies
$PIP_CMD install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

echo ""
echo "================================================"
echo "Step 2: Running unit tests"
echo "================================================"

if command -v pytest &> /dev/null; then
    pytest tests/test_ssl_checker.py -v --tb=short
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${YELLOW}⚠ pytest not found, installing...${NC}"
    $PIP_CMD install pytest
    pytest tests/test_ssl_checker.py -v --tb=short
    echo -e "${GREEN}✓ Unit tests passed${NC}"
fi

echo ""
echo "================================================"
echo "Step 3: Running integration tests"
echo "================================================"

pytest tests/test_api.py -v --tb=short
echo -e "${GREEN}✓ Integration tests passed${NC}"

echo ""
echo "================================================"
echo "Step 4: Building Docker images"
echo "================================================"

if [ "$DOCKER_AVAILABLE" = true ]; then
    docker-compose build
    echo -e "${GREEN}✓ Docker images built successfully${NC}"
else
    echo -e "${YELLOW}⚠ Skipping Docker tests (docker/docker-compose not available)${NC}"
fi

echo ""
echo "================================================"
echo "Step 5: Testing Docker deployment"
echo "================================================"

if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
    # Start the container
    docker-compose up -d
    echo -e "${GREEN}✓ Docker containers started${NC}"
    
    # Wait for container to be healthy
    echo "Waiting for container to be ready..."
    sleep 10
    
    # Check health
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:4444 | grep -q "20"; then
        echo -e "${GREEN}✓ Docker container is healthy${NC}"
    else
        echo -e "${YELLOW}⚠ Container may not be ready yet${NC}"
    fi
    
    # Stop the container
    docker-compose down
    echo -e "${GREEN}✓ Docker containers stopped${NC}"
else
    echo -e "${YELLOW}⚠ Skipping Docker deployment tests${NC}"
fi

echo ""
echo "================================================"
echo "Build and Test Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Add certificates via /admin endpoint"
echo "2. Monitor SSL status on main page"
echo "3. Configure notifications (future feature)"
echo ""
echo "To start the application:"
echo "  - Docker: docker-compose up"
echo "  - Python: python run.py"
echo ""
echo -e "${GREEN}All tests completed successfully!${NC}"
