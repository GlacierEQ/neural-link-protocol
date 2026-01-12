# Neural Link Protocol - Technical Specification

**Version**: 1.0  
**Status**: Active Development  
**Last Updated**: January 12, 2026

## Table of Contents

1. [Overview](#overview)
2. [Protocol Architecture](#protocol-architecture)
3. [Message Format](#message-format)
4. [Authentication](#authentication)
5. [Directive Vocabulary](#directive-vocabulary)
6. [Response Format](#response-format)
7. [Error Handling](#error-handling)
8. [Security](#security)
9. [Integration Points](#integration-points)
10. [Performance Requirements](#performance-requirements)

---

## 1. Overview

The Neural Link Protocol (NLP) implements a secure, scalable agent-to-agent communication framework based on the Janus Protocol Bridge architecture.

### Design Principles

- **Security First**: Cryptographic authentication for all messages
- **Async by Design**: Non-blocking message passing
- **Extensible**: Easy to add new agents and directives
- **Observable**: Built-in monitoring and telemetry
- **Fault Tolerant**: Graceful degradation and error recovery

### Use Cases

- Multi-agent orchestration across 790+ repositories
- Cross-platform memory synchronization
- Automated DevOps workflows
- Federal case integration and compliance
- Real-time system monitoring and alerting

---

## 2. Protocol Architecture

### Layered Architecture

```
┌─────────────────────────────────────────┐
│     Application Layer (Agents)          │
├─────────────────────────────────────────┤
│     Protocol Layer (Messages)           │
├─────────────────────────────────────────┤
│     Security Layer (Auth & Crypto)      │
├─────────────────────────────────────────┤
│     Transport Layer (HTTP/WebSocket)    │
├─────────────────────────────────────────┤
│     Network Layer (TCP/IP)              │
└─────────────────────────────────────────┘
```

### Component Responsibilities

**Janus Bridge Server**
- Message routing and distribution
- Authentication and authorization
- Agent discovery and registration
- Rate limiting and throttling

**Agent Runtime**
- Message construction and validation
- Directive execution
- State management
- Error handling

**Integration Adapters**
- External service connections
- Protocol translation
- Data transformation

---

## 3. Message Format

### Core Message Structure

```json
{
  "agent_id": "string",
  "auth_sigil": "string",
  "directive": "string",
  "payload": {
    "key": "value"
  },
  "metadata": {
    "timestamp": "ISO8601",
    "correlation_id": "uuid",
    "protocol_version": "string",
    "message_id": "uuid",
    "priority": "int",
    "ttl": "int"
  }
}
```

### Field Specifications

#### agent_id (required)
- **Type**: String
- **Format**: `{AgentName}-{Role}`
- **Example**: `"Microwave-Juggernaut"`
- **Max Length**: 100 characters
- **Pattern**: `^[A-Za-z0-9-_]+$`

#### auth_sigil (required)
- **Type**: String
- **Format**: `{PREFIX}-{ROLE}-{TIER}-{TYPE}-{TOKEN}:{SIGNATURE}`
- **Example**: `"MW-JGN-TIER1-SNTNL-9c8b7a6d5e4f3g2h1:abc123"`
- **Validation**: HMAC-SHA256 signature required

#### directive (required)
- **Type**: String
- **Format**: SCREAMING_SNAKE_CASE
- **Example**: `"INITIATE_NEURAL_LINK"`
- **Validation**: Must be registered in DirectiveRegistry

#### payload (required)
- **Type**: Object
- **Content**: Flexible key-value pairs
- **Max Size**: 10MB
- **Validation**: Valid JSON

#### metadata (optional)
- **Type**: Object
- **Auto-generated**: If not provided
- **Fields**:
  - `timestamp`: ISO8601 UTC timestamp
  - `correlation_id`: UUID v4
  - `protocol_version`: Semantic version
  - `message_id`: UUID v4
  - `priority`: 0-10 (10 highest)
  - `ttl`: Time-to-live in seconds

---

## 4. Authentication

### Auth Sigil Structure

```
Format: {PREFIX}-{ROLE}-{TIER}-{TYPE}-{TOKEN}:{SIGNATURE}

Components:
  PREFIX   : 2-char agent type identifier
  ROLE     : 3-char role code
  TIER     : Access tier (TIER1/TIER2/TIER3)
  TYPE     : Sigil type (SNTNL/SRVC/TEMP)
  TOKEN    : 20-char hex random token
  SIGNATURE: 16-char HMAC-SHA256(sigil:secret)

Example:
  MW-JGN-TIER1-SNTNL-9c8b7a6d5e4f3g2h1:a1b2c3d4e5f6g7h8
```

### Agent Prefixes

| Prefix | Agent Type | Description |
|--------|-----------|-------------|
| MW | Microwave | Juggernaut orchestrator |
| SY | Synthesizer | Memory steward |
| FC | Filesystem | File operations |
| QM | Quantum | Memory storage |
| OM | Omni | Big brain engine |
| RQ | RepoQueue | Repository controller |

### Roles

| Role | Code | Capabilities |
|------|------|-------------|
| Juggernaut | JGN | Full orchestration, deployment, agent management |
| Steward | STW | Memory ops, sync, aggregation |
| Operator | OPR | Service execution, monitoring |
| Sentinel | SNT | Security audit, alerting |
| Worker | WKR | Task execution only |

### Access Tiers

| Tier | Permissions | Use Case |
|------|------------|----------|
| TIER1 | read, write, delete, admin | Production agents |
| TIER2 | read, write | Service accounts |
| TIER3 | read | Monitoring/audit |

### Sigil Types

| Type | Code | Expiry | Use Case |
|------|------|--------|----------|
| Sentinel | SNTNL | 90 days | Permanent agents |
| Service | SRVC | 30 days | Service accounts |
| Temporary | TEMP | 24 hours | One-time operations |

### Authentication Flow

```
1. Agent → Generate sigil with SigilAuthenticator
2. Agent → Include sigil in message.auth_sigil
3. Agent → Send message to Janus Bridge
4. Bridge → Extract sigil and agent_secret
5. Bridge → Validate HMAC signature
6. Bridge → Check tier permissions
7. Bridge → Check role capabilities
8. Bridge → Route message or reject
```

---

## 5. Directive Vocabulary

### Core Protocol Directives

#### INITIATE_NEURAL_LINK
- **Purpose**: Establish agent connection
- **Auth Required**: Yes (TIER1+)
- **Payload**:
  ```json
  {
    "status": "string",
    "capabilities": ["string"],
    "version": "string"
  }
  ```
- **Response**: Handshake acknowledgment

#### TERMINATE_LINK
- **Purpose**: Gracefully close connection
- **Auth Required**: Yes
- **Payload**: `{"reason": "string"}`
- **Response**: Shutdown confirmation

#### HEARTBEAT
- **Purpose**: Keep-alive signal
- **Auth Required**: Yes
- **Payload**: `{"timestamp": "ISO8601"}`
- **Response**: Ack with server timestamp

### Memory Operations

#### SYNC_MEMORY
- **Purpose**: Synchronize memory state
- **Auth Required**: Yes (STW role)
- **Payload**:
  ```json
  {
    "memory_data": {},
    "platforms": ["perplexity", "claude"],
    "priority": 5
  }
  ```

#### QUERY_MEMORY
- **Purpose**: Search memory stores
- **Auth Required**: Yes
- **Payload**: `{"query": "string", "limit": 10}`

#### UPDATE_MEMORY
- **Purpose**: Update memory entry
- **Auth Required**: Yes (TIER2+)
- **Payload**: `{"memory_id": "uuid", "data": {}}`

### GitHub Operations

#### GITHUB_QUERY
- **Purpose**: Query GitHub repositories
- **Auth Required**: Yes
- **Payload**: `{"query": "user:GlacierEQ", "limit": 100}`

#### GITHUB_UPDATE
- **Purpose**: Update repository
- **Auth Required**: Yes (TIER1)
- **Payload**: `{"repo": "owner/name", "action": "update", "data": {}}`

#### GITHUB_CREATE
- **Purpose**: Create repository resource
- **Auth Required**: Yes (TIER1)
- **Payload**: `{"repo": "owner/name", "resource_type": "issue", "data": {}}`

### Safety & Emergency

#### REQUEST_SANCTUARY_PROTOCOL
- **Purpose**: Activate safe mode
- **Auth Required**: Yes (TIER1)
- **Payload**: `{"reason": "string", "scope": "agent|system"}`
- **Response**: Safe mode status

#### EMERGENCY_SHUTDOWN
- **Purpose**: Emergency system halt
- **Auth Required**: Yes (JGN role only)
- **Payload**: `{"reason": "string", "countdown": 10}`

### Telemetry

#### TRANSMIT_TELEMETRY
- **Purpose**: Send agent metrics
- **Auth Required**: Optional
- **Payload**: `{"metrics": {}, "logs": []}`

#### QUERY_CAPABILITY
- **Purpose**: Request agent capabilities
- **Auth Required**: Optional
- **Payload**: `{}`
- **Response**: Capability manifest

---

## 6. Response Format

### Standard Response

```json
{
  "status": "success|error|pending",
  "message": "Human-readable description",
  "data": {
    "result": "..."
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid",
  "processing_time_ms": 123
}
```

### Status Codes

- `success`: Operation completed successfully
- `error`: Operation failed
- `pending`: Operation in progress (async)

### HTTP Status Mapping

| Status | HTTP Code | Meaning |
|--------|-----------|----------|
| success | 200 | OK |
| error | 400 | Bad Request |
| error | 401 | Unauthorized |
| error | 403 | Forbidden |
| error | 404 | Not Found |
| error | 500 | Internal Server Error |
| pending | 202 | Accepted (async) |

---

## 7. Error Handling

### Error Response

```json
{
  "status": "error",
  "error_code": "AUTH_FAILED",
  "message": "Authentication signature invalid",
  "details": {
    "sigil_format": "valid",
    "signature_match": false
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTH_FAILED` | Authentication failed | 401 |
| `INVALID_SIGIL` | Malformed sigil | 400 |
| `PERMISSION_DENIED` | Insufficient permissions | 403 |
| `INVALID_DIRECTIVE` | Unknown directive | 400 |
| `PAYLOAD_TOO_LARGE` | Payload exceeds limit | 413 |
| `RATE_LIMIT` | Too many requests | 429 |
| `AGENT_OFFLINE` | Target agent unavailable | 503 |
| `TIMEOUT` | Operation timed out | 504 |
| `INTERNAL_ERROR` | Server error | 500 |

---

## 8. Security

### Threat Model

**Protected Against**:
- Replay attacks (timestamp + correlation_id)
- Sigil forgery (HMAC signature)
- Unauthorized access (tier + role validation)
- Message tampering (signature verification)
- DoS attacks (rate limiting)

### Best Practices

1. **Rotate sigils every 90 days**
2. **Store agent secrets in secure vault**
3. **Use TLS in production**
4. **Monitor auth failures**
5. **Implement rate limiting**
6. **Log all security events**

---

## 9. Integration Points

### GitHub (790 Repos)
- **Adapter**: `GitHubAdapter`
- **Authentication**: GitHub PAT
- **Rate Limit**: 5000 req/hour
- **Capabilities**: Query, create, update, delete

### MemoryPlugin MCP
- **Adapter**: `MemoryPluginBridge`
- **Sync Platforms**: 16+ AI platforms
- **Capabilities**: Store, query, sync

### Perplexity AI
- **Context Injection**: Native memory
- **Global Context**: LFVBLPUL3N8N8K2FLYGCSCKMSMSRHSG9
- **Capabilities**: Context persistence

### Quantum Memory
- **Systems**: Mem0 + SuperMemory
- **Storage**: Vector embeddings
- **Capabilities**: Long-term retention, semantic search

---

## 10. Performance Requirements

### Latency Targets

- Message routing: < 10ms
- Auth validation: < 5ms
- End-to-end: < 100ms (p95)
- Database queries: < 50ms

### Throughput

- Messages/second: 1000+
- Concurrent agents: 100+
- Active connections: 500+

### Scalability

- Horizontal scaling: Stateless design
- Load balancing: Round-robin + health checks
- Caching: Redis for hot data

---

**Document Status**: Living specification  
**Contributors**: GlacierEQ  
**License**: MIT  
