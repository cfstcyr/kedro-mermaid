from typing import Protocol

import click

from kedro_mermaid.lib.graph import DiagramGraph


class DiagramOutputFunction(Protocol):
    def __call__(self, diagram_graph: DiagramGraph) -> None: ...


class DiagramEncodedOutputFunction(Protocol):
    def __call__(self, encoded_diagram: str) -> None: ...

def encoded_output(func: DiagramEncodedOutputFunction) -> DiagramOutputFunction:
    def wrapper(diagram_graph: DiagramGraph) -> None:
        diagram_str = diagram_graph.render()
        encoded_diagram = DiagramGraph.encode_diagram(diagram_str)
        func(encoded_diagram)
    return wrapper

def get_diagram(diagram_graph: DiagramGraph) -> None:
    diagram_str = diagram_graph.render()
    click.echo(diagram_str)

def get_encoded_diagram(encoded_diagram: str) -> None:
    click.echo(encoded_diagram)

def get_image_url(encoded_diagram: str, *, url: str = "https://mermaid.ink/img/{encoded_diagram}") -> None:
    click.echo(url.format(encoded_diagram=encoded_diagram))

def get_edit_url(encoded_diagram: str, *, url: str = "https://mermaid.live/edit#pako:{encoded_diagram}") -> None:
    click.echo(url.format(encoded_diagram=encoded_diagram))

def get_view_url(encoded_diagram: str, *, url: str = "https://mermaid.live/view#pako:{encoded_diagram}") -> None:
    click.echo(url.format(encoded_diagram=encoded_diagram))

DIAGRAM_OUTPUTS: dict[str, DiagramOutputFunction] = {
    "diagram": get_diagram,
    "encoded": encoded_output(get_encoded_diagram),
    "image_url": encoded_output(get_image_url),
    "edit_url": encoded_output(get_edit_url),
    "view_url": encoded_output(get_view_url),
}
