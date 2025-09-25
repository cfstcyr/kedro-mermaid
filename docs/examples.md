# Examples

## Basic usage

```bash
kedro mermaid generate
```

## Full example

```bash
kedro mermaid generate \
    --from-inputs=raw_data \          # Start from the `raw_data` dataset
    --to-outputs=report \             # End at the `report` dataset
    --nodes=clean_data,train_model,report_results \  # Include only these nodes
    --tags=model,reporting \          # Include only nodes tagged with `model` or `reporting`
    --namespaces=data,model \         # Include only nodes in the `data` or `model` namespaces
    --pipeline=data_science \         # Target the `data_science` pipeline
    --set-node-attr pattern="(?P<category>\w+)__(?P<node>\w+)" \  # Group nodes by prefix before `__`
    --set-node-attr params.shape=circle \  # Change node shape to circles
    --set-graph-attr declaration="flowchart TB" \  # Change layout to top-to-bottom
    --set-graph-attr config.layout=elk \  # Use the ELK layout engine
    --set-edge-attr params.arrow='---'  # Change edge arrows to dashed lines
```

## Filter the diagram

### Based on datasets, nodes, tags, or namespaces

```bash
kedro mermaid generate \
    --tags=model,reporting \
    --from-inputs=raw_data \
    --pipeline=data_science
```

### Only show the nodes in a specific format

For instance, if your nodes are named like `data__load_data`, `data__clean_data`, `model__train_model`, and `model__evaluate_model`, you can use:

```bash
kedro mermaid generate --set-node-attr pattern="(?P<category>\w+)__(?P<node>\w+)"
```

This will group nodes into subgraphs based on the `category` prefix and label them with the `node_name`:

- `data__load_data`: appears in the `data` subgraph with the label `Load Data`
- `data__clean_data`: appears in the `data` subgraph with the label `Clean Data`
- `model__train_model`: appears in the `model` subgraph with the label `Train Model`
- `model__evaluate_model`: appears in the `model` subgraph with the label `Evaluate Model`

### Limit the granularity of the diagram

If your nodes are named with an indicative pattern, such as `level1.level2.level3.level4`, you can create a regex pattern to capture only the top-level namespace:

```bash
kedro mermaid generate --set-node-attr pattern="(?P<category>[^.]+)(?:[.](?P<node>[^.]+)){2}"
```

**Breakdown of the regex:**
- `(?P<category>[^.]+)`: Captures the first segment before the first dot as the `category`.
- `(?:[.](?P<node>[^.]+)){2}`: Non-capturing group that matches a dot followed by a segment, repeated twice to capture the next two segments as `node`.

This pattern will group nodes into subgraphs based on the top-level namespace and label them with the next two segments, effectively reducing the diagram's complexity while retaining meaningful structure. For example:
- `data.load.clean.transform`: appears in the `data` subgraph with the label `Load Clean`
    - `data.load.clean.aggregate`: Will be merged with `data.load.clean.transform` as they share the same category and node labels.
- `model.train.evaluate.report`: appears in the `model` subgraph with the label `Train Evaluate`

## Style the diagram

### Change the layout

```bash
kedro mermaid generate --set-graph-attr declaration="flowchart TB"
```

### Use the ELK layout engine

```bash
kedro mermaid generate --set-graph-attr config.layout=elk
```
