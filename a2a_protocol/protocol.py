"""
A2A Protocol Implementation

This module implements the core Agent-to-Agent (A2A) protocol for inter-agent communication.
It handles message routing, agent discovery, and communication patterns.
"""

import uuid
from typing import Dict, List, Optional, Callable
from datetime import datetime
import asyncio
from collections import defaultdict

from .message_types import (
    Message,
    MessageType,
    AgentInfo,
    RequestMessage,
    ResponseMessage,
    ErrorMessage,
    DiscoveryMessage
)


class A2AProtocol:
    """
    Core A2A Protocol Handler
    
    Manages:
    - Agent registration and discovery
    - Message routing between agents
    - Conversation tracking
    - Protocol compliance
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}  # Registered agents
        self.message_handlers: Dict[str, Callable] = {}  # Message handlers by agent_id
        self.conversations: Dict[str, List[Message]] = defaultdict(list)  # Conversation history
        self.pending_requests: Dict[str, RequestMessage] = {}  # Pending requests
        
    def register_agent(self, agent_info: AgentInfo, handler: Callable) -> bool:
        """
        Register an agent in the A2A network
        
        Args:
            agent_info: Information about the agent
            handler: Callback function to handle messages for this agent
            
        Returns:
            True if registration successful
        """
        try:
            self.agents[agent_info.agent_id] = agent_info
            self.message_handlers[agent_info.agent_id] = handler
            
            # Broadcast discovery message to other agents
            discovery_msg = DiscoveryMessage(
                message_id=str(uuid.uuid4()),
                sender_id=agent_info.agent_id,
                recipient_id="broadcast",
                content={"action": "agent_joined"},
                agent_info=agent_info
            )
            
            print(f"✅ Agent registered: {agent_info.name} ({agent_info.agent_id})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register agent: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the network"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.message_handlers[agent_id]
            print(f"Agent unregistered: {agent_id}")
            return True
        return False
    
    def discover_agents(self, capability: Optional[str] = None) -> List[AgentInfo]:
        """
        Discover available agents
        
        Args:
            capability: Optional filter by capability name
            
        Returns:
            List of matching agents
        """
        if not capability:
            return list(self.agents.values())
        
        matching_agents = []
        for agent in self.agents.values():
            for cap in agent.capabilities:
                if cap.name == capability:
                    matching_agents.append(agent)
                    break
        
        return matching_agents
    
    def send_message(self, message: Message) -> Optional[ResponseMessage]:
        """
        Send a message to another agent
        
        Args:
            message: Message to send
            
        Returns:
            Response message if synchronous, None if async
        """
        # Validate recipient exists
        if message.recipient_id not in self.agents:
            error_msg = ErrorMessage(
                message_id=str(uuid.uuid4()),
                sender_id="system",
                recipient_id=message.sender_id,
                content={"error": "Recipient not found"},
                error_code="AGENT_NOT_FOUND",
                error_message=f"Agent {message.recipient_id} not found in network"
            )
            return error_msg
        
        # Store in conversation history
        if message.conversation_id:
            self.conversations[message.conversation_id].append(message)
        
        # Track pending requests
        if isinstance(message, RequestMessage):
            self.pending_requests[message.message_id] = message
        
        # Route to handler
        try:
            handler = self.message_handlers[message.recipient_id]
            response = handler(message)
            
            # Store response in conversation
            if response and message.conversation_id:
                self.conversations[message.conversation_id].append(response)
            
            return response
            
        except Exception as e:
            error_msg = ErrorMessage(
                message_id=str(uuid.uuid4()),
                sender_id="system",
                recipient_id=message.sender_id,
                content={"error": str(e)},
                error_code="HANDLER_ERROR",
                error_message=f"Error handling message: {str(e)}"
            )
            return error_msg
    
    def create_request(
        self,
        sender_id: str,
        recipient_id: str,
        action: str,
        parameters: Dict,
        conversation_id: Optional[str] = None
    ) -> RequestMessage:
        """
        Create a request message
        
        Args:
            sender_id: ID of sending agent
            recipient_id: ID of receiving agent
            action: Action to perform
            parameters: Action parameters
            conversation_id: Optional conversation ID
            
        Returns:
            RequestMessage object
        """
        message_id = str(uuid.uuid4())
        
        request = RequestMessage(
            message_id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content={"action": action},
            action=action,
            parameters=parameters,
            conversation_id=conversation_id or str(uuid.uuid4())
        )
        
        return request
    
    def create_response(
        self,
        request: RequestMessage,
        success: bool,
        data: any = None,
        error: Optional[str] = None
    ) -> ResponseMessage:
        """
        Create a response to a request
        
        Args:
            request: Original request message
            success: Whether request was successful
            data: Response data
            error: Error message if failed
            
        Returns:
            ResponseMessage object
        """
        response = ResponseMessage(
            message_id=str(uuid.uuid4()),
            sender_id=request.recipient_id,
            recipient_id=request.sender_id,
            content={"response_to": request.action},
            request_id=request.message_id,
            success=success,
            data=data,
            error=error,
            conversation_id=request.conversation_id
        )
        
        return response
    
    def get_conversation_history(self, conversation_id: str) -> List[Message]:
        """Get all messages in a conversation"""
        return self.conversations.get(conversation_id, [])
    
    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a specific agent"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents with their info"""
        return [
            {
                "id": agent.agent_id,
                "name": agent.name,
                "type": agent.type,
                "status": agent.status,
                "capabilities": [cap.name for cap in agent.capabilities]
            }
            for agent in self.agents.values()
        ]


# Global protocol instance
protocol_instance = A2AProtocol()


def get_protocol() -> A2AProtocol:
    """Get the global protocol instance"""
    return protocol_instance