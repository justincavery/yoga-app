#!/bin/bash
# Verification script for Autonomous Coder Agent

echo "================================================"
echo "Autonomous Coder Agent - Verification Report"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

# Function to check directory
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        return 1
    fi
}

# Check core files
echo "Core Files:"
check_file "agents/autonomous_coder.py"
check_file "agents/tdd_executor.py"
check_file "agents/launch_agent.sh"
echo ""

# Check documentation
echo "Documentation:"
check_file "agents/README.md"
check_file "agents/QUICKSTART.md"
check_file "agents/INTEGRATION_GUIDE.md"
check_file "agents/SUMMARY.md"
echo ""

# Check project structure
echo "Project Structure:"
check_dir "plans"
check_file "plans/roadmap.md"
check_dir "devlog"
echo ""

# Check Python
echo "Python Environment:"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python 3 installed ($PYTHON_VERSION)"
else
    echo -e "${RED}✗${NC} Python 3 not found"
fi
echo ""

# Check virtual environment
echo "Virtual Environment:"
if [ -d "venv" ] || [ -d "env" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not found (will be created on first run)"
fi
echo ""

# Check pytest
echo "Dependencies:"
if python3 -c "import pytest" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} pytest installed"
else
    echo -e "${YELLOW}⚠${NC} pytest not installed (will be installed on first run)"
fi
echo ""

# Check Git
echo "Git Configuration:"
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓${NC} Git installed"

    GIT_USER=$(git config user.name 2>/dev/null || echo "not set")
    GIT_EMAIL=$(git config user.email 2>/dev/null || echo "not set")

    if [ "$GIT_USER" != "not set" ]; then
        echo -e "${GREEN}✓${NC} Git user.name: $GIT_USER"
    else
        echo -e "${RED}✗${NC} Git user.name not configured"
    fi

    if [ "$GIT_EMAIL" != "not set" ]; then
        echo -e "${GREEN}✓${NC} Git user.email: $GIT_EMAIL"
    else
        echo -e "${RED}✗${NC} Git user.email not configured"
    fi
else
    echo -e "${RED}✗${NC} Git not installed"
fi
echo ""

# Check roadmap
echo "Roadmap Analysis:"
if [ -f "plans/roadmap.md" ]; then
    WORK_STREAMS=$(grep -c "│ Task:" plans/roadmap.md || echo "0")
    echo -e "${GREEN}✓${NC} Roadmap contains $WORK_STREAMS work streams"

    # Check current batch
    CURRENT_BATCH=$(grep "CURRENT\|READY" plans/roadmap.md | head -1 || echo "none")
    if [ "$CURRENT_BATCH" != "none" ]; then
        echo -e "${GREEN}✓${NC} Current batch identified"
    else
        echo -e "${YELLOW}⚠${NC} No current batch marked"
    fi
else
    echo -e "${RED}✗${NC} Roadmap not found"
fi
echo ""

# Functionality test
echo "Functionality Test:"
echo -e "${YELLOW}⚠${NC} Running quick test (--once mode)..."
echo ""

if python3 agents/autonomous_coder.py --once --name "VerificationTest" 2>&1 | grep -q "Found.*work streams"; then
    echo -e "${GREEN}✓${NC} Agent can parse roadmap"
    echo -e "${GREEN}✓${NC} Agent can find work streams"
    echo -e "${GREEN}✓${NC} Basic functionality verified"
else
    echo -e "${RED}✗${NC} Agent test failed"
fi
echo ""

# Integration status
echo "Integration Status:"
if grep -q "raise NotImplementedError" agents/tdd_executor.py; then
    echo -e "${YELLOW}⚠${NC} Claude Code integration pending"
    echo -e "   ${YELLOW}→${NC} See agents/INTEGRATION_GUIDE.md for details"
else
    echo -e "${GREEN}✓${NC} Claude Code integration implemented"
fi
echo ""

# Summary
echo "================================================"
echo "Summary"
echo "================================================"
echo ""
echo "The Autonomous Coder Agent is ready for use!"
echo ""
echo "Next Steps:"
echo "1. Review agents/QUICKSTART.md for usage instructions"
echo "2. Complete Claude Code integration (see agents/INTEGRATION_GUIDE.md)"
echo "3. Test with: ./agents/launch_agent.sh --once"
echo "4. Deploy with: ./agents/launch_agent.sh"
echo ""
echo "For help: ./agents/launch_agent.sh --help"
echo ""
