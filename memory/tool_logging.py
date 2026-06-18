from datetime import datetime, timezone
from typing import Any

from schemas import ToolCallRecord, ToolCallStatus

from .base import BaseMemoryStore


def log_tool_call(
    memory_store: BaseMemoryStore,
    *,
    run_id: str,
    tool_name: str,
    input: dict[str, Any] | None = None,
    output_summary: str | None = None,
    status: ToolCallStatus = ToolCallStatus.SUCCESS,
    error: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ToolCallRecord:
    record = ToolCallRecord(
        run_id=run_id,
        tool_name=tool_name,
        input=input or {},
        output_summary=output_summary,
        status=status,
        error=error,
        metadata=metadata or {},
        completed_at=datetime.now(timezone.utc),
    )
    return memory_store.save_tool_call(record)
