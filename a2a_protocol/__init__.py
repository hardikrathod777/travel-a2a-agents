"""
A2A Protocol Package

Agent-to-Agent communication protocol implementation
"""

from .protocol import A2AProtocol, get_protocol
from .message_types import (
    Message,
    MessageType,
    AgentInfo,
    AgentCapability,
    RequestMessage,
    ResponseMessage,
    ErrorMessage,
    NotificationMessage,
    DiscoveryMessage,
    FlightSearchRequest,
    HotelSearchRequest,
    ActivitySearchRequest,
    GuideRequest,
    TravelPlanRequest
)

__all__ = [
    'A2AProtocol',
    'get_protocol',
    'Message',
    'MessageType',
    'AgentInfo',
    'AgentCapability',
    'RequestMessage',
    'ResponseMessage',
    'ErrorMessage',
    'NotificationMessage',
    'DiscoveryMessage',
    'FlightSearchRequest',
    'HotelSearchRequest',
    'ActivitySearchRequest',
    'GuideRequest',
    'TravelPlanRequest'
]