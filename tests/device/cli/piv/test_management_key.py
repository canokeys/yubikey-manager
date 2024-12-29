from .util import (
    old_new_new,
    DEFAULT_PIN,
    DEFAULT_MANAGEMENT_KEY,
    NON_DEFAULT_MANAGEMENT_KEY,
)
import re
import pytest


class TestManagementKey:
    def test_change_management_key_force_fails_without_generate(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli(
                "piv",
                "access",
                "change-management-key",
                "-P",
                DEFAULT_PIN,
                "-m",
                DEFAULT_MANAGEMENT_KEY,
                "-f",
            )

    def test_change_management_key_protect_random(self, ckman_cli):
        ckman_cli(
            "piv",
            "access",
            "change-management-key",
            "-p",
            "-P",
            DEFAULT_PIN,
            "-m",
            DEFAULT_MANAGEMENT_KEY,
        )
        output = ckman_cli("piv", "info").output
        assert "Management key is stored on the YubiKey, protected by PIN" in output

        with pytest.raises(SystemExit):
            # Should fail - wrong current key
            ckman_cli(
                "piv",
                "access",
                "change-management-key",
                "-p",
                "-P",
                DEFAULT_PIN,
                "-m",
                DEFAULT_MANAGEMENT_KEY,
            )

        # Should succeed - PIN as key
        ckman_cli("piv", "access", "change-management-key", "-p", "-P", DEFAULT_PIN)

    def test_change_management_key_protect_prompt(self, ckman_cli):
        ckman_cli(
            "piv",
            "access",
            "change-management-key",
            "-p",
            "-P",
            DEFAULT_PIN,
            input=DEFAULT_MANAGEMENT_KEY,
        )
        output = ckman_cli("piv", "info").output
        assert "Management key is stored on the YubiKey, protected by PIN" in output

        with pytest.raises(SystemExit):
            # Should fail - wrong current key
            ckman_cli(
                "piv",
                "access",
                "change-management-key",
                "-p",
                "-P",
                DEFAULT_PIN,
                "-m",
                DEFAULT_MANAGEMENT_KEY,
            )

        # Should succeed - PIN as key
        ckman_cli("piv", "access", "change-management-key", "-p", "-P", DEFAULT_PIN)

    def test_change_management_key_no_protect_generate(self, ckman_cli):
        output = ckman_cli(
            "piv", "access", "change-management-key", "-m", DEFAULT_MANAGEMENT_KEY, "-g"
        ).output

        assert re.match(
            r"^Generated management key: [a-f0-9]{48}$", output, re.MULTILINE
        )

        output = ckman_cli("piv", "info").output
        assert "Management key is stored on the YubiKey" not in output

    def test_change_management_key_no_protect_arg(self, ckman_cli):
        output = ckman_cli(
            "piv",
            "access",
            "change-management-key",
            "-m",
            DEFAULT_MANAGEMENT_KEY,
            "-n",
            NON_DEFAULT_MANAGEMENT_KEY,
        ).output
        assert "" == output
        output = ckman_cli("piv", "info").output
        assert "Management key is stored on the YubiKey" not in output

        with pytest.raises(SystemExit):
            ckman_cli(
                "piv",
                "access",
                "change-management-key",
                "-m",
                DEFAULT_MANAGEMENT_KEY,
                "-n",
                NON_DEFAULT_MANAGEMENT_KEY,
            )

        output = ckman_cli(
            "piv",
            "access",
            "change-management-key",
            "-m",
            NON_DEFAULT_MANAGEMENT_KEY,
            "-n",
            DEFAULT_MANAGEMENT_KEY,
        ).output
        assert "" == output

    def test_change_management_key_no_protect_arg_bad_length(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli(
                "piv",
                "access",
                "change-management-key",
                "-m",
                DEFAULT_MANAGEMENT_KEY,
                "-n",
                "10020304050607080102030405060708",
            )

    def test_change_management_key_no_protect_prompt(self, ckman_cli):
        output = ckman_cli(
            "piv",
            "access",
            "change-management-key",
            input=old_new_new(DEFAULT_MANAGEMENT_KEY, NON_DEFAULT_MANAGEMENT_KEY),
        ).output
        assert "Generated" not in output
        output = ckman_cli("piv", "info").output
        assert "Management key is stored on the YubiKey" not in output

        with pytest.raises(SystemExit):
            ckman_cli(
                "piv",
                "access",
                "change-management-key",
                input=old_new_new(DEFAULT_MANAGEMENT_KEY, NON_DEFAULT_MANAGEMENT_KEY),
            )

        ckman_cli(
            "piv",
            "access",
            "change-management-key",
            input=old_new_new(NON_DEFAULT_MANAGEMENT_KEY, DEFAULT_MANAGEMENT_KEY),
        )
        assert "Generated" not in output

    def test_change_management_key_new_key_conflicts_with_generate(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli(
                "piv",
                "access",
                "change-management-key",
                "-m",
                DEFAULT_MANAGEMENT_KEY,
                "-n",
                NON_DEFAULT_MANAGEMENT_KEY,
                "-g",
            )
