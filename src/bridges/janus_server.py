#!/usr/bin/env python3
"""Janus Bridge Server - Production implementation."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional
from aiohttp import web
import aiohttp
from dataclasses import dataclass, asdict
import uuid

from ..core.protocol import NeuralMessage
from ..core.auth import SigilAuthenticator, AccessTier
from ..core.directives import DirectiveRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentConnection:
    """Active agent connection state."""
    agent_id: str
    connected_at: str
    last_heartbeat: str
    capabilities: list
    endpoint: Optional[str] = None
    websocket: Optional[web.WebSocketResponse] = None


class JanusBridgeServer:
    """Production Janus Bridge server with WebSocket support."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.authenticator = SigilAuthenticator()
        self.directive_registry = DirectiveRegistry()
        
        # Connection tracking
        self.connected_agents: Dict[str, AgentConnection] = {}
        self.websockets: Set[web.WebSocketResponse] = set()
        
        # Metrics
        self.metrics = {
            "messages_processed": 0,
            "messages_failed": 0,
            "auth_failures": 0,
            "active_connections": 0
        }
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure HTTP routes."""
        self.app.router.add_post('/invoke', self.handle_invoke)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/metrics', self.handle_metrics)
        self.app.router.add_post('/agents/register', self.handle_register)
        self.app.router.add_get('/agents/discover', self.handle_discover)
        self.app.router.add_get('/ws', self.handle_websocket)
    
    async def handle_invoke(self, request: web.Request) -> web.Response:
        """Handle synchronous message invocation."""
        try:
            data = await request.json()
            
            # Validate required fields
            if not all(k in data for k in ['agent_id', 'auth_sigil', 'directive', 'payload']):
                return web.json_response({
                    "status": "error",
                    "error_code": "MISSING_FIELDS",
                    "message": "Missing required fields: agent_id, auth_sigil, directive, payload"
                }, status=400)
            
            # Authenticate
            auth_result = self.authenticator.validate_sigil(
                data['auth_sigil'],
                data['agent_id']
            )
            
            if not auth_result['valid']:
                self.metrics['auth_failures'] += 1
                return web.json_response({
                    "status": "error",
                    "error_code": "AUTH_FAILED",
                    "message": "Authentication failed",
                    "details": auth_result
                }, status=401)
            
            # Validate directive
            directive = data['directive']
            if not self.directive_registry.is_valid_directive(directive):
                return web.json_response({
                    "status": "error",
                    "error_code": "INVALID_DIRECTIVE",
                    "message": f"Unknown directive: {directive}"
                }, status=400)
            
            # Check permissions
            required_tier = self.directive_registry.get_required_tier(directive)
            if not self._check_tier(auth_result['tier'], required_tier):
                return web.json_response({
                    "status": "error",
                    "error_code": "PERMISSION_DENIED",
                    "message": f"Insufficient permissions. Required: {required_tier}"
                }, status=403)
            
            # Route message
            result = await self._route_message(data)
            self.metrics['messages_processed'] += 1
            
            return web.json_response({
                "status": "success",
                "message": "Message routed successfully",
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": data.get('metadata', {}).get('correlation_id', str(uuid.uuid4()))
            })
            
        except json.JSONDecodeError:
            return web.json_response({
                "status": "error",
                "error_code": "INVALID_JSON",
                "message": "Invalid JSON payload"
            }, status=400)
        except Exception as e:
            logger.error(f"Error handling invoke: {e}")
            self.metrics['messages_failed'] += 1
            return web.json_response({
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": str(e)
            }, status=500)
    
    async def handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for real-time communication."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)
        self.metrics['active_connections'] += 1
        
        agent_id = None
        
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    # First message should be INITIATE_NEURAL_LINK
                    if not agent_id and data.get('directive') == 'INITIATE_NEURAL_LINK':
                        auth_result = self.authenticator.validate_sigil(
                            data['auth_sigil'],
                            data['agent_id']
                        )
                        
                        if auth_result['valid']:
                            agent_id = data['agent_id']
                            self.connected_agents[agent_id] = AgentConnection(
                                agent_id=agent_id,
                                connected_at=datetime.utcnow().isoformat(),
                                last_heartbeat=datetime.utcnow().isoformat(),
                                capabilities=data.get('payload', {}).get('capabilities', []),
                                websocket=ws
                            )
                            await ws.send_json({
                                "status": "success",
                                "message": "Neural link established",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            logger.info(f"Agent {agent_id} connected via WebSocket")
                        else:
                            await ws.send_json({
                                "status": "error",
                                "error_code": "AUTH_FAILED",
                                "message": "Authentication failed"
                            })
                            break
                    
                    elif agent_id:
                        # Handle authenticated messages
                        if data.get('directive') == 'HEARTBEAT':
                            self.connected_agents[agent_id].last_heartbeat = datetime.utcnow().isoformat()
                            await ws.send_json({
                                "status": "success",
                                "message": "Heartbeat acknowledged",
                                "server_time": datetime.utcnow().isoformat()
                            })
                        else:
                            result = await self._route_message(data)
                            await ws.send_json(result)
                    
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        
        finally:
            self.websockets.discard(ws)
            self.metrics['active_connections'] -= 1
            if agent_id and agent_id in self.connected_agents:
                del self.connected_agents[agent_id]
                logger.info(f"Agent {agent_id} disconnected")
        
        return ws
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "uptime": "running",
            "active_agents": len(self.connected_agents),
            "active_websockets": len(self.websockets),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_metrics(self, request: web.Request) -> web.Response:
        """Prometheus-style metrics endpoint."""
        metrics_text = "\n".join([
            f"neural_link_messages_processed_total {self.metrics['messages_processed']}",
            f"neural_link_messages_failed_total {self.metrics['messages_failed']}",
            f"neural_link_auth_failures_total {self.metrics['auth_failures']}",
            f"neural_link_active_connections {self.metrics['active_connections']}",
            f"neural_link_registered_agents {len(self.connected_agents)}"
        ])
        return web.Response(text=metrics_text, content_type='text/plain')
    
    async def handle_register(self, request: web.Request) -> web.Response:
        """Register agent with the bridge."""
        try:
            data = await request.json()
            agent_id = data.get('agent_id')
            capabilities = data.get('capabilities', [])
            endpoint = data.get('endpoint')
            
            if not agent_id:
                return web.json_response({
                    "status": "error",
                    "message": "agent_id required"
                }, status=400)
            
            self.connected_agents[agent_id] = AgentConnection(
                agent_id=agent_id,
                connected_at=datetime.utcnow().isoformat(),
                last_heartbeat=datetime.utcnow().isoformat(),
                capabilities=capabilities,
                endpoint=endpoint
            )
            
            logger.info(f"Agent {agent_id} registered")
            return web.json_response({
                "status": "success",
                "message": "Agent registered",
                "agent_id": agent_id
            })
        
        except Exception as e:
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)
    
    async def handle_discover(self, request: web.Request) -> web.Response:
        """Discover registered agents."""
        agents = [
            {
                "agent_id": conn.agent_id,
                "capabilities": conn.capabilities,
                "connected_at": conn.connected_at,
                "last_heartbeat": conn.last_heartbeat,
                "endpoint": conn.endpoint
            }
            for conn in self.connected_agents.values()
        ]
        
        return web.json_response({
            "status": "success",
            "agents": agents,
            "count": len(agents)
        })
    
    async def _route_message(self, data: dict) -> dict:
        """Route message to appropriate handler."""
        directive = data['directive']
        
        # Handle built-in directives
        if directive == 'INITIATE_NEURAL_LINK':
            return {"status": "success", "message": "Link established"}
        
        elif directive == 'TERMINATE_LINK':
            return {"status": "success", "message": "Link terminated"}
        
        elif directive == 'HEARTBEAT':
            return {
                "status": "success",
                "server_time": datetime.utcnow().isoformat()
            }
        
        elif directive == 'QUERY_CAPABILITY':
            return {
                "status": "success",
                "capabilities": list(self.directive_registry.directives.keys())
            }
        
        # Broadcast to other agents if needed
        return {
            "status": "success",
            "message": f"Directive {directive} processed",
            "routed_to": "handler"
        }
    
    def _check_tier(self, agent_tier: str, required_tier: str) -> bool:
        """Check if agent tier meets required tier."""
        tier_order = {"TIER3": 1, "TIER2": 2, "TIER1": 3}
        return tier_order.get(agent_tier, 0) >= tier_order.get(required_tier, 0)
    
    def run(self):
        """Start the server."""
        logger.info(f"Starting Janus Bridge Server on {self.host}:{self.port}")
        web.run_app(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    server = JanusBridgeServer()
    server.run()
