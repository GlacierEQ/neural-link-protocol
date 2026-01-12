"""Neural Link Protocol - Core Message Structure

Implements the Janus Protocol Bridge for agent-to-agent communication.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid
import json


@dataclass
class NeuralMessage:
    """Core message structure for agent communication via Janus Protocol"""
    
    agent_id: str
    auth_sigil: str
    directive: str
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize metadata if not provided"""
        if not self.metadata:
            self.metadata = {
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": str(uuid.uuid4()),
                "protocol_version": "1.0",
                "message_id": str(uuid.uuid4())
            }
    
    def validate(self) -> bool:
        """Validate message structure and auth sigil format
        
        Sigil Format: PREFIX-ROLE-TIER-TYPE-TOKEN
        Example: MW-JGN-TIER1-SNTNL-9c8b7a6d5e4f3g2h1
        """
        # Check required fields
        if not all([self.agent_id, self.auth_sigil, self.directive]):
            return False
        
        # Validate sigil format
        sigil_parts = self.auth_sigil.split('-')
        if len(sigil_parts) < 5:
            return False
        
        # Validate directive is uppercase
        if not self.directive.isupper():
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary for serialization"""
        return {
            "agent_id": self.agent_id,
            "auth_sigil": self.auth_sigil,
            "directive": self.directive,
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NeuralMessage':
        """Create message from dictionary"""
        return cls(
            agent_id=data["agent_id"],
            auth_sigil=data["auth_sigil"],
            directive=data["directive"],
            payload=data["payload"],
            metadata=data.get("metadata")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'NeuralMessage':
        """Create message from JSON string"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class NeuralResponse:
    """Response structure for agent communication"""
    
    status: str  # success | error | pending
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class DirectiveRegistry:
    """Registry of valid directives for the protocol"""
    
    # Core Protocol Directives
    INITIATE_NEURAL_LINK = "INITIATE_NEURAL_LINK"
    TERMINATE_LINK = "TERMINATE_LINK"
    HEARTBEAT = "HEARTBEAT"
    
    # Memory Operations
    SYNC_MEMORY = "SYNC_MEMORY"
    QUERY_MEMORY = "QUERY_MEMORY"
    UPDATE_MEMORY = "UPDATE_MEMORY"
    
    # GitHub Operations
    GITHUB_QUERY = "GITHUB_QUERY"
    GITHUB_UPDATE = "GITHUB_UPDATE"
    GITHUB_CREATE = "GITHUB_CREATE"
    
    # Sanctuary & Safety
    REQUEST_SANCTUARY_PROTOCOL = "REQUEST_SANCTUARY_PROTOCOL"
    EMERGENCY_SHUTDOWN = "EMERGENCY_SHUTDOWN"
    
    # Telemetry
    TRANSMIT_TELEMETRY = "TRANSMIT_TELEMETRY"
    QUERY_CAPABILITY = "QUERY_CAPABILITY"
    
    @classmethod
    def is_valid(cls, directive: str) -> bool:
        """Check if directive is registered"""
        return hasattr(cls, directive)
    
    @classmethod
    def list_all(cls) -> list:
        """List all registered directives"""
        return [attr for attr in dir(cls) if attr.isupper()]
