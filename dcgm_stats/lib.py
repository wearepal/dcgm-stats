from __future__ import annotations
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final, Generic, TypeVar, Union
import urllib.request

T = TypeVar("T")


@dataclass
class Metric(Generic[T]):
    column: str
    converter: Callable[[str], T]
    suffix: str = ""


METRICS: Final[dict[str, Union[Metric[int], Metric[float]]]] = {
    "GPU util": Metric("DCGM_FI_DEV_GPU_UTIL", float, "%"),
    "temp.": Metric("DCGM_FI_DEV_GPU_TEMP", int, "C"),
    "power": Metric("DCGM_FI_DEV_POWER_USAGE", float, "W"),
    "mem util": Metric("DCGM_FI_DEV_MEM_COPY_UTIL", float, "%"),
}


def main() -> None:
    with urllib.request.urlopen("http://localhost:9400/metrics") as connection:
        dcgm_output = connection.read().decode("utf-8")
    all_values = extract(dcgm_output)
    render(all_values)


def extract(dcgm_output: str) -> dict[int, dict[str, str]]:
    """Extract all the metric values from the DCGM output."""
    all_values: defaultdict[int, dict[str, str]] = defaultdict(dict)
    for name, metric in METRICS.items():
        values_per_gpu = convert(filter(dcgm_output, metric.column), metric.converter)
        for gpu, value in values_per_gpu.items():
            all_values[gpu].update({name: f"{value}{metric.suffix}"})
    return dict(all_values)


def filter(dcgm_output: str, prefix: str) -> list[str]:
    """Filter for those entries that match the given metric name."""
    prefix_len = len(prefix)
    return [
        line[prefix_len:] for line in dcgm_output.split("\n") if line.startswith(prefix)
    ]


def convert(extracts: list[str], converter: Callable[[str], T]) -> dict[int, T]:
    """Read an extracted line from the DCGM output and convert it to something usable."""
    results: dict[int, T] = {}
    for line in extracts:
        # the GPU information is stored as 'gpu="3"'
        # so we first split on 'gpu=' and then we split on the quotes
        gpu = int(line.split("gpu=")[1].split('"')[1])
        # the actual value is at the end of the line, separated by a space
        results[gpu] = converter(line.split(" ")[-1])
    return results


def render(all_values: dict[int, dict[str, str]]) -> None:
    """Render the extracted information."""
    header = (f"{name:>10}" for name in METRICS)
    print(f'GPU |{" | ".join(header)}')
    for gpu, values in all_values.items():
        row = (f"{values[name]:>10}" for name in METRICS)
        print(f'  {gpu} |{" | ".join(row)}')
