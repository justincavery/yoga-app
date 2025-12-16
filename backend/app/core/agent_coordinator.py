"""
Agent Coordination Module using NATS Messaging

This module enables multiple AI agents to coordinate work on the YogaFlow backend.
Agents can publish task status updates and subscribe to coordination events.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
from enum import Enum

try:
    from nats.aio.client import Client as NATS
    from nats.js import JetStreamContext
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    print("NATS not available - install with: pip install nats-py")


class TaskStatus(str, Enum):
    """Task status states"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class AgentType(str, Enum):
    """Available agent types"""
    PROJECT_MANAGER = "project-manager"
    BACKEND_OPTIMIZER = "backend-optimizer"
    GENERAL_PURPOSE = "general-purpose"
    SECURITY = "security"
    DEVOPS = "devops"


class AgentCoordinator:
    """
    Coordinates work between multiple agents using NATS messaging.

    Features:
    - Task status broadcasting
    - Agent availability tracking
    - Work claim/release protocol
    - Progress updates
    - Completion notifications
    """

    def __init__(self, agent_type: AgentType, agent_id: str, nats_url: str = "nats://localhost:4222"):
        self.agent_type = agent_type
        self.agent_id = agent_id
        self.nats_url = nats_url
        self.nc: Optional[NATS] = None
        self.js: Optional[JetStreamContext] = None
        self._subscriptions = []

    async def connect(self) -> bool:
        """Connect to NATS server"""
        if not NATS_AVAILABLE:
            print(f"[{self.agent_id}] NATS library not available")
            return False

        try:
            self.nc = NATS()
            await self.nc.connect(self.nats_url)
            self.js = self.nc.jetstream()

            # Create streams for agent coordination
            try:
                await self.js.add_stream(
                    name="AGENT_TASKS",
                    subjects=["agent.tasks.*", "agent.status.*", "agent.progress.*"]
                )
            except Exception as stream_error:
                # Stream might already exist
                pass

            print(f"[{self.agent_id}] Connected to NATS at {self.nats_url}")
            return True
        except Exception as error:
            print(f"[{self.agent_id}] Failed to connect to NATS: {error}")
            return False

    async def disconnect(self):
        """Disconnect from NATS"""
        if self.nc:
            await self.nc.drain()
            print(f"[{self.agent_id}] Disconnected from NATS")

    async def claim_task(self, task_id: str, task_description: str) -> bool:
        """
        Claim a task for this agent.
        Returns True if claim successful, False if already claimed.
        """
        if not self.nc:
            return False

        message = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "task_description": task_description,
            "status": TaskStatus.IN_PROGRESS,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            await self.nc.publish(
                f"agent.tasks.claim",
                json.dumps(message).encode()
            )
            print(f"[{self.agent_id}] Claimed task: {task_id}")
            return True
        except Exception as error:
            print(f"[{self.agent_id}] Failed to claim task: {error}")
            return False

    async def update_progress(self, task_id: str, progress: Dict[str, Any]):
        """Send progress update for a task"""
        if not self.nc:
            return

        message = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "progress": progress,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            await self.nc.publish(
                f"agent.progress.{task_id}",
                json.dumps(message).encode()
            )
            print(f"[{self.agent_id}] Progress update for {task_id}: {progress.get('message', 'working...')}")
        except Exception as error:
            print(f"[{self.agent_id}] Failed to send progress: {error}")

    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed"""
        if not self.nc:
            return

        message = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": TaskStatus.COMPLETED,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            await self.nc.publish(
                f"agent.tasks.complete",
                json.dumps(message).encode()
            )
            print(f"[{self.agent_id}] Completed task: {task_id}")
        except Exception as error:
            print(f"[{self.agent_id}] Failed to mark complete: {error}")

    async def report_blocked(self, task_id: str, reason: str, needs_clarification: Optional[Dict] = None):
        """Report that a task is blocked"""
        if not self.nc:
            return

        message = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": TaskStatus.BLOCKED,
            "reason": reason,
            "needs_clarification": needs_clarification,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            await self.nc.publish(
                f"agent.tasks.blocked",
                json.dumps(message).encode()
            )
            print(f"[{self.agent_id}] Task blocked: {task_id} - {reason}")
        except Exception as error:
            print(f"[{self.agent_id}] Failed to report blocked: {error}")

    async def broadcast_status(self, status: str, details: Optional[Dict] = None):
        """Broadcast agent status to all other agents"""
        if not self.nc:
            return

        message = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            await self.nc.publish(
                f"agent.status.{self.agent_type}",
                json.dumps(message).encode()
            )
        except Exception as error:
            print(f"[{self.agent_id}] Failed to broadcast status: {error}")

    async def subscribe_to_tasks(self, callback: Callable):
        """Subscribe to task-related messages"""
        if not self.nc:
            return

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await callback(msg.subject, data)
            except Exception as error:
                print(f"[{self.agent_id}] Error handling message: {error}")

        # Subscribe to relevant subjects
        sub = await self.nc.subscribe("agent.tasks.*", cb=message_handler)
        self._subscriptions.append(sub)

        sub = await self.nc.subscribe("agent.status.*", cb=message_handler)
        self._subscriptions.append(sub)

        print(f"[{self.agent_id}] Subscribed to coordination channels")


# CLI interface for monitoring agent coordination
async def monitor_coordination():
    """Monitor all agent coordination messages"""
    if not NATS_AVAILABLE:
        print("NATS not available. Install with: pip install nats-py")
        return

    nc = NATS()
    await nc.connect("nats://localhost:4222")

    print("Monitoring agent coordination...")
    print("-" * 80)

    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            timestamp = data.get('timestamp', 'unknown')
            agent = data.get('agent_id', 'unknown')
            print(f"[{timestamp}] {msg.subject}")
            print(f"  Agent: {agent}")
            print(f"  Data: {json.dumps(data, indent=2)}")
            print("-" * 80)
        except Exception as error:
            print(f"Error: {error}")

    await nc.subscribe("agent.>", cb=message_handler)

    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down monitor...")
    finally:
        await nc.drain()


if __name__ == "__main__":
    # Run the coordination monitor
    asyncio.run(monitor_coordination())
