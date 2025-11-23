"""
Human-in-the-Loop (HITL) stock research agent using LangGraph.

Scenario: For queries like "Give me revenue growth for Tata Motors", the agent
must ask the user which data source to use when multiple tools apply, then
pause for approval before executing the chosen tool.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from dotenv import load_dotenv
from tools import TOOLS

import getpass
import os

load_dotenv()

def _set_env(var: str, key):
    if not os.environ.get(var):
        os.environ[var] = key


def build_agent():
    """Create the HITL-enabled agent with tool approvals."""
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
    )

    # Force HITL for every tool call so the user can approve/edit/reject.
    interrupt_on = {tool.name: True for tool in TOOLS}

    middleware = [
        HumanInTheLoopMiddleware(
            interrupt_on=interrupt_on,
            description_prefix="Tool execution pending approval",
        )
    ]

    # System prompt nudges the model to ask for a source choice when ambiguous.
    system_prompt = (
        "You are a stock-research agent focused on revenue growth. "
        "Available data sources: Yahoo Finance, Internal DB, Analyst PDF. "
        "When more than one source could be used, ask the user which to run. "
        "Then call exactly one tool that matches their choice."
    )

    checkpointer = InMemorySaver()

    agent = create_agent(
        model=model,
        tools=TOOLS,
        middleware=middleware,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
    )
    return agent
