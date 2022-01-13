# smawg

Python backend for
[Small World](https://en.m.wikipedia.org/wiki/Small_World_(board_game))
board game,
designed for writing third-party AIs and clients around it.

It has a bundled CLI client for interactive use
and easy interoperability with other programming languages.

## Features:

* High level API for performing in-game actions and getting current stats.
    * Imperatively or by setting hooks on game events.
* Automatic maintainance of game state (manages tokens, calculates score, etc).
* Automatic checks for violation of the rules.
* Support for custom maps, races, powers and other constants/resources.
* Deterministic or randomized outcomes.

### **Missing essential features** (in progress):

* A lot of core concepts: maps, attacking, redeploying, rewarding...
* Implementation of unique race abilities.

### Future plans:

* JSONs with full sets of races and abilities, original maps, etc.
* Options for more machine-readable CLI output.
* In-house AI and GUI examples.
* Support for plugins with new ability types ???


# Requirements

* Python 3.9+ (currently, only 3.9 is tested)
* [tabulate](https://github.com/astanin/python-tabulate) (for `smawg.cli`)


# Installation

* `git clone https://github.com/Expurple/smawg.git`
* `cd smawg/`
* `pip install --user .`


# Usage

## As a CLI app

Generally, it's invoked as
* `python3 -m smawg.cli`

A simple example set of options would be
* `python3 -m smawg.cli --players=2 assets/tiny.json`

It should guide you through the usage.

## As a library, imperative-style

```python
import json

# These two classes are really everything you need from the library.
#
# If you're dealing with (possibly invalid) user input,
# you might want to also import `RulesViolation` for catching it.
from smawg.engine import Data, Game


# If you want, you can directly construct `data_json` dict
# instead of reading from file.
with open('some/path/to/data.json') as data_file:
    data_json = json.load(data_file)

data = Data(data_json)

# Provide different arguments, if needed.
game = Game(data, n_players=2)
# Call `game` methods to perform actions.
# Read `game` properties to monitor the game state.
# See `help(Game)` for more info.
```

You can also find "real world" examples in
[cli.py](./smawg/cli.py) and [test_engine.py](./smawg/tests/test_engine.py)

## As a library, hooks-style

See [docs/hooks.md](./docs/hooks.md)


# Contributing

Feel free to open a
[Github issue](https://github.com/Expurple/smawg/issues/new/choose)
or contact me personally.

If you wish to participate in development, this should get you started:
* Fork this repo on Github.
* `git clone git@github.com:YOUR-USERNAME/smawg.git`
* `cd smawg/`
* `pip install --user .[dev]`
* `bin/add-pre-commit-hook.sh`

Any contributions are welcome, but [missing featues](##Features:) and
[open issues](https://github.com/Expurple/smawg/issues) should be prioritized.

Before submitting a pull request, please test and document your changes.

## Tests

Can be run using the standard library's
* `python3 -m unittest discover smawg/tests/`
* or any other test runner that supports `unittest` format.


# Contacts

* **Home page** - [smawg](https://github.com/expurple/smawg)

* **Author** - Dmitry Alexandrov <adk230@yandex.ru\>


# Licence

Copyright (c) 2022 Dmitry Alexandrov.

Licensed under [GPL v.3](./LICENSE)

This copyright only applies to the code and other documents in this repository,
**not** the concept, title or any other property of the original game.
