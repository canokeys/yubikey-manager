# Set-PSDebug -Trace 1

$ErrorActionPreference = "Stop"

$CWD = pwd
$SOURCE_DIR = "$CWD\ckman"

$VERSION = $(& "$SOURCE_DIR\ckman.exe" --version).Split(' ')[-1]

echo "Release version: $VERSION"
echo "Binaries: $SOURCE_DIR"

$SIMPLE_VERSION = "$($VERSION.Split('-')[0]).0"

cd $PSScriptRoot

((Get-Content -path ckman.wxs.in -Raw) -replace '{RELEASE_VERSION}',$SIMPLE_VERSION) | Set-Content -Path ckman.wxs

$env:SRCDIR = $SOURCE_DIR

echo "Running heat..."
& "$env:WIX\bin\heat.exe" dir $SOURCE_DIR -out fragment.wxs -gg -scom -srd -sfrag -sreg -dr INSTALLDIR -cg ApplicationFiles -var env.SRCDIR
echo "Running candle..."
& "$env:WIX\bin\candle.exe" fragment.wxs "ckman.wxs" -ext WixUtilExtension  -arch "x64"
echo "Running light..."
& "$env:WIX\bin\light.exe" -v fragment.wixobj "ckman.wixobj" -ext WixUIExtension -ext WixUtilExtension -o "ckman.msi"

# Move to dist
$OUTPUT="$CWD\ckman.msi"
if (Test-Path $OUTPUT) {
  Remove-Item $OUTPUT
}
mv ckman.msi $OUTPUT

# Cleanup
rm fragment.wxs
rm fragment.wixobj
rm ckman.wxs
rm ckman.wixobj
rm ckman.wixpdb

cd $CWD
