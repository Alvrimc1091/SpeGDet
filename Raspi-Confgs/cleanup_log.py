with open("boot_log.log", "rb") as infile, open("cleaned_boot_log.log", "wb") as outfile:
    for line in infile:
        if b'\x00' not in line:  # Check for null bytes
            outfile.write(line)
