"""Node for LLM-based text generation using LiteLlm."""

from __future__ import annotations

import functools
from typing import Any, TYPE_CHECKING

from mknodes.basenodes import mktext
from mknodes.utils import log, resources
from upath import UPath

if TYPE_CHECKING:
    import os
    from collections.abc import Sequence


logger = log.get_logger(__name__)


@functools.cache
def complete_llm(user_prompt: str, system_prompt: str, model: str, context: str) -> str:
    from llmling_agent_functional import run

    return run.run_agent_sync(
        user_prompt + "\n\n" + context,
        model=model,
        system_prompt=system_prompt,
    )


class MkLlm(mktext.MkText):
    """Node for LLM-based text generation."""

    ICON = "material/format-list-group"
    REQUIRED_PACKAGES = [resources.Package("litellm")]

    def __init__(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        model: str = "openai:gpt-4o-mini",
        context: str | None = None,
        extra_files: Sequence[str | os.PathLike[str]] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Args:
            user_prompt: Main prompt for the LLM
            system_prompt: System prompt to set LLM behavior
            model: LLM model identifier to use
            context: Main context string
            extra_files: Additional context files or strings
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.user_prompt = user_prompt
        self.system_prompt = system_prompt
        self._model = model
        self._context = context
        self._extra_files = extra_files or []

    def _process_extra_files(self) -> list[str]:
        """Process extra context items, reading files if necessary.

        Returns:
            List of context strings.
        """
        context_items: list[str] = []

        def process_dir(path: UPath) -> list[str]:
            return [f.read_text() for f in path.rglob("*") if f.is_file()]

        for item in self._extra_files:
            try:
                path = UPath(item)
                if path.is_file():
                    context_items.append(path.read_text())
                elif path.is_dir():
                    context_items.extend(process_dir(path))
                else:
                    context_items.append(str(item))
            except Exception as exc:
                err_msg = f"Failed to read context file: {item}"
                logger.warning(err_msg)
                raise ValueError(err_msg) from exc

        return context_items

    @property
    def text(self) -> str:
        """Generate text using the LLM.

        Returns:
            Generated text content.
        """
        context_items = self._process_extra_files()
        combined_context = (
            "\n".join(filter(None, [self._context, *context_items])) or None
        )

        return complete_llm(
            self.user_prompt,
            self.system_prompt or "",
            model=self._model,
            context=combined_context or "",
        )


if __name__ == "__main__":
    node = MkLlm("Say hello, introduce yourself", model="openai:gpt-4o-mini")
    print(node)
