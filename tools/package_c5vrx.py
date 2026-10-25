"""Package only unbound C5VRX Backpack images; never read device flash.

Uses ExpressLRS Backpack's own appended-options format. Generated binary,
ZIP and checksum files are release artifacts, not repository source.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import UnifiedConfiguration  # noqa: E402

ENVIRONMENTS = {
    "c3": ("HDZero_ESP32C3_SuperMini_C5VRX_Backpack_DEBUG", "esp32c3"),
    "s3": ("HDZero_ESP32S3_SuperMini_C5VRX_Backpack_DEBUG", "esp32s3"),
}


def verify_unbound(path):
    """Fail closed on missing options or any identity/credential option."""
    data = path.read_bytes()
    if b"-DMY_BINDING_PHRASE=" in data:
        raise ValueError("Compiled binding phrase found; public images must be unbound")
    with path.open("rb") as firmware:
        firmware.seek(UnifiedConfiguration.findFirmwareEnd(firmware))
        raw = firmware.read(513).split(b"\0", 1)[0]
    options = json.loads(raw)
    if not isinstance(options, dict):
        raise ValueError("Firmware options must be an object")
    if set(options) - {"product-name", "flash-discriminator"}:
        raise ValueError("Identity, Wi-Fi or unknown options found; refusing public package")
    if not options.get("product-name") or not options.get("flash-discriminator"):
        raise ValueError("Missing firmware identity metadata")
    return options


def verify_config():
    for name in ("user_defines.txt", "super_defines.txt"):
        path = ROOT / name
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            value = line.strip()
            if value.startswith("-D") and any(word in value for word in
                    ("MY_BINDING_PHRASE", "MY_UID", "HOME_WIFI_SSID", "HOME_WIFI_PASSWORD")):
                raise ValueError(f"Active personal setting in {name}; refusing public package")


def package(board):
    verify_config()
    environment, chip = ENVIRONMENTS[board]
    build = ROOT / ".pio" / "build" / environment
    options = verify_unbound(build / "firmware.bin")
    if options["product-name"] != environment:
        raise ValueError("Built target does not match requested board")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT):
        raise ValueError("Tracked source is dirty; commit source before packaging")
    out = ROOT / "dist" / f"c5vrx-backpack-{board}"
    out.mkdir(parents=True, exist_ok=True)
    # Only known, fresh files can enter the archive; no globs over build or logs.
    names = ["bootloader.bin", "partitions.bin", "boot_app0.bin", "firmware.bin"]
    for name in names:
        shutil.copyfile(build / name, out / name)
    subprocess.run([
        sys.executable, "-m", "esptool", "--chip", chip, "merge_bin",
        "--flash_mode", "dio", "--flash_size", "4MB",
        "-o", str(out / "firmware-merged.bin"),
        "0x0", str(out / "bootloader.bin"),
        "0x8000", str(out / "partitions.bin"),
        "0xe000", str(out / "boot_app0.bin"),
        "0x10000", str(out / "firmware.bin"),
    ], check=True)
    # Verify the actual application embedded at its merged-image offset too.
    merged = (out / "firmware-merged.bin").read_bytes()
    app = (out / "firmware.bin").read_bytes()
    if merged[0x10000:0x10000 + len(app)] != app:
        raise ValueError("Merged image application differs from verified unbound app")
    (out / "COMMIT.txt").write_text(commit + "\n")
    (out / "OPTIONS.json").write_text(json.dumps(options, indent=2) + "\n")
    shutil.copyfile(ROOT / "LICENSE", out / "LICENSE")
    shutil.copyfile(ROOT / "docs" / "SETUP.md", out / "SETUP.md")
    names += ["firmware-merged.bin", "COMMIT.txt", "OPTIONS.json", "LICENSE", "SETUP.md"]
    sums = "".join(f"{hashlib.sha256((out / name).read_bytes()).hexdigest()}  {name}\n"
                   for name in sorted(names))
    (out / "SHA256SUMS").write_text(sums)
    archive = ROOT / "dist" / f"c5vrx-backpack-{board}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in sorted(names + ["SHA256SUMS"]):
            bundle.write(out / name, name)
    print(f"Verified unbound {chip} package: {archive}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", choices=ENVIRONMENTS, required=True)
    package(parser.parse_args().board)
