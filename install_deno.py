
import io
import os
import platform
import stat
import urllib.request
import zipfile
from pathlib import Path

# Install Deno in the project's local tools directory.
destination = Path(__file__).resolve().parent / ".tools"
destination.mkdir(exist_ok=True)

if platform.system() != "Linux":
    raise RuntimeError("This installer is for Linux deployments.")

machine = platform.machine().lower()

if machine in ("x86_64", "amd64"):
    architecture = "x86_64"
elif machine in ("aarch64", "arm64"):
    architecture = "aarch64"
else:
    raise RuntimeError(f"Unsupported architecture: {machine}")

version = "v2.6.10"

url = (
    "https://github.com/denoland/deno/releases/download/"
    f"{version}/deno-{architecture}-unknown-linux-gnu.zip"
)

archive = urllib.request.urlopen(url, timeout=60).read()

with zipfile.ZipFile(io.BytesIO(archive)) as z:
    deno_binary = z.read("deno")

deno_path = destination / "deno"
deno_path.write_bytes(deno_binary)

deno_path.chmod(
    deno_path.stat().st_mode
    | stat.S_IXUSR
    | stat.S_IXGRP
    | stat.S_IXOTH
)

print(f"Deno installed at: {deno_path}")
