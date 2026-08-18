## Volleyball-Specific Modeling Scope

BALL 001 is an indoor-volleyball engineering study. Its dimensional and mass
targets are based on regulation-scale volleyball geometry, but not every
intermediate computational model should be interpreted as a proposed final
volleyball construction.

### Current dimensional basis

BALL 001 currently uses:

- Nominal circumference: 660 mm
- Nominal mass target: 270 g
- Spherical outer geometry derived from circumference
- Layered skin / compliance / reinforcement / bladder architecture

These values establish volleyball-scale geometry rather than basketball-scale
geometry.

### Abstract seam topology controls

The one-, two-, and three-great-circle seam models developed during the early
surface-topology study are intentionally simplified control geometries.

They are used to study:

- seam-length scaling
- CAD Boolean behavior
- surface-region count
- groove-volume removal
- mass sensitivity
- topology complexity

They are **not proposed BALL 001 panel architectures**.

In particular, the three mutually perpendicular great-circle model can appear
visually similar to a basketball. That geometry is retained as an abstract
topology control, not as a realistic representation of an elite indoor
volleyball.

### Volleyball benchmark direction

The Mikasa V200W is used as an elite indoor-volleyball benchmark for relevant
construction and surface characteristics, including:

- 18-panel laminated construction
- curved / aerodynamically arranged panel architecture
- microfiber + polyurethane outer construction
- double-dimple surface treatment

BALL 001 is an independent concept study and is not affiliated with or
commissioned by Mikasa.

The V200W benchmark does **not** imply that BALL 001 will use 18 panels.
Instead, it provides a volleyball-specific reference against which alternative
architectures can later be compared.

### Seam and texture distinction

The model will treat three surface features separately:

1. **Panel architecture**  
   The large-scale regions that partition the volleyball surface.

2. **Panel joints / seams**  
   The boundaries between neighboring surface regions.

3. **Surface microtexture**  
   Dimples and finer-scale texture affecting contact and aerodynamic behavior.

The current 2.5 mm seam width and 0.4 mm seam depth are **PENDING computational
design variables**. They are not claimed to be measured Mikasa V200W seam
dimensions.

Likewise, the current smooth CAD surfaces do not yet represent the complete
double-dimple / microtextured volleyball surface.

### Internal construction and FEA

The current skin, compliance, reinforcement, and bladder layers are
computational abstractions used for parametric mass and geometry studies.

The reinforcement layer should ultimately represent volleyball-specific
bladder reinforcement / winding behavior rather than being interpreted as a
basketball carcass construction.

Two different meanings of "mesh" are kept separate:

- **Physical reinforcement mesh / winding** — part of the ball construction
- **Finite-element mesh** — numerical discretization used for simulation

Before structural FEA is treated as volleyball-representative, the model will
introduce a volleyball benchmark layer containing:

- inflation-pressure requirements
- realistic volleyball panel-boundary geometry
- surface-texture representation or effective properties
- appropriate bladder behavior
- effective reinforcement behavior
- clearly documented benchmark, literature, target, simulated, measured, and
  pending evidence classes

### Evidence discipline

All model quantities are classified where appropriate as:

- BENCHMARK
- LITERATURE
- TARGET
- SIMULATED
- MEASURED
- PENDING

Provisional seam dimensions, material properties, layer thicknesses, and
surface parameters must not be presented as measured properties of BALL 001 or
of an existing commercial volleyball.

The abstract topology studies remain in the repository because they document
the computational development process and provide useful control cases. Future
volleyball-specific geometry will build on those methods rather than silently
replacing or relabeling them.