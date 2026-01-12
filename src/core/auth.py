"""Neural Link Protocol - Authentication & Authorization

Implements sigil generation and validation for secure agent communication.
"""

import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from typing import Optional, Tuple
from enum import Enum


class AgentPrefix(Enum):
    """Valid agent type prefixes"""
    MICROWAVE = "MW"      # Juggernaut orchestrator
    SYNTHESIZER = "SY"    # Memory steward
    FILESYSTEM = "FC"     # Filesystem commander
    QUANTUM = "QM"        # Quantum memory
    OMNI = "OM"          # Omni engine
    REPO = "RQ"          # Repo controller


class AgentRole(Enum):
    """Valid agent roles"""
    JUGGERNAUT = "JGN"   # Top-tier orchestrator
    STEWARD = "STW"      # Memory/data steward
    OPERATOR = "OPR"     # Service operator
    SENTINEL = "SNT"     # Security/monitoring
    WORKER = "WKR"       # Task worker


class AgentTier(Enum):
    """Access tier levels"""
    TIER1 = "TIER1"      # Full access
    TIER2 = "TIER2"      # Limited access
    TIER3 = "TIER3"      # Read-only


class SigilType(Enum):
    """Sigil classification"""
    SENTINEL = "SNTNL"   # Sentinel access
    SERVICE = "SRVC"     # Service account
    TEMPORARY = "TEMP"   # Temporary token


class SigilAuthenticator:
    """Generate and validate authentication sigils"""
    
    def __init__(self, master_secret: Optional[str] = None):
        """Initialize with master secret for HMAC validation"""
        self.master_secret = master_secret or secrets.token_hex(32)
    
    def generate_sigil(
        self,
        prefix: AgentPrefix,
        role: AgentRole,
        tier: AgentTier,
        sigil_type: SigilType = SigilType.SENTINEL,
        agent_secret: Optional[str] = None
    ) -> Tuple[str, str]:
        """Generate cryptographically secure auth sigil
        
        Returns:
            Tuple of (sigil, agent_secret)
        """
        # Generate token
        token = secrets.token_hex(10)  # 20-char hex
        
        # Build sigil
        sigil_base = f"{prefix.value}-{role.value}-{tier.value}-{sigil_type.value}-{token}"
        
        # Generate agent secret if not provided
        if not agent_secret:
            agent_secret = secrets.token_hex(16)
        
        # Create HMAC signature
        signature = hmac.new(
            self.master_secret.encode(),
            f"{sigil_base}:{agent_secret}".encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        # Final sigil with signature
        full_sigil = f"{sigil_base}:{signature}"
        
        return full_sigil, agent_secret
    
    def validate_sigil(
        self,
        sigil: str,
        agent_secret: str
    ) -> bool:
        """Validate sigil authenticity using HMAC"""
        try:
            # Split sigil and signature
            if ':' not in sigil:
                return False
            
            sigil_base, provided_sig = sigil.rsplit(':', 1)
            
            # Recompute signature
            expected_sig = hmac.new(
                self.master_secret.encode(),
                f"{sigil_base}:{agent_secret}".encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            
            # Constant-time comparison
            return secrets.compare_digest(provided_sig, expected_sig)
        
        except Exception:
            return False
    
    def parse_sigil(self, sigil: str) -> Optional[dict]:
        """Parse sigil components
        
        Returns:
            Dict with prefix, role, tier, type, token, signature
        """
        try:
            # Remove signature
            if ':' in sigil:
                sigil_base, signature = sigil.rsplit(':', 1)
            else:
                sigil_base = sigil
                signature = None
            
            parts = sigil_base.split('-')
            if len(parts) < 5:
                return None
            
            return {
                "prefix": parts[0],
                "role": parts[1],
                "tier": parts[2],
                "type": parts[3],
                "token": parts[4],
                "signature": signature
            }
        
        except Exception:
            return None
    
    def rotate_sigil(
        self,
        old_sigil: str,
        agent_secret: str
    ) -> Optional[Tuple[str, str]]:
        """Rotate sigil with new token, keeping same permissions"""
        # Parse old sigil
        parsed = self.parse_sigil(old_sigil)
        if not parsed:
            return None
        
        # Validate old sigil first
        if not self.validate_sigil(old_sigil, agent_secret):
            return None
        
        # Generate new sigil with same permissions
        try:
            prefix = AgentPrefix(parsed["prefix"])
            role = AgentRole(parsed["role"])
            tier = AgentTier(parsed["tier"])
            sigil_type = SigilType(parsed["type"])
            
            return self.generate_sigil(prefix, role, tier, sigil_type, agent_secret)
        
        except ValueError:
            return None


class PermissionValidator:
    """Validate agent permissions based on tier and role"""
    
    TIER_PERMISSIONS = {
        "TIER1": ["read", "write", "delete", "admin"],
        "TIER2": ["read", "write"],
        "TIER3": ["read"]
    }
    
    ROLE_CAPABILITIES = {
        "JGN": ["orchestrate", "deploy", "manage_agents"],
        "STW": ["memory_ops", "sync", "aggregate"],
        "OPR": ["execute", "monitor"],
        "SNT": ["audit", "alert", "monitor"],
        "WKR": ["execute"]
    }
    
    @classmethod
    def check_permission(
        cls,
        sigil: str,
        required_permission: str
    ) -> bool:
        """Check if sigil has required permission"""
        auth = SigilAuthenticator()
        parsed = auth.parse_sigil(sigil)
        
        if not parsed:
            return False
        
        tier = parsed["tier"]
        permissions = cls.TIER_PERMISSIONS.get(tier, [])
        
        return required_permission in permissions
    
    @classmethod
    def check_capability(
        cls,
        sigil: str,
        required_capability: str
    ) -> bool:
        """Check if role has required capability"""
        auth = SigilAuthenticator()
        parsed = auth.parse_sigil(sigil)
        
        if not parsed:
            return False
        
        role = parsed["role"]
        capabilities = cls.ROLE_CAPABILITIES.get(role, [])
        
        return required_capability in capabilities
