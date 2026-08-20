from pathlib import Path

import gmsh

from ball001.calculix_deck import SolverNode


def load_mesh_nodes(
    mesh_path: Path,
) -> tuple[SolverNode, ...]:
    if not mesh_path.exists():
        raise FileNotFoundError(
            f"Mesh file does not exist: {mesh_path}"
        )

    gmsh.initialize()

    try:
        gmsh.option.setNumber(
            "General.Terminal",
            0,
        )

        gmsh.open(
            str(mesh_path)
        )

        node_tags, node_coords, _ = (
            gmsh.model.mesh.getNodes()
        )

        nodes = []

        for index, node_tag in enumerate(
            node_tags
        ):
            coordinate_index = 3 * index

            nodes.append(
                SolverNode(
                    tag=int(node_tag),
                    x_mm=float(
                        node_coords[
                            coordinate_index
                        ]
                    ),
                    y_mm=float(
                        node_coords[
                            coordinate_index + 1
                        ]
                    ),
                    z_mm=float(
                        node_coords[
                            coordinate_index + 2
                        ]
                    ),
                )
            )

        if not nodes:
            raise ValueError(
                "Mesh contains no nodes."
            )

        return tuple(
            sorted(
                nodes,
                key=lambda node: node.tag,
            )
        )

    finally:
        gmsh.finalize()