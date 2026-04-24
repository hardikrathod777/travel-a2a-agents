"""
A2A Protocol Message Types

This module defines the standard message types used in Agent-to-Agent communication.
Based on the A2A protocol specification for inter-agent messaging.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MessageType(str, Enum):
    """Standard A2A message types"""
    REQUEST = "request"          # Agent requests action from another agent
    RESPONSE = "response"        # Agent responds to a request
    NOTIFICATION = "notification" # One-way notification
    ERROR = "error"              # Error occurred during processing
    DISCOVERY = "discovery"      # Agent discovery/registration
    HEARTBEAT = "heartbeat"      # Keep-alive signal


class AgentCapability(BaseModel):
    """Defines what an agent can do"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AgentInfo(BaseModel):
    """Information about an agent"""
    agent_id: str
    name: str
    type: str
    capabilities: List[AgentCapability] = Field(default_factory=list)
    status: str = "active"
    endpoint: Optional[str] = None


class Message(BaseModel):
    """Base A2A Protocol Message"""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    content: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RequestMessage(Message):
    """Request message from one agent to another"""
    message_type: MessageType = MessageType.REQUEST
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ResponseMessage(Message):
    """Response message"""
    message_type: MessageType = MessageType.RESPONSE
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None


class NotificationMessage(Message):
    """Notification message"""
    message_type: MessageType = MessageType.NOTIFICATION
    event_type: str
    event_data: Dict[str, Any] = Field(default_factory=dict)


class ErrorMessage(Message):
    """Error message"""
    message_type: MessageType = MessageType.ERROR
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None


class DiscoveryMessage(Message):
    """Agent discovery message"""
    message_type: MessageType = MessageType.DISCOVERY
    agent_info: AgentInfo


# Task-specific message schemas

class FlightSearchRequest(BaseModel):
    """Flight search request schema"""
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    class_type: str = "economy"


class HotelSearchRequest(BaseModel):
    """Hotel search request schema"""
    location: str
    check_in: str
    check_out: str
    guests: int = 1
    rooms: int = 1
    budget: Optional[str] = None


class ActivitySearchRequest(BaseModel):
    """Activity search request schema"""
    location: str
    date: str
    interests: List[str] = Field(default_factory=list)
    budget: Optional[str] = None


class GuideRequest(BaseModel):
    """Guide information request schema"""
    location: str
    topics: List[str] = Field(default_factory=list)
    language: str = "en"


class TravelPlanRequest(BaseModel):
    """Complete travel plan request"""
    destination: str
    duration: int  # days
    budget: str  # low, medium, high
    interests: List[str] = Field(default_factory=list)
    departure_date: Optional[str] = None
    origin: Optional[str] = None