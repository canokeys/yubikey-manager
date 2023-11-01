import os

from cryptography.hazmat.primitives import serialization
from ....util import generate_self_signed_certificate
from canokit.core import Tlv
from canokit.piv import OBJECT_ID, SLOT
import pytest


DEFAULT_MANAGEMENT_KEY = "010203040506070801020304050607080102030405060708"


class TestReadWriteObject:
    def test_write_read_preserves_ansi_escapes(self, ckman_cli):
        red = b"\x00\x1b[31m"
        blue = b"\x00\x1b[34m"
        reset = b"\x00\x1b[0m"
        data = (
            b"Hello, "
            + red
            + b"red"
            + reset
            + b" and "
            + blue
            + b"blue"
            + reset
            + b" world!"
        )
        ckman_cli(
            "piv",
            "objects",
            "import",
            "-m",
            DEFAULT_MANAGEMENT_KEY,
            "0x5f0001",
            "-",
            input=data,
        )
        output_data = ckman_cli(
            "piv", "objects", "export", "0x5f0001", "-"
        ).stdout_bytes
        assert data == output_data

    def test_read_write_read_is_noop(self, ckman_cli):
        data = os.urandom(32)

        ckman_cli(
            "piv",
            "objects",
            "import",
            hex(OBJECT_ID.AUTHENTICATION),
            "-",
            "-m",
            DEFAULT_MANAGEMENT_KEY,
            input=data,
        )

        output1 = ckman_cli(
            "piv", "objects", "export", hex(OBJECT_ID.AUTHENTICATION), "-"
        ).stdout_bytes
        assert output1 == data

        ckman_cli(
            "piv",
            "objects",
            "import",
            hex(OBJECT_ID.AUTHENTICATION),
            "-",
            "-m",
            DEFAULT_MANAGEMENT_KEY,
            input=output1,
        )

        output2 = ckman_cli(
            "piv", "objects", "export", hex(OBJECT_ID.AUTHENTICATION), "-"
        ).stdout_bytes
        assert output2 == data

    def test_read_write_certificate_as_object(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli("piv", "objects", "export", hex(OBJECT_ID.AUTHENTICATION), "-")

        cert = generate_self_signed_certificate()
        cert_bytes_der = cert.public_bytes(encoding=serialization.Encoding.DER)

        input_tlv = Tlv(0x70, cert_bytes_der) + Tlv(0x71, b"\0") + Tlv(0xFE, b"")

        ckman_cli(
            "piv",
            "objects",
            "import",
            hex(OBJECT_ID.AUTHENTICATION),
            "-",
            "-m",
            DEFAULT_MANAGEMENT_KEY,
            input=input_tlv,
        )

        output1 = ckman_cli(
            "piv", "objects", "export", hex(OBJECT_ID.AUTHENTICATION), "-"
        ).stdout_bytes
        output_cert_bytes = Tlv.parse_dict(output1)[0x70]
        assert output_cert_bytes == cert_bytes_der

        output2 = ckman_cli(
            "piv",
            "certificates",
            "export",
            hex(SLOT.AUTHENTICATION),
            "-",
            "--format",
            "DER",
        ).stdout_bytes
        assert output2 == cert_bytes_der
