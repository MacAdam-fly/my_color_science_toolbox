"""Simple registry for agent-facing color tools."""

from __future__ import annotations

from typing import Callable, Dict

TOOL_REGISTRY: Dict[str, Callable] = {}


def register_tool(name: str):
    def decorator(func: Callable):
        TOOL_REGISTRY[name] = func
        return func

    return decorator


def get_tool(name: str) -> Callable:
    return TOOL_REGISTRY[name]
