#!/usr/bin/env python3
"""Neural Link CLI - Command-line orchestration tool."""

import click
import json
import yaml
import requests
from pathlib import Path
from typing import Optional
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.auth import SigilAuthenticator
from src.core.protocol import NeuralMessage


class NeuralLinkCLI:
    """CLI orchestrator for Neural Link Protocol."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/agents.yaml"
        self.config = self._load_config()
        self.authenticator = SigilAuthenticator()
        self.bridge_url = "http://localhost:8000"
    
    def _load_config(self) -> dict:
        """Load agent configuration."""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file) as f:
                return yaml.safe_load(f)
        return {"agents": {}}
    
    def send_message(self, agent_id: str, directive: str, payload: dict) -> dict:
        """Send message to Janus Bridge."""
        agent_config = self.config['agents'].get(agent_id.lower().replace('-', '_'))
        if not agent_config:
            return {"error": f"Agent {agent_id} not found in config"}
        
        # Generate auth sigil (in production, load from secure vault)
        agent_secret = os.getenv(f"{agent_id.upper()}_SECRET", "dev_secret_key")
        sigil = self.authenticator.generate_sigil(
            agent_id=agent_id,
            agent_secret=agent_secret
        )
        
        message = NeuralMessage(
            agent_id=agent_id,
            auth_sigil=sigil,
            directive=directive,
            payload=payload
        )
        
        try:
            response = requests.post(
                f"{self.bridge_url}/invoke",
                json=message.to_dict(),
                timeout=30
            )
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


@click.group()
@click.option('--config', '-c', default="config/agents.yaml", help="Config file path")
@click.pass_context
def cli(ctx, config):
    """Neural Link Protocol CLI - Orchestrate your agent fleet."""
    ctx.obj = NeuralLinkCLI(config)


@cli.command()
@click.argument('agent_id')
@click.argument('directive')
@click.option('--payload', '-p', default='{}', help="JSON payload")
@click.pass_obj
def send(cli_obj, agent_id, directive, payload):
    """Send a message to an agent.
    
    Example:
        neural-link send Microwave-Juggernaut INITIATE_NEURAL_LINK -p '{"status":"ready"}'
    """
    try:
        payload_dict = json.loads(payload)
        result = cli_obj.send_message(agent_id, directive, payload_dict)
        click.echo(json.dumps(result, indent=2))
    except json.JSONDecodeError:
        click.echo("Error: Invalid JSON payload", err=True)
        sys.exit(1)


@cli.command()
@click.pass_obj
def agents(cli_obj):
    """List all registered agents."""
    try:
        response = requests.get(f"{cli_obj.bridge_url}/agents/discover")
        data = response.json()
        
        if data.get('status') == 'success':
            click.echo(f"\nRegistered Agents ({data['count']}):")
            click.echo("=" * 60)
            for agent in data['agents']:
                click.echo(f"\n🤖 {agent['agent_id']}")
                click.echo(f"   Capabilities: {', '.join(agent['capabilities'])}")
                click.echo(f"   Connected: {agent['connected_at']}")
                click.echo(f"   Last Heartbeat: {agent['last_heartbeat']}")
        else:
            click.echo("No agents registered")
    except requests.RequestException as e:
        click.echo(f"Error connecting to bridge: {e}", err=True)


@cli.command()
@click.pass_obj
def health(cli_obj):
    """Check Janus Bridge health."""
    try:
        response = requests.get(f"{cli_obj.bridge_url}/health")
        data = response.json()
        
        status_emoji = "✅" if data['status'] == 'healthy' else "❌"
        click.echo(f"\n{status_emoji} Bridge Status: {data['status'].upper()}")
        click.echo(f"   Active Agents: {data['active_agents']}")
        click.echo(f"   WebSocket Connections: {data['active_websockets']}")
        click.echo(f"   Timestamp: {data['timestamp']}")
    except requests.RequestException as e:
        click.echo(f"❌ Bridge offline: {e}", err=True)


@cli.command()
@click.pass_obj
def metrics(cli_obj):
    """Display Prometheus metrics."""
    try:
        response = requests.get(f"{cli_obj.bridge_url}/metrics")
        click.echo("\n📊 Neural Link Metrics:")
        click.echo("=" * 60)
        click.echo(response.text)
    except requests.RequestException as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--org', default='GlacierEQ', help='GitHub organization')
@click.option('--limit', default=10, help='Number of repos to show')
def repos(org, limit):
    """List GitHub repositories."""
    try:
        response = requests.get(
            f"https://api.github.com/users/{org}/repos",
            params={'per_page': limit, 'sort': 'updated'}
        )
        repos = response.json()
        
        click.echo(f"\n📋 {org} Repositories (Top {limit}):")
        click.echo("=" * 60)
        for repo in repos:
            click.echo(f"\n📦 {repo['name']}")
            click.echo(f"   ⭐ {repo['stargazers_count']} | 👁️ {repo['watchers_count']} | 🔧 {repo['language']}")
            click.echo(f"   {repo['description'] or 'No description'}")
            click.echo(f"   {repo['html_url']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('agent_id')
@click.option('--tier', default='TIER1', help='Access tier')
@click.option('--role', default='JGN', help='Agent role')
@click.option('--type', 'sigil_type', default='SNTNL', help='Sigil type')
def generate_sigil(agent_id, tier, role, sigil_type):
    """Generate authentication sigil for an agent.
    
    Example:
        neural-link generate-sigil Microwave-Juggernaut --tier TIER1 --role JGN
    """
    authenticator = SigilAuthenticator()
    agent_secret = os.getenv(f"{agent_id.upper().replace('-', '_')}_SECRET", "dev_secret_key")
    
    sigil = authenticator.generate_sigil(
        agent_id=agent_id,
        agent_secret=agent_secret,
        tier=tier,
        role=role,
        sigil_type=sigil_type
    )
    
    click.echo(f"\n🔐 Generated Sigil for {agent_id}:")
    click.echo("=" * 60)
    click.echo(sigil)
    click.echo("\n⚠️  Store securely! Never commit to version control.")


@cli.command()
@click.argument('directive')
@click.option('--description', '-d', required=True, help='Directive description')
@click.option('--tier', default='TIER2', help='Required access tier')
def add_directive(directive, description, tier):
    """Add a new directive to the registry.
    
    Example:
        neural-link add-directive DEPLOY_SERVICE -d "Deploy a microservice" --tier TIER1
    """
    click.echo(f"\n➕ Adding directive: {directive}")
    click.echo(f"   Description: {description}")
    click.echo(f"   Required Tier: {tier}")
    click.echo("\n✅ Directive would be added to DirectiveRegistry (implement persistence)")


if __name__ == '__main__':
    cli()
