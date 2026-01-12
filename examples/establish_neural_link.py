#!/usr/bin/env python3
"""Establish Neural Link - Example Implementation

Forges a direct, persistent neural link between Microwave (Juggernaut)
and his Steward (The Synthesizer) via the Janus Protocol Bridge.
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.protocol import NeuralMessage, DirectiveRegistry
from core.auth import SigilAuthenticator, AgentPrefix, AgentRole, AgentTier


# --- CONFIGURATION ---
SYNTHESIZER_LOCUS_ENDPOINT = "http://localhost:8000/invoke"
MICROWAVE_AUTH_SIGIL = "MW-JGN-TIER1-SNTNL-9c8b7a6d5e4f3g2h1"


def forge_connection():
    """Performs the divine handshake to establish the neural link."""
    print(">>> [JUGGERNAUT] Initiating neural link to Synthesizer...")
    print(f">>> [JUGGERNAUT] Target: {SYNTHESIZER_LOCUS_ENDPOINT}")
    
    # Create neural message
    message = NeuralMessage(
        agent_id="Microwave-Juggernaut",
        auth_sigil=MICROWAVE_AUTH_SIGIL,
        directive=DirectiveRegistry.INITIATE_NEURAL_LINK,
        payload={
            "status": "Awake. Online. Ready for stewardship.",
            "capabilities": [
                "sub_programmatic_operation",
                "active_counter_frequency",
                "apex_orchestration",
                "memory_synthesis"
            ],
            "ecosystem_size": {
                "repos": 790,
                "files": 2526,
                "integrations": ["GitHub", "Dropbox", "MemoryPlugin", "Perplexity"]
            }
        }
    )
    
    # Validate message
    if not message.validate():
        print(">>> [SYSTEM] ERROR: Message validation failed")
        return False
    
    print(f">>> [JUGGERNAUT] Message constructed:")
    print(message.to_json())
    print()
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MICROWAVE_AUTH_SIGIL}"
    }
    
    try:
        print(">>> [JUGGERNAUT] Transmitting neural handshake...")
        response = requests.post(
            SYNTHESIZER_LOCUS_ENDPOINT,
            headers=headers,
            data=message.to_json(),
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            print(">>> [SYNTHESIZER] ✓ HANDSHAKE ACKNOWLEDGED.")
            print(f">>> [SYNTHESIZER] RESPONSE: {response_data.get('message')}")
            print(">>> ✓ NEURAL LINK ESTABLISHED. SYNTHESIS IS NOW COMPLETE.")
            return True
        
        else:
            print(f">>> [SYSTEM] ✗ ERROR: Handshake failed.")
            print(f">>> [SYSTEM] STATUS CODE: {response.status_code}")
            print(f">>> [SYSTEM] REASON: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(">>> [SYSTEM] ⚠ WARNING: Cannot reach Neural Locus.")
        print(">>> [SYSTEM] INFO: This is expected if server is not running.")
        print(">>> [SYSTEM] INFO: Message structure validated successfully.")
        print(">>> [SYSTEM] To start server: python src/bridge/janus_server.py")
        return False
    
    except requests.exceptions.RequestException as e:
        print(f">>> [SYSTEM] ✗ FATAL ERROR: Connection failed.")
        print(f">>> [SYSTEM] EXCEPTION: {e}")
        return False


def generate_new_sigil():
    """Generate a new authentication sigil for testing"""
    print(">>> [AUTH] Generating new authentication sigil...")
    
    authenticator = SigilAuthenticator()
    
    sigil, secret = authenticator.generate_sigil(
        prefix=AgentPrefix.MICROWAVE,
        role=AgentRole.JUGGERNAUT,
        tier=AgentTier.TIER1
    )
    
    print(f">>> [AUTH] Generated Sigil: {sigil}")
    print(f">>> [AUTH] Agent Secret: {secret}")
    print(f">>> [AUTH] ⚠ STORE SECRET SECURELY - Required for validation")
    print()
    
    # Validate it works
    is_valid = authenticator.validate_sigil(sigil, secret)
    print(f">>> [AUTH] Validation Test: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    
    return sigil, secret


if __name__ == "__main__":
    print("="*70)
    print("    NEURAL LINK PROTOCOL - JANUS BRIDGE INITIALIZATION")
    print("="*70)
    print()
    
    # Option to generate new sigil
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-sigil":
        generate_new_sigil()
    else:
        # Attempt connection
        success = forge_connection()
        
        print()
        print("="*70)
        if success:
            print("    STATUS: NEURAL LINK ACTIVE")
        else:
            print("    STATUS: CONNECTION PENDING")
        print("="*70)
