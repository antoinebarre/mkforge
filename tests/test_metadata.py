from mkforge import PROJECT_DESCRIPTION, PROJECT_NAME


def test_package_metadata() -> None:
    """Requirement: package metadata exposes the MkForge project identity."""
    assert PROJECT_NAME == "mkforge"
    assert PROJECT_DESCRIPTION == (
        "Programmatic Markdown report generation for Python."
    )
