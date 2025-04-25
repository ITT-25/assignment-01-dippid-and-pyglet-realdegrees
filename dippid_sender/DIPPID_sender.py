from __future__ import annotations
import math
import click
import socket
import json
import time
from simpleeval import simple_eval
from typing import TypedDict
from typing import Dict
import random


class Config(TypedDict):
    interval: int
    ip: str
    port: int
    mocks: Dict[str, Dict[str, str]]


class EvaluatedConfig(Config):
    mocks: Dict[str, Dict[str, float]]


def get_data(mocks: Dict[str, Dict[str, str]], t: float) -> Dict[str, Dict[str, float]]:
    evaluated: Dict[str, Dict[str, float]] = {}

    for capability, values in mocks.items():
        evaluated[capability] = {}
        for value_name, leaf in values.items():
            if not isinstance(leaf, str):
                raise TypeError(
                    f"Invalid configuration for {capability}: {leaf}")
            else:
                evaluated[capability][value_name] = evaluate(leaf, t)

    return evaluated


def evaluate(math_expr: str, t: float) -> float:
    names = {'t': t}
    functions = {
        'sin': lambda n: 0.5*(1 + math.sin(2 * n * math.pi)), 'cos': lambda n: 0.5*(1 + math.cos(2 * n * math.pi)), 'tan': lambda n: 0.5*(1 + math.tan(2 * n * math.pi)),
        'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
        'abs': abs, 'pow': math.pow, 'random': lambda: random.uniform(0, 1)
    }
    return simple_eval(math_expr, functions=functions, names=names)


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

    ip, port, interval = cfg.get('ip', '127.0.0.1'), cfg.get(
        'port', 5700), cfg.get('interval', 100)
    if verbose:
        print(f"Sending to {ip}:{port} every {interval}ms")

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
