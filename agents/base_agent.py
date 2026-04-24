"""
Base Agent Class

This is the foundation for all agents in the A2A system.
It handles A2A protocol communication and provides common functionality.
"""

import os
import uuid
from typing import Dict, Any, List, Optional
import requests
import re
import html as html_lib
from abc import ABC, abstractmethod
from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator
from dotenv import load_dotenv

from a2a_protocol import (
    get_protocol,
    AgentInfo,
    AgentCapability,
    Message,
    RequestMessage,
    ResponseMessage,
    MessageType
)

# Load environment variables
load_dotenv()


class BaseAgent(ABC):
    """
    Base class for all A2A agents
    
    Provides:
    - A2A protocol integration
    - OpenAI API integration
    - Message handling
    - Common utilities
    """
    
    def __init__(
        self,
        name: str,
        agent_type: str,
        capabilities: List[Dict[str, str]],
        system_prompt: str
    ):
        """
        Initialize base agent
        
        Args:
            name: Human-readable agent name
            agent_type: Type of agent (e.g., 'flight', 'hotel')
            capabilities: List of capabilities this agent has
            system_prompt: System prompt for OpenAI
        """
        self.agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        
        # Initialize Strands agent (OpenAI model)
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print(f"⚠️ Warning: No OpenAI API key found for {name}")
            self.use_openai = False
            self.strands_agent = None
        else:
            self.use_openai = True
            model_id = os.getenv('AGENT_MODEL', 'gpt-4o-mini')
            model = OpenAIModel(
                client_args={"api_key": api_key},
                model_id=model_id,
                params={
                    "max_tokens": int(os.getenv("AGENT_MAX_TOKENS", "2000")),
                    "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.7"))
                }
            )
            self.strands_agent = Agent(
                name=name,
                model=model,
                tools=[calculator],
                system_prompt=system_prompt
            )
        
        # SerpApi configuration (optional)
        self.serpapi_key = os.getenv('SERPAPI_API_KEY')
        
        # Get A2A protocol instance
        self.protocol = get_protocol()
        
        # Create agent capabilities
        self.capabilities = [
            AgentCapability(
                name=cap['name'],
                description=cap['description'],
                parameters=cap.get('parameters', {})
            )
            for cap in capabilities
        ]
        
        # Create agent info
        self.agent_info = AgentInfo(
            agent_id=self.agent_id,
            name=name,
            type=agent_type,
            capabilities=self.capabilities,
            status="active"
        )
        
        # Register with A2A protocol
        self.protocol.register_agent(self.agent_info, self.handle_message)
        
        print(f"🤖 {self.name} initialized (ID: {self.agent_id})")
    
    @abstractmethod
    def process_request(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a specific request
        
        Args:
            action: Action to perform
            parameters: Parameters for the action
            
        Returns:
            Result dictionary
        """
        pass
    
    def handle_message(self, message: Message) -> Optional[ResponseMessage]:
        """
        Handle incoming A2A messages
        
        Args:
            message: Incoming message
            
        Returns:
            Response message
        """
        print(f"📨 {self.name} received message: {message.message_type}")
        
        if message.message_type == MessageType.REQUEST:
            return self._handle_request(message)
        elif message.message_type == MessageType.DISCOVERY:
            return self._handle_discovery(message)
        else:
            print(f"⚠️ Unhandled message type: {message.message_type}")
            return None
    
    def _handle_request(self, request: RequestMessage) -> ResponseMessage:
        """Handle request message"""
        try:
            # Process the request using the agent's specific logic
            result = self.process_request(request.action, request.parameters)
            
            # Create success response
            response = self.protocol.create_response(
                request=request,
                success=True,
                data=result
            )
            
            print(f"✅ {self.name} completed request: {request.action}")
            return response
            
        except Exception as e:
            print(f"❌ {self.name} error: {str(e)}")
            # Create error response
            response = self.protocol.create_response(
                request=request,
                success=False,
                error=str(e)
            )
            return response
    
    def _handle_discovery(self, message: Message) -> None:
        """Handle discovery message"""
        print(f"🔍 Discovery: {message.content.get('action', 'unknown')}")
        return None
    
    def send_request(
        self,
        recipient_id: str,
        action: str,
        parameters: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> ResponseMessage:
        """
        Send a request to another agent
        
        Args:
            recipient_id: Target agent ID
            action: Action to request
            parameters: Request parameters
            conversation_id: Optional conversation ID
            
        Returns:
            Response from the agent
        """
        # Create request message
        request = self.protocol.create_request(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            action=action,
            parameters=parameters,
            conversation_id=conversation_id
        )
        
        # Send via protocol
        response = self.protocol.send_message(request)
        
        return response
    
    def call_openai(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Call OpenAI API for AI-powered responses
        
        Args:
            prompt: User prompt
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            AI-generated response
        """
        if not self.use_openai or not self.strands_agent:
            return self._fallback_response(prompt)
        
        try:
            response = self.strands_agent(prompt)
            return self._normalize_markdown(str(response))
            
        except Exception as e:
            print(f"⚠️ OpenAI API error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Provide fallback response when OpenAI is unavailable"""
        return f"[{self.name}] Processing your request: {prompt[:100]}..."

    def _normalize_markdown(self, text: str) -> str:
        """Ensure model output is Markdown, not HTML."""
        if not text:
            return text
        cleaned = text.strip()
        cleaned = html_lib.unescape(cleaned)
        if re.search(r"<\s*/?\s*[a-z][^>]*>", cleaned, re.IGNORECASE):
            cleaned = self._html_to_markdown(cleaned)
        return cleaned

    def _html_to_markdown(self, html: str) -> str:
        """Convert basic HTML to Markdown without extra dependencies."""
        if not html:
            return ""
        text = html.replace("\r\n", "\n")
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<hr\s*/?>", "\n---\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<h1[^>]*>", "# ", text, flags=re.IGNORECASE)
        text = re.sub(r"<h2[^>]*>", "## ", text, flags=re.IGNORECASE)
        text = re.sub(r"<h3[^>]*>", "### ", text, flags=re.IGNORECASE)
        text = re.sub(r"<h4[^>]*>", "#### ", text, flags=re.IGNORECASE)
        text = re.sub(r"<h5[^>]*>", "##### ", text, flags=re.IGNORECASE)
        text = re.sub(r"<h6[^>]*>", "###### ", text, flags=re.IGNORECASE)
        text = re.sub(r"</h[1-6]>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<p[^>]*>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<li[^>]*>", "- ", text, flags=re.IGNORECASE)
        text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<ul[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</ul>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<ol[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</ol>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<strong[^>]*>", "**", text, flags=re.IGNORECASE)
        text = re.sub(r"</strong>", "**", text, flags=re.IGNORECASE)
        text = re.sub(r"<b[^>]*>", "**", text, flags=re.IGNORECASE)
        text = re.sub(r"</b>", "**", text, flags=re.IGNORECASE)
        text = re.sub(r"<em[^>]*>", "*", text, flags=re.IGNORECASE)
        text = re.sub(r"</em>", "*", text, flags=re.IGNORECASE)
        text = re.sub(r"<i[^>]*>", "*", text, flags=re.IGNORECASE)
        text = re.sub(r"</i>", "*", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _serpapi_search(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call SerpApi if an API key is configured."""
        if not self.serpapi_key:
            return None
        request_params = dict(params)
        request_params["api_key"] = self.serpapi_key
        try:
            response = requests.get("https://serpapi.com/search", params=request_params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and data.get("error"):
                raise RuntimeError(data["error"])
            return data
        except Exception as exc:
            print(f"âš ï¸ SerpApi request failed: {exc}")
            return None
    
    def discover_agents_by_type(self, agent_type: str) -> List[AgentInfo]:
        """
        Find agents of a specific type
        
        Args:
            agent_type: Type of agent to find
            
        Returns:
            List of matching agents
        """
        all_agents = self.protocol.discover_agents()
        return [agent for agent in all_agents if agent.type == agent_type]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": "active",
            "capabilities": [cap.name for cap in self.capabilities],
            "using_openai": self.use_openai
        }
