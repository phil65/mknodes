from __future__ import annotations

import abc

from collections.abc import Sequence

from mknodes.pages import mkpage, processors
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkTemplatePage(mkpage.MkPage, metaclass=abc.ABCMeta):
    """Abstact Page used for templates."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build()

    @abc.abstractmethod
    def get_pageprocessors(self) -> Sequence[processors.ContainerProcessor]:
        raise NotImplementedError

    def _build(self):
        self.items = []
        for processor in self.get_pageprocessors():
            if processor.check_if_apply(self):
                processor.append_section(self)

    # def to_markdown(self) -> str:
    #     self._build()
    #     return super().to_markdown()
