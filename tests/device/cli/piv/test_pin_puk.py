from .util import (
    old_new_new,
    DEFAULT_PIN,
    NON_DEFAULT_PIN,
    DEFAULT_PUK,
    NON_DEFAULT_PUK,
)

import pytest


class TestPin:
    def test_change_pin(self, ckman_cli):
        ckman_cli(
            "piv", "access", "change-pin", "-P", DEFAULT_PIN, "-n", NON_DEFAULT_PIN
        )
        ckman_cli(
            "piv", "access", "change-pin", "-P", NON_DEFAULT_PIN, "-n", DEFAULT_PIN
        )

    def test_change_pin_prompt(self, ckman_cli):
        ckman_cli(
            "piv",
            "access",
            "change-pin",
            input=old_new_new(DEFAULT_PIN, NON_DEFAULT_PIN),
        )
        ckman_cli(
            "piv",
            "access",
            "change-pin",
            input=old_new_new(NON_DEFAULT_PIN, DEFAULT_PIN),
        )


class TestPuk:
    def test_change_puk(self, ckman_cli):
        o1 = ckman_cli(
            "piv", "access", "change-puk", "-p", DEFAULT_PUK, "-n", NON_DEFAULT_PUK
        ).output
        assert "New PUK set." in o1

        o2 = ckman_cli(
            "piv", "access", "change-puk", "-p", NON_DEFAULT_PUK, "-n", DEFAULT_PUK
        ).output
        assert "New PUK set." in o2

        with pytest.raises(SystemExit):
            ckman_cli(
                "piv", "access", "change-puk", "-p", NON_DEFAULT_PUK, "-n", DEFAULT_PUK
            )

    def test_change_puk_prompt(self, ckman_cli):
        ckman_cli(
            "piv",
            "access",
            "change-puk",
            input=old_new_new(DEFAULT_PUK, NON_DEFAULT_PUK),
        )
        ckman_cli(
            "piv",
            "access",
            "change-puk",
            input=old_new_new(NON_DEFAULT_PUK, DEFAULT_PUK),
        )
