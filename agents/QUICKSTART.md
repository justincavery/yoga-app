# Quick Start Guide - Autonomous Coder Agent

Get up and running with the Autonomous Coder Agent in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Git configured with user.name and user.email
- Terminal/command line access

## Installation

### 1. Navigate to Project Root

```bash
cd /Users/justinavery/claude/yoga-app
```

### 2. Verify Files

Check that the agent files exist:

```bash
ls -la agents/
# Should see:
# - autonomous_coder.py
# - tdd_executor.py
# - launch_agent.sh
# - README.md
# - QUICKSTART.md
```

### 3. Make Launch Script Executable

```bash
chmod +x agents/launch_agent.sh
```

## Quick Test

Test the agent in "once" mode (process one work stream and exit):

```bash
./agents/launch_agent.sh --once --name "TestAgent"
```

You should see output like:
```
[INFO] Autonomous Coder Agent Configuration:
  Agent Name:    TestAgent
  Project Root:  /Users/justinavery/claude/yoga-app
  Poll Interval: 60s
  Run Mode:      once

[SUCCESS] Starting Autonomous Coder Agent...
```

The agent will:
1. ✅ Load the roadmap from `plans/roadmap.md`
2. ✅ Find the first unclaimed work stream
3. ✅ Claim it by updating the Owner field
4. ⚠️  Attempt TDD workflow (requires Claude Code integration - see below)

## Running in Production

### Continuous Monitoring Mode

Start the agent to continuously monitor and process work streams:

```bash
./agents/launch_agent.sh --name "Agent-Backend-1"
```

The agent will:
- Check roadmap every 60 seconds
- Claim available work streams
- Execute TDD workflow
- Commit and update roadmap
- Repeat indefinitely

Press `Ctrl+C` to stop.

### Custom Polling Interval

Process work faster with shorter polling:

```bash
./agents/launch_agent.sh --name "Agent-Backend-1" --interval 30
```

### Multiple Agents in Parallel

Run multiple agents simultaneously (each in a separate terminal):

```bash
# Terminal 1
./agents/launch_agent.sh --name "Agent-Backend"

# Terminal 2
./agents/launch_agent.sh --name "Agent-Frontend"

# Terminal 3
./agents/launch_agent.sh --name "Agent-DevOps"
```

Each agent will claim different work streams.

## What Works Now

✅ **Roadmap Management**
- Parses roadmap.md
- Finds unclaimed work streams
- Claims work by updating owner
- Marks work complete when done

✅ **TDD Workflow Structure**
- Analyzes task requirements
- Generates test plans
- Defines implementation phases
- Tracks modified files

✅ **Git Integration**
- Commits specific files
- Uses descriptive commit messages
- Follows git best practices

✅ **Dev Log**
- Writes entries to /devlog
- Timestamps all work
- Documents completion

✅ **Logging**
- Comprehensive logging to file and console
- Color-coded output
- Error tracking

## What Needs Integration

⚠️ **Claude Code Integration** (In Progress)

The TDD executor generates prompts but needs integration with Claude Code to actually:
- Write test code
- Implement features
- Fix bugs
- Refactor code

### Integration Options

#### Option 1: Claude Code API (Recommended)
Integrate with Claude Code's API to invoke Claude programmatically:

```python
# In tdd_executor.py
response = claude_code.execute(prompt, context_files)
```

#### Option 2: CLI Invocation
Call Claude Code CLI from Python:

```python
result = subprocess.run(
    ['claude-code', 'execute', '--prompt', prompt],
    capture_output=True
)
```

#### Option 3: MCP Server
Use the Model Context Protocol to connect:

```python
from mcp import MCPClient
client = MCPClient()
response = client.invoke('claude-code', prompt)
```

## Current Status

The autonomous coder agent is **80% complete**:

| Component | Status | Notes |
|-----------|--------|-------|
| Roadmap Parser | ✅ Done | Fully functional |
| Work Stream Claiming | ✅ Done | Updates roadmap correctly |
| TDD Workflow Structure | ✅ Done | Phases defined |
| Test Plan Generation | ✅ Done | Creates comprehensive plans |
| Git Integration | ✅ Done | Commits and messages work |
| Dev Log Writing | ✅ Done | Documents all work |
| Test Execution | ✅ Done | Runs pytest |
| **Claude Code Integration** | ⚠️ Pending | Needs API/CLI integration |
| **Code Generation** | ⚠️ Pending | Depends on Claude integration |

## Next Steps to Complete

1. **Integrate Claude Code API**
   - Research Claude Code's API/SDK
   - Implement `ClaudeCodeInterface` class
   - Add authentication/configuration

2. **Test with Real Work Stream**
   - Start with small task
   - Verify tests are written correctly
   - Verify code implementation works
   - Validate commit and dev log

3. **Add Error Recovery**
   - Handle API failures gracefully
   - Retry logic for transient errors
   - Fallback to manual intervention

4. **Monitoring Dashboard**
   - Web UI to monitor agents
   - Show claimed work streams
   - Display logs in real-time

## Troubleshooting

### "Roadmap not found"
- Ensure you're in the project root: `/Users/justinavery/claude/yoga-app`
- Check that `plans/roadmap.md` exists

### "No work streams found"
- Verify roadmap has work streams in box format
- Check that owners are generic roles (Backend Dev 1, etc.)

### "TDD workflow execution failed"
- Expected until Claude Code integration is complete
- Agent will still claim work and generate test plans

### "Import error: tdd_executor"
- Ensure both files are in `agents/` directory
- Check Python path includes agents directory

## Configuration

### Environment Variables

You can set these environment variables:

```bash
export AUTONOMOUS_CODER_NAME="MyAgent"
export AUTONOMOUS_CODER_INTERVAL=30
export CLAUDE_CODE_API_KEY="your-key"
```

### Config File (Future)

Create `agents/config.json`:

```json
{
  "agent_name": "Agent-Backend-1",
  "poll_interval": 60,
  "max_retries": 3,
  "log_level": "INFO",
  "claude_code": {
    "api_key": "...",
    "model": "claude-sonnet-4-5",
    "max_tokens": 4096
  }
}
```

## Logs

Agent logs are written to:
- **File**: `agents/autonomous_coder.log`
- **Console**: Real-time colored output

To tail the log:

```bash
tail -f agents/autonomous_coder.log
```

To search logs:

```bash
grep "ERROR" agents/autonomous_coder.log
```

## Getting Help

1. Check the full README: `agents/README.md`
2. Review the logs: `agents/autonomous_coder.log`
3. Test in `--once` mode first
4. Check the roadmap format matches expected structure

## Example Session

Here's what a successful run looks like:

```
$ ./agents/launch_agent.sh --once

[INFO] Checking dependencies...
[INFO] Autonomous Coder Agent Configuration:
  Agent Name:    AutonomousCoder-1
  Project Root:  /Users/justinavery/claude/yoga-app
  Poll Interval: 60s
  Run Mode:      once

[SUCCESS] Starting Autonomous Coder Agent...

2025-12-05 22:17:22 - INFO - Loaded roadmap from plans/roadmap.md
2025-12-05 22:17:22 - INFO - Initialized AutonomousCoder: AutonomousCoder-1
2025-12-05 22:17:22 - INFO - Looking for work to claim...
2025-12-05 22:17:22 - INFO - Found 89 work streams in roadmap
2025-12-05 22:17:22 - INFO - Found work stream: User Registration & Login API
2025-12-05 22:17:22 - INFO - Claimed work stream: User Registration & Login API
2025-12-05 22:17:22 - INFO - Starting TDD workflow for: User Registration & Login API
2025-12-05 22:17:22 - INFO - === TDD Phase 1: Write Tests (Red) ===
2025-12-05 22:17:22 - WARNING - Test writing requires Claude Code integration
```

## Contributing

To improve the agent:

1. Fork or branch
2. Make changes to `autonomous_coder.py` or `tdd_executor.py`
3. Test with `--once` mode
4. Update documentation
5. Submit pull request

## License

Part of the YogaFlow project.
