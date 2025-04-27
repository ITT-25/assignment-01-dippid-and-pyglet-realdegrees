from __future__ import annotations
from collections import deque
import math
import click
import socket
import json
import time
from simpleeval import simple_eval
from typing import Optional, TypedDict
from typing import Dict
import random


DEFAULT_PORT = 5700
DEFAULT_IP = "127.0.0.1"
DEFAULT_INTERVAL = 50


class ButtonState:
    """Helper class to persist buttons across multiple loops. Stores the last 3 values to determine if the curve has flipped direction."""

    def __init__(self, name: str, expr: str):
        self.name = name
        self.expr = expr
        self.values = deque(maxlen=3)

    def update(self, t: float) -> bool:
        val = evaluate_expr(self.expr, t)
        self.values.appendleft(val)
        if len(self.values) < 3:
            return False
        # Detect a local maximum
        return self.values[0] < self.values[1] > self.values[2]


class Config(TypedDict):
    interval: int
    ip: str
    port: int
    mocks: MockConfig


MockConfig = Dict[str, Dict[str, str] | str]
MockData = Dict[str, Dict[str, float] | float]


def evaluate_expr(math_expr: str, t: float) -> float:
    """Evaluates a math expression with the given time value. Supports basic math functions."""
    functions = {
        "sin": lambda n: 0.5 * (1 + math.sin(2 * math.pi * n)),
        "cos": lambda n: 0.5 * (1 + math.cos(2 * math.pi * n)),
        "tan": lambda n: 0.5 * (1 + math.tan(2 * math.pi * n)),
        "sqrt": math.sqrt,
        "log": math.log,
        "exp": math.exp,
        "abs": abs,
        "pow": math.pow,
        "random": lambda: random.random(),
    }
    try:
        return simple_eval(math_expr, functions=functions, names={"t": t})
    except Exception:
        print(f"Unable to evaluate '{math_expr}'")
        return 0.0


@click.command()
@click.option(
    "--config", "-c", required=True, help="JSON string or path/to/file.json", type=str
)
@click.option(
    "--verbose", "-v", required=False, is_flag=True, help="Enable to print messages"
)
@click.option(
    "--truncate",
    "-t",
    required=False,
    help="Truncate values to this many decimal places",
    type=int,
)
def run(config: str, verbose: bool, truncate: Optional[int]):
    # Attempt to load the config from a JSON string or file, exit if it fails
    cfg: Config = {}
    try:
        cfg = json.loads(config)
    except json.JSONDecodeError:
        try:
            with open(config) as f:
                cfg = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {config}")

    # Retrieve config values with defaults
    ip = cfg.get("ip", DEFAULT_IP)
    port = cfg.get("port", DEFAULT_PORT)
    interval = cfg.get("interval", DEFAULT_INTERVAL)
    mocks = cfg.get("mocks", {})

    if verbose:
        print(
            f"Sending to {ip}:{port} every {interval}ms\nConfig:\n{json.dumps(mocks, indent=2)}"
        )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start = time.time()
    # Store button states to be able to detect button presses
    buttons: Dict[str, ButtonState] = {}

    while True:
        # Store the time since start for capability evaluations
        t = time.time() - start
        data: MockData = {}

        # Build each capability from the config and time
        for capability, value in mocks.items():
            sub = build_capability(capability, value, t, truncate, buttons)
            data[capability] = sub.get(None) if None in sub else sub

        # Send the data
        msg = json.dumps(data)
        if verbose:
            print(
                f"\nMockData at {f'{t // 3600:02.0f}:{t % 3600 // 60:02.0f}:{t % 60:06.3f}'}\n",
                json.dumps(data, indent=4),
            )
        sock.sendto(msg.encode(), (ip, port))
        time.sleep(interval / 1000)


def build_capability(
    capability: str,
    value: str | Dict[str, str],
    t: float,
    truncate: Optional[int],
    buttons: Dict[str, ButtonState],
) -> Dict[str, float]:
    """Builds a capability from the given value. If the value is a string, it is treated as a single value capability with no subkeys."""

    # Wrap the value in a dict with None key if it's a string
    if isinstance(value, str):
        value = {None: value}

    # Evaluate each subkey
    sub: Dict[str, float] = {}
    for key, expr in value.items():
        if not isinstance(expr, str):
            raise ValueError(f"Value for '{capability}.{key}' is not a string: {expr}")

        if expr.startswith("button:"):
            # Create or get the existing button state
            button_name = (capability + "." + key) if key else capability
            button = buttons.get(button_name, None) or ButtonState(
                button_name, expr.split(":", 1)[1]
            )

            if button_name not in buttons:
                buttons[button_name] = button

            # Update the button state and set result
            button_pressed = button.update(t)
            result = 1 if button_pressed else 0
        else:
            # Default math expression evaluation
            result = evaluate_expr(expr, t)

        # Truncate the result if specified
        if truncate is not None and truncate >= 0:
            result = round(result, truncate)

        sub[key] = result
    return sub


if __name__ == "__main__":
    run()
