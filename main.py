from datetime import datetime
from subprocess import PIPE, DEVNULL, run
from os import mkdir, getenv

from android_flavored_fstab import parse_fstab_file

backup_partitions = [
    "data"
]

# TODO implement this sometime!
# TODO implement backup restore procedure
backup_devimgs = [
    "boot"
]

# TODO command line argument parsing to populate these!

print("""You are using: 7902 (put cheesy ASCII here)               
- by @greysoh, @kyolinedev et al.
- special thanks to @kyolinedev for testing purposes
""")

print("Please wait while I initialize backups...")

try:
    mkdir("backups")
except FileExistsError:
    pass

now = datetime.now()
dt_string = now.strftime("%d_%m_%Y#%H:%M:%S")

dir_name = f"backups/{dt_string}"

mkdir(dir_name)

print("Preparing")
run(["adb", "root"])

print("Getting /etc/fstab")
fstab_file = run(["adb", "shell", "cat", "/vendor/etc/fstab*"], stdout=PIPE, stderr=DEVNULL).stdout
fstab_file = fstab_file.decode("utf8")

with open(f"{dir_name}/fstab", "w") as file:
    file.write(fstab_file)

parsed_fstab_file = parse_fstab_file(fstab_file)

print("Making the device read only")
run(["adb", "shell", "setprop", "ctl.stop", "media"])
run(["adb", "shell", "setprop", "ctl.stop", "zygote"])
run(["adb", "shell", "setprop", "ctl.stop", "bootanim"])

run(["adb", "shell", "echo s > /proc/sysrq-trigger"])
run(["adb", "shell", "echo u > /proc/sysrq-trigger"])

print("Backing up file system entries")

for fstab_entry in parsed_fstab_file:
    if fstab_entry["friendly_name"] not in backup_partitions: continue

    print(f" - Backing up '{fstab_entry['friendly_name']}'...")
    backup_file = f"{dir_name}/{fstab_entry['friendly_name']}.tar.gz"
    
    with open(backup_file, "wb") as file:
        if getenv("SHOW_STDERR"):
            run(["adb", "shell", "tar", "-czv", fstab_entry["mountpoint"]], stdout=file) # stdout=file
        else:
            # hacky
            run(["adb", "shell", "tar", "-czv", fstab_entry["mountpoint"]], stdout=file, stderr=DEVNULL) # stdout=file

if not getenv("DEBUG"):
    print("Cleaning up")
    run(["adb", "shell", "reboot"])

print("Done!")