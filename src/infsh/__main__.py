import sys
import click
from .cli import create_app, login, predeploy, deploy

@click.group()
def cli():
    """inference.sh CLI tool"""
    pass

@cli.command(name="create")
def create_cmd():
    """Create a new inference.sh application"""
    create_app()

@cli.command(name="login")
def login_cmd():
    """Login to inference.sh"""
    login()

@cli.command(name="predeploy")
def predeploy_cmd():
    """Run predeploy checks and generate OpenAPI schema"""
    predeploy()

@cli.command(name="deploy")
def deploy_cmd():
    """Deploy the app to inference.sh"""
    deploy()

if __name__ == "__main__":
    cli()