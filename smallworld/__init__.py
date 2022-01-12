"""Backend engine for Small World board game.

See https://github.com/expurple/smallworld for more info.
"""

import importlib.metadata
from configparser import ConfigParser
from pathlib import Path


_PACKAGE_DIR = Path(__file__).parent.resolve()
"""Path to `smallworld` package.

This in an **unreliable** helper for development and testing.

If you've a user and installed `smallworld` through `pip` or `setup.py`,
you should use this instead:
```
import sysconfig
smallworld_package_dir = sysconfig.get_path("smallworld")
```
"""

_REPO_DIR = _PACKAGE_DIR.parent
"""Path to checked out `smallworld` repository.

This in an **unreliable** helper for development and testing.
It only works correctly if you execute/import modules
from a local `smallworld` repository.

If you've installed `smallworld` through `pip` or `setup.py`,
you shouldn't use this.
"""

_EXAMPLES_DIR = Path(f"{_REPO_DIR}/examples")
"""Path to `examples/` directory in checked out `smallworld` repository.

This in an **unreliable** helper for development and testing.
It only works correctly if you execute/import modules
from a local `smallworld` repository.

If you've installed `smallworld` through `pip` or `setup.py`,
you shouldn't use this.
"""

VERSION: str
"""The version of `smallworld` package as an `"x.y.z"` format string."""

try:
    # This will work if the package is installed (e.g. with `setup.py`, `pip`).
    VERSION = importlib.metadata.version("smallworld")
except importlib.metadata.PackageNotFoundError:
    # If `smallworld` is not installed,
    # Assume that we're in a repo and try to fall back on local `setup.cfg`:
    cfg = ConfigParser()
    cfg.read(f"{_REPO_DIR}/setup.cfg")
    VERSION = cfg["metadata"]["version"]
    del cfg


# Clean up namespace
del ConfigParser, importlib, Path
