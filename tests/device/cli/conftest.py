from canokit.core import TRANSPORT
from ckman._cli.__main__ import cli, _DefaultFormatter
from ckman._cli.aliases import apply_aliases
from ckman._cli.util import CliFail
from click.testing import CliRunner
from functools import partial
import logging
import pytest


@pytest.fixture(scope="module")
def ckman_cli(device, info):
    if device.transport == TRANSPORT.NFC:
        return partial(_ckman_cli, "--reader", device.reader.name)
    elif info.serial is not None:
        return partial(_ckman_cli, "--device", info.serial)
    else:
        return _ckman_cli


def _ckman_cli(*argv, **kwargs):
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(_DefaultFormatter())
    logging.getLogger().addHandler(handler)

    argv = apply_aliases(["ckman"] + [str(a) for a in argv])
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli, argv[1:], obj={}, **kwargs)
    if result.exit_code != 0:
        if isinstance(result.exception, CliFail):
            raise SystemExit()
        raise result.exception
    return result
