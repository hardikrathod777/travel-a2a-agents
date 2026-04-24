"""
A2A Runtime

Starts A2A servers for specialized agents using Strands A2A.
"""

import threading
from typing import Dict

import json
from strands.multiagent.a2a import A2AServer
from a2a.types import AgentSkill


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORTS = {
    "flight": 9101,
    "hotel": 9102,
    "activity": 9103,
    "guide": 9104
}


class DirectA2AAgent:
    """Minimal agent adapter that executes actions directly without LLMs."""

    def __init__(self, name: str, description: str, action_handler):
        self.name = name
        self.description = description
        self._action_handler = action_handler

    async def stream_async(self, content_blocks, invocation_state=None):
        text_parts = []
        for block in content_blocks or []:
            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
        payload_text = "\n".join(text_parts).strip()

        try:
            payload = json.loads(payload_text) if payload_text else {}
        except Exception:
            payload = {}

        action = payload.get("action")
        parameters = payload.get("parameters", {})
        if not action:
            result = {"error": "Missing action in A2A request payload"}
        else:
            try:
                result = self._action_handler(action, parameters)
            except Exception as exc:
                result = {"error": str(exc)}

        yield {"result": json.dumps(result)}


def _run_server(server: A2AServer) -> None:
    server.serve()


def start_a2a_servers(
    flight_agent,
    hotel_agent,
    activity_agent,
    guide_agent,
    host: str = DEFAULT_HOST,
    ports: Dict[str, int] | None = None
) -> Dict[str, str]:
    ports = ports or DEFAULT_PORTS
    servers = []
    urls = {}
    
    agents = [
        ("flight", flight_agent, "Search flights and provide flight options"),
        ("hotel", hotel_agent, "Search hotels and provide lodging options"),
        ("activity", activity_agent, "Find activities and tours"),
        ("guide", guide_agent, "Provide local guide information")
    ]
    
    for agent_type, agent, description in agents:
        port = ports[agent_type]
        url = f"http://{host}:{port}/"
        urls[agent_type] = url
        
        wrapper_agent = DirectA2AAgent(
            name=agent.name,
            description=description,
            action_handler=agent.process_request
        )
        
        server = A2AServer(
            agent=wrapper_agent,
            host=host,
            port=port,
            enable_a2a_compliant_streaming=True,
            skills=[
                AgentSkill(
                    id="process_request",
                    name="Process request",
                    description=description,
                    tags=["travel"]
                )
            ]
        )
        
        thread = threading.Thread(
            target=_run_server,
            args=(server,),
            daemon=True
        )
        servers.append(thread)
    
    for thread in servers:
        thread.start()
    
    return urls
