#!/bin/bash

# Reverse Turing Game Startup Script
# This script sets up and starts the complete game environment

set -e

echo "🎮 REVERSE TURING GAME STARTUP"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available"
}

# Start database services
start_services() {
    print_status "Starting PostgreSQL and Redis..."
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if PostgreSQL is ready
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U user -d reverse_turing &> /dev/null; then
            print_success "PostgreSQL is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "PostgreSQL failed to start"
            exit 1
        fi
        sleep 2
    done
    
    # Check if Redis is ready
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        print_success "Redis is ready"
    else
        print_warning "Redis may not be fully ready"
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cp .env.example .env
        print_warning "Please edit backend/.env with your settings"
    fi
    
    cd ..
    print_success "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm dependencies..."
        npm install
    fi
    
    cd ..
    print_success "Frontend setup complete"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    cd backend
    source venv/bin/activate
    
    python3 -c "
from app import app, db
from database import Player, Room, Prompt
import sys

try:
    with app.app_context():
        db.create_all()
        print('✓ Database tables created')
        
        # Add sample prompts if none exist
        if Prompt.query.count() == 0:
            sample_prompts = [
                Prompt(text='What is your favorite childhood memory?', room_type='personal'),
                Prompt(text='Write a haiku about technology', room_type='poetry'),
                Prompt(text='Should AI have rights? Argue your position.', room_type='debate'),
                Prompt(text='Describe a world where gravity works backwards', room_type='creative'),
            ]
            for prompt in sample_prompts:
                db.session.add(prompt)
            db.session.commit()
            print('✓ Sample prompts added')
        
        print('✓ Database initialization complete')
except Exception as e:
    print(f'✗ Database initialization failed: {e}')
    sys.exit(1)
"
    
    cd ..
}

# Start the application
start_app() {
    print_status "Starting the Reverse Turing Game..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    nohup python3 app.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 5
    
    # Check if backend is running
    if ps -p $BACKEND_PID > /dev/null; then
        print_success "Backend started (PID: $BACKEND_PID)"
    else
        print_error "Backend failed to start. Check backend.log for details."
        exit 1
    fi
    
    # Start frontend
    print_status "Starting frontend server..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend_pid
    echo $FRONTEND_PID > .frontend_pid
    
    print_success "🎉 Reverse Turing Game is starting!"
    echo ""
    echo "📊 Services:"
    echo "  - Backend:  http://localhost:5000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "📝 Logs:"
    echo "  - Backend: backend.log"
    echo "  - Frontend: Check terminal output"
    echo ""
    echo "🛑 To stop the game:"
    echo "  ./stop_game.sh"
    echo ""
    echo "🎮 Game should open in your browser automatically!"
}

# Main execution
main() {
    # Check arguments
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --setup-only   Only setup dependencies, don't start"
        echo "  --no-db-init   Skip database initialization"
        echo ""
        exit 0
    fi
    
    check_docker
    start_services
    setup_backend
    setup_frontend
    
    if [ "$1" != "--no-db-init" ]; then
        init_database
    fi
    
    if [ "$1" != "--setup-only" ]; then
        start_app
    else
        print_success "Setup complete! Run './start_game.sh' to start the game."
    fi
}

# Trap to cleanup on script exit
cleanup() {
    print_status "Cleaning up..."
    if [ -f .backend_pid ]; then
        BACKEND_PID=$(cat .backend_pid)
        if ps -p $BACKEND_PID > /dev/null; then
            kill $BACKEND_PID
        fi
        rm .backend_pid
    fi
    if [ -f .frontend_pid ]; then
        FRONTEND_PID=$(cat .frontend_pid)
        if ps -p $FRONTEND_PID > /dev/null; then
            kill $FRONTEND_PID
        fi
        rm .frontend_pid
    fi
}

trap cleanup EXIT

# Run main function
main "$@"