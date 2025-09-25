# Architecture Overview

The plugin is intentionally lightweight. It integrates with Kedro's CLI, converts a pipeline into a simplified dependency graph, and renders Mermaid markup. Understanding the moving parts makes customisation and contributions easier.

## Entry Points
- `kedro_mermaid.plugin.commands` defines the root `kedro mermaid` command group. Kedro discovers it via the `kedro.hooks` entry point and provides `ProjectMetadata` for logging and context.
- `kedro_mermaid.cli.generate.generate` implements the `kedro mermaid generate` command. It parses CLI flags, looks up the requested pipeline, and applies Kedro's filtering API (`Pipeline.filter`).

## Graph Construction
`kedro_mermaid.lib.graph.DiagramGraph` performs the heavy lifting:

1. **Collect edges** – Every Kedro node becomes an edge between each input dataset and output dataset (`DiagramEdge`). Self-loops are discarded (`input != output`).
2. **Parse names** – Nodes are wrapped in `DiagramNode`, which consults `ParsedName` to apply regex patterns from `--set-node-attr pattern=...`.
3. **Simplify** – After filters remove nodes, `DiagramGraph.simplify` reconnects surviving nodes so the diagram remains readable. It traverses from each included node to the next reachable included node, skipping hidden intermediates.
4. **Group categories** – When `ParsedName` emits a category, the renderer surrounds the grouped nodes with a subgraph and auto-generates colour accents.
5. **Render** – `DiagramGraph.render` emits Markdown-friendly Mermaid blocks. Optional Mermaid config is written as YAML front matter, which Mermaid Live Editor understands out of the box.

## Name Parsing
`kedro_mermaid.lib.parsed_name.ParsedName` centralises regex handling.

- Named capture groups labelled `category` create subgraphs.
- Named (or numbered) groups labelled `node` form the rendered node label.
- If the regex does not match, the node remains in the graph with its original name but is flagged as `is_match=False` so simplification can skip it when requested.

The implementation relies on the third-party [`regex`](https://pypi.org/project/regex/) module so advanced features like repeated named groups (`(?P<node>...)`) are available.

## Utilities
- `kedro_mermaid.lib.utils.parse_list` converts comma-separated CLI options into Python lists (`click` uses it as a callback on list-like options).
- Tests in `tests/kedro_mermaid/lib/test_parsed_name.py` cover the name parsing behaviour to guarantee backwards compatibility when upgrading the regex logic.

Understanding the structure above should give you enough confidence to extend the CLI, add new filters, or alter the rendering step.
