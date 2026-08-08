from dataclasses import dataclass
from typing import List


@dataclass
class AgentConfig:
    name: str
    max_tokens: int
    timeout: int
    retry_limit: int
    allowed_tools: List[str]
    allow_network: bool
    allow_file_write: bool


AGENT_CONFIGS = {

    "Planner": AgentConfig(
        name="Planner",
        max_tokens=2500,
        timeout=60,
        retry_limit=1,
        allowed_tools=["llm"],
        allow_network=False,
        allow_file_write=False,
    ),

    "Researcher": AgentConfig(
        name="Researcher",
        max_tokens=5000,
        timeout=120,
        retry_limit=2,
        allowed_tools=["llm"],
        allow_network=True,
        allow_file_write=False,
    ),

    "Summarizer": AgentConfig(
        name="Summarizer",
        max_tokens=4000,
        timeout=60,
        retry_limit=1,
        allowed_tools=["llm"],
        allow_network=False,
        allow_file_write=False,
    ),

    "Verifier": AgentConfig(
        name="Verifier",
        max_tokens=2500,
        timeout=60,
        retry_limit=1,
        allowed_tools=["llm"],
        allow_network=False,
        allow_file_write=False,
    ),

}