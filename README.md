# smallworld

Python backend for
[Small World](https://en.m.wikipedia.org/wiki/Small_World_(board_game))
board game,
designed for writing third-party AIs and clients around it.

### Features:

* API for performing in-game actions and getting current stats.
* Automatic maintainance of game state (manages tokens, calculates score, etc).
* Automatic checks for violation of the rules.
* Support for custom maps, races, powers and other constants/resources.
* Deterministic or randomized outcomes.

### **Missing essential features** (in progress):

* A bunch of core mechanics: attacking, redeployment, rewarding, etc.
* Example JSONs with full sets of races and abilities, full maps, etc.
* Implementation of unique race abilities.

### Future plans:

* Better documentation for code and JSONs.
* More tests.
* Callback slots for AIs.
* In-house AI and GUI examples.
* CLI for easy interoperability with AIs and GUIs written in other languages.
* Support for plugins with new ability types ???


# Requirements

* Python 3.9+ (other versions not tested).

No additional libraries or tools are required to use the engine and run
tests/examples.

Although, you'll need `mypy` and `flake8`,
if you wish to [contribute](#Contributing).


# Usage

Minimal example of a normal 2-player game:

```python
import json

from smallworld.engine import Data, Game


with open('some/path/to/data.json') as data_file:
    data_json = json.load(data_file)
data = Data(data_json)
game = Game(data, n_players=2)
# Call `game` methods to perform actions.
# Read `game` properties to monitor the game state.
# See `help(Game)` for more info.
```


# Contributing

Any contributions are welcome, but [missing featues](#smallworld) should be
prioritized.

Before submitting, please make sure that:
* Your code uses type hinting.
* `mypy` doesn't report any errors (when run with default options).
* `flake8` doesn't report any errors (when run with default options).

The easiest way to do that is to configure a pre-commit hook.

On *nix systems, you can do that by executing `./add-pre-commit-hook.sh`


# Contacts

* **Home page** - [smallworld](https://github.com/expurple/smallworld)

* **Author** - Dmitry Alexandrov <adk230@yandex.ru\>


# Licence

Copyright (c) 2022 Dmitry Alexandrov.

Licensed under [GPL v.3](./LICENSE)

This copyright only applies to the code and other documents in this repository,
**not** the concept, title or any other property of the original game.
