import subprocess
import shlex
print("testing cmd...")

cmd = shlex.split("which mediainfo")

print(subprocess.Popen(["which", "mediainfo"]))
