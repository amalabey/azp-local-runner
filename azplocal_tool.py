import click
from app.application import run_pipeline
from app.application import validate_pipeline


@click.group()
def cli():
    pass


@cli.command()
@click.option('-o', '--org', type=str, required=True, help='Url to Azure DevOps organisation')
@click.option('-p', '--project', type=str, required=True, help='Project name in Azure DevOps')
@click.option('-t', '--token', type=str, required=True, help='Personal Access Token (PAT) to access Azure DevOps')
@click.option('-r', '--repo_path', type=str, required=True, help='Path to local repository clone')
@click.option('-f', '--file', type=str, required=True, help='Patht to yaml file relative to the repository')
@click.option('-i', '--id', type=str, required=True, help='Pipeline definitionId from the url to Pipeline')
def validate(org, project, token, repo_path, file, id):
    click.echo(f"Validating azure pipeline: {file}")
    validate_pipeline(org, project, id, token, repo_path, file)
    click.echo("Done")


@cli.command()
@click.option('-o', '--org', type=str, required=True, help='Url to Azure DevOps organisation')
@click.option('-p', '--project', type=str, required=True, help='Project name in Azure DevOps')
@click.option('-t', '--token', type=str, required=True, help='Personal Access Token (PAT) to access Azure DevOps')
@click.option('-r', '--repo_path', type=str, required=True, help='Path to local repository clone')
@click.option('-f', '--file', type=str, required=True, help='Patht to yaml file relative to the repository')
@click.option('-i', '--id', type=str, required=True, help='Pipeline definitionId from the url to Pipeline')
@click.option('-d', '--debug', is_flag=True, help='Pipeline definitionId from the url to Pipeline')
def run(org, project, token, repo_path, file, id, debug):
    click.echo(f"Running azure pipeline: {file} with debug={debug}")
    run_pipeline(org, project, id, token, repo_path, file, debug)
    click.echo("Done")
