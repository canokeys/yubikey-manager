from canokit.management import CAPABILITY
from ... import condition
import pytest


@pytest.fixture(autouse=True)
@condition.capability(CAPABILITY.PIV)
def ensure_piv(ckman_cli):
    ckman_cli("piv", "reset", "-f")
