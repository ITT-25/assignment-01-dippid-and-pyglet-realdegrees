[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/auQkrO9W)

# Setup

1. Clone the repo
2. `cd` into the root folder
3. Setup a virtual env
4. `pip install -r requirements.txt`

# dippid_sender

## Usage

```sh
python dippid_sender/DIPPID_sender.py -c dippid_sender/mock_config.json -v
```

Config can be adjusted to change mock data.  
The `mock` field of the config should mirror the desired json object but replace the actual values with a string that holds a math equation.  
This math equation is evaluated each tick based on the current time. Use the variable `t` and functions like `sin()`, `cos()` etc. to build an evaluation function.  
Prefixing the string with `button:` (e.g. `"button: sin(t) * 4 - 2"`) to send a button press every time the supplied math function bounces at the upper limit.

# 2d_game

## Usage

```sh
python 2d_game/game.py
```

Follow the prompts at the top of the window, use a `DIPPID.UDPSensor` to connect to the game (requires `gravity` capability with a `z` value and a `button_1` capability).  
If only one player is connected the game can be played against a simple NPC, two connected players can play against each other.  