import base64
import json
import logging
import zlib
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from typing import cast

import yaml
from kedro.pipeline import Pipeline
from omegaconf import DictConfig, OmegaConf

from kedro_mermaid.lib.parsed_name import ParsedName, ParsedValue

logger = logging.getLogger(__name__)

@dataclass
class DiagramNode:
    name: str
    pattern: str | None = None
    params: dict = field(default_factory=dict)

    @cached_property
    def id(self) -> str:
        if self.parsed_name.category:
            return f"{self.parsed_name.category.id}__{self.parsed_name.name.id}"
        return self.parsed_name.name.id

    @cached_property
    def parsed_name(self) -> ParsedName:
        return ParsedName.parse_name(self.name, self.pattern)

    def should_include(self) -> bool:
        return self.parsed_name.is_match
    
    def to_mermaid_declaration(self) -> str:
        return f"{self.id}@{json.dumps({ **self.params, 'label': self.parsed_name.name.label })}"

    def __lt__(self, other) -> bool:
        if not isinstance(other, DiagramNode):
            return NotImplemented
        return self.id < other.id

    def __eq__(self, other) -> bool:
        if not isinstance(other, DiagramNode):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class DiagramEdge:
    source: DiagramNode
    target: DiagramNode
    params: dict = field(default_factory=dict)

    def to_mermaid_declaration(self, index: int) -> list[str]:
        params = self.params.copy()

        edge_id = f"e{index}"
        arrow = params.pop("arrow", "-->")
        label = params.pop("label", None)

        if label:
            arrow = f"{arrow}|\"{label}\"|"

        lines = [f"{self.source.id} {edge_id}@{arrow} {self.target.id}"]

        if params:
            lines.append(f"{edge_id}@{json.dumps(params)}")

        return lines

    def __lt__(self, other) -> bool:
        if not isinstance(other, DiagramEdge):
            return NotImplemented
        return self.source < other.source if self.source != other.source else self.target < other.target


@dataclass
class DiagramGraph:
    edges: list[DiagramEdge]
    attrs: dict = field(repr=False)
    edge_attrs: dict = field(repr=False)
    node_attrs: dict = field(repr=False)
    declaration: str = "flowchart LR"
    config: dict | None = None
    colors: list[tuple[str, str]] = field(
        default_factory=lambda: [
            ("#FFE0B2", "#FFF3E0"),
            ("#C8E6C9", "#E8F5E8"),
            ("#BBDEFB", "#E3F2FD"),
            ("#E1BEE7", "#F3E5F5"),
            ("#FFF9C4", "#FFFDE7"),
            ("#FFCDD2", "#FFEBEE"),
        ]
    )

    @classmethod
    def from_pipeline(
        cls,
        pipeline: Pipeline,
        attrs: DictConfig,
        edge_attrs: DictConfig,
        node_attrs: DictConfig,
    ) -> "DiagramGraph":
        attrs_dict = cast(dict, OmegaConf.to_container(attrs, resolve=True))
        edge_attrs_dict = cast(dict, OmegaConf.to_container(edge_attrs, resolve=True))
        node_attrs_dict = cast(dict, OmegaConf.to_container(node_attrs, resolve=True))

        return cls(
            edges=[
                DiagramEdge(
                    source=DiagramNode(
                        name=input_name,
                        **node_attrs_dict,
                    ),
                    target=DiagramNode(
                        name=output_name,
                        **node_attrs_dict,
                    ),
                    **edge_attrs_dict,
                )
                for node in pipeline.nodes
                for input_name in node.inputs
                for output_name in node.outputs
                if input_name != output_name
            ],
            attrs=attrs_dict,
            edge_attrs=edge_attrs_dict,
            node_attrs=node_attrs_dict,
            **attrs_dict,
        )

    @classmethod
    def encode_diagram(cls, diagram_str: str) -> str:
        return base64.urlsafe_b64encode(
            zlib.compress(
                json.dumps(
                    {
                        "code": diagram_str,
                    }
                ).encode("ascii"),
                level=9,
            )
        ).decode("ascii")
    
    def all_nodes(self) -> set[DiagramNode]:
        nodes = set()
        for edge in self.edges:
            nodes.add(edge.source)
            nodes.add(edge.target)
        return nodes
    
    def _collect_sources(self) -> dict[str, list[DiagramNode]]:
        sources = defaultdict(list)
        for edge in self.edges:
            sources[edge.source.id].append(edge.target)
        return sources
    
    def _collect_categories(self) -> dict[ParsedValue, list[DiagramNode]]:
        categories = defaultdict(list)
        for node in self.all_nodes():
            if node.parsed_name.category:
                categories[node.parsed_name.category].append(node)
        return categories
    
    def _find_immediate_final_nodes(
        self,
        current: DiagramNode,
        sources: dict[str, list[DiagramNode]],
        visited: set[str],
        *,
        is_start: bool = True,
    ) -> set[DiagramNode]:
        """
        Find the immediate final nodes reachable from the current node.
        Stops exploring once a final node is found (no transitive connections).

        Args:
            current: The current node being explored
            graph: The adjacency list representation of the graph
            visited: Set of already visited node IDs
            is_start: Whether this is the starting node of the search

        Returns:
            Set of immediately reachable final nodes
        """
        reachable = set()
        if current.id in visited:
            return reachable
        visited.add(current.id)

        # If this is a final node and not the starting node, add it and STOP exploring
        if current.should_include() and not is_start:
            reachable.add(current)
            return reachable  # Stop here - don't explore further

        # Continue exploring neighbors only if current node is not final (or is the start)
        for neighbor in sources.get(current.id, []):
            reachable.update(
                self._find_immediate_final_nodes(
                    neighbor, sources, visited.copy(), is_start=False
                )
            )

        return reachable
    
    def simplify(self) -> "DiagramGraph":
        sources = self._collect_sources()

        included_nodes: list[DiagramNode] = []
        included_nodes_names: set[str] = set()

        for edge in self.edges:
            if edge.source.id in included_nodes_names:
                continue
            if not edge.source.should_include():
                continue

            included_nodes.append(edge.source)
            included_nodes_names.add(edge.source.id)

        for targets in sources.values():
            for target in targets:
                if target.id in included_nodes_names:
                    continue
                if not target.should_include():
                    continue

                included_nodes.append(target)
                included_nodes_names.add(target.id)

        simplified_edges: list[DiagramEdge] = []
        for final_node in included_nodes:
            reachable_finals = self._find_immediate_final_nodes(
                final_node, sources, set()
            )
            # Remove self to avoid self-loops
            reachable_finals.discard(final_node)

            for dest_final in reachable_finals:
                simplified_edges.append(DiagramEdge(final_node, dest_final, **self.edge_attrs))

        return DiagramGraph(
            edges=simplified_edges,
            declaration=self.declaration,
            config=self.config,
            attrs=self.attrs,
            edge_attrs=self.edge_attrs,
            node_attrs=self.node_attrs,
        )

    def render(self) -> str:
        lines = [
            *(
                ["---", yaml.dump({"config": self.config}).strip(), "---"]
                if self.config
                else []
            ),
            self.declaration,
        ]

        # Add nodes
        lines.extend(f"\t{node.to_mermaid_declaration()}" for node in sorted(self.all_nodes()))

        # Add edges
        for index, edge in enumerate(sorted(self.edges)):
            lines.extend([f"\t{line}" for line in edge.to_mermaid_declaration(index=index)])

        for index, (category, nodes) in enumerate(sorted(self._collect_categories().items())):
            color, bgcolor = self.colors[index % len(self.colors)]
            class_name = f"cat_{category.id}"
            
            lines.extend([
                f"subgraph {category.id}[\"{category.label}\"]",
                f"\tstyle {category.id} fill:{bgcolor},stroke:{color},stroke-width:2px",
                f"\tclassDef {class_name} fill:{color},stroke:{color},stroke-width:2px",
                *[f"\t{node.id}:::{class_name}" for node in nodes],
                "end",
            ])

        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Graph<{self.edges!r}>"
