import pathlib

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def resources_dir():
    return pathlib.Path(__file__).parent.parent / "mknodes/resources/"


FAKE_LLM_TEXT = "*(fake LLM text from tests/conftest.py)*"


async def _fake_llm(**_kwargs: object) -> str:
    return FAKE_LLM_TEXT


def pytest_configure(config: pytest.Config) -> None:
    """No paid LLM calls in tests (`MkLlm` examples render while collecting tests)."""
    from mknodes.templatenodes import mkllm

    mkllm.complete_llm = _fake_llm  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def _isolated_inputs(monkeypatch: pytest.MonkeyPatch):
    """Fresh inputs store for nodes outside a tree.

    Nodes without a context share the fallback context, whose inputs store would carry
    resolved inputs (icons, ...) from test to test.
    """
    from mknodes.basenodes import mknode
    from mknodes.inputs import InputStore

    monkeypatch.setattr(mknode.get_fallback_ctx(), "inputs", InputStore())
