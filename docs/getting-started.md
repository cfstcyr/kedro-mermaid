# Getting Started

This guide walks you through installing `kedro-mermaid`, validating the setup, and generating your first Mermaid diagram.

## Prerequisites
- A Kedro project with pipelines registered in `register_pipelines`.
- Python 3.9 or later.
- Kedro 0.19.8+ (Kedro 1.x projects are supported as well).

## Installation
Install the plugin in the same environment as your Kedro project:

```bash
pip install kedro-mermaid
```

The installation registers a new `kedro mermaid` command group that becomes available once the environment is activated.

## Verify the CLI Entry Point
From your Kedro project directory run:

```bash
kedro mermaid --help
```

You should see the plugin-specific commands. If the command is missing, double-check that the environment is activated and that Kedro can discover entry points (`pip list | grep kedro-mermaid`).

## Generate Your First Diagram
With the project environment active:

```bash
kedro mermaid generate
```

The command prints:

1. Mermaid markup (for example, a `flowchart LR` block).
2. A `mermaidchart.com` link that opens the same diagram in the live editor.

Paste the markup into Markdown, Confluence, Notion, or any tool that understands Mermaid. The shareable link is perfect for lightweight collaboration or presenting a live diagram during reviews.

## Next Steps
- Use the filtering flags to focus on a subset of the pipeline: see [Filter the diagram](how-to/filter-the-diagram.md).
- Adjust the diagram orientation, layout, or colours with [`--set-graph-attr` and friends](how-to/customise-the-diagram.md).
