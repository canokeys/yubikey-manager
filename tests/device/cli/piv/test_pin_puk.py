from .util import (
    old_new_new,
    DEFAULT_PIN,
    NON_DEFAULT_PIN,
    DEFAULT_PUK,
    NON_DEFAULT_PUK,
    DEFAULT_MANAGEMENT_KEY,
)
from ckman.piv import OBJECT_ID_PIVMAN_DATA, PivmanData

import pytest
import re


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

    def test_unblock_pin(self, ckman_cli):
        for _ in range(3):
            with pytest.raises(SystemExit):
                ckman_cli(
                    "piv",
                    "access",
                    "change-pin",
                    "-P",
                    NON_DEFAULT_PIN,
                    "-n",
                    DEFAULT_PIN,
                )

        o = ckman_cli("piv", "info").output
        assert re.search(r"PIN tries remaining:\s+0(/3)?", o)

        with pytest.raises(SystemExit):
            ckman_cli(
                "piv", "access", "change-pin", "-p", DEFAULT_PIN, "-n", NON_DEFAULT_PIN
            )

        o = ckman_cli(
            "piv", "access", "unblock-pin", "-p", DEFAULT_PUK, "-n", DEFAULT_PIN
        ).output
        assert "PIN unblocked" in o
        o = ckman_cli("piv", "info").output
        assert re.search(r"PIN tries remaining:\s+3(/3)?", o)


class TestSetRetries:
    def test_set_retries(self, ckman_cli, version):
        ckman_cli(
            "piv",
            "access",
            "set-retries",
            "5",
            "6",
            input=f"{DEFAULT_MANAGEMENT_KEY}\n{DEFAULT_PIN}\ny\n",
        )

        o = ckman_cli("piv", "info").output
        assert re.search(r"PIN tries remaining:\s+5(/5)?", o)
        if version >= (5, 3):
            assert re.search(r"PUK tries remaining:\s+6/6", o)

    def test_set_retries_clears_puk_blocked(self, ckman_cli):
        for _ in range(3):
            with pytest.raises(SystemExit):
                ckman_cli(
                    "piv",
                    "access",
                    "change-puk",
                    "-p",
                    NON_DEFAULT_PUK,
                    "-n",
                    DEFAULT_PUK,
                )

        pivman = PivmanData()
        pivman.puk_blocked = True

        ckman_cli(
            "piv",
            "objects",
            "import",
            hex(OBJECT_ID_PIVMAN_DATA),
            "-",
            "-m",
            DEFAULT_MANAGEMENT_KEY,
            input=pivman.get_bytes(),
        )

        o = ckman_cli("piv", "info").output
        assert "PUK is blocked" in o

        ckman_cli(
            "piv",
            "access",
            "set-retries",
            "3",
            "3",
            input=f"{DEFAULT_MANAGEMENT_KEY}\n{DEFAULT_PIN}\ny\n",
        )

        o = ckman_cli("piv", "info").output
        assert "PUK is blocked" not in o
