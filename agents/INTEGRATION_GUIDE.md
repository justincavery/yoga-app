# Claude Code Integration Guide

This guide explains how to complete the integration between the Autonomous Coder Agent and Claude Code to enable full autonomous TDD workflow.

## Overview

The Autonomous Coder Agent is designed to work with Claude Code to:
1. Generate test code based on requirements
2. Implement features to satisfy tests
3. Fix bugs and refactor code
4. Follow TDD red-green-refactor cycle

Currently, the agent generates detailed prompts but needs a bridge to execute them via Claude Code.

## Architecture

```
┌─────────────────────────┐
│  Autonomous Coder Agent │
│  (Python orchestration) │
└───────────┬─────────────┘
            │
            │ Generates prompts
            ▼
┌─────────────────────────┐
│  TDD Executor           │
│  (Workflow management)  │
└───────────┬─────────────┘
            │
            │ Needs integration
            ▼
┌─────────────────────────┐
│  Claude Code Interface  │ ◄── TO BE IMPLEMENTED
│  (API/CLI bridge)       │
└───────────┬─────────────┘
            │
            │ Invokes
            ▼
┌─────────────────────────┐
│  Claude Code            │
│  (AI code generation)   │
└─────────────────────────┘
```

## Integration Options

### Option 1: Claude Code Task Tool (Recommended)

Use Claude Code's Task tool to spawn agents that execute the TDD workflow.

**Implementation:**

```python
# In tdd_executor.py

import subprocess
import json

class ClaudeCodeInterface:
    """Interface to Claude Code using Task tool."""

    @staticmethod
    def execute_tdd_task(prompt: str, context_files: List[str]) -> Dict:
        """
        Execute a TDD task using Claude Code.

        Args:
            prompt: The detailed prompt for Claude
            context_files: List of files to provide as context

        Returns:
            Dict with:
              - success: bool
              - files_modified: List[str]
              - output: str
        """
        # Prepare the task description
        task_json = {
            "subagent_type": "general-purpose",
            "prompt": prompt,
            "description": "TDD workflow execution"
        }

        # Write task to temp file
        task_file = '/tmp/claude_task.json'
        with open(task_file, 'w') as f:
            json.dump(task_json, f)

        # Invoke Claude Code (adjust based on actual API)
        result = subprocess.run(
            ['claude-code', 'task', '--file', task_file],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return {
                'success': True,
                'files_modified': parse_modified_files(result.stdout),
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'files_modified': [],
                'output': result.stderr
            }
```

**Usage in TDD Executor:**

```python
def write_tests(self) -> Tuple[bool, List[str]]:
    """Write tests using Claude Code."""
    prompt = self.generate_test_prompt()

    result = ClaudeCodeInterface.execute_tdd_task(
        prompt=prompt,
        context_files=self.get_relevant_files()
    )

    if result['success']:
        return True, result['files_modified']
    else:
        logger.error(f"Failed to write tests: {result['output']}")
        return False, []
```

### Option 2: MCP (Model Context Protocol)

Use the MCP server integration to communicate with Claude Code.

**Implementation:**

```python
# In tdd_executor.py

from mcp_client import MCPClient

class ClaudeCodeInterface:
    """Interface to Claude Code via MCP."""

    def __init__(self):
        self.client = MCPClient()
        self.client.register_handle("autonomous-coder-agent")

    def execute_prompt(self, prompt: str, context_files: List[str]) -> str:
        """Execute a prompt via MCP."""
        # Read context files
        context = ""
        for file_path in context_files:
            with open(file_path, 'r') as f:
                context += f"\n\n# File: {file_path}\n{f.read()}"

        # Combine prompt and context
        full_prompt = f"{context}\n\n{prompt}"

        # Send to Claude via MCP
        response = self.client.chat(
            prompt=full_prompt,
            channel="parallel-work",
            continuation_id=self.continuation_id
        )

        return response
```

### Option 3: Direct API Integration

Use Claude's API directly (requires API key).

**Implementation:**

```python
# In tdd_executor.py

import anthropic

class ClaudeCodeInterface:
    """Interface to Claude API directly."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def execute_prompt(self, prompt: str, context_files: List[str]) -> str:
        """Execute a prompt via Claude API."""
        # Read context files
        context = self._read_context_files(context_files)

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"{context}\n\n{prompt}"
            }]
        )

        return message.content[0].text

    def _read_context_files(self, files: List[str]) -> str:
        """Read and format context files."""
        context = ""
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    context += f"\n\n# File: {file_path}\n```\n{f.read()}\n```"
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        return context
```

### Option 4: Subprocess Invocation

Invoke Claude Code CLI directly from Python.

**Implementation:**

```python
# In tdd_executor.py

import subprocess
import tempfile

class ClaudeCodeInterface:
    """Interface to Claude Code CLI."""

    @staticmethod
    def execute_prompt(prompt: str, context_files: List[str]) -> str:
        """Execute a prompt via Claude Code CLI."""
        # Write prompt to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name

        try:
            # Build command with context files
            cmd = ['claude-code', '--prompt-file', prompt_file]
            for file_path in context_files:
                cmd.extend(['--context', file_path])

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            return result.stdout

        finally:
            # Clean up temp file
            os.unlink(prompt_file)
```

## Recommended Approach

**Use Option 1: Claude Code Task Tool**

This is the recommended approach because:
- ✅ Native integration with Claude Code
- ✅ Supports specialized agents (general-purpose, Explore, etc.)
- ✅ Handles file operations automatically
- ✅ Manages context and conversation history
- ✅ Built-in error handling
- ✅ Parallel execution support

## Implementation Steps

### Step 1: Research Claude Code API

Determine how to invoke Claude Code programmatically:

```bash
# Check if Claude Code has a CLI
claude-code --help

# Look for API documentation
ls -la ~/.claude-code/
```

### Step 2: Implement ClaudeCodeInterface

Update `tdd_executor.py`:

```python
class ClaudeCodeInterface:
    """Interface to Claude Code."""

    @staticmethod
    def execute_prompt(prompt: str, context_files: List[str] = None) -> Dict:
        """
        Execute a prompt using Claude Code.

        Args:
            prompt: The prompt to send to Claude
            context_files: List of files to include as context

        Returns:
            {
                'success': bool,
                'response': str,
                'files_modified': List[str],
                'error': str or None
            }
        """
        # IMPLEMENTATION GOES HERE
        # Choose one of the options above

        raise NotImplementedError("Claude Code integration pending")
```

### Step 3: Update TDD Executor

Modify `write_tests()` and `implement_code()` methods:

```python
def write_tests(self) -> Tuple[bool, List[str]]:
    """Write tests using Claude Code."""
    requirements = self.analyze_requirements()
    test_plan = self.generate_test_plan()

    prompt = f"{requirements}\n\n{test_plan}\n\nWrite comprehensive tests following TDD."

    # Get relevant context files
    context_files = self._identify_context_files()

    # Execute via Claude Code
    result = ClaudeCodeInterface.execute_prompt(prompt, context_files)

    if result['success']:
        logger.info(f"Tests written successfully: {result['files_modified']}")
        return True, result['files_modified']
    else:
        logger.error(f"Failed to write tests: {result['error']}")
        return False, []

def implement_code(self, test_files: List[str]) -> Tuple[bool, List[str]]:
    """Implement code using Claude Code."""
    prompt = f"""
    Tests have been written: {', '.join(test_files)}

    Now implement the code to make these tests pass.
    Follow TDD green phase principles.
    """

    context_files = test_files + self._identify_implementation_files()

    result = ClaudeCodeInterface.execute_prompt(prompt, context_files)

    if result['success']:
        logger.info(f"Code implemented: {result['files_modified']}")
        return True, result['files_modified']
    else:
        logger.error(f"Failed to implement code: {result['error']}")
        return False, []
```

### Step 4: Test Integration

Test with a simple work stream:

```bash
# Create a test work stream in roadmap
# Then run the agent
./agents/launch_agent.sh --once --name "IntegrationTest"
```

Verify:
- [ ] Tests are written to files
- [ ] Tests fail initially (red phase)
- [ ] Code is implemented
- [ ] Tests pass (green phase)
- [ ] Files are committed
- [ ] Dev log is written
- [ ] Roadmap is updated

### Step 5: Add Error Handling

Handle edge cases:

```python
class ClaudeCodeInterface:
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds

    @staticmethod
    def execute_prompt_with_retry(prompt: str, context_files: List[str] = None) -> Dict:
        """Execute prompt with retry logic."""
        for attempt in range(ClaudeCodeInterface.MAX_RETRIES):
            try:
                result = ClaudeCodeInterface.execute_prompt(prompt, context_files)
                if result['success']:
                    return result

                logger.warning(f"Attempt {attempt + 1} failed: {result['error']}")
                time.sleep(ClaudeCodeInterface.RETRY_DELAY)

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} exception: {e}")
                time.sleep(ClaudeCodeInterface.RETRY_DELAY)

        return {
            'success': False,
            'response': '',
            'files_modified': [],
            'error': f'Failed after {ClaudeCodeInterface.MAX_RETRIES} attempts'
        }
```

## Configuration

Create `agents/config.json`:

```json
{
  "claude_code": {
    "mode": "task_tool",
    "api_key": "${CLAUDE_API_KEY}",
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 300,
    "retry_attempts": 3,
    "retry_delay": 5
  },
  "tdd": {
    "test_framework": "pytest",
    "coverage_threshold": 80,
    "test_directory": "tests",
    "verify_tests_fail_first": true
  }
}
```

Load configuration:

```python
import json

class Config:
    """Configuration loader."""

    @staticmethod
    def load():
        config_path = Path(__file__).parent / 'config.json'
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}

# In TDD executor
config = Config.load()
claude_config = config.get('claude_code', {})
```

## Testing the Integration

### Unit Test for ClaudeCodeInterface

Create `tests/test_claude_interface.py`:

```python
import pytest
from agents.tdd_executor import ClaudeCodeInterface

def test_execute_simple_prompt():
    """Test basic prompt execution."""
    prompt = "Write a simple function that adds two numbers"
    result = ClaudeCodeInterface.execute_prompt(prompt)

    assert result['success'] is True
    assert len(result['files_modified']) > 0

def test_execute_with_context():
    """Test prompt with context files."""
    prompt = "Add a test for this function"
    context = ['src/calculator.py']

    result = ClaudeCodeInterface.execute_prompt(prompt, context)

    assert result['success'] is True

def test_error_handling():
    """Test error handling."""
    prompt = ""  # Empty prompt should fail
    result = ClaudeCodeInterface.execute_prompt(prompt)

    assert result['success'] is False
    assert result['error'] is not None
```

### Integration Test

Create `tests/test_integration.py`:

```python
import pytest
from agents.autonomous_coder import AutonomousCoder

@pytest.fixture
def agent():
    return AutonomousCoder("TestAgent", ".")

def test_full_tdd_cycle(agent):
    """Test complete TDD workflow."""
    # Setup a simple work stream
    work_stream = {
        'task': 'Simple Calculator',
        'owner': 'TestAgent',
        'effort': 'XS (2 days)',
        'output': 'Add, subtract, multiply, divide functions'
    }

    agent.current_work_stream = work_stream

    # Execute TDD workflow
    success, files = agent.execute_tdd_workflow()

    assert success is True
    assert len(files) > 0

    # Verify tests were created
    test_files = [f for f in files if f.startswith('tests/')]
    assert len(test_files) > 0

    # Verify implementation was created
    impl_files = [f for f in files if f.startswith('src/')]
    assert len(impl_files) > 0
```

## Debugging

Enable debug logging:

```python
# In autonomous_coder.py
logging.basicConfig(level=logging.DEBUG)
```

Log Claude Code requests and responses:

```python
class ClaudeCodeInterface:
    @staticmethod
    def execute_prompt(prompt: str, context_files: List[str] = None) -> Dict:
        logger.debug(f"Executing prompt: {prompt[:100]}...")
        logger.debug(f"Context files: {context_files}")

        result = # ... execute prompt

        logger.debug(f"Result: {result}")
        return result
```

## Performance Optimization

### Caching

Cache Claude Code responses for identical prompts:

```python
import hashlib
import json

class ClaudeCodeCache:
    """Cache Claude Code responses."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_key(self, prompt: str, context_files: List[str]) -> str:
        """Generate cache key."""
        data = json.dumps({
            'prompt': prompt,
            'context_files': sorted(context_files or [])
        })
        return hashlib.sha256(data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Dict]:
        """Get cached response."""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def set(self, key: str, value: Dict):
        """Cache response."""
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump(value, f)
```

### Parallel Execution

Process multiple work streams in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

class AutonomousCoder:
    def run_parallel(self, max_workers: int = 3):
        """Run multiple work streams in parallel."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            # Find multiple work streams
            for i in range(max_workers):
                if self.find_and_claim_work():
                    future = executor.submit(self.execute_tdd_workflow)
                    futures.append(future)

            # Wait for completion
            for future in futures:
                success, files = future.result()
                if success:
                    self.verify_and_commit(files)
                    self.finalize_work_stream()
```

## Next Steps

1. **Choose Integration Method** - Select Option 1, 2, 3, or 4
2. **Implement ClaudeCodeInterface** - Write the actual integration code
3. **Test with Simple Work Stream** - Verify end-to-end functionality
4. **Add Error Handling** - Handle edge cases and failures
5. **Optimize Performance** - Add caching and parallel execution
6. **Deploy in Production** - Run continuously on real roadmap

## Support

For questions or issues:
1. Check the agent logs: `agents/autonomous_coder.log`
2. Test with `--once` mode first
3. Verify Claude Code is accessible
4. Check configuration in `agents/config.json`

## Resources

- Claude API Documentation: https://docs.anthropic.com/
- Claude Code Documentation: Check `/help` in Claude Code
- MCP Protocol: https://modelcontextprotocol.io/
- Project Requirements: `plans/requirements.md`
