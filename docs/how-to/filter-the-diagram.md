# Filter the Diagram

`kedro-mermaid` lets you focus diagrams on the slices of the pipeline that matter. All filters stack, so you can combine datasets, nodes, namespaces, and tags to tighten the view.

## Target a Specific Pipeline
Pass the pipeline name with `--pipeline` (defaults to `__default__`):

```bash
kedro mermaid generate --pipeline=data_science
```

If the name is invalid the command reports the list of registered pipelines so you can pick the right one.

## Trim by Datasets
Use `--from-inputs` and `--to-outputs` to cut the diagram around datasets:

```bash
kedro mermaid generate --from-inputs=raw_customers,raw_products --to-outputs=model_predictions
```

- `--from-inputs` keeps only paths reachable from the listed datasets.
- `--to-outputs` keeps only paths that lead to the listed outputs.

## Trim by Nodes
When you need to focus on specific Kedro nodes, you have three options:

```bash
kedro mermaid generate \
  --from-nodes=data_preprocessing.clean_customers \
  --to-nodes=model_training.train_model \
  --nodes=model_training.evaluate_model
```

- `--from-nodes` starts traversal from selected nodes.
- `--to-nodes` stops traversal when a listed node is reached.
- `--nodes` only includes the nodes you list, collapsing edges through any missing nodes.

## Filter by Tags or Namespaces
Kedro metadata can scope the diagram too:

```bash
kedro mermaid generate --tags=model,reporting
kedro mermaid generate --namespaces=data_science.pipelines
```

- `--tags` keeps nodes that carry the specified Kedro tags.
- `--namespaces` keeps nodes inside selected namespaces. On Kedro 0.x projects the plugin transparently falls back to the legacy `node_namespace` argument.

## Filter by Regex Pattern
Regex parsing acts as another filter layer via `--set-node-attr pattern=<regex>`:

```bash
kedro mermaid generate \
  --set-node-attr pattern="(?P<category>\w+)__(?P<node>\w+)__?(?P<node>\w+)?"
```

When the pattern matches a node name:

- Named captures labelled `node` (or numbered groups) populate the node label. Multiple captures are joined with spaces and capitalised.
- A named capture labelled `category` groups nodes into a subgraph. Each category appears as a coloured box with autoregistered styling.

Nodes that do **not** match the pattern are hidden from the final diagram, but the graph traverser still uses them to maintain continuity between any nodes that stay visible. Skip the pattern or make it permissive if you want every node to remain.

### Understand Simplification
After category and pattern parsing, the plugin simplifies the graph:

1. Nodes that fail filters (including regex patterns) are removed.
2. Direct paths are re-linked so you never see dangling intermediates when focusing on a subset.
3. Self-loops are dropped automatically.

A simple example: `A -> B -> C` becomes `A -> C` when only `A` and `C` match the filters.

You can inspect the simplified edges by checking the output markup or sending it to a file:

```bash
kedro mermaid generate > pipeline.mmd
```

From there, open the file in the Mermaid Live Editor or embed it in your docs pipeline.

## Combine Filters
Filters combine, so you can stack criteria:

```bash
kedro mermaid generate \
  --pipeline=pipelines.data_science \
  --from-inputs=raw_transactions \
  --to-outputs=reporting.kpis \
  --tags=reporting
```

The command above follows the reporting path within the `data_science` pipeline, starting from the raw transactions dataset, ending at the KPI report, and keeping only reporting-tagged nodes.

When an overly strict combination yields an empty result, `kedro-mermaid` prints a simplified diagram with no edges. Loosen the filters until the desired section appears.
