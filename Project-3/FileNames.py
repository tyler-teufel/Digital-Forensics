# Define file extensions to search for in directory entries (common ASCII extensions)
common_extensions = [b'JPG', b'PNG', b'GIF', b'AVI', b'PDF']

# Open the disk image in binary mode
with open('Project-3/disk-drives/Project3.dd', 'rb') as disk_image:
    data = disk_image.read()


def is_likely_directory_entry(entry):
    # Check if the entry has a valid ASCII name in the first 11 bytes (name + extension)
    name_part = entry[:8]
    ext_part = entry[8:11]
    
    # Ensure name and extension are ASCII and non-empty
    if not all(32 <= byte < 127 for byte in name_part + ext_part):
        return False
    
    # Check if the extension is one of the known types
    if ext_part not in common_extensions:
        return False
    
    return True
    
# files = {}
# # Function to parse and display details of a directory entry
# def parse_directory_entry(entry, offset):
    
#     # Extract file name and extension
#     file_name = entry[:8].decode('ascii', errors='ignore').strip()
#     file_ext = entry[8:11].decode('ascii', errors='ignore').strip()
#     files[file_ext] = file_name


def find_directory_entries(data):
    files = {}

    # Scan through data to find potential directory entries
    for i in range(0, len(data) - 32, 32):  # Step through data in 32-byte blocks
        entry = data[i:i + 32]
        if is_likely_directory_entry(entry):
            file_name = entry[:8].decode('ascii', errors='ignore').strip()
            file_ext = entry[8:11].decode('ascii', errors='ignore').strip()
            files[file_ext] = file_name
    return files


all_files = find_directory_entries(data)
print(all_files)