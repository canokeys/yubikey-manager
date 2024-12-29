from canokit.core import TRANSPORT, YUBIKEY
from canokit.management import CAPABILITY
from .. import condition

import pytest


VALID_LOCK_CODE = "a" * 32
INVALID_LOCK_CODE_NON_HEX = "z" * 32


def _fido_only(capabilities):
    return capabilities & ~(CAPABILITY.U2F | CAPABILITY.FIDO2) == 0


def not_sky(device, info):
    if info.is_sky:
        return False
    if device.transport == TRANSPORT.NFC:
        return not (
            info.serial is None
            and _fido_only(info.supported_capabilities[TRANSPORT.USB])
        )
    else:
        return device.pid.yubikey_type != YUBIKEY.SKY


class TestConfigUSB:
    @pytest.fixture(autouse=True)
    @condition.check(not_sky)
    @condition.min_version(5)
    def enable_all(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--enable-all", "-f")
        await_reboot()
        yield None
        ckman_cli("config", "usb", "--enable-all", "-f")
        await_reboot()

    @condition.capability(CAPABILITY.OTP, TRANSPORT.USB)
    def test_disable_otp(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--disable", "OTP", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "OTP" not in output

    @condition.capability(CAPABILITY.U2F, TRANSPORT.USB)
    def test_disable_u2f(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--disable", "U2F", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "FIDO U2F" not in output

    @condition.capability(CAPABILITY.OPENPGP, TRANSPORT.USB)
    def test_disable_openpgp(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--disable", "OPENPGP", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "OpenPGP" not in output

    @condition.capability(CAPABILITY.OPENPGP, TRANSPORT.USB)
    def test_disable_openpgp_alternative_syntax(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--disable", "openpgp", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "OpenPGP" not in output

    @condition.capability(CAPABILITY.PIV, TRANSPORT.USB)
    def test_disable_piv(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--disable", "PIV", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "PIV" not in output

    @condition.capability(CAPABILITY.OATH, TRANSPORT.USB)
    def test_disable_oath(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--disable", "OATH", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "OATH" not in output

    @condition.capability(CAPABILITY.FIDO2, TRANSPORT.USB)
    def test_disable_fido2(self, ckman_cli, await_reboot):
        ckman_cli("config", "usb", "--disable", "FIDO2", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "FIDO2" not in output

    @condition.capability(CAPABILITY.FIDO2, TRANSPORT.USB)
    def test_disable_and_enable(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli("config", "usb", "--disable", "FIDO2", "--enable", "FIDO2", "-f")
        with pytest.raises(SystemExit):
            ckman_cli("config", "usb", "--enable-all", "--disable", "FIDO2", "-f")

    def test_disable_all(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli(
                "config",
                "usb",
                "-d",
                "FIDO2",
                "-d",
                "U2F",
                "-d",
                "OATH",
                "-d",
                "OPENPGP",
                "-d",
                "PIV",
                "-d",
                "OTP",
            )

    @condition.capability(CAPABILITY.U2F, TRANSPORT.USB)
    def test_mode_command(self, ckman_cli, await_reboot):
        ckman_cli("config", "mode", "ccid", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "FIDO U2F" not in output
        assert "FIDO2" not in output
        assert "OTP" not in output

        ckman_cli("config", "mode", "otp", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "FIDO U2F" not in output
        assert "FIDO2" not in output
        assert "OpenPGP" not in output
        assert "PIV" not in output
        assert "OATH" not in output

        ckman_cli("config", "mode", "fido", "-f")
        await_reboot()
        output = ckman_cli("config", "usb", "--list").output
        assert "OTP" not in output
        assert "OATH" not in output
        assert "PIV" not in output
        assert "OpenPGP" not in output


class TestConfigNFC:
    @pytest.fixture(autouse=True)
    @condition.check(not_sky)
    @condition.min_version(5)
    @condition.has_transport(TRANSPORT.NFC)
    def enable_all_nfc(self, ckman_cli, await_reboot):
        ckman_cli("config", "nfc", "--enable-all", "-f")
        await_reboot()
        yield None
        ckman_cli("config", "nfc", "--enable-all", "-f")
        await_reboot()

    @condition.capability(CAPABILITY.OTP, TRANSPORT.NFC)
    def test_disable_otp(self, ckman_cli):
        ckman_cli("config", "nfc", "--disable", "OTP", "-f")
        output = ckman_cli("config", "nfc", "--list").output
        assert "OTP" not in output

    @condition.capability(CAPABILITY.U2F, TRANSPORT.NFC)
    def test_disable_u2f(self, ckman_cli):
        ckman_cli("config", "nfc", "--disable", "U2F", "-f")
        output = ckman_cli("config", "nfc", "--list").output
        assert "FIDO U2F" not in output

    @condition.capability(CAPABILITY.OPENPGP, TRANSPORT.NFC)
    def test_disable_openpgp(self, ckman_cli):
        ckman_cli("config", "nfc", "--disable", "OPENPGP", "-f")
        output = ckman_cli("config", "nfc", "--list").output
        assert "OpenPGP" not in output

    @condition.capability(CAPABILITY.PIV, TRANSPORT.NFC)
    def test_disable_piv(self, ckman_cli):
        ckman_cli("config", "nfc", "--disable", "PIV", "-f")
        output = ckman_cli("config", "nfc", "--list").output
        assert "PIV" not in output

    @condition.capability(CAPABILITY.OATH, TRANSPORT.NFC)
    def test_disable_oath(self, ckman_cli):
        ckman_cli("config", "nfc", "--disable", "OATH", "-f")
        output = ckman_cli("config", "nfc", "--list").output
        assert "OATH" not in output

    @condition.capability(CAPABILITY.FIDO2, TRANSPORT.NFC)
    def test_disable_fido2(self, ckman_cli):
        ckman_cli("config", "nfc", "--disable", "FIDO2", "-f")
        output = ckman_cli("config", "nfc", "--list").output
        assert "FIDO2" not in output

    @condition.transport(TRANSPORT.USB)
    def test_disable_all(self, ckman_cli):
        ckman_cli("config", "nfc", "--disable-all", "-f")
        output = ckman_cli("config", "nfc", "--list").output
        assert not output

    @condition.capability(CAPABILITY.FIDO2, TRANSPORT.NFC)
    def test_disable_and_enable(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli("config", "nfc", "--disable", "FIDO2", "--enable", "FIDO2", "-f")
        with pytest.raises(SystemExit):
            ckman_cli("config", "nfc", "--disable-all", "--enable", "FIDO2", "-f")
        with pytest.raises(SystemExit):
            ckman_cli("config", "nfc", "--enable-all", "--disable", "FIDO2", "-f")
        with pytest.raises(SystemExit):
            ckman_cli("config", "nfc", "--enable-all", "--disable-all", "FIDO2", "-f")


class TestConfigLockCode:
    @pytest.fixture(autouse=True)
    @condition.min_version(5)
    def preconditions(self):
        pass

    def test_set_lock_code(self, ckman_cli):
        ckman_cli("config", "set-lock-code", "--new-lock-code", VALID_LOCK_CODE)
        output = ckman_cli("info").output
        assert "Configured capabilities are protected by a lock code" in output
        ckman_cli("config", "set-lock-code", "-l", VALID_LOCK_CODE, "--clear")
        output = ckman_cli("info").output
        assert "Configured capabilities are protected by a lock code" not in output

    def test_set_invalid_lock_code(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli("config", "set-lock-code", "--new-lock-code", "aaaa")

        with pytest.raises(SystemExit):
            ckman_cli(
                "config", "set-lock-code", "--new-lock-code", INVALID_LOCK_CODE_NON_HEX
            )
