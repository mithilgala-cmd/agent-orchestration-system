"""
Thread-safe EventBus for streaming real-time agent events to SSE clients.
Uses standard library queue.SimpleQueue so it works from any thread.
"""
import queue
import json
from typing import Dict, Optional


class EventBus:
    def __init__(self):
        self._channels: Dict[str, queue.SimpleQueue] = {}

    def create_channel(self, thread_id: str) -> queue.SimpleQueue:
        """Create a new event channel for a task thread."""
        q = queue.SimpleQueue()
        self._channels[thread_id] = q
        return q

    def emit(self, thread_id: str, event_type: str, data: dict):
        """Emit an event to a specific thread's channel (thread-safe)."""
        if thread_id in self._channels:
            self._channels[thread_id].put({"type": event_type, "data": data})

    def emit_sentinel(self, thread_id: str):
        """Signal end-of-stream (None is the sentinel value)."""
        if thread_id in self._channels:
            self._channels[thread_id].put(None)

    def get_channel(self, thread_id: str) -> Optional[queue.SimpleQueue]:
        return self._channels.get(thread_id)

    def close_channel(self, thread_id: str):
        self._channels.pop(thread_id, None)


# Singleton — imported by both main.py and api.py
event_bus = EventBus()
