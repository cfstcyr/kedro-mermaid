from typing import cast

import click
import kedro
from kedro.framework.project import pipelines
from kedro.framework.startup import ProjectMetadata
from kedro.pipeline import Pipeline
from omegaconf import OmegaConf
from packaging import version

from kedro_mermaid.lib.diagram_output import DIAGRAM_OUTPUTS
from kedro_mermaid.lib.graph import DiagramGraph
from kedro_mermaid.lib.utils import parse_list


@click.command()
@click.option(
    "-p",
    "--pipeline",
    "pipeline_name",
    default="__default__",
    help="Name of the registered pipeline. If not set, the `__default__` pipeline is used.",
)
@click.option(
    "--from-inputs",
    help="A list of dataset names which should be used as a starting point.",
    callback=parse_list,
)
@click.option(
    "--to-outputs",
    help="A list of dataset names which should be used as ending points.",
    callback=parse_list,
)
@click.option(
    "--from-nodes",
    help="A list of node names which should be used as a starting point.",
    callback=parse_list,
)
@click.option(
    "--to-nodes",
    help="A list of node names which should be used as ending points.",
    callback=parse_list,
)
@click.option(
    "-n",
    "--nodes",
    help="Include only nodes with specified names.",
    callback=parse_list,
)
@click.option(
    "-t",
    "--tags",
    help="Include only nodes with specified tags.",
    callback=parse_list,
)
@click.option(
    "-ns",
    "--namespaces",
    help="Include only nodes within specified namespaces.",
    callback=parse_list,
)
@click.option(
    "--set-graph-attr",
    "graph_attrs",
    multiple=True,
    help='Set graph attributes. Can be used multiple times. Example: --set-graph-attr "declaration=flowchart LR" --set-graph-attr config.theme=dark',
)
@click.option(
    "--set-edge-attr",
    "edge_attrs",
    multiple=True,
    help=(
        "Set edge attributes. Supported keys are params.arrow and params.label, "
        "for example --set-edge-attr params.arrow='---' --set-edge-attr params.label='Batch'."
    ),
)
@click.option(
    "--set-node-attr",
    "node_attrs",
    multiple=True,
    help="Set node attributes. Use 'pattern=' to control regex parsing, e.g. --set-node-attr pattern='(?P<category>\\w+)__(?P<node>\\w+)'.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(list(DIAGRAM_OUTPUTS.keys()), case_sensitive=False),
    default="diagram",
    help="Output format. Currently only 'mermaid' is supported.",
)
@click.pass_obj
def generate(
    metadata: ProjectMetadata,
    pipeline_name: str,
    from_inputs: list[str] | None,
    to_outputs: list[str] | None,
    from_nodes: list[str] | None,
    to_nodes: list[str] | None,
    nodes: list[str] | None,
    tags: list[str] | None,
    namespaces: str | None,
    graph_attrs: list[str],
    edge_attrs: list[str],
    node_attrs: list[str],
    output_format: str,
):
    pipeline = cast(Pipeline | None, pipelines.get(pipeline_name))

    if not pipeline:
        raise ValueError(
            f"Pipeline '{pipeline_name}' not found. Available pipelines: {list(pipelines.keys())}"
        )

    filter_args = {
        "tags": tags,
        "from_nodes": from_nodes,
        "to_nodes": to_nodes,
        "node_names": nodes,
        "from_inputs": from_inputs,
        "to_outputs": to_outputs,
        "node_namespaces": namespaces,
    }

    if version.parse(kedro.__version__) < version.parse("1.0.0"):
        # Handle the older API where 'node_namespaces' is named 'node_namespace'
        filter_args["node_namespace"] = filter_args.pop("node_namespaces")

    pipeline = pipeline.filter(**filter_args)

    graph = DiagramGraph.from_pipeline(
        pipeline,
        attrs=OmegaConf.from_dotlist(graph_attrs),
        edge_attrs=OmegaConf.from_dotlist(edge_attrs),
        node_attrs=OmegaConf.from_dotlist(node_attrs),
    ).simplify()

    DIAGRAM_OUTPUTS[output_format](graph)
