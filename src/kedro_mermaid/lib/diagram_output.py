from pathlib import Path
from typing import Protocol

import click

from kedro_mermaid.contants import EDIT_URL, IMAGE_URL, VIEW_URL
from kedro_mermaid.lib.graph import DiagramGraph


class DiagramOutputFunction(Protocol):
    def __call__(self, diagram_graph: DiagramGraph, **kwargs) -> None: ...


class DiagramEncodedOutputFunction(Protocol):
    def __call__(self, encoded_diagram: str, **kwargs) -> None: ...


def encoded_output(func: DiagramEncodedOutputFunction) -> DiagramOutputFunction:
    def wrapper(diagram_graph: DiagramGraph, **kwargs) -> None:
        diagram_str = diagram_graph.render()
        encoded_diagram = DiagramGraph.encode_diagram(diagram_str)
        func(encoded_diagram, **kwargs)

    return wrapper


def get_diagram(diagram_graph: DiagramGraph) -> None:
    diagram_str = diagram_graph.render()
    click.echo(diagram_str)


def get_encoded_diagram(encoded_diagram: str) -> None:
    click.echo(encoded_diagram)


def get_image_url(encoded_diagram: str, *, url: str = IMAGE_URL) -> None:
    click.echo(url.format(diagram=encoded_diagram))


def get_edit_url(encoded_diagram: str, *, url: str = EDIT_URL) -> None:
    click.echo(url.format(diagram=encoded_diagram))


def get_view_url(encoded_diagram: str, *, url: str = VIEW_URL) -> None:
    click.echo(url.format(diagram=encoded_diagram))


def insert_to_file(
    diagram_graph: DiagramGraph,
    *,
    file_path: str,
    template: str = "{marker_start}\n```mermaid\n{diagram}\n```\nView the diagram on [Mermaid]({view_url}) ([edit on Mermaid]({edit_url}), [view as an image]({image_url}))\n{marker_end}",
    marker: str = "kedro-mermaid",
    marker_start_format: str = "<!-- DIAGRAM:START:{marker} -->",
    marker_end_format: str = "<!-- DIAGRAM:END:{marker} -->",
) -> None:
    marker_start = marker_start_format.format(marker=marker)
    marker_end = marker_end_format.format(marker=marker)

    result = template.format(
        marker_start=marker_start,
        marker_end=marker_end,
        diagram=diagram_graph.render(),
        edit_url=EDIT_URL.format(
            diagram=DiagramGraph.encode_diagram(diagram_graph.render())
        ),
        view_url=VIEW_URL.format(
            diagram=DiagramGraph.encode_diagram(diagram_graph.render())
        ),
        image_url=IMAGE_URL.format(
            diagram=DiagramGraph.encode_diagram(diagram_graph.render())
        ),
    )

    file = Path(file_path)

    with file.open("r") as f:
        content = f.read()

        if marker_start not in content or marker_end not in content:
            raise ValueError(
                f"Markers '{marker_start}' and '{marker_end}' not found in file '{file_path}'."
            )

        if result in content:
            click.echo(
                f"Diagram already up to date in file '{file_path}'. No changes made."
            )
            return

        pre_content = content.split(marker_start)[0]
        post_content = content.split(marker_end)[-1]

    with Path.open(file, "w") as f:
        f.write(pre_content)
        f.write(result)
        f.write(post_content)

    click.echo(f"Diagram inserted into file '{file_path}'.")


DIAGRAM_OUTPUTS = {
    "diagram": get_diagram,
    "encoded": encoded_output(get_encoded_diagram),
    "image_url": encoded_output(get_image_url),
    "edit_url": encoded_output(get_edit_url),
    "view_url": encoded_output(get_view_url),
    "insert_to_file": insert_to_file,
}
