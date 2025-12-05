# Autonomous Coder Agent System

An autonomous agent system that follows Test-Driven Development (TDD) practices to implement features from the project roadmap.

## Overview

The Autonomous Coder Agent is designed to:

1. **Monitor the Roadmap** - Continuously check `/plans/roadmap.md` for work streams
2. **Claim Work** - Identify and claim unclaimed work streams by updating the owner
3. **Follow TDD** - Write tests first, then implement code to satisfy them
4. **Ensure Quality** - Run all tests before committing, fix any bugs
5. **Document Progress** - Write dev log entries and update the roadmap
6. **Commit Changes** - Only commit files that were actually modified

## Architecture

```
agents/
├── autonomous_coder.py    # Main agent orchestration
├── tdd_executor.py        # TDD workflow implementation
├── launch_agent.sh        # Launcher script
└── README.md             # This file
```

### Components

#### 1. `autonomous_coder.py`
The main agent that orchestrates the workflow:
- `RoadmapParser` - Reads and updates roadmap.md
- `TestRunner` - Executes pytest test suites
- `GitManager` - Handles git operations (add, commit)
- `DevLogWriter` - Creates dev log entries
- `AutonomousCoder` - Main agent class that ties it all together

#### 2. `tdd_executor.py`
Implements the TDD workflow:
- `TDDExecutor` - Executes the Red-Green-Refactor cycle
- `ClaudeCodeInterface` - Interfaces with Claude Code for AI-powered development

#### 3. `launch_agent.sh`
Bash launcher script with:
- Command-line argument parsing
- Virtual environment management
- Dependency installation
- Colored output for better UX

## Usage

### Basic Usage

Start the agent in continuous monitoring mode:

```bash
./agents/launch_agent.sh
```

This will:
- Monitor the roadmap every 60 seconds
- Claim the next available work stream
- Execute the TDD workflow
- Commit and update the roadmap
- Loop back to find more work

### Custom Configuration

```bash
# Custom agent name
./agents/launch_agent.sh --name "Agent-Backend-1"

# Faster polling (30 seconds)
./agents/launch_agent.sh --interval 30

# Run once and exit
./agents/launch_agent.sh --once

# Combine options
./agents/launch_agent.sh --name "Agent-Frontend" --interval 45 --once
```

### Available Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--name` | `-n` | Agent name for claiming work | `AutonomousCoder-1` |
| `--project-root` | `-p` | Project root directory | Auto-detected |
| `--interval` | `-i` | Poll interval in seconds | `60` |
| `--once` | `-o` | Run once instead of continuous | Continuous mode |
| `--help` | `-h` | Display help message | - |

## TDD Workflow

The agent follows a strict Test-Driven Development approach:

### Phase 1: RED (Write Tests First)
1. Analyze work stream requirements
2. Generate comprehensive test plan
3. Write tests covering:
   - Happy path scenarios
   - Edge cases
   - Error conditions
   - Input validation
4. Verify tests fail initially (expected in TDD)

### Phase 2: GREEN (Implement Code)
1. Read and understand each test
2. Implement minimum code to pass tests
3. Follow project coding standards
4. Add error handling and docstrings
5. Run tests frequently during implementation

### Phase 3: REFACTOR (Improve Code)
1. Analyze code for refactoring opportunities
2. Simplify complex logic
3. Improve naming and structure
4. Ensure all tests still pass

### Phase 4: VERIFY & COMMIT
1. Run full test suite
2. Fix any failing tests or bugs
3. Ensure 80%+ code coverage
4. Commit only modified files
5. Write descriptive commit message

### Phase 5: FINALIZE
1. Write dev log entry
2. Update roadmap to mark COMPLETE
3. Return to monitoring for next work stream

## Roadmap Format

The agent expects work streams in this format:

```
┌─────────────────────────────────────────────────────────┐
│ Task: User Registration & Login API                     │
│ Owner: Backend Dev 1                                    │
│ Effort: M (1.5 weeks)                                   │
│ Output: POST /register, /login, /logout endpoints       │
└─────────────────────────────────────────────────────────┘
```

### Work Stream States

- **Unclaimed** - Owner is a generic role (e.g., "Backend Dev 1")
- **Claimed** - Owner is set to agent name with `[IN PROGRESS]`
- **Complete** - Owner has `[COMPLETE ✅]` marker

Example progression:
```
Owner: Backend Dev 1                    # Unclaimed
Owner: AutonomousCoder-1 [IN PROGRESS] # Claimed
Owner: AutonomousCoder-1 [COMPLETE ✅] # Complete
```

## Project Integration

### Following CLAUDE.md Guidelines

The agent follows all practices defined in `/CLAUDE.md`:

- ✅ Checks Context7 for library documentation before using SDKs
- ✅ Uses Python as primary language
- ✅ Never uses single-letter variable names
- ✅ Implements centralized logging for each component
- ✅ Creates plans in `/plans` directory
- ✅ Writes dev log entries in `/devlog`
- ✅ Uses virtual environments (`./venv` or `./env`)
- ✅ Prioritizes integration tests over mocked unit tests
- ✅ Never comments out existing features
- ✅ Uses feature flags for temporary disabling

### File Organization

```
yoga-app/
├── plans/
│   ├── roadmap.md              # Work stream tracking
│   ├── requirements.md         # Project requirements
│   └── plan.md                 # Execution plan
├── devlog/
│   ├── user-registration.md    # Dev log entries
│   ├── pose-library.md
│   └── ...
├── agents/
│   ├── autonomous_coder.py
│   ├── tdd_executor.py
│   ├── launch_agent.sh
│   ├── autonomous_coder.log    # Agent logs
│   └── README.md
└── tests/
    ├── test_api.py             # Tests written by agent
    └── ...
```

## Logging

The agent creates detailed logs at:
- **File**: `agents/autonomous_coder.log`
- **Console**: Real-time output with color coding

Log levels:
- `INFO` - Normal operation, progress updates
- `WARNING` - Non-critical issues, skipped operations
- `ERROR` - Failures, exceptions

## Error Handling

The agent handles errors gracefully:

1. **Test Failures** - Does not commit, logs error details
2. **Git Conflicts** - Logs error, waits for manual resolution
3. **Missing Dependencies** - Attempts auto-install, logs if fails
4. **Roadmap Parse Errors** - Logs error, continues monitoring
5. **TDD Execution Errors** - Logs error, marks work stream for review

## Requirements

- Python 3.8+
- pytest
- Git
- Virtual environment (auto-created if missing)

## Examples

### Example 1: Start Multiple Agents

Run multiple agents in parallel for different work streams:

```bash
# Terminal 1 - Backend agent
./agents/launch_agent.sh --name "Agent-Backend"

# Terminal 2 - Frontend agent
./agents/launch_agent.sh --name "Agent-Frontend"

# Terminal 3 - DevOps agent
./agents/launch_agent.sh --name "Agent-DevOps"
```

Each agent will claim work from their respective swim lanes.

### Example 2: One-Time Execution

Process a single work stream and exit:

```bash
./agents/launch_agent.sh --once
```

Useful for:
- Testing the agent
- Processing a specific work stream
- CI/CD integration

### Example 3: Fast Iteration

For rapid development, use shorter polling:

```bash
./agents/launch_agent.sh --interval 10
```

Checks for new work every 10 seconds.

## Development Log Format

The agent writes dev log entries in this format:

```markdown
## 2025-12-05 22:30:00

### Completed: User Registration & Login API

**Effort:** M (1.5 weeks)
**Output:** POST /register, /login, /logout endpoints

**Implementation Notes:**
- Followed TDD approach
- All tests passing
- Code committed to repository

**Agent:** AutonomousCoder-1

---
```

## Troubleshooting

### Agent Not Finding Work
- Check that roadmap.md exists at `/plans/roadmap.md`
- Verify work streams have unclaimed owners
- Check agent logs for parse errors

### Tests Not Running
- Ensure pytest is installed: `pip install pytest`
- Check that tests are in `tests/` directory
- Verify virtual environment is activated

### Git Commit Failures
- Check git configuration (user.name, user.email)
- Ensure no merge conflicts exist
- Verify file permissions

### TDD Executor Fails
- Check that tdd_executor.py is in agents/ directory
- Verify all dependencies are installed
- Check agent logs for detailed error messages

## Future Enhancements

Planned improvements:
- [ ] Claude Code API integration for AI-powered TDD
- [ ] Multi-repository support
- [ ] Parallel work stream execution
- [ ] Web dashboard for monitoring agents
- [ ] Slack/Discord notifications
- [ ] Automatic dependency detection and installation
- [ ] Code review before commit
- [ ] Performance benchmarking

## Contributing

To extend the agent:

1. Add new capabilities to `autonomous_coder.py`
2. Implement TDD workflow extensions in `tdd_executor.py`
3. Update this README with new features
4. Test with `--once` mode first
5. Update `/plans/plan.md` with changes

## License

Part of the YogaFlow project.
