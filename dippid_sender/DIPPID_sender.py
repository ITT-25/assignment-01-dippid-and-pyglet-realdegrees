from __future__ import annotations
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

def eval_cfg(cfg: JSONType, t: float) -> JSONType:

    if isinstance(cfg, dict):
        if set(cfg.keys()) == {"min", "max", "eval"}:
            return eval_value(cfg["min"], cfg["max"], cfg["eval"], t)
        return {key: eval_cfg(value, t) for key, value in cfg.items()}

    elif isinstance(cfg, list):
        return [eval_cfg(item, t) for item in cfg]

    return cfg

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
