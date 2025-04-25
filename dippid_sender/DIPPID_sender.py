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


class ButtonState:
    def __init__(self, name: str, expr: str):
        self.name = name
        self.expr = expr
        self.state = False
        self.value_history = deque(maxlen=3)

    def set_value(self, value: float):
        self.value_history.appendleft(value)

    def get_value(self) -> Optional[float]:
        if len(self.value_history) == 0:
            return None
        else:
            return self.value_history[0]

    def check_value_flip(self) -> bool:
        """Check if the value has bounced at the upper limit"""
        if len(self.value_history) < 3:
            return False
        else:
            return self.value_history[0] < self.value_history[1] and self.value_history[1] > self.value_history[2]


button_states: list[ButtonState] = list()


class Config(TypedDict):
    interval: int
    ip: str
    port: int
    mocks: Dict[str, Dict[str, str]]


class EvaluatedConfig(Config):
    mocks: Dict[str, Dict[str, float]]


def get_data(mocks: Dict[str, Dict[str, str]], t: float) -> Dict[str, Dict[str, float | ButtonState]]:
    evaluated: Dict[str, Dict[str, float | ButtonState]] = {}

    def evaluate_leaf(name: str, leaf: str) -> float:
        # Default math evaluation
        if not leaf.startswith('button:'):
            evaluated[capability][name] = evaluate_math_expr(leaf, t)
            return

        # Special case for buttons
        button = next((b for b in button_states if b.name == name), None)
        if not button:
            button = ButtonState(name, leaf.split(':', 1)[1])
            button_states.append(button)

        button.set_value(evaluate_math_expr(button.expr, t))
        evaluated[capability][name] = 1 if button.check_value_flip() else 0

    for capability, value in mocks.items():
        evaluated[capability] = {}

        if isinstance(value, str):
            evaluate_leaf(capability, value)
            continue
        elif isinstance(value, dict):
            for value_name, leaf in value.items():
                if not isinstance(leaf, str):
                    raise TypeError(
                        f"Invalid configuration for {capability}.{value_name}: Expected str, got {type(leaf)}")
                evaluate_leaf(value_name, leaf)
        else:
            raise TypeError(
                f"Invalid configuration for {capability}: Expected str or dict, got {type(value)}")

    return evaluated


def evaluate_math_expr(math_expr: str, t: float) -> float:
    names = {'t': t}
    functions = {
        'sin': lambda n: 0.5*(1 + math.sin(2 * n * math.pi)), 'cos': lambda n: 0.5*(1 + math.cos(2 * n * math.pi)), 'tan': lambda n: 0.5*(1 + math.tan(2 * n * math.pi)),
        'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
        'abs': abs, 'pow': math.pow, 'random': lambda: random.uniform(0, 1)
    }
    try:
        return simple_eval(math_expr, functions=functions, names=names)
    except Exception:
        print(f"Unable to evaluate '{math_expr}'")
        return 0.0

@click.command()
@click.option('--config', '-c', required=True, help='JSON string or @path/to/file.json')
@click.option('--verbose', '-v', required=False, is_flag=True, help='Enable to print messages')
def run(config: str, verbose: bool):
    cfg: Config = {}
    try:
        cfg = json.loads(config)
    except json.JSONDecodeError:
        try:
            with open(config) as f:
                cfg = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {config}")

    ip, port, interval, mocks = cfg.get('ip', '127.0.0.1'), cfg.get(
        'port', 5700), cfg.get('interval', 100), cfg.get('mocks', {})
    if verbose:
        print(f"Sending to {ip}:{port} every {interval}ms\nConfig:\n{json.dumps(mocks, indent=2)}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()

    while True:
        t = (time.time() - start_time)
        payload = get_data(cfg["mocks"], t)
        message = json.dumps(payload)
        if verbose:
            print('→', message)

        sock.sendto(message.encode(), (ip, port))

        time.sleep(interval / 1000)


if __name__ == "__main__":
    run()
