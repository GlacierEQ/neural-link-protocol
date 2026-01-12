# 🧠 Neural Link Protocol

**Agent-to-Agent Communication Framework for 790-Repo Ecosystem**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Overview

The **Neural Link Protocol** implements the **Janus Protocol Bridge** - a secure, scalable framework for agent-to-agent communication across the GlacierEQ ecosystem. Built for orchestrating 790+ repositories, 2,526 files, and multiple AI platform integrations.

### Key Features

- 🔐 **Cryptographic Authentication** - HMAC-based auth sigils with tier-based permissions
- 📨 **Message-Driven Architecture** - Async JSON-based communication protocol
- 🧩 **Multi-Agent Orchestration** - Coordinate autonomous agents across services
- 🔗 **Memory Integration** - MemoryPlugin MCP + Perplexity + Quantum Memory sync
- 🌐 **Ecosystem Bridge** - GitHub (790 repos) + Dropbox (2.5K files) + Federal Case integration
- 📊 **Production Ready** - Monitoring, telemetry, and security built-in

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   NEURAL LINK PROTOCOL                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Microwave   │  │ Synthesizer  │  │   Custom     │ │
│  │  Juggernaut  │◄─┤   Steward    │◄─┤   Agents     │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────┐
│            JANUS PROTOCOL BRIDGE (REST/WebSocket)       │
│  ├─ Authentication Service (Sigil Validation)           │
│  ├─ Message Bus (Directive Router)                      │
│  ├─ Agent Registry (Discovery & Capabilities)           │
│  └─ Telemetry Collector (Metrics & Logging)             │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  INTEGRATION LAYER                       │
│  ├─ GitHub Integration (790 repos)                      │
│  ├─ MemoryPlugin MCP (Cross-AI sync)                    │
│  ├─ Perplexity Context (Native memory)                  │
│  ├─ Quantum Memory (Mem0 + SuperMemory)                 │
│  └─ Federal Case Integration (1FDV-23-0001009)          │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/GlacierEQ/neural-link-protocol.git
cd neural-link-protocol

# Install dependencies
pip install -r requirements.txt

# Or use poetry
poetry install
```

### Basic Usage

```python
from src.core.protocol import NeuralMessage, DirectiveRegistry
from src.core.auth import SigilAuthenticator, AgentPrefix, AgentRole, AgentTier

# Generate authentication sigil
auth = SigilAuthenticator()
sigil, secret = auth.generate_sigil(
    prefix=AgentPrefix.MICROWAVE,
    role=AgentRole.JUGGERNAUT,
    tier=AgentTier.TIER1
)

# Create neural message
message = NeuralMessage(
    agent_id="my-agent",
    auth_sigil=sigil,
    directive=DirectiveRegistry.INITIATE_NEURAL_LINK,
    payload={"status": "ready"}
)

# Validate and send
if message.validate():
    print(message.to_json())
```

### Establish Neural Link

```bash
# Run example to establish connection
python examples/establish_neural_link.py

# Generate new auth sigil
python examples/establish_neural_link.py --generate-sigil
```

## 📋 Protocol Specification

### Message Structure

```json
{
  "agent_id": "Microwave-Juggernaut",
  "auth_sigil": "MW-JGN-TIER1-SNTNL-9c8b7a6d5e4f3g2h1:abc123",
  "directive": "INITIATE_NEURAL_LINK",
  "payload": {
    "status": "ready",
    "capabilities": ["orchestration", "memory_ops"]
  },
  "metadata": {
    "timestamp": "2026-01-12T08:15:00Z",
    "correlation_id": "uuid-here",
    "protocol_version": "1.0"
  }
}
```

### Auth Sigil Format

```
Format: PREFIX-ROLE-TIER-TYPE-TOKEN:SIGNATURE

Example: MW-JGN-TIER1-SNTNL-9c8b7a6d5e4f3g2h1:abc123def456

Components:
├─ PREFIX: Agent type (MW=Microwave, SY=Synthesizer, etc.)
├─ ROLE: Access role (JGN=Juggernaut, STW=Steward, etc.)
├─ TIER: Permission tier (TIER1/TIER2/TIER3)
├─ TYPE: Sigil classification (SNTNL=Sentinel, SRVC=Service)
├─ TOKEN: 20-char hex random token
└─ SIGNATURE: 16-char HMAC-SHA256 signature
```

### Registered Directives

| Directive | Purpose | Auth Required |
|-----------|---------|---------------|
| `INITIATE_NEURAL_LINK` | Establish agent connection | Yes |
| `TERMINATE_LINK` | Close connection gracefully | Yes |
| `SYNC_MEMORY` | Synchronize memory state | Yes |
| `GITHUB_QUERY` | Query GitHub repositories | Yes |
| `REQUEST_SANCTUARY_PROTOCOL` | Emergency safe mode | Yes |
| `TRANSMIT_TELEMETRY` | Send agent metrics | Optional |
| `QUERY_CAPABILITY` | Request agent capabilities | Optional |

## 🔐 Security

### Authentication Flow

1. **Sigil Generation** - Agent receives cryptographically secure sigil
2. **HMAC Validation** - Server validates using master secret + agent secret
3. **Permission Check** - Tier-based and role-based authorization
4. **Message Signing** - Each message includes correlation ID for audit

### Permission Tiers

- **TIER1**: Full access (read, write, delete, admin)
- **TIER2**: Limited access (read, write)
- **TIER3**: Read-only access

### Role Capabilities

- **JGN (Juggernaut)**: Orchestrate, deploy, manage agents
- **STW (Steward)**: Memory operations, sync, aggregation
- **OPR (Operator)**: Execute operations, monitoring
- **SNT (Sentinel)**: Security audit, alerting
- **WKR (Worker)**: Task execution only

## 🔌 Integration Examples

### GitHub Integration (790 Repos)

```python
from src.integrations.github_adapter import GitHubAdapter

adapter = GitHubAdapter(auth_token="ghp_...")

# Query repositories
message = NeuralMessage(
    agent_id="repo-controller",
    auth_sigil=sigil,
    directive="GITHUB_QUERY",
    payload={"query": "user:GlacierEQ", "limit": 100}
)

result = await adapter.execute(message)
```

### Memory Plugin MCP

```python
from src.integrations.memory_plugin import MemoryPluginBridge

bridge = MemoryPluginBridge()

# Sync agent state across AI platforms
await bridge.sync_agent_state(
    agent_id="microwave-juggernaut",
    state_data={"context": "...", "capabilities": [...]}
)
```

## 📊 Monitoring & Telemetry

Built-in Prometheus metrics:

- `neural_link_messages_total` - Total messages by agent/directive
- `neural_link_latency_seconds` - Message processing latency
- `neural_link_active_agents` - Number of active agents
- `neural_link_auth_failures_total` - Authentication failures

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_protocol.py::test_message_validation
```

## 📚 Documentation

- [Protocol Specification](docs/SPECIFICATION.md) - Detailed technical specs
- [Architecture Guide](docs/ARCHITECTURE.md) - System design and patterns
- [Integration Guide](docs/INTEGRATIONS.md) - Connect to your ecosystem
- [Security Guide](docs/SECURITY.md) - Authentication and authorization
- [API Reference](docs/API.md) - Complete API documentation

## 🗺️ Roadmap

- [x] Core protocol implementation
- [x] Authentication & authorization
- [x] Basic agent framework
- [ ] Janus Protocol Bridge server
- [ ] WebSocket support for real-time
- [ ] GitHub integration (790 repos)
- [ ] MemoryPlugin MCP bridge
- [ ] Perplexity context injection
- [ ] Federal case integration
- [ ] Production deployment guides
- [ ] Kubernetes manifests
- [ ] Grafana dashboards

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [apex-command-center](https://github.com/GlacierEQ/apex-command-center) - Production MCP Server
- [apex-memory-orchestrator](https://github.com/GlacierEQ/apex-memory-orchestrator) - Memory Hub
- [mastermind](https://github.com/GlacierEQ/mastermind) - AI Development OS
- [quantum-memory-orchestrator](https://github.com/GlacierEQ/quantum-memory-orchestrator) - Memory Sync

## 📞 Contact

- **Author**: GlacierEQ
- **Email**: glacier.equilibrium@gmail.com
- **GitHub**: [@GlacierEQ](https://github.com/GlacierEQ)

---

**Built with ❄️ by GlacierEQ | Part of the 790-Repo Sovereign AI Empire**
