from .. import condition
import pytest


class TestYkmanInfo:
    def test_ckman_info(self, ckman_cli, info):
        output = ckman_cli("info").output
        assert "Device type:" in output
        if info.serial is not None:
            assert "Serial number:" in output
        assert "Firmware version:" in output

    @condition.yk4_fips(False)
    def test_ckman_info_does_not_report_fips_for_non_fips_device(self, ckman_cli):
        with pytest.raises(SystemExit):
            ckman_cli("info", "--check-fips")

    @condition.yk4_fips(True)
    def test_ckman_info_reports_fips_status(self, ckman_cli):
        info = ckman_cli("info", "--check-fips").output
        assert "FIPS Approved Mode:" in info
        assert "  FIDO U2F:" in info
        assert "  OATH:" in info
        assert "  OTP:" in info
