from subprocess import DEVNULL, run
from os import getenv, listdir
from time import sleep
from sys import argv

print("""ADBackup (Restore)
- by @kyolinedev, @greysoh et al.
      
THIS CODE IS UNTESTED, PLEASE REPORT ANY ISSUES.
""")

backup_dir = argv[1]
backup_dir_contents = listdir(backup_dir)

print("Please wait while I initialize backups...")

print("Preparing")
run(["adb", "root"])

print("Bringing the device down")
run(["adb", "shell", "setprop", "ctl.stop", "media"])
run(["adb", "shell", "setprop", "ctl.stop", "zygote"])
run(["adb", "shell", "setprop", "ctl.stop", "bootanim"])

print("Restoring file system entries")
print("WARNING: This will wipe ALL data on the device, and restore from the backup.")
print("Waiting 5 seconds before continuing")

sleep(5)

for entry in backup_dir_contents:
    if entry == "fstab": continue

    part_name = entry[0:entry.index(".")]
    real_entry = f"{backup_dir}/{entry}"

    if part_name == "system":
        print(f"Preparing to image '/{part_name}'...")
        print("Rebooting to recovery...")
        run(["adb", "reboot", "recovery"])
        input("Press 'enter' to continue when you are in an ADB root shell while in recovery")
        print("Preparing")
        run(["adb", "root"])

        print(f"Wiping '/{part_name}'...")
        run(["adb", "shell", "rm", "-rf", f"/{part_name}/*"])

        print(f"Restoring '/{part_name}'...")
        with open(real_entry, "r") as file:
            run(["adb", "shell", "tar", "-xzvf", "-"], stdin=file)
        
        print(f"Rebooting device")
        run(["adb", "reboot"])
        
        input("Press 'enter' to continue when you are back in normal mode")
        print("Rerunning init steps...")

        print(" - Preparing")
        run(["adb", "root"])

        print(" - Bringing the device down")
        run(["adb", "shell", "setprop", "ctl.stop", "media"])
        run(["adb", "shell", "setprop", "ctl.stop", "zygote"])
        run(["adb", "shell", "setprop", "ctl.stop", "bootanim"])
    else:
        print(f"Wiping '/{part_name}'...")
        run(["adb", "shell", "rm", "-rf", f"/{part_name}/*"])

        with open(real_entry, "r") as file:
            run(["adb", "shell", "tar", "-xzvf", "-"], stdin=file, stdout=DEVNULL)

if not getenv("DEBUG"):
    print("Cleaning up")
    run(["adb", "reboot"])

print("Done!")