from dataclasses import dataclass


@dataclass(frozen=True)
class GreatCircleSeam:
    name: str
    rotation_x_deg: float
    rotation_y_deg: float


@dataclass(frozen=True)
class SeamTopology:
    name: str
    seams: tuple[GreatCircleSeam, ...]


TOPOLOGY_1_SEAM = SeamTopology(
    name="one_great_circle",
    seams=(
        GreatCircleSeam(
            name="equator",
            rotation_x_deg=0.0,
            rotation_y_deg=0.0,
        ),
    ),
)


TOPOLOGY_2_SEAM = SeamTopology(
    name="two_great_circles",
    seams=(
        GreatCircleSeam(
            name="equator",
            rotation_x_deg=0.0,
            rotation_y_deg=0.0,
        ),
        GreatCircleSeam(
            name="vertical_x",
            rotation_x_deg=90.0,
            rotation_y_deg=0.0,
        ),
    ),
)


TOPOLOGY_3_SEAM = SeamTopology(
    name="three_great_circles",
    seams=(
        GreatCircleSeam(
            name="equator",
            rotation_x_deg=0.0,
            rotation_y_deg=0.0,
        ),
        GreatCircleSeam(
            name="vertical_x",
            rotation_x_deg=90.0,
            rotation_y_deg=0.0,
        ),
        GreatCircleSeam(
            name="vertical_y",
            rotation_x_deg=0.0,
            rotation_y_deg=90.0,
        ),
    ),
)