from __future__ import annotations
import math
import click
import socket
import json
import time
from simpleeval import simple_eval
from typing import TypedDict
from typing import Dict
from GUI import Visualizer
import random

class ValueConfig(TypedDict):
    min: float
    max: float
    eval: str


class Config(TypedDict):
    interval: int
    ip: str
    port: int
    mocks: Dict[str, Dict[str, ValueConfig]]


class EvaluatedConfig(Config):
    mocks: Dict[str, Dict[str, float]]


def eval_cfg(mocks: Dict[str, Dict[str, ValueConfig]], t: float) -> Dict[str, Dict[str, float]]:
    evaluated: Dict[str, Dict[str, float]] = {}

    for capability, values in mocks.items():
        evaluated[capability] = {}
        for value_name, leaf in values.items():
            try:
                parsed_leaf = ValueConfig(**leaf)
                evaluated[capability][value_name] = eval_leaf(parsed_leaf, t)
            except TypeError:
                raise TypeError(
                    f"Invalid configuration for {capability}: {leaf}")

            
    return evaluated


def eval_leaf(leaf: ValueConfig, t: float) -> float:
    names = {'t': t}
    functions = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
        'abs': abs, 'pow': math.pow, 'random': lambda: random.uniform(0, 1)
    }
    # evaluate the expression and normalize it to the range [min, max]
    result = simple_eval(leaf['eval'], functions=functions, names=names)
    normalized_result = (result + 1) / 2  # normalize to [0, 1]
    return normalized_result * (leaf['max'] - leaf['min']) + leaf['min']


@click.command()
@click.option('--config', '-c', required=True, help='JSON string or @path/to/file.json')
@click.option('--verbose', '-v', required=False, is_flag=True, help='Enable to print messages')
@click.option('--gui', '-g', required=False, is_flag=True, help='Enable to open a GUI showing the data')
def run(config: str, verbose: bool, gui: bool):
    cfg: Config = {}
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
    visualizer = Visualizer(cfg["mocks"]) if gui else None

    while True:
        t = (time.time() - start_time)
        payload = eval_cfg(cfg["mocks"], t)

        message = json.dumps(payload)
        if verbose:
            print('→', message)

        if visualizer:
            visualizer.update(payload)

        sock.sendto(message.encode(), (ip, port))

        time.sleep(interval / 1000)


if __name__ == "__main__":
    run()
