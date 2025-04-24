from __future__ import annotations
import enum
import math
from typing import Callable, Dict, List, Union
import click
import socket
import json
import time

JSONType = Union[
    Dict[str, "JSONType"],
    List["JSONType"],
    float,
    str,
    bool,
    None
]


class ECurve(enum.Enum):
    Sin = "sin"
    Cos = "cos"
    Tan = "tan"
    Sqrt = "sqrt"
    Log = "log"
    Exp = "exp"
    Abs = "abs"


# Source: The normalization of the curves was done by github copilot
# Prompt: "/edit  some of these are returned in radians however I need the result to always be between 1 and 0 based on the time so the result basically goes along the curve as t increases"
curves: dict[ECurve, Callable[[float], float]] = {
    ECurve.Sin: lambda t: (math.sin(t) + 1) / 2,
    ECurve.Cos: lambda t: (math.cos(t) + 1) / 2,
    ECurve.Tan: lambda t: (math.tan(t) % 1 + 1) / 2,  # Normalize to [0, 1]
    # Ensure non-negative
    ECurve.Sqrt: lambda t: (math.sqrt(t % 1) if t % 1 >= 0 else 0),
    # Avoid log(0)
    ECurve.Log: lambda t: (math.log(t % 1 + 1) if t % 1 > 0 else 0),
    ECurve.Exp: lambda t: (math.exp(t % 1) % 1),  # Normalize to [0, 1]
    ECurve.Abs: lambda t: (abs(t) % 1),  # Example using abs of sin
}


def eval_cfg(cfg: JSONType, t: float) -> JSONType:

    if isinstance(cfg, dict):
        if set(cfg.keys()) == {"min", "max", "eval"}:
            return eval_value(cfg["min"], cfg["max"], cfg["eval"], t)
        return {key: eval_cfg(value, t) for key, value in cfg.items()}

    elif isinstance(cfg, list):
        return [eval_cfg(item, t) for item in cfg]

    return cfg


def eval_value(min: float, max: float, eval_curve: str, t: float) -> float:
    # evaluate the curve
    try:
        fn = ECurve(eval_curve)
        result = curves[fn](t)
    except ValueError as curve_not_found_error:
        raise ValueError(
            f"eval must be one of {list(ECurve.__members__.keys())}") from curve_not_found_error
        
    # interpolate the result to the range [min, max]
    result = result * (max - min) + min
    return result


@click.command()
@click.option('--config', '-c', required=True, help='JSON string or @path/to/file.json')
@click.option('--verbose', '-v', required=True, is_flag=True, help='Enable to print messages')
def run(config: str, verbose: bool):
    cfg: JSONType = {}
    try:
        cfg = json.loads(config)
    except json.JSONDecodeError:
        try:
            with open(config) as f:
                cfg = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {config}")

    ip, port, interval = cfg.get('ip', '127.0.0.1'), cfg.get(
        'port', 5700), cfg.get('interval', 100)
    if verbose:
        print(f"Sending to {ip}:{port} every {interval}ms")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()

    while True:
        t = (time.time() - start_time)
        payload = eval_cfg(cfg["mocks"], t)

        message = json.dumps(payload)
        if verbose:
            print('→', message)
        sock.sendto(message.encode(), (ip, port))

        time.sleep(interval / 1000)


if __name__ == "__main__":
    run()
