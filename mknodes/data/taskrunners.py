from __future__ import annotations

import dataclasses

from typing import Literal


@dataclasses.dataclass
class TaskRunner:
    identifier: TaskRunnerStr
    website: str
    filenames: list[str]
    help_cmd: list[str]


TaskRunnerStr = Literal["makefile", "task", "just", "duty", "invoke", "doit"]


makefile = TaskRunner(
    identifier="makefile",
    website="https://www.gnu.org/software/make/manual/make.html",
    filenames=["Makefile"],
    help_cmd=["make", "help"],
)

task = TaskRunner(
    identifier="task",
    website="https://taskfile.dev/",
    filenames=[
        "Taskfile.yml",
        "taskfile.yml",
        "Taskfile.yaml",
        "taskfile.yaml",
        "Taskfile.dist.yml",
        "taskfile.dist.yml",
        "Taskfile.dist.yaml",
        "taskfile.dist.yaml",
    ],
    help_cmd=["task", "--list"],
)

just = TaskRunner(
    identifier="just",
    website="https://github.com/casey/just",
    filenames=["justfile"],
    help_cmd=["just", "--list"],
)

duty = TaskRunner(
    identifier="duty",
    website="https://github.com/pawamoy/duty",
    filenames=["duties.py"],
    help_cmd=["duty", "--list"],
)

invoke = TaskRunner(
    identifier="invoke",
    website="https://www.pyinvoke.org",
    filenames=["invoke.yaml", "invoke.yml", "invoke.json", "invoke.py"],
    help_cmd=["invoke", "--list"],
)

doit = TaskRunner(
    identifier="doit",
    website="http://pydoit.org",
    filenames=["dodo.py"],
    help_cmd=["doit", "list"],
)

TASK_RUNNERS: dict[TaskRunnerStr, TaskRunner] = {
    p.identifier: p for p in [makefile, task, just, duty, invoke, doit]
}
