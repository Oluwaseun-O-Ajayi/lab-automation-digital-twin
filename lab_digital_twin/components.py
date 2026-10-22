"""Devices, workflows and processing-time distributions."""

from dataclasses import dataclass
from typing import Callable, Sequence, Tuple, Union

import numpy as np

# A duration is a fixed number, a distribution tuple, or a callable taking a
# numpy Generator and returning a number:
#   5.0                      fixed duration
#   ("exponential", mean)    exponential with the given mean
#   ("normal", mean, sd)     normal, truncated at zero
#   ("uniform", low, high)   uniform between low and high
Duration = Union[float, int, Tuple, Callable[[np.random.Generator], float]]


def draw(duration: Duration, rng: np.random.Generator) -> float:
    """Draw one non-negative duration."""
    if callable(duration):
        value = float(duration(rng))
    elif isinstance(duration, (int, float)):
        value = float(duration)
    else:
        kind, *args = duration
        if kind == "exponential":
            value = float(rng.exponential(args[0]))
        elif kind == "normal":
            value = max(0.0, float(rng.normal(args[0], args[1])))
        elif kind == "uniform":
            value = float(rng.uniform(args[0], args[1]))
        else:
            raise ValueError(f"Unknown distribution '{kind}'")
    if value < 0:
        raise ValueError("Durations must be non-negative")
    return value


def mean_duration(duration: Duration) -> float:
    """Expected value of a duration (callables are not supported)."""
    if isinstance(duration, (int, float)):
        return float(duration)
    if callable(duration):
        raise ValueError("The mean of a callable duration is not known")
    kind, *args = duration
    if kind in ("exponential", "normal"):
        return float(args[0])
    if kind == "uniform":
        return (args[0] + args[1]) / 2
    raise ValueError(f"Unknown distribution '{kind}'")


@dataclass
class Device:
    """A workcell station.

    Args:
        name: unique name used in workflow steps.
        capacity: number of samples the device can process at the same time.
        process_time: time to process one sample (see Duration).
    """

    name: str
    capacity: int = 1
    process_time: Duration = 1.0

    def __post_init__(self):
        if not isinstance(self.capacity, int) or self.capacity < 1:
            raise ValueError(f"Device '{self.name}': capacity must be a positive integer")
        if isinstance(self.process_time, (int, float)) and self.process_time < 0:
            raise ValueError(f"Device '{self.name}': process_time must be non-negative")


@dataclass
class Workflow:
    """An ordered list of device names that every sample visits in turn."""

    name: str
    steps: Sequence[str]

    def __post_init__(self):
        self.steps = list(self.steps)
        if not self.steps:
            raise ValueError(f"Workflow '{self.name}' has no steps")
