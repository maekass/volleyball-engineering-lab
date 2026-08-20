from dataclasses import dataclass
from pathlib import Path

import gmsh

from ball001.calculix_deck import (
    SolverNode,
)
from ball001.effective_shell import (
    EffectiveShellMaterial,
)
from ball001.pressure import (
    PressureLoadCase,
)


@dataclass(frozen=True)
class QuadraticSolverTriangle:
    tag: int
    node_1: int
    node_2: int
    node_3: int
    node_4: int
    node_5: int
    node_6: int


@dataclass(frozen=True)
class QuadraticSolverMesh:
    nodes: tuple[SolverNode, ...]
    triangles: tuple[
        QuadraticSolverTriangle,
        ...
    ]
    flipped_triangle_count: int


@dataclass(frozen=True)
class QuadraticCalculixDeckSummary:
    node_count: int
    triangle_count: int
    flipped_triangle_count: int
    pin_x_tag: int
    pin_y_tag: int
    pin_z_tag: int
    applied_pressure_n_mm2: float
    deck_path: Path


def _subtract(
    point_a: tuple[float, float, float],
    point_b: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        point_a[0] - point_b[0],
        point_a[1] - point_b[1],
        point_a[2] - point_b[2],
    )


def _cross(
    vector_a: tuple[float, float, float],
    vector_b: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        vector_a[1] * vector_b[2]
        - vector_a[2] * vector_b[1],
        vector_a[2] * vector_b[0]
        - vector_a[0] * vector_b[2],
        vector_a[0] * vector_b[1]
        - vector_a[1] * vector_b[0],
    )


def _dot(
    vector_a: tuple[float, float, float],
    vector_b: tuple[float, float, float],
) -> float:
    return (
        vector_a[0] * vector_b[0]
        + vector_a[1] * vector_b[1]
        + vector_a[2] * vector_b[2]
    )


def load_quadratic_solver_mesh(
    mesh_path: Path,
) -> QuadraticSolverMesh:
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

        nodes_by_tag = {}

        for index, node_tag in enumerate(
            node_tags
        ):
            coordinate_index = 3 * index

            node = SolverNode(
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

            nodes_by_tag[node.tag] = node

        triangle_type = (
            gmsh.model.mesh.getElementType(
                "triangle",
                2,
            )
        )

        (
            triangle_tags,
            triangle_node_tags,
        ) = gmsh.model.mesh.getElementsByType(
            triangle_type
        )

        if len(triangle_tags) == 0:
            raise ValueError(
                "Quadratic mesh contains no "
                "six-node triangles."
            )

        triangles = []
        flipped_triangle_count = 0

        for index, triangle_tag in enumerate(
            triangle_tags
        ):
            start = 6 * index

            connectivity = [
                int(
                    triangle_node_tags[
                        start + offset
                    ]
                )
                for offset in range(6)
            ]

            node_1 = nodes_by_tag[
                connectivity[0]
            ]
            node_2 = nodes_by_tag[
                connectivity[1]
            ]
            node_3 = nodes_by_tag[
                connectivity[2]
            ]

            point_1 = (
                node_1.x_mm,
                node_1.y_mm,
                node_1.z_mm,
            )

            point_2 = (
                node_2.x_mm,
                node_2.y_mm,
                node_2.z_mm,
            )

            point_3 = (
                node_3.x_mm,
                node_3.y_mm,
                node_3.z_mm,
            )

            vector_12 = _subtract(
                point_2,
                point_1,
            )

            vector_13 = _subtract(
                point_3,
                point_1,
            )

            normal = _cross(
                vector_12,
                vector_13,
            )

            centroid = (
                (
                    point_1[0]
                    + point_2[0]
                    + point_3[0]
                )
                / 3.0,
                (
                    point_1[1]
                    + point_2[1]
                    + point_3[1]
                )
                / 3.0,
                (
                    point_1[2]
                    + point_2[2]
                    + point_3[2]
                )
                / 3.0,
            )

            if _dot(
                normal,
                centroid,
            ) < 0.0:
                # Original second-order triangle:
                #
                # 1, 2, 3 = corner nodes
                # 4 = edge 1-2
                # 5 = edge 2-3
                # 6 = edge 3-1
                #
                # Reversing 2 and 3 therefore requires:
                #
                # 1, 3, 2, 6, 5, 4
                connectivity = [
                    connectivity[0],
                    connectivity[2],
                    connectivity[1],
                    connectivity[5],
                    connectivity[4],
                    connectivity[3],
                ]

                flipped_triangle_count += 1

            triangles.append(
                QuadraticSolverTriangle(
                    tag=int(
                        triangle_tag
                    ),
                    node_1=connectivity[0],
                    node_2=connectivity[1],
                    node_3=connectivity[2],
                    node_4=connectivity[3],
                    node_5=connectivity[4],
                    node_6=connectivity[5],
                )
            )

        return QuadraticSolverMesh(
            nodes=tuple(
                nodes_by_tag[tag]
                for tag in sorted(
                    nodes_by_tag
                )
            ),
            triangles=tuple(
                triangles
            ),
            flipped_triangle_count=(
                flipped_triangle_count
            ),
        )

    finally:
        gmsh.finalize()


def _select_axis_nodes(
    mesh: QuadraticSolverMesh,
) -> tuple[
    SolverNode,
    SolverNode,
    SolverNode,
]:
    x_node = max(
        mesh.nodes,
        key=lambda node: node.x_mm,
    )

    y_node = max(
        mesh.nodes,
        key=lambda node: node.y_mm,
    )

    z_node = max(
        mesh.nodes,
        key=lambda node: node.z_mm,
    )

    if len(
        {
            x_node.tag,
            y_node.tag,
            z_node.tag,
        }
    ) != 3:
        raise ValueError(
            "Axis constraint nodes must be unique."
        )

    return (
        x_node,
        y_node,
        z_node,
    )


def export_quadratic_calculix_deck(
    mesh_path: Path,
    deck_path: Path,
    load_case: PressureLoadCase,
    material: EffectiveShellMaterial,
    shell_thickness_m: float,
) -> QuadraticCalculixDeckSummary:
    if shell_thickness_m <= 0.0:
        raise ValueError(
            "Shell thickness must be positive."
        )

    mesh = load_quadratic_solver_mesh(
        mesh_path
    )

    (
        x_node,
        y_node,
        z_node,
    ) = _select_axis_nodes(
        mesh
    )

    shell_thickness_mm = (
        shell_thickness_m
        * 1000.0
    )

    youngs_modulus_n_mm2 = (
        material.youngs_modulus_pa
        / 1_000_000.0
    )

    pressure_n_mm2 = (
        load_case.pressure_pa
        / 1_000_000.0
    )

    lines = [
        "** BALL 001 — CalculiX S6 verification deck",
        "**",
        "** Units: mm, N",
        "** Artificial solver-verification material.",
        "*NODE",
    ]

    for node in mesh.nodes:
        lines.append(
            
                f"{node.tag}, "
                f"{node.x_mm:.9f}, "
                f"{node.y_mm:.9f}, "
                f"{node.z_mm:.9f}"
            
        )

    lines.append(
        "*ELEMENT, TYPE=S6, ELSET=EALL"
    )

    for triangle in mesh.triangles:
        lines.append(
            
                f"{triangle.tag}, "
                f"{triangle.node_1}, "
                f"{triangle.node_2}, "
                f"{triangle.node_3}, "
                f"{triangle.node_4}, "
                f"{triangle.node_5}, "
                f"{triangle.node_6}"
            
        )

    lines.extend(
        [
            "*MATERIAL, NAME=VERIFICATION",
            "*ELASTIC",
            (
                f"{youngs_modulus_n_mm2:.9f}, "
                f"{material.poisson_ratio:.9f}"
            ),
            (
                "*SHELL SECTION, "
                "ELSET=EALL, "
                "MATERIAL=VERIFICATION"
            ),
            f"{shell_thickness_mm:.9f}",
            "*NSET, NSET=PIN_X",
            str(x_node.tag),
            "*NSET, NSET=PIN_Y",
            str(y_node.tag),
            "*NSET, NSET=PIN_Z",
            str(z_node.tag),
            "*STEP",
            "*STATIC",
            "*BOUNDARY",
            "PIN_X, 2, 3, 0.0",
            "PIN_Y, 1, 1, 0.0",
            "PIN_Y, 3, 3, 0.0",
            "PIN_Z, 1, 2, 0.0",
            "*DLOAD",
            (
                "EALL, P, "
                f"{pressure_n_mm2:.9f}"
            ),
            "*EL FILE, OUTPUT=2D",
            "S, E, NOE",
            "*NODE FILE",
            "U",
            "*END STEP",
        ]
    )

    deck_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    deck_path.write_text(
        "\n".join(lines) + "\n"
    )

    return QuadraticCalculixDeckSummary(
        node_count=len(
            mesh.nodes
        ),
        triangle_count=len(
            mesh.triangles
        ),
        flipped_triangle_count=(
            mesh.flipped_triangle_count
        ),
        pin_x_tag=x_node.tag,
        pin_y_tag=y_node.tag,
        pin_z_tag=z_node.tag,
        applied_pressure_n_mm2=(
            pressure_n_mm2
        ),
        deck_path=deck_path,
    )