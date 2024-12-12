# -*- coding: utf-8 -*-

from ckman.oath import STEAM_CHAR_TABLE
from canokit.management import CAPABILITY
from .. import condition
from base64 import b32encode
import pytest


URI_HOTP_EXAMPLE = (
    "otpauth://hotp/Example:demo@example.com?"
    "secret=JBSWY3DPK5XXE3DEJ5TE6QKUJA======&issuer=Example&counter=1"
)

URI_TOTP_EXAMPLE = (
    "otpauth://totp/ACME%20Co:john.doe@email.com?"
    "secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=ACME%20Co"
    "&algorithm=SHA1&digits=6&period=30"
)

URI_TOTP_EXAMPLE_B = (
    "otpauth://totp/ACME%20Co:john.doe.b@email.com?"
    "secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=ACME%20Co"
    "&algorithm=SHA1&digits=6&period=30"
)

URI_TOTP_EXAMPLE_EXTRA_PARAMETER = (
    "otpauth://totp/ACME%20Co:john.doe.extra@email.com?"
    "secret=HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ&issuer=ACME%20Co"
    "&algorithm=SHA1&digits=6&period=30&skid=JKS3424d"
)

PASSWORD = "aaaa"


@pytest.fixture(autouse=True)
@condition.capability(CAPABILITY.OATH)
def preconditions(ckman_cli):
    ckman_cli("oath", "reset", "-f")


class TestOATH:
    def test_oath_info(self, ckman_cli):
        output = ckman_cli("oath", "info").output
        assert "version:" in output

    @condition.yk4_fips(False)
    def test_info_does_not_indicate_fips_mode_for_non_fips_key(self, ckman_cli):
        info = ckman_cli("oath", "info").output
        assert "FIPS:" not in info

    def test_oath_add_credential(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "test-name", "abba")
        creds = ckman_cli("oath", "accounts", "list").output
        assert "test-name" in creds

    def test_oath_add_credential_prompt(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "test-name-2", input="abba")
        creds = ckman_cli("oath", "accounts", "list").output
        assert "test-name-2" in creds

    def test_oath_add_credential_with_space(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "test-name-space", "ab ba")
        creds = ckman_cli("oath", "accounts", "list").output
        assert "test-name-space" in creds

    def test_oath_hidden_cred(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "_hidden:name", "abba")
        creds = ckman_cli("oath", "accounts", "code").output
        assert "_hidden:name" not in creds
        creds = ckman_cli("oath", "accounts", "code", "-H").output
        assert "_hidden:name" in creds

    def test_oath_add_uri_hotp(self, ckman_cli):
        ckman_cli("oath", "accounts", "uri", URI_HOTP_EXAMPLE)
        creds = ckman_cli("oath", "accounts", "list").output
        assert "Example:demo" in creds

    def test_oath_add_uri_totp(self, ckman_cli):
        ckman_cli("oath", "accounts", "uri", URI_TOTP_EXAMPLE)
        creds = ckman_cli("oath", "accounts", "list").output
        assert "john.doe" in creds

    def test_oath_add_uri_totp_extra_parameter(self, ckman_cli):
        ckman_cli("oath", "accounts", "uri", URI_TOTP_EXAMPLE_EXTRA_PARAMETER)
        creds = ckman_cli("oath", "accounts", "list").output
        assert "john.doe.extra" in creds

    def test_oath_add_uri_totp_prompt(self, ckman_cli):
        ckman_cli("oath", "accounts", "uri", input=URI_TOTP_EXAMPLE_B)
        creds = ckman_cli("oath", "accounts", "list").output
        assert "john.doe" in creds

    def test_oath_code(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "test-name2", "abba")
        creds = ckman_cli("oath", "accounts", "code").output
        assert "test-name2" in creds

    def test_oath_code_query_single(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "query-me", "abba")
        creds = ckman_cli("oath", "accounts", "code", "query-me").output
        assert "query-me" in creds

    def test_oath_code_query_multiple(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "foo", "abba")
        ckman_cli("oath", "accounts", "add", "query-me", "abba")
        ckman_cli("oath", "accounts", "add", "bar", "abba")
        lines = (
            ckman_cli("oath", "accounts", "code", "query").output.strip().splitlines()
        )
        assert len(lines) == 1
        assert "query-me" in lines[0]

    def test_oath_reset(self, ckman_cli):
        output = ckman_cli("oath", "reset", "-f").output
        assert "Success! All OATH accounts have been deleted from the YubiKey" in output

    def test_oath_hotp_vectors_6(self, ckman_cli):
        ckman_cli(
            "oath",
            "accounts",
            "add",
            "-o",
            "HOTP",
            "testvector",
            b32encode(b"12345678901234567890").decode(),
        )
        for code in ["755224", "287082", "359152", "969429", "338314"]:
            words = ckman_cli("oath", "accounts", "code", "testvector").output.split()
            assert code in words

    def test_oath_hotp_vectors_8(self, ckman_cli):
        ckman_cli(
            "oath",
            "accounts",
            "add",
            "-o",
            "HOTP",
            "-d",
            "8",
            "testvector8",
            b32encode(b"12345678901234567890").decode(),
        )
        for code in ["84755224", "94287082", "37359152", "26969429", "40338314"]:
            words = ckman_cli("oath", "accounts", "code", "testvector8").output.split()
            assert code in words

    def test_oath_hotp_code(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "-o", "HOTP", "hotp-cred", "abba")
        words = ckman_cli("oath", "accounts", "code", "hotp-cred").output.split()
        assert "659165" in words

    def test_oath_hotp_code_single(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "-o", "HOTP", "hotp-cred", "abba")
        words = ckman_cli(
            "oath", "accounts", "code", "hotp-cred", "--single"
        ).output.split()
        assert "659165" in words

    def test_oath_totp_steam_code(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "Steam:steam-cred", "abba")
        cred = ckman_cli("oath", "accounts", "code", "steam-cred").output.strip()
        code = cred.split()[-1]
        assert 5 == len(code), f"cred wrong length: {code!r}"
        assert all(
            c in STEAM_CHAR_TABLE for c in code
        ), f"{code!r} contains non-steam characters"

    def test_oath_totp_steam_code_single(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "Steam:steam-cred", "abba")
        code = ckman_cli("oath", "accounts", "code", "-s", "steam-cred").output.strip()
        assert 5 == len(code), f"cred wrong length: {code!r}"
        assert all(
            c in STEAM_CHAR_TABLE for c in code
        ), f"{code!r} contains non-steam characters"

    def test_oath_code_output_no_touch(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "TOTP:normal", "aaaa")
        ckman_cli("oath", "accounts", "add", "Steam:normal", "aaba")
        ckman_cli("oath", "accounts", "add", "-o", "HOTP", "HOTP:normal", "abaa")

        lines = ckman_cli("oath", "accounts", "code").output.strip().splitlines()
        entries = {line.split()[0]: line for line in lines}
        assert "HOTP Account" in entries["HOTP:normal"]

        code = entries["Steam:normal"].split()[-1]
        assert 5 == len(code), f"cred wrong length: {code!r}"
        assert all(
            c in STEAM_CHAR_TABLE for c in code
        ), f"{code!r} contains non-steam characters"

        code = entries["TOTP:normal"].split()[-1]
        assert 6 == len(code)
        int(code)

    @condition.min_version(4)
    def test_oath_code_output(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "TOTP:normal", "aaaa")
        ckman_cli("oath", "accounts", "add", "--touch", "TOTP:touch", "aaab")
        ckman_cli("oath", "accounts", "add", "Steam:normal", "aaba")
        ckman_cli("oath", "accounts", "add", "--touch", "Steam:touch", "aabb")
        ckman_cli("oath", "accounts", "add", "-o", "HOTP", "HOTP:normal", "abaa")

        lines = ckman_cli("oath", "accounts", "code").output.strip().splitlines()
        entries = {line.split()[0]: line for line in lines}
        assert "Requires Touch" in entries["TOTP:touch"]
        assert "Requires Touch" in entries["Steam:touch"]
        assert "HOTP Account" in entries["HOTP:normal"]

        code = entries["Steam:normal"].split()[-1]
        assert 5 == len(code), f"cred wrong length: {code!r}"
        assert all(
            c in STEAM_CHAR_TABLE for c in code
        ), f"{code!r} contains non-steam characters"

        code = entries["TOTP:normal"].split()[-1]
        assert 6 == len(code)
        int(code)

    @condition.min_version(4)
    def test_oath_totp_steam_touch_not_in_code_output(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "--touch", "Steam:steam-cred", "abba")
        ckman_cli("oath", "accounts", "add", "TOTP:totp-cred", "abba")
        lines = ckman_cli("oath", "accounts", "code").output.strip().splitlines()
        assert "Requires Touch" in lines[0]

    def test_oath_delete(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "delete-me", "abba")
        ckman_cli("oath", "accounts", "delete", "delete-me", "-f")
        assert "delete-me", ckman_cli("oath", "accounts" not in "list")

    def test_oath_unicode(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "😃", "abba")
        ckman_cli("oath", "accounts", "code")
        ckman_cli("oath", "accounts", "list")
        ckman_cli("oath", "accounts", "delete", "😃", "-f")

    @condition.yk4_fips(False)
    @condition.min_version(4, 3, 1)
    def test_oath_sha512(self, ckman_cli):
        ckman_cli("oath", "accounts", "add", "abba", "abba", "--algorithm", "SHA512")
        ckman_cli("oath", "accounts", "delete", "abba", "-f")

    # NEO credential capacity may vary based on configuration
    @condition.min_version(4)
    def test_add_max_creds(self, ckman_cli, version):
        n_creds = 32 if version < (5, 7, 0) else 64
        for i in range(n_creds):
            ckman_cli("oath", "accounts", "add", "test" + str(i), "abba")
            output = ckman_cli("oath", "accounts", "list").output
            lines = output.strip().split("\n")
            assert len(lines) == i + 1

        with pytest.raises(SystemExit):
            ckman_cli("oath", "accounts", "add", "testx", "abba")

    @condition.min_version(5, 3, 1)
    def test_rename(self, ckman_cli):
        ckman_cli("oath", "accounts", "uri", URI_TOTP_EXAMPLE)
        ckman_cli(
            "oath", "accounts", "rename", "john.doe", "Example:user@example.com", "-f"
        )

        creds = ckman_cli("oath", "accounts", "list").output
        assert "john.doe" not in creds
        assert "Example:user@example.com" in creds


class TestOathFips:
    @pytest.fixture(autouse=True)
    @condition.yk4_fips(True)
    def check_fips(self):
        pass

    def test_no_fips_mode_without_password(self, ckman_cli):
        output = ckman_cli("oath", "info").output
        assert "FIPS Approved Mode: No" in output

    def test_fips_mode_with_password(self, ckman_cli):
        ckman_cli("oath", "access", "change", "-n", PASSWORD)
        output = ckman_cli("oath", "info").output
        assert "FIPS Approved Mode: Yes" in output

    def test_sha512_not_supported(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli(
                "oath", "accounts", "add", "abba", "abba", "--algorithm", "SHA512"
            )
