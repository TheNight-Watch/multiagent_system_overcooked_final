"""
CamelAI-based Multi-Agent Overcooked System - Agents Module

This module contains specialized agents for the Overcooked cooking collaboration system.
"""

from .order_manager import make_order_manager
from .cooking_agent import (
    make_universal_chef,
    make_universal_chef_team
)

__all__ = [
    'make_order_manager', 
    'make_universal_chef',
    'make_universal_chef_team'
]