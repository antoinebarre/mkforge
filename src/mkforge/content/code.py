"""Code block content element.

A fenced code block with an optional language info string for syntax
highlighting.  Both the code body and the language hint are validated as
strings at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass

from mkforge.input_checks import require_string


@dataclass(frozen=True)
class CodeBlock:
    """Fenced code block with an optional language info string.

    Attributes:
        code: Source code text (may be empty).
        language: Language hint for syntax highlighting (may be empty).
    """

    code: str
    language: str = ""

    def __post_init__(self) -> None:
        """Validate code block fields."""
        require_string(self.code, "CodeBlock code", allow_empty=True)
        require_string(self.language, "CodeBlock language", allow_empty=True)

    def render(self) -> str:
        """Render the code block as a Markdown fenced block.

        Returns:
            Fenced code block string, with language hint when set.
        """
        fence = f"```{self.language}" if self.language else "```"
        return f"{fence}\n{self.code}\n```"
