from ball001.panel_reference import V200W_PANEL_REFERENCE


def main() -> None:
    reference = V200W_PANEL_REFERENCE

    print("BALL 001 — VOLLEYBALL PANEL REFERENCE")
    print("=" * 60)
    print(f"Reference:             {reference.name}")
    print(f"Panel count:           {reference.panel_count}")
    print(
        f"Panel-count evidence:  "
        f"{reference.panel_count_evidence}"
    )
    print(
        f"Panel-shape evidence:  "
        f"{reference.panel_shape_evidence}"
    )
    print(
        f"Seam-geometry evidence:"
        f" {reference.seam_geometry_evidence}"
    )

    print()
    print("NOTE:")
    print(reference.note)
    print()
    print(
        "The reference does not imply that BALL 001 "
        "will use 18 panels."
    )


if __name__ == "__main__":
    main()