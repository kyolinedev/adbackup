test_fstab = """#
/dev/block/platform/13200000.ufs/by-name/efs /mnt/vendor/efs f2fs defaults 0 0
/dev/block/platform/13200000.ufs/by-name/efs_backup /mnt/vendor/efs_backup f2fs defaults 0 0
/dev/block/platform/13200000.ufs/by-name/modem_userdata /mnt/vendor/modem_userdata f2fs defaults 0 0
/dev/block/platform/13200000.ufs/by-name/metadata /metadata f2fs defaults 0 0
/dev/block/platform/13200000.ufs/by-name/userdata /data f2fs discard,reserve_root=32768,resgid=1065,fsync_mode=nobarrier,compress_extension=apk,compress_extension=apex,compress_extension=so,compress_extension=vdex,compress_extension=odex,,atgc,checkpoint_merge,compress_cache 0 0
#"""

def parse_fstab_file(fstab: str):
    new_line = fstab.split("\n")
    output = []
    mountpoints = []

    for fstab_entry in new_line:
        if fstab_entry.startswith("#"): continue
        if fstab_entry.startswith("\n"): continue

        if "\t" in fstab_entry: continue
   
        split_fstab = fstab_entry.split(" ")
        split_fstab = [x for x in split_fstab if x != ""]
        
        if len(split_fstab) == 0: continue

        friendly_name = split_fstab[1]

        try:
            friendly_name = friendly_name[friendly_name.rindex("/")+1:len(friendly_name)]
        except ValueError:
            pass

        if split_fstab[1] in mountpoints: continue

        output.append({
            "drive": split_fstab[0],
            "mountpoint": split_fstab[1],

            "friendly_name": friendly_name
        })

        mountpoints.append(split_fstab[1])
    
    return output

if __name__ == "__main__":
    print(parse_fstab_file(test_fstab))