"""Node for LLM-based text generation using LiteLlm."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
from upathtools import to_upath

from mknodes.basenodes import mktext
from mknodes.utils import log, resources
from anyio import functools as anyio_functools

if TYPE_CHECKING:
    from tokonomics import ModelName
    from upath import UPath
    import os
    from collections.abc import Sequence


logger = log.get_logger(__name__)


@anyio_functools.cache
async def complete_llm(user_prompt: str, system_prompt: str, model: str, context: str) -> str:
    from agentpool.functional import run

    return await run.run_agent(
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
        model: str | ModelName = "openai:gpt-4o-mini",
        context: str | None = None,
        extra_files: Sequence[str | os.PathLike[str]] | None = None,
        **kwargs: Any,
    ) -> None:
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
            return [f.read_text("utf-8") for f in path.rglob("*") if f.is_file()]

        for item in self._extra_files:
            try:
                path = to_upath(item)
                if path.is_file():
                    context_items.append(path.read_text("utf-8"))
                elif path.is_dir():
                    context_items.extend(process_dir(path))
                else:
                    context_items.append(str(item))
            except Exception as exc:
                err_msg = f"Failed to read context file: {item}"
                logger.warning(err_msg)
                raise ValueError(err_msg) from exc

        return context_items

    async def get_text(self) -> str:
        """Generate text using the LLM.

        Returns:
            Generated text content.
        """
        context_items = self._process_extra_files()
        combined_context = "\n".join(filter(None, [self._context, *context_items])) or None

        return await complete_llm(
            self.user_prompt,
            self.system_prompt or "",
            model=self._model,
            context=combined_context or "",
        )


if __name__ == "__main__":
    node = MkLlm("Say hello, introduce yourself", model="openai:gpt-5-nano")
    print(node)
