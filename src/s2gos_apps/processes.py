import time
from typing import Annotated

from pydantic import Field

from procodile import JobContext, ProcessRegistry

registry = ProcessRegistry()

from .common import (
    generation,
    simulation
)

@registry.process(id="my-process-1")
def my_process_1(
    path: Annotated[str, Field(title="path")], 
    threshold: Annotated[float, Field(title="threshold")] = 0.5
) -> str:
    ctx = JobContext.get()
    print("something")
    ctx.report_progress(progress=15, message="Initialized sources")
    time.sleep()

