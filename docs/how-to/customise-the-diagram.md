# Customise the Diagram

`kedro-mermaid` exposes three families of attributes that map directly onto Mermaid configuration:

- `--set-graph-attr` changes top-level diagram behaviour (orientation, layout engine, config block).
- `--set-node-attr` influences how nodes are parsed and rendered.
- `--set-edge-attr` tweaks edge appearance.

Each option accepts repeated `key=value` pairs. Under the hood the plugin feeds these into `omegaconf.OmegaConf.from_dotlist`, so dotted keys create nested maps (for example `config.layout=elk`).

## Change the Diagram Declaration
Override the declaration to switch orientation or pick another Mermaid diagram type:

```bash
kedro mermaid generate --set-graph-attr declaration="flowchart TB"
```

Common values:

- `flowchart LR` (default) – left-to-right layout.
- `flowchart TB` – top-to-bottom layout.
- `graph LR` – Mermaid graph syntax if you prefer the legacy style.

## Apply Mermaid Config
You can pass Mermaid's global config values through the `config` attribute. Because the plugin emits front matter, the editor loads the config automatically.

```bash
kedro mermaid generate --set-graph-attr config.layout=elk
```

The command above enables the ELK layout engine, which can produce clearer diagrams for dense pipelines.

## Control Edge Arrows and Labels
Edge-level attributes let you tweak the arrow glyph and optional label that appear on every rendered connection:

```bash
kedro mermaid generate \
  --set-edge-attr params.arrow='---' \
  --set-edge-attr params.label='Batch'
```

Only the `params.arrow` and `params.label` keys are supported. Arrow values must use Mermaid's standard edge syntax (for example `-->`, `---`), and labels appear inline on every edge.

## Group nodes into Subgraphs
Node attributes support a `pattern` (any Python regex) so you can split node names into categories and labels using named capture groups. Use the `category` capture for the subgraph label and one or more `node` captures for the node label.

```bash
kedro mermaid generate \
  --set-node-attr pattern="(?P<category>\w+)__(?P<node>\w+)__?(?P<node>\w+)?"
```

For more information about the "pattern" attribute, see the [Filter the Diagram](filter-the-diagram.md/#filter-by-regex-pattern) guide.
