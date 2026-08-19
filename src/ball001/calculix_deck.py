from dataclasses import dataclass
from pathlib import Path

import gmsh

from ball001.effective_shell import EffectiveShellMaterial
from ball001.pressure import PressureLoadCase


@dataclass(frozen=True)
class SolverNode:
    tag: int
    x_mm: float
    y_mm: float
    z_mm: float


@dataclass(frozen=True)
class SolverTriangle:
    tag: int
    node_a: int
    node_b: int
    node_c: int


@dataclass(frozen=True)
class SolverMesh:
    nodes: tuple[SolverNode, ...]
    triangles: tuple[SolverTriangle, ...]
    flipped_triangle_count: int


@dataclass(frozen=True)
class AxisConstraintNodes:
    x_node: SolverNode
    y_node: SolverNode
    z_node: SolverNode


@dataclass(frozen=True)
class CalculixDeckSummary:
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


def load_solver_mesh(
    mesh_path: Path,
) -> SolverMesh:
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
            coordinate_index = (
                3 * index
            )

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
                1,
            )
        )

        (
            triangle_tags,
            triangle_node_tags,
        ) = gmsh.model.mesh.getElementsByType(
            triangle_type
        )

        triangles = []
        flipped_triangle_count = 0

        for index, triangle_tag in enumerate(
            triangle_tags
        ):
            node_index = (
                3 * index
            )

            node_a_tag = int(
                triangle_node_tags[
                    node_index
                ]
            )

            node_b_tag = int(
                triangle_node_tags[
                    node_index + 1
                ]
            )

            node_c_tag = int(
                triangle_node_tags[
                    node_index + 2
                ]
            )

            node_a = nodes_by_tag[
                node_a_tag
            ]
            node_b = nodes_by_tag[
                node_b_tag
            ]
            node_c = nodes_by_tag[
                node_c_tag
            ]

            point_a = (
                node_a.x_mm,
                node_a.y_mm,
                node_a.z_mm,
            )

            point_b = (
                node_b.x_mm,
                node_b.y_mm,
                node_b.z_mm,
            )

            point_c = (
                node_c.x_mm,
                node_c.y_mm,
                node_c.z_mm,
            )

            vector_ab = _subtract(
                point_b,
                point_a,
            )

            vector_ac = _subtract(
                point_c,
                point_a,
            )

            normal = _cross(
                vector_ab,
                vector_ac,
            )

            centroid = (
                (
                    point_a[0]
                    + point_b[0]
                    + point_c[0]
                )
                / 3.0,
                (
                    point_a[1]
                    + point_b[1]
                    + point_c[1]
                )
                / 3.0,
                (
                    point_a[2]
                    + point_b[2]
                    + point_c[2]
                )
                / 3.0,
            )

            if _dot(
                normal,
                centroid,
            ) < 0.0:
                (
                    node_b_tag,
                    node_c_tag,
                ) = (
                    node_c_tag,
                    node_b_tag,
                )

                flipped_triangle_count += 1

            triangles.append(
                SolverTriangle(
                    tag=int(
                        triangle_tag
                    ),
                    node_a=node_a_tag,
                    node_b=node_b_tag,
                    node_c=node_c_tag,
                )
            )

        if not nodes_by_tag:
            raise ValueError(
                "Solver mesh contains no nodes."
            )

        if not triangles:
            raise ValueError(
                "Solver mesh contains no triangles."
            )

        return SolverMesh(
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


def select_axis_constraint_nodes(
    mesh: SolverMesh,
) -> AxisConstraintNodes:
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

    selected_tags = {
        x_node.tag,
        y_node.tag,
        z_node.tag,
    }

    if len(selected_tags) != 3:
        raise ValueError(
            "Axis constraint nodes must be unique."
        )

    return AxisConstraintNodes(
        x_node=x_node,
        y_node=y_node,
        z_node=z_node,
    )


def export_calculix_verification_deck(
    mesh_path: Path,
    deck_path: Path,
    load_case: PressureLoadCase,
    material: EffectiveShellMaterial,
    shell_thickness_m: float,
) -> CalculixDeckSummary:
    if shell_thickness_m <= 0.0:
        raise ValueError(
            "Shell thickness must be positive."
        )

    mesh = load_solver_mesh(
        mesh_path
    )

    constraints = (
        select_axis_constraint_nodes(
            mesh
        )
    )

    shell_thickness_mm = (
        shell_thickness_m
        * 1000.0
    )

    youngs_modulus_n_mm2 = (
        material.youngs_modulus_pa
        / 1_000_000.0
    )

    # N/mm² is numerically equivalent to MPa.
    pressure_n_mm2 = (
        load_case.pressure_pa
        / 1_000_000.0
    )

    # Triangles are explicitly oriented outward.
    # This trial sign is chosen to generate outward
    # inflation and must be verified from the result.
    applied_pressure_n_mm2 = (
        -pressure_n_mm2
    )

    lines = [
        "** BALL 001 — CalculiX shell verification deck",
        "**",
        "** Units: mm, N",
        "** Material values are artificial verification inputs.",
        "** This is not a measured volleyball material model.",
        "*NODE",
    ]

    for node in mesh.nodes:
        lines.append(
            
                f"{node.tag}, "
                f"{node.x_mm:.9f}, "
                f"{node.y_mm:.9f}, "
                f"{node.z_mm:.9f}"
            
        )

    lines.extend(
        [
            "*ELEMENT, TYPE=S3, ELSET=EALL",
        ]
    )

    for triangle in mesh.triangles:
        lines.append(
            
                f"{triangle.tag}, "
                f"{triangle.node_a}, "
                f"{triangle.node_b}, "
                f"{triangle.node_c}"
            
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
            str(
                constraints.x_node.tag
            ),
            "*NSET, NSET=PIN_Y",
            str(
                constraints.y_node.tag
            ),
            "*NSET, NSET=PIN_Z",
            str(
                constraints.z_node.tag
            ),
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
                f"{applied_pressure_n_mm2:.9f}"
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

    return CalculixDeckSummary(
        node_count=len(
            mesh.nodes
        ),
        triangle_count=len(
            mesh.triangles
        ),
        flipped_triangle_count=(
            mesh.flipped_triangle_count
        ),
        pin_x_tag=(
            constraints.x_node.tag
        ),
        pin_y_tag=(
            constraints.y_node.tag
        ),
        pin_z_tag=(
            constraints.z_node.tag
        ),
        applied_pressure_n_mm2=(
            applied_pressure_n_mm2
        ),
        deck_path=deck_path,
    )