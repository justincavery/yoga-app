#!/bin/bash
# Launch script for Autonomous Coder Agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
AGENT_NAME="AutonomousCoder-1"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POLL_INTERVAL=60
RUN_MODE="continuous"

# Function to print colored output
print_info() {
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

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Launch the Autonomous Coder Agent that follows TDD practices.

OPTIONS:
    -n, --name NAME          Agent name (default: AutonomousCoder-1)
    -p, --project-root PATH  Project root directory (default: auto-detected)
    -i, --interval SECONDS   Poll interval in seconds (default: 60)
    -o, --once               Run once instead of continuously
    -h, --help               Display this help message

EXAMPLES:
    # Start agent with default settings (continuous mode)
    $0

    # Start agent with custom name and 30-second polling
    $0 --name "Agent-Backend-1" --interval 30

    # Run once to claim and process a single work stream
    $0 --once

DESCRIPTION:
    The Autonomous Coder Agent monitors the project roadmap and:
    1. Finds unclaimed or assigned work streams
    2. Claims the work stream and marks as IN PROGRESS
    3. Writes tests first (TDD approach)
    4. Implements code to satisfy tests
    5. Runs tests and fixes bugs
    6. Commits changes with descriptive messages
    7. Writes dev log entry
    8. Updates roadmap to mark COMPLETE

    The agent follows all practices defined in CLAUDE.md including:
    - Using Context7 for library documentation
    - Centralized logging
    - No single-letter variables
    - Comprehensive testing
    - Proper error handling

EOF
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            AGENT_NAME="$2"
            shift 2
            ;;
        -p|--project-root)
            PROJECT_ROOT="$2"
            shift 2
            ;;
        -i|--interval)
            POLL_INTERVAL="$2"
            shift 2
            ;;
        -o|--once)
            RUN_MODE="once"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/plans/roadmap.md" ]; then
    print_error "Roadmap not found at $PROJECT_ROOT/plans/roadmap.md"
    print_info "Please run this script from the yoga-app directory or specify --project-root"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ] && [ ! -d "$PROJECT_ROOT/env" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv "$PROJECT_ROOT/venv"
    print_success "Virtual environment created at $PROJECT_ROOT/venv"
fi

# Activate virtual environment
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/env" ]; then
    source "$PROJECT_ROOT/env/bin/activate"
fi

# Install dependencies if needed
print_info "Checking dependencies..."
pip install -q pytest requests > /dev/null 2>&1 || true

# Create agents directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/agents"

# Display configuration
print_info "Autonomous Coder Agent Configuration:"
echo "  Agent Name:    $AGENT_NAME"
echo "  Project Root:  $PROJECT_ROOT"
echo "  Poll Interval: ${POLL_INTERVAL}s"
echo "  Run Mode:      $RUN_MODE"
echo ""

# Build the command
CMD="python3 $PROJECT_ROOT/agents/autonomous_coder.py"
CMD="$CMD --name \"$AGENT_NAME\""
CMD="$CMD --project-root \"$PROJECT_ROOT\""
CMD="$CMD --poll-interval $POLL_INTERVAL"

if [ "$RUN_MODE" == "once" ]; then
    CMD="$CMD --once"
fi

# Run the agent
print_success "Starting Autonomous Coder Agent..."
print_info "Press Ctrl+C to stop"
echo ""

eval $CMD
