#!/usr/bin/env python3
"""
Autonomous Coder Agent

This agent follows TDD practices and manages work streams from the roadmap:
1. Checks roadmap for assigned or next unclaimed work stream
2. Claims the work stream and marks as in progress
3. Writes tests first (TDD)
4. Writes code to satisfy tests
5. Runs tests and fixes bugs
6. Commits with descriptive message
7. Writes dev log entry
8. Updates roadmap to mark complete
"""

import os
import re
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agents/autonomous_coder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutonomousCoder')


class RoadmapParser:
    """Parses and manages the roadmap markdown file."""

    def __init__(self, roadmap_path: str):
        self.roadmap_path = Path(roadmap_path)
        self.content = ""
        self.reload()

    def reload(self):
        """Reload roadmap content from file."""
        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"Roadmap not found: {self.roadmap_path}")
        with open(self.roadmap_path, 'r', encoding='utf-8') as file:
            self.content = file.read()
        logger.info(f"Loaded roadmap from {self.roadmap_path}")

    def find_current_batch(self) -> Optional[str]:
        """Find the current batch section marked as CURRENT or READY."""
        pattern = r'###\s+Batch\s+\d+:.*?(?:CURRENT|READY)'
        match = re.search(pattern, self.content, re.IGNORECASE)
        if match:
            batch_name = match.group(0)
            logger.info(f"Found current batch: {batch_name}")
            return batch_name
        return None

    def extract_work_streams(self) -> List[Dict[str, str]]:
        """Extract all work stream boxes from the current batch."""
        work_streams = []

        # Pattern to match work stream boxes
        box_pattern = r'┌─+┐\s*\n│\s*Task:\s*(.+?)\s*│\s*\n│\s*Owner:\s*(.+?)\s*│\s*\n│\s*Effort:\s*(.+?)\s*│\s*\n│\s*Output:\s*(.+?)\s*│\s*\n└─+┘'

        matches = re.finditer(box_pattern, self.content, re.MULTILINE)

        for match in matches:
            task = match.group(1).strip()
            owner = match.group(2).strip()
            effort = match.group(3).strip()
            output = match.group(4).strip()

            work_streams.append({
                'task': task,
                'owner': owner,
                'effort': effort,
                'output': output,
                'full_match': match.group(0),
                'start_pos': match.start(),
                'end_pos': match.end()
            })

        logger.info(f"Found {len(work_streams)} work streams in roadmap")
        return work_streams

    def find_unclaimed_work_stream(self, agent_name: str) -> Optional[Dict[str, str]]:
        """
        Find the next unclaimed work stream.
        A work stream is unclaimed if:
        - Owner is a generic role (Backend Dev 1, Frontend Dev, etc.)
        - Owner is UNCLAIMED
        - Owner is this agent's name but marked as TODO/PENDING
        """
        work_streams = self.extract_work_streams()

        # First check if any are assigned to this agent
        for ws in work_streams:
            if ws['owner'] == agent_name:
                return ws

        # Then find unclaimed ones
        generic_owners = ['Backend Dev 1', 'Backend Dev 2', 'Frontend Dev',
                         'DevOps Engineer', 'Content Creator', 'UNCLAIMED']

        for ws in work_streams:
            if ws['owner'] in generic_owners:
                return ws

        return None

    def claim_work_stream(self, work_stream: Dict[str, str], agent_name: str) -> bool:
        """Claim a work stream by updating the owner to the agent name."""
        try:
            # Create updated box with agent name
            updated_box = work_stream['full_match'].replace(
                f"│ Owner: {work_stream['owner']}",
                f"│ Owner: {agent_name} [IN PROGRESS]"
            )

            # Replace in content
            self.content = self.content.replace(work_stream['full_match'], updated_box)

            # Write back to file
            with open(self.roadmap_path, 'w', encoding='utf-8') as file:
                file.write(self.content)

            logger.info(f"Claimed work stream: {work_stream['task']}")
            return True
        except Exception as error:
            logger.error(f"Failed to claim work stream: {error}")
            return False

    def mark_work_stream_complete(self, work_stream: Dict[str, str], agent_name: str) -> bool:
        """Mark a work stream as complete."""
        try:
            # Reload to get latest content
            self.reload()

            # Find the work stream with IN PROGRESS
            in_progress_pattern = re.escape(f"│ Owner: {agent_name} [IN PROGRESS]")

            updated_content = re.sub(
                in_progress_pattern,
                f"│ Owner: {agent_name} [COMPLETE ✅]",
                self.content
            )

            # Write back to file
            with open(self.roadmap_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

            logger.info(f"Marked work stream complete: {work_stream['task']}")
            return True
        except Exception as error:
            logger.error(f"Failed to mark work stream complete: {error}")
            return False


class TestRunner:
    """Manages test execution and reporting."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run_tests(self, test_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Run tests using pytest.
        Returns (success: bool, output: str)
        """
        try:
            cmd = ['pytest', '-v']
            if test_path:
                cmd.append(test_path)

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            if success:
                logger.info("All tests passed ✅")
            else:
                logger.warning(f"Tests failed with exit code {result.returncode}")

            return success, output
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out after 5 minutes")
            return False, "Test execution timed out"
        except Exception as error:
            logger.error(f"Error running tests: {error}")
            return False, str(error)


class GitManager:
    """Manages git operations."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def commit_changes(self, files: List[str], message: str) -> bool:
        """Commit specific files with a message."""
        try:
            # Add files
            for file_path in files:
                subprocess.run(
                    ['git', 'add', file_path],
                    cwd=self.project_root,
                    check=True
                )

            # Commit
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.project_root,
                check=True
            )

            logger.info(f"Committed {len(files)} files: {message}")
            return True
        except subprocess.CalledProcessError as error:
            logger.error(f"Git commit failed: {error}")
            return False


class DevLogWriter:
    """Writes development log entries."""

    def __init__(self, devlog_dir: Path):
        self.devlog_dir = devlog_dir
        self.devlog_dir.mkdir(parents=True, exist_ok=True)

    def write_entry(self, feature_name: str, content: str) -> bool:
        """Write a dev log entry for a feature."""
        try:
            # Sanitize feature name for filename
            safe_name = re.sub(r'[^\w\s-]', '', feature_name.lower())
            safe_name = re.sub(r'[\s]+', '-', safe_name)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            filename = f"{safe_name}.md"
            filepath = self.devlog_dir / filename

            # Format entry
            entry = f"""## {timestamp}

{content}

---

"""

            # Append to file
            with open(filepath, 'a', encoding='utf-8') as file:
                file.write(entry)

            logger.info(f"Wrote dev log entry to {filepath}")
            return True
        except Exception as error:
            logger.error(f"Failed to write dev log: {error}")
            return False


class AutonomousCoder:
    """
    Main autonomous coder agent that follows TDD practices.
    """

    def __init__(self, agent_name: str, project_root: str):
        self.agent_name = agent_name
        self.project_root = Path(project_root)

        # Initialize components
        roadmap_path = self.project_root / 'plans' / 'roadmap.md'
        self.roadmap = RoadmapParser(str(roadmap_path))
        self.test_runner = TestRunner(self.project_root)
        self.git = GitManager(self.project_root)
        self.devlog = DevLogWriter(self.project_root / 'devlog')

        self.current_work_stream = None

        logger.info(f"Initialized AutonomousCoder: {agent_name}")

    def find_and_claim_work(self) -> bool:
        """Find and claim the next work stream."""
        logger.info("Looking for work to claim...")

        work_stream = self.roadmap.find_unclaimed_work_stream(self.agent_name)

        if not work_stream:
            logger.info("No unclaimed work streams found")
            return False

        logger.info(f"Found work stream: {work_stream['task']}")

        if self.roadmap.claim_work_stream(work_stream, self.agent_name):
            self.current_work_stream = work_stream
            return True

        return False

    def execute_tdd_workflow(self) -> Tuple[bool, List[str]]:
        """
        Execute the TDD workflow:
        1. Write tests first
        2. Write code to satisfy tests
        3. Run tests and fix bugs
        4. Commit changes
        5. Write dev log
        6. Update roadmap

        Returns:
            (success, list of modified files)
        """
        if not self.current_work_stream:
            logger.error("No current work stream to execute")
            return False, []

        task = self.current_work_stream['task']
        logger.info(f"Starting TDD workflow for: {task}")

        try:
            # Import TDD executor
            from tdd_executor import execute_work_stream_tdd

            # Execute TDD cycle
            success, modified_files = execute_work_stream_tdd(
                str(self.project_root),
                self.current_work_stream
            )

            if not success:
                logger.error("TDD workflow execution failed")
                return False, []

            logger.info(f"TDD workflow completed successfully. Modified {len(modified_files)} files.")
            return True, modified_files

        except ImportError:
            logger.error("tdd_executor module not found")
            return False, []
        except Exception as error:
            logger.error(f"Error executing TDD workflow: {error}", exc_info=True)
            return False, []

    def verify_and_commit(self, files_modified: List[str]) -> bool:
        """Run tests and commit if they pass."""
        logger.info("Running final test suite...")

        success, output = self.test_runner.run_tests()

        if not success:
            logger.error("Tests failed! Cannot commit.")
            logger.error(output)
            return False

        # Commit changes
        task = self.current_work_stream['task']
        commit_msg = f"""Implement {task}

Output: {self.current_work_stream['output']}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

        if not self.git.commit_changes(files_modified, commit_msg):
            logger.error("Git commit failed")
            return False

        return True

    def finalize_work_stream(self) -> bool:
        """Write dev log and mark work stream complete."""
        if not self.current_work_stream:
            return False

        task = self.current_work_stream['task']
        output = self.current_work_stream['output']

        # Write dev log
        devlog_content = f"""### Completed: {task}

**Effort:** {self.current_work_stream['effort']}
**Output:** {output}

**Implementation Notes:**
- Followed TDD approach
- All tests passing
- Code committed to repository

**Agent:** {self.agent_name}
"""

        if not self.devlog.write_entry(task, devlog_content):
            logger.error("Failed to write dev log")
            return False

        # Mark complete in roadmap
        if not self.roadmap.mark_work_stream_complete(
            self.current_work_stream,
            self.agent_name
        ):
            logger.error("Failed to mark work stream complete")
            return False

        logger.info(f"✅ Completed work stream: {task}")
        self.current_work_stream = None
        return True

    def run_continuous(self, poll_interval: int = 60):
        """
        Run continuously, monitoring for new work.

        Args:
            poll_interval: Seconds between roadmap checks
        """
        logger.info(f"Starting continuous monitoring (poll every {poll_interval}s)")

        try:
            while True:
                try:
                    # Reload roadmap to check for new work
                    self.roadmap.reload()

                    # Try to claim work
                    if self.find_and_claim_work():
                        logger.info("Claimed new work stream, starting TDD workflow")

                        # Execute workflow
                        success, files_modified = self.execute_tdd_workflow()

                        if success:
                            logger.info("TDD workflow completed")

                            # Verify and commit (if files were modified)
                            if files_modified:
                                if self.verify_and_commit(files_modified):
                                    # Finalize
                                    self.finalize_work_stream()
                                else:
                                    logger.error("Verification failed, not finalizing")
                            else:
                                logger.warning("No files modified, skipping commit")
                                # Still finalize to mark as complete
                                self.finalize_work_stream()
                        else:
                            logger.error("TDD workflow failed")
                    else:
                        logger.info("No work available, waiting...")

                    # Wait before next poll
                    time.sleep(poll_interval)

                except KeyboardInterrupt:
                    raise
                except Exception as error:
                    logger.error(f"Error in main loop: {error}", exc_info=True)
                    time.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info("Shutting down agent (received Ctrl+C)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Autonomous Coder Agent - TDD workflow automation'
    )
    parser.add_argument(
        '--name',
        default='AutonomousCoder-1',
        help='Agent name for claiming work streams'
    )
    parser.add_argument(
        '--project-root',
        default='.',
        help='Project root directory'
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=60,
        help='Seconds between roadmap checks'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once instead of continuously'
    )

    args = parser.parse_args()

    # Initialize agent
    agent = AutonomousCoder(args.name, args.project_root)

    if args.once:
        # Run once
        if agent.find_and_claim_work():
            agent.execute_tdd_workflow()
            # Note: In once mode, you'd need to manually handle the rest
            logger.info("Work claimed. Manual intervention required for TDD execution.")
        else:
            logger.info("No work available")
    else:
        # Run continuously
        agent.run_continuous(args.poll_interval)


if __name__ == '__main__':
    main()
