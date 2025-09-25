import logging

import click
from kedro.framework.startup import ProjectMetadata

from kedro_mermaid import cli
from kedro_mermaid.lib.utils import silence_kedro_logs

logger = logging.getLogger(__name__)


@click.group(name="kedro-mermaid")
def commands():
    pass


@commands.group(name="mermaid")
@click.pass_obj
def mermaid_commands(metadata: ProjectMetadata):
    silence_kedro_logs()
    logger.debug("kedro-mermaid using project `%s`", metadata.project_name)


mermaid_commands.add_command(cli.generate)
