"""
CamelAI-based Multi-Agent Overcooked System - Agents Module

This module contains specialized agents for the Overcooked cooking collaboration system.
"""

from .order_manager import make_order_manager, generate_cooking_tasks
from .cooking_agent import (
    make_universal_chef,
    make_universal_chef_team,
    get_next_task_for_agent,
    start_task_execution,
    complete_task_execution
)

__all__ = [
    'make_order_manager', 
    'make_universal_chef',
    'make_universal_chef_team',
    'generate_cooking_tasks',
    'get_next_task_for_agent',
    'start_task_execution',
    'complete_task_execution'
]