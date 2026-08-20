# Volley Lab / BALL 001

Independent volleyball engineering research at the intersection of player experience, mechanics, materials, computation, and circular design.

> How much of a great volleyball is actually necessary—and can the sport preserve what players trust while participating more responsibly in the material world?

**Status:** Active research · CalculiX structural baseline in active development · cross-solver / CFD expansion staged · physical performance and sustainability claims remain pending validation

**Source of truth:** This repository README is the canonical project summary. Capability claims, roadmap status, and evidence labels should be updated here only when supported by repository artifacts, solver outputs, documented tests, or physical measurements.

---

## Technical Profile

**Independent Researcher | Computational Engineering | Product R&D | Sports Engineering**

Volley Lab demonstrates applied work across computational engineering, product development, finite element analysis (FEA), computational fluid dynamics (CFD), parametric CAD, mesh generation, structural mechanics, dynamics and contact, biomechanics, materials engineering, design of experiments (DOE), verification and validation (V&V), optimization, lifecycle assessment (LCA), and reproducible scientific software development.

### Core Competencies

- Computational engineering and numerical methods
- Finite element analysis (FEA) and structural mechanics
- Computational fluid dynamics (CFD) and aerodynamics
- Parametric CAD and geometry automation
- Triangular surface meshing and tetrahedral volume meshing
- Mesh quality assessment and mesh-convergence studies
- Contact mechanics, impact dynamics, and pneumatic systems
- Sports biomechanics and human-equipment interaction
- Materials engineering and multilayer product architecture
- Design of experiments (DOE), sensitivity analysis, and optimization
- Model verification, experimental validation, and cross-solver comparison
- Product research and development (R&D) and systems engineering
- Circular design, repairability, recoverability, and lifecycle assessment (LCA)
- Scientific Python, experiment tracking, software testing, and reproducible workflows
- Technical research, patent / prior-art analysis, market research, and engineering documentation

### Selected Engineering Contributions

- Defined a controlled A/B/C experimental architecture to isolate the effect of material-layer simplification while controlling circumference, mass, internal pressure, and geometry.
- Built a Python-based parametric CAD foundation using CadQuery and OpenCascade/OCP for repeatable geometry generation and architecture studies.
- Developed computational-geometry and meshing workflows using Gmsh and Trimesh, including triangular surface meshes, tetrahedral volume meshes, topology checks, watertightness checks, and mesh-quality review.
- Built and actively developing the current structural pipeline around CalculiX, including the baseline model, pressure-envelope robustness work, and structural decision documentation.
- Defined an independent cross-solver verification architecture in which FEniCSx and, where available, ANSYS Mechanical are added after the CalculiX baseline is stabilized.
- Verified NVIDIA Warp installation and CPU execution in prior computational method-development work; Volley Lab–specific Warp kernels are a staged expansion item rather than a completed BALL 001 integration.
- Defined an OpenFOAM CFD pathway for seams, panel orientation, surface topology, drag, and wake behavior; CFD implementation follows the structural baseline and common artifact contracts.
- Designed a volleyball-specific verification and validation framework linking theory, numerical simulation, physical experiments, and engineering decisions.
- Developed a setter-centered biomechanics protocol covering force-time response, impulse, contact duration, deformation, release velocity, release angle, spin, trajectory consistency, target error, and athlete adaptation cost.
- Structured a test program spanning benchmark teardown, compression, impact, pneumatics, surface characterization, durability, player contact, circularity, and lifecycle analysis.
- Implemented reproducibility and software-quality practices with pytest, Ruff, mypy, pre-commit, Pydantic, Hydra, Git, Docker, Conda, and MLflow.
- Integrated materials, competition, market, regulatory, patent / prior-art, and lifecycle research into a single product-development decision framework.

### Technologies

- **Programming / Scientific Computing:** Python, NumPy, SciPy, scikit-learn, CasADi, NLopt
- **CAD / Geometry:** CadQuery, OpenCascade / OCP, FreeCAD
- **Meshing:** Gmsh, Trimesh, triangular surface meshes, tetrahedral volume meshes
- **Finite Element Analysis:** FEniCSx, DOLFINx, PETSc, CalculiX
- **Dynamics / Contact:** NVIDIA Warp
- **CFD:** OpenFOAM
- **Visualization:** VTK, PyVista, ParaView
- **Optimization / Sensitivity:** SALib, Optuna, scikit-learn, CasADi, NLopt
- **Experiment Tracking / Configuration:** MLflow, Hydra, Pydantic
- **Lifecycle Analysis:** Brightway
- **Software Engineering / Reproducibility:** Git, Docker, Conda, pytest, Ruff, mypy, pre-commit

---

## Executive Summary

Volley Lab is the convergence of two forms of learning: years in the gym and meticulous hours in the library.

Years of playing, setting, competing, coaching, observing, and working inside volleyball taught me what athletes notice: touch, release, grip, flight, rebound, pressure, predictability, and trust. Technical study in mechanics, materials, numerical methods, CAD, meshing, simulation, experimental design, and lifecycle analysis gave me a second language for the same object.

**The gym taught me what to notice. The library taught me how to interrogate it.**

BALL 001 is the first structured investigation within Volley Lab. It asks whether the functions that make an elite volleyball feel familiar and trustworthy can be isolated, measured, modeled, and ultimately reproduced with less material complexity and greater recoverability—without asking athletes to accept a worse ball or a worse game.

| Research frame | Current definition |
| --- | --- |
| Reference system | MIKASA as the experiential and technical elite-performance benchmark |
| Principal question | How far can material and layer architecture be simplified before meaningful performance changes appear? |
| Core method | Question → requirements → architecture → model → verify → build → measure → validate → compare → decide → iterate |
| Primary lenses | Mechanics, player contact, setter control, pneumatics, aerodynamics, durability, circularity |
| Evidence rule | Standard, benchmark, literature, target, simulated, measured, pending, and unknown remain explicitly separated |

BALL 001 is not only a one-off ball concept. It is the first controlled demonstrator for a broader traceable product-engineering methodology in which geometry, materials, mechanics, human interaction, manufacturing, and environmental impact must answer to one another. The volleyball remains the center of the work because it is personally meaningful and technically demanding; the transferable contribution is the disciplined decision process built around it.

---

## 1. Why This Project Exists

Volleyball is not a convenient object chosen to demonstrate engineering skills. It is one of the most enduring communities in my life.

My connection to the sport spans family, competition, coaching, elite training environments, collegiate volleyball, national-team pathways, and the contemporary women's professional game. I competed nationally and internationally, participated in USA Volleyball development environments, trained in high-level collegiate and national-team settings, and was recruited by Ivy League and ACC programs to play Division I. I later coached across age levels and worked closely with setters in collegiate environments.

That perspective is also intergenerational and international. My mother played through college and graduate school before competing professionally in Switzerland, Japan, and elsewhere in Europe, and she represented Team USA. During part of my childhood I was around FIVB training environments, including beach volleyball in Geneva, Switzerland, and was exposed to different volleyballs used in different countries and systems.

My relationship with the game now extends beyond playing and coaching through continued involvement in women's volleyball, including USA Volleyball / Team USA, recognition through an AVCA scholarship, work with The Nine associated with LOVB San Francisco, and advisory work with MLV DC.

College volleyball and national-team volleyball are especially personal communities to me. Volley Lab grew from a stewardship question:

> Could I use what the sport has taught me to explore whether volleyball can become a more materially responsible participant without sacrificing the performance, familiarity, and player relationship that make the game itself?

This is not sustainability as styling. It is sustainability as an engineering constraint—considered alongside touch, flight, durability, pressure retention, manufacturability, repairability, and performance.

The long-term design problem is therefore systemic rather than cosmetic:

**performance constraint → architecture → material choice → simulation → prototype → physical validation → environmental evaluation → redesign**

The project does not assume that fewer layers, recycled content, or lower mass automatically produce a better environmental outcome. Those choices only matter if the resulting ball still performs, lasts, can be serviced or recovered through a real pathway, and improves impact per useful service delivered.

---

## 2. The Observation Behind the Investigation

Growing up around volleyball in different countries, clubs, training environments, and competition systems exposed me to meaningful variation in balls and playing conditions.

Across those environments, MIKASA repeatedly felt like the standard: the reference point for what a serious competition volleyball was supposed to be.

That produced an observation I understood as an athlete before I could express it as an engineer:

> Volleyballs can satisfy the same basic rules and still feel meaningfully different.

Experienced players notice those differences quickly. A ball can feel heavier at similar mass, leave the hands more cleanly, feel easier to locate as a setter, rebound more crisply, float differently, or become trusted through repetition.

Volley Lab asks whether those perceptions can be connected to measurable physical variables.

MIKASA therefore serves as an experiential and technical reference, not as a design to copy or an answer to defend. The objective is to understand which physical functions make the reference system work, which parts of its architecture are necessary, and which may simply reflect one historical path to achieving elite performance.

---

## 3. Principal Investigation

**Human question**

> What makes a volleyball feel and perform like the ball experienced players trust?

**Engineering question**

> Which measurable material, structural, pneumatic, surface, dynamic, and aerodynamic properties create those behaviors—and how far can the underlying construction be simplified before they meaningfully change?

**Principal research question**

> To what extent can the materials and structural layers of a competition volleyball be reduced while preserving the measurable behaviors that define the performance of an elite reference ball?

In plain language:

> How much can I take out of a volleyball before it stops behaving like the ball I grew up trusting?

The sustainability question follows directly:

> If we can identify what is truly necessary, can we use that knowledge to make participation in volleyball materially more responsible without asking athletes to accept a worse game?

---

## 4. Thesis and Hypothesis

### Thesis

Volley Lab proposes that the qualities players describe as *feel* are not mysterious properties of a brand or aesthetic. They emerge from interacting physical functions.

| Player experience | Candidate physical contributors |
| --- | --- |
| Softness | Compliance, deformation rate, hysteresis |
| Clean contact | Contact duration, surface friction, local deformation, symmetry, vibration |
| Liveliness | Energy return, impact response, rebound behavior |
| Stable / unusual flight | Surface topology, seam geometry, orientation, drag, wake behavior |
| Trust | Repeatability of those behaviors from contact to contact |

The recognizable performance of an elite volleyball is not produced by material complexity itself, but by a set of physical functions that may be achievable with a simpler, more recoverable, and more intentionally engineered material architecture.

### Working hypothesis

> A reduced-material volleyball architecture can preserve the critical mechanical, pneumatic, aerodynamic, and player-contact behaviors of a conventional elite reference volleyball if the remaining components are engineered to perform multiple functions.

The experiment is designed to determine where that statement stops being true.

**Finding the limit is the project.**

---

## 5. The Setter as an Experimental Lens

Setters have a particularly high-frequency relationship with the ball.

A setter repeatedly receives an incoming state and deliberately transforms it into an outgoing one for athletes with different approach speeds, jump heights, arm swings, locations, tempos, and hitting styles across both the front and back row.

The same ball may need to become a first-tempo middle, fast outside set, high bailout ball, back set, slide, pipe, or another back-row attack. The setter is therefore repeatedly solving a physical control problem:

$$
\text{incoming ball state}
\rightarrow
\text{hand–ball interaction}
\rightarrow
\text{outgoing ball state}
$$

Over thousands of repetitions, setters develop a highly personal and unusually sensitive relationship with the object. Volley Lab treats that expertise as a source of testable questions, not a substitute for instrumentation.

### Setter metrics

| Player observation | Candidate physical metrics |
| --- | --- |
| "It sits in my hands." | Contact duration, deformation, compliance, friction |
| "It shoots off my hands." | Release velocity, contact duration, stiffness, energy return |
| "I can locate it." | Target error, release-angle variance, trajectory variance |
| "It feels heavy." | Required impulse, force-time profile, deformation rate |
| "My back set feels different." | Bilateral force symmetry, spin, release angle, wrist/hand kinematics |
| "It feels predictable." | Trial-to-trial variance across force, trajectory, spin, and target position |

### Primary setter measurements

- hand–ball contact time;
- peak contact force;
- impulse, $J = \int F(t)\,dt$;
- ball deformation during contact;
- release velocity and angle;
- post-release spin rate and spin axis;
- three-dimensional trajectory;
- apex height and time to hitter contact zone;
- target error and trial-to-trial repeatability;
- left/right hand symmetry where measurable;
- selected wrist, elbow, and shoulder kinematics;
- blinded subjective ratings of grip, controllability, responsiveness, release cleanliness, predictability, comfort, and confidence.

### Setter adaptation cost

A skilled setter can compensate for equipment differences. Two balls reaching the same target therefore do not necessarily represent the same athlete–equipment interaction.

Volley Lab asks:

> How much did the setter have to change to produce the same result?

For equivalent trajectories, adaptation can be evaluated through changes in force, impulse, contact time, release mechanics, joint excursion, whole-body contribution, and trajectory correction.

This distinguishes **output equivalence** from **interaction equivalence**.

---

## 6. Experimental Architecture

The central experiment compares progressively simplified material systems while holding the defining properties of the ball as constant as practical.

| Architecture | Construction concept | Experimental purpose |
| --- | --- | --- |
| **A — Conventional control** | Performance skin → compliance → reinforcement → structural substrate → bladder | Establish reference behavior |
| **B — Reduced architecture** | Performance skin → integrated compliance / reinforcement → bladder | Test functional consolidation |
| **C — Minimum architecture** | Structural-performance skin → reinforcement → bladder | Identify the simplification boundary |

### Controlled variables

Where experimentally possible:

- 66.0 cm nominal circumference;
- 270 g nominal mass;
- protocol-controlled internal pressure;
- comparable geometry;
- conditioning environment;
- instrumentation;
- test procedure.

The question is not whether the simplest ball wins.

> At what point does removing material begin to remove performance?

---

## 7. Evidence Standard

Volley Lab distinguishes rigorously between what is regulated, known, predicted, measured, and still unknown.

| Label | Meaning |
| --- | --- |
| STANDARD / REGULATED | Governing rule or competition requirement |
| BENCHMARK | Existing competition ball or published / observed reference |
| LITERATURE | External research |
| TARGET | Internal design objective |
| SIMULATED | Computational output; not a physical result |
| MEASURED | Physical BALL 001 result |
| PENDING | Planned but not yet validated |
| UNKNOWN | Evidence is not yet sufficient |

A simulation is not a measurement. A target is not a result. A sustainability intention is not an environmental outcome.

This matters especially for material reduction and circularity. Fewer layers do not automatically make a product more sustainable. A lighter ball that fails sooner, cannot be repaired, or cannot enter a real recovery pathway may perform worse over its useful life.

### Traceable design process

Every meaningful design decision should be traceable through a documented chain:

**observation → hypothesis → requirement → model assumption → simulation → measurement → evidence → decision**

That traceability is intended to connect specimen records, material batches, geometry versions, mesh settings, solver decks, boundary conditions, test IDs, experiment artifacts, evidence labels, and design decisions. The goal is not simply to produce a result; it is to preserve enough provenance that another engineer can understand why the result exists and what decision it supports.

---

## 8. Test Program

The test program treats volleyball performance as a system, not a single number.

| Study | Human question | Engineering measures |
| --- | --- | --- |
| Benchmark teardown | What is already there? | Layer count, thickness, mass, material, attachment, reinforcement, bladder, valve, recoverability |
| Compression | How does the ball give under load? | Force–displacement response, stiffness, hysteresis, permanent deformation |
| Impact | Where does the energy go? | Peak force, contact time, impulse, rebound, energy return |
| Surface | What do the hands and air actually touch? | Dry/wet friction, contact area, topology, abrasion, texture DOE |
| Pneumatic | Does the ball remain playable? | Pressure decay, temperature, leakage, permeability |
| Durability | Does performance survive repeated use? | Metric drift before/after controlled cycling |
| Player contact | Do mechanically similar balls actually feel similar? | Force-time response, deformation, vibration, subjective feel |
| Circularity | What happens when the ball is no longer new? | Repair access, separability, recoverable mass, disassembly time, waste, verified recovery |
| Life-cycle analysis | Did the design actually improve environmental performance? | Impact per useful service delivered |

---

## 9. Verification, Validation, and Engineering Decision

Volley Lab separates two questions that are often collapsed.

**Verification — did I solve the mathematical model correctly?**

Methods include:

- analytical checks;
- unit tests;
- mesh convergence;
- time-step convergence;
- conservation checks;
- solver-to-solver comparison.

**Validation — does the model describe the real volleyball well enough to support a decision?**

Validation requires physical compression, impact, pressure, material, contact, and eventually aerodynamic testing.

The intended evidence chain is:

$$
\boxed{
\text{Theory}
\leftrightarrow
\text{Numerical model A}
\leftrightarrow
\text{Numerical model B}
\leftrightarrow
\text{Experiment}
}
$$

The project does not end with *the simulation ran*.

It ends with:

> What does the evidence justify building next?

---

## 10. Technical Skills and Development Stack

Volley Lab is intentionally broader than conventional CAD work. The objective is a reproducible computational-engineering pipeline in which geometry, discretization, solvers, experiments, and provenance connect.

### Geometry and parametric CAD

| Technology | Role |
| --- | --- |
| Python | Connective layer for geometry, simulation, testing, optimization, and data processing |
| CadQuery | Programmable parametric solid modeling |
| OpenCascade / OCP | CAD geometry kernel used through CadQuery |
| FreeCAD | Interactive inspection and interoperability |

### Meshing and computational geometry

| Technology | Role |
| --- | --- |
| Gmsh | Automated surface and volume mesh generation |
| Triangular surface meshes | Shell / dynamic representation of the curved ball surface |
| Tetrahedral volume meshes | Volumetric discretization where through-thickness behavior matters |
| Trimesh | Mesh inspection, connectivity, normals, watertightness, and QA |

The competency is not simply generating elements. It is determining whether the discretization represents the physics sufficiently and whether refinement materially changes the answer.

### Finite Element Analysis (FEA) and Structural Mechanics

| Technology | Current status | Role |
| --- | --- | --- |
| CalculiX | Current structural baseline | Primary structural pipeline being stabilized, stress-tested across the pressure envelope, visualized, documented, and prepared for the baseline BALL 001 computational release |
| FEniCSx / DOLFINx | Planned independent verification | Programmable finite-element implementation for an independent formulation and solver comparison after the baseline interface is standardized |
| PETSc | Planned through FEniCSx | Numerical solver infrastructure within FEniCSx workflows |
| ANSYS Mechanical | Planned if available | Commercial cross-solver structural verification after common cases, units, and artifact contracts are defined |

Target verification logic:

$$
\text{analytical check}
\approx
\text{CalculiX baseline}
\approx
\text{FEniCSx independent model}
\approx
\text{ANSYS, if available}
\approx
\text{experiment}
$$

within a justified tolerance and with model-form differences documented rather than hidden.

### Dynamics, Computational Fluid Dynamics (CFD), Visualization, and Optimization

| Domain | Technologies | Current status / role |
| --- | --- | --- |
| Dynamics & contact | NVIDIA Warp | Warp is installed and has executed successfully on Apple Silicon CPU in prior method-development work; BALL 001–specific computational kernels are staged in 09G |
| CFD | OpenFOAM | Planned 10A CFD pathway for seams, panel orientation, surface topology, boundary-layer behavior, drag, and wake studies |
| CFD cross-verification | ANSYS Fluent | Planned 10B verification path if available, followed by 10C cross-solver comparison |
| Scientific visualization | VTK, PyVista, ParaView | 08K / 09D pathway for structural result inspection and a unified solver-agnostic results layer |
| Sensitivity / optimization | SALib, Optuna, scikit-learn, NLopt, CasADi | Planned parameter importance, search, surrogate modeling, and constrained optimization after solver interfaces stabilize |
| Experiment tracking | MLflow | Parameters, metrics, artifacts, and run provenance |
| Lifecycle analysis | Brightway | Computational LCA framework; inventory data sourced separately |

### Software engineering and reproducibility

- **Pydantic** — typed input and configuration validation;
- **Hydra** — experiment configuration;
- **pytest** — automated verification;
- **Ruff** — linting and code quality;
- **mypy** — static type checking;
- **pre-commit** — automated quality gates;
- **Git** — versioned engineering history;
- **Docker** — environment and solver reproducibility;
- **Conda / virtual environments** — dependency isolation.

---

## 11. Current Research State

### Established / Completed Foundations

- Defined principal research question, thesis, and working hypothesis;
- Established MIKASA as the elite reference / benchmark case study;
- Defined FIVB-controlled dimensional and pneumatic basis;
- Created evidence taxonomy and provenance rules;
- Designed controlled A/B/C material-architecture experiment;
- Built programmable parametric CAD foundation;
- Developed mesh-generation and computational-geometry workflow;
- Built the current CalculiX structural pipeline and defined the cross-solver verification architecture;
- Structured a test matrix spanning compression, impact, surface, durability, pneumatics, player contact, circularity, and LCA;
- Built reproducible computational-engineering stack;
- Implemented software testing, configuration, and experiment documentation;
- Designed setter-centered biomechanics and player-interaction research framework.

### Still to be earned through physical evidence

- benchmark teardown;
- material coupon characterization;
- physical compression curves;
- BALL 001 impact testing;
- pressure-retention testing;
- surface friction and topology characterization;
- durability cycling;
- setter / player-contact instrumentation;
- recoverability and disassembly data;
- lifecycle inventory and quantitative LCA.

Design can be discussed before these tests are complete. Performance and sustainability claims cannot.

### Prior computational method development — not BALL 001 evidence

Before the current volleyball structural pipeline, earlier inflatable-ball work was used to develop and stress-test numerical methods. One rigid-body drop study reproduced analytical mechanics closely: approximately 5.945 m/s simulated vs. 5.943 m/s theoretical impact velocity, and 1.299 m simulated vs. 1.300 m theoretical rebound height, corresponding to roughly 72.2% returned gravitational potential energy under the assumed restitution model.

Those values are retained only as method-development evidence. They are not BALL 001 volleyball performance results and must never be presented as such. Later deformable shell / gas-coupling experiments also produced numerical instability and NaN failures; those failures remain part of the engineering record because they informed solver choice, time-step discipline, model simplification, and the current verification strategy.

### Go-forward computational build roadmap

The sequence below is the canonical implementation plan unless superseded by a later repository update.

**CURRENT BUILD — complete the baseline structural release**

| ID | Build item | Purpose |
| --- | --- | --- |
| 08J-E | Pressure-envelope robustness | Confirm structural behavior and numerical stability across the controlled internal-pressure range |
| 08J-F | Final structural-model decision summary | Record the selected baseline formulation, assumptions, rejected alternatives, and decision rationale |
| 08K | Structural results visualization | Turn solver outputs into inspectable, reproducible stress / displacement / field artifacts |
| 08L | Documentation / README / reproducibility cleanup | Align code, commands, evidence labels, and documentation before release |
| 08M | Baseline BALL 001 computational release | Freeze a defensible baseline computational implementation before adding more solvers |

**THEN EXPAND — standardize interfaces, verify independently, then add physics**

| ID | Build item | Purpose |
| --- | --- | --- |
| 09A | Toolchain registry | Register CadQuery, Gmsh, Trimesh, CalculiX, FEniCSx, Warp, OpenFOAM, PyVista, VTK, ParaView, and ANSYS capabilities / availability |
| 09B | Common case + units + artifact contracts | Define solver-independent case inputs, units, naming, outputs, and artifact expectations |
| 09C | CalculiX backend refactor | Place the existing CalculiX pipeline behind a common backend interface |
| 09D | PyVista / VTK unified results layer | Normalize structural result loading, inspection, plotting, and comparison across backends |
| 09E | FEniCSx independent structural verification | Reproduce selected structural cases independently rather than sharing solver assumptions by construction |
| 09F | ANSYS Mechanical cross-solver verification | Add commercial structural verification if available |
| 09G | NVIDIA Warp computational kernels | Add Volley Lab–specific high-performance kernels for dynamics, contact, and future parameter sweeps |
| 10A | OpenFOAM CFD pathway | Establish aerodynamics workflow for seams, topology, orientation, drag, side force, and wake structure |
| 10B | ANSYS Fluent CFD verification | Add commercial CFD comparison if available |
| 10C | CFD cross-solver comparison | Compare OpenFOAM and Fluent on common cases and document agreement / model-form differences |
| 11 | Multiphysics / optimization / design studies | Couple validated disciplines and begin structured sensitivity, optimization, and design-space studies |

The sequencing is deliberate:

**baseline → abstraction → independent verification → CFD expansion → multiphysics / optimization**

The objective is not to accumulate software logos. Each new tool must either reduce model risk, improve reproducibility, expose a useful physical variable, or support a better engineering decision.

---

## 12. Applied Engineering and Professional Development

This repository is also a record of how I learn.

I wanted one place where technical disciplines would have to answer to one another instead of existing as isolated exercises. BALL 001 is the first demonstrator for that methodology: a familiar physical product treated as a parameterized engineering object whose geometry, layer architecture, material properties, pressure, surface topology, and manufacturing assumptions can eventually be varied and evaluated against mechanics, player interaction, durability, recoverability, and environmental performance.

The transferable idea is not "a ball simulation." It is a disciplined product-development method for products in which geometry + materials + mechanics + human interaction + manufacturing + environmental impact must be optimized together.

| Discipline | What it contributes |
| --- | --- |
| CAD | Controls geometry |
| Meshing | Forces explicit numerical-representation choices |
| FEA | Exposes assumptions about mechanics |
| Dynamics | Introduces time and contact |
| CFD | Makes surface design a flight problem |
| Materials science | Explains structural behavior |
| Statistics | Tests whether differences are meaningful |
| Experimental mechanics | Tests whether predictions deserve trust |
| Setter / player research | Connects equipment behavior to real volleyball tasks |
| Market / competition research | Places the work in a real sport ecosystem |
| Patent / prior-art research | Establishes the existing design space |
| LCA | Tests whether environmental intuition survives quantitative scrutiny |
| Software engineering | Makes the work reproducible |
| Technical writing | Makes the reasoning inspectable |

This is not years in the gym versus hours in the library.

It is what happens when they finally meet.

**Experience tells me where to look. Measurement tells me what is actually there.**

---

## 13. Installation

The repository includes a reproducible installation bundle for the volleyball shell, impact, CFD, optimization, and life-cycle-analysis workflow.

### Included systems

- **Geometry / CAD:** CadQuery, Gmsh, FreeCAD
- **Current structural FEA:** CalculiX
- **Planned independent structural verification:** FEniCSx / DOLFINx
- **Dynamics / contact expansion:** NVIDIA Warp
- **Visualization:** PyVista, VTK, ParaView
- **CFD expansion:** OpenFOAM through Docker; ANSYS Fluent if available
- **Optimization:** Optuna, SALib, scikit-learn
- **Experiment tracking:** MLflow
- **Life-cycle analysis:** Brightway
- **Quality / reproducibility:** pytest, Ruff, mypy, pre-commit, Pydantic, Hydra

### macOS

```bash
cd volleyball-engineering-stack
./scripts/install_macos.sh
conda activate volleyball-engineering
python scripts/verify_stack.py
```

The installer creates a Python 3.11 Conda environment and installs native desktop applications where practical. OpenFOAM and an alternate FEniCSx environment are supplied through Docker for improved reproducibility on macOS.

### Linux

```bash
cd volleyball-engineering-stack
./scripts/install_linux.sh
conda activate volleyball-engineering
python scripts/verify_stack.py
```

### Containers

**OpenFOAM**

```bash
cd containers
docker compose run --rm openfoam bash
```

**FEniCSx**

```bash
cd containers
docker compose run --rm fenicsx bash
```

### Current limitations

- Installer scripts cannot activate proprietary licenses for ANSYS, Abaqus, Granta EduPack, or commercial material databases.
- NVIDIA Warp has been verified to install and execute on Apple Silicon CPU in prior method-development work; the Volley Lab–specific 09G kernel integration remains pending.
- Brightway provides the framework; life-cycle inventory databases must be imported according to their own licensing terms.
- Docker Desktop must be running before container commands work on macOS.
- CalculiX is the current BALL 001 structural baseline pipeline. Cross-solver claims remain pending until common cases are reproduced independently in FEniCSx and, if available, ANSYS Mechanical.

---

## Professional Domains Demonstrated

Computational Engineering · Mechanical Engineering · Product R&D · Sports Engineering · Finite Element Analysis · Computational Fluid Dynamics · CAD Automation · Mesh Generation · Structural Mechanics · Contact Dynamics · Biomechanics · Materials Engineering · Experimental Design · Verification and Validation · Optimization · Sustainability Engineering · Lifecycle Assessment · Scientific Software · Technical Documentation

---

## Project Statement

Volley Lab is years of volleyball experience and meticulous technical study compiled into one place: an attempt to understand the ball deeply enough to preserve what players trust while asking whether our participation in the sport can become more materially responsible. BALL 001 is the first controlled demonstrator—a parameterized, traceable engineering system connecting CAD, meshing, FEA, dynamics, CFD, experiment, circularity, and design decisions without confusing simulations, intentions, or targets for earned evidence.

---

# Appendix: Volleyball-Specific Modeling Scope

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
