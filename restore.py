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

if "system.tar.gz" in backup_dir_contents:
    backup_dir_contents.append(backup_dir_contents.pop(backup_dir_contents.index("system.tar.gz")))

# Not the best code ever, but it works
for backup_dir_content_index in range(len(backup_dir_contents)):
    cycles = 0

    while True:
        backup_dir_content = backup_dir_contents[backup_dir_content_index]

        if backup_dir_content.endswith(".img") and cycles < 2:
            backup_dir_contents.append(backup_dir_contents.pop(backup_dir_contents.index(backup_dir_content)))
            cycles += 1
        else:
            break

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

    if entry.endswith("tar.gz"):
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

            print(f"Restoring '/{part_name}'...")
            with open(real_entry, "r") as file:
                run(["adb", "shell", "tar", "-xzvf", "-"], stdin=file, stdout=DEVNULL)
    elif entry.endswith("img"):
        print(f"Flashing image '{part_name}'...")
        
        run(["adb", "shell", "reboot", "bootloader"], stdout=DEVNULL, stderr=DEVNULL)
        run(["fastboot", "reboot", "bootloader"], stdout=DEVNULL, stderr=DEVNULL)

        run(["fastboot", "flash", part_name, real_entry])

if not getenv("DEBUG"):
    print("Cleaning up")
    run(["adb", "reboot"])

print("Done!")