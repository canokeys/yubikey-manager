# Set-PSDebug -Trace 1

$ErrorActionPreference = "Stop"

$CWD = pwd
$SOURCE_DIR = "$CWD\ckman"

echo "Signing ckman.exe"
signtool.exe sign /sha1 cb7cade8f51d0985d806bcd28e1fec57d3034187 /fd SHA256 /t http://timestamp.digicert.com "$SOURCE_DIR\ckman.exe"

$VERSION = $(& "$SOURCE_DIR\ckman.exe" --version).Split(' ')[-1]

& $PSScriptRoot\make_msi.ps1

echo "Signing .msi"
$OUTPUT_FILE = "yubikey-manager-$VERSION-win64.msi"
mv ".\ckman.msi" $OUTPUT_FILE

signtool.exe sign /sha1 cb7cade8f51d0985d806bcd28e1fec57d3034187 /fd SHA256 /t http://timestamp.digicert.com /d "YubiKey Manager CLI" ".\$OUTPUT_FILE"

echo "Installer signed: $OUTPUT_FILE"
