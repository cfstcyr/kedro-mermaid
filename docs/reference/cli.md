# CLI Reference

`kedro-mermaid` extends the Kedro CLI with a `mermaid` command group. Each command accepts standard Kedro options (`--config`, `--env`, and so on) alongside the plugin-specific flags documented below.

## `kedro mermaid generate`
Render the selected pipeline as Mermaid markup and print a shareable `mermaidchart.com` link.

| Option | Description |
| --- | --- |
| `-p, --pipeline <name>` | Name of the registered pipeline to render. Defaults to `__default__`. Missing names raise an error with the list of available pipelines. |
| `--from-inputs <list>` | Comma-separated dataset names to use as starting points. |
| `--to-outputs <list>` | Comma-separated dataset names to use as ending points. |
| `--from-nodes <list>` | Comma-separated node names to use as starting points. |
| `--to-nodes <list>` | Comma-separated node names to use as ending points. |
| `-n, --nodes <list>` | Only include nodes with the specified names. |
| `-t, --tags <list>` | Only include nodes that have the specified Kedro tags. |
| `-ns, --namespaces <list>` | Only include nodes in the listed namespaces. Accepts a comma-separated list. On Kedro 0.x the option maps to the legacy `node_namespace` filter. |
| `--set-graph-attr <key=value>` | Set diagram-level attributes. Repeatable. Supports dot notation (e.g. `config.layout=elk`). |
| `--set-edge-attr <key=value>` | Set edge attributes. Supported keys: `params.arrow` and `params.label`. Repeatable. |
| `--set-node-attr <key=value>` | Set node attributes. Use `pattern=<regex>` to control regex parsing. Repeatable. |

### Output
- Mermaid definition, starting with the configured declaration (`flowchart LR` by default). When a `config.*` attribute is supplied the command injects YAML front matter so Mermaid Live Editor understands the configuration.
- Encoded `https://www.mermaidchart.com/play` link that opens the diagram online.

### Error Handling
- Unknown pipeline names raise a `ValueError` listing the registered pipelines.
- Kedro 0.x projects automatically fall back to the legacy filter argument names, so no manual version detection is required.

## Exit Codes
- `0` – Diagram generated successfully (even if empty after filters).
- Non-zero – Raised errors (for example, `ValueError` for a missing pipeline).

## Tips
- Pipe the output to a file (`kedro mermaid generate > dag.mmd`) to store the markup alongside reports.
- Combine with `jq` or other shell tools if you want to post-process the generated link.
- Keep your filters inclusive: when no nodes survive, the `flowchart` block renders without edges, signalling that the filter set might be too narrow.
