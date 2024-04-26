from subprocess import PIPE, DEVNULL, run
from datetime import datetime
from os import mkdir, getenv
import argparse

from android_flavored_fstab import parse_fstab_file

default_backup_partitions = ["data", "system"]
default_backup_devimgs = []

print("""ADBackup (Backup)
- by @kyolinedev, @greysoh et al.
""")

parser = argparse.ArgumentParser(description="Backs up your Android phone, NANDroid style")

# Define optional arguments to customize backup
parser.add_argument(
    "--partitions", nargs="+", default=default_backup_partitions, 
    help="Specify the partitions to backup (default: data, system)"
)

parser.add_argument(
    "--devimgs", nargs="+", default=default_backup_devimgs, 
    help="Specify the ABSOLUTE PATH TO device images to backup (default: none)"
)

args = parser.parse_args()

# Append user-specified partitions and device images to the default lists
backup_partitions = default_backup_partitions + args.partitions
backup_devimgs = default_backup_devimgs + args.devimgs

print(backup_partitions)

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

print("Bringing the device down")
run(["adb", "shell", "setprop", "ctl.stop", "media"])
run(["adb", "shell", "setprop", "ctl.stop", "zygote"])
run(["adb", "shell", "setprop", "ctl.stop", "bootanim"])

if getenv("ANDROID_RO"):
    print("Making file system read only")
    run(["adb", "shell", "echo s > /proc/sysrq-trigger"])
    run(["adb", "shell", "echo u > /proc/sysrq-trigger"])

print("Backing up file system entries")

for fstab_entry in parsed_fstab_file:
    if fstab_entry["friendly_name"] not in backup_partitions: continue

    print(f" - Backing up '{fstab_entry['friendly_name']}'...")
    backup_file = f"{dir_name}/{fstab_entry['friendly_name']}.tar.gz"
    
    with open(backup_file, "wb") as file:
        # TODO: hacky!
        if getenv("SHOW_STDERR"):
            run(["adb", "shell", "tar", "-czv", fstab_entry["mountpoint"]], stdout=file)
        else:
            run(["adb", "shell", "tar", "-czv", fstab_entry["mountpoint"]], stdout=file, stderr=DEVNULL)

for devimg in backup_devimgs:
    friendly_name = devimg[devimg.rindex("/")+1:len(devimg)]
    backup_file = f"{dir_name}/{friendly_name}.img"

    print(f" - Dumping device image '{friendly_name}'...")

    with open(backup_file, "wb") as file:
        if getenv("SHOW_STDERR"):
            run(["adb", "shell", "dd", f"if={devimg}"], stdout=file)
        else:
            run(["adb", "shell", "dd", f"if={devimg}"], stdout=file, stderr=DEVNULL)

if not getenv("DEBUG"):
    print("Cleaning up")
    run(["adb", "shell", "setprop", "ctl.start", "bootanim"])
    run(["adb", "shell", "setprop", "ctl.start", "zygote"])
    run(["adb", "shell", "setprop", "ctl.start", "media"])

    if getenv("ANDROID_RO"):
        run(["adb", "reboot"])

print("Done!")