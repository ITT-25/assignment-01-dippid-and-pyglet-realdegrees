from __future__ import annotations
import math
from typing import Dict, List, Union
import click
import socket
import json
import time
from simpleeval import simple_eval

JSONType = Union[
    Dict[str, "JSONType"],
    List["JSONType"],
    float,
    str,
    bool,
    None
]

def eval_cfg(cfg: JSONType, t: float) -> JSONType:
    if isinstance(cfg, dict):
        if all([key in cfg for key in ["min", "max", "eval"]]):
            return eval_value(cfg["min"], cfg["max"], cfg["eval"], t)
        return {key: eval_cfg(value, t) for key, value in cfg.items()}

    elif isinstance(cfg, list):
        return [eval_cfg(item, t) for item in cfg]

    return cfg


def eval_value(min: float, max: float, eval: str, t: float) -> float:
    names = {'t': t}
    functions = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
        'abs': abs, 'pow': math.pow
    }
    # evaluate the expression and normalize it to the range [min, max]
    result = simple_eval(eval, functions=functions, names=names)
    normalized_result = result % 1
    return normalized_result * (max - min) + min


@click.command()
@click.option('--config', '-c', required=True, help='JSON string or @path/to/file.json')
@click.option('--verbose', '-v', required=False, is_flag=True, help='Enable to print messages')
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
