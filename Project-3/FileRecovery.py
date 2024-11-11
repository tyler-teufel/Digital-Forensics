'''
* Script for COMP-5350 Project 3
*
* This script reads the binary data from the disk dump file 'Project3.dd',
* with the goal of recovering several files from the disk image based on file signature.

'''

import hashlib



# Read the binary data from the disk dump file
with open('Project-3/disk-drives/Project3.dd', 'rb') as disk_image:
    data = disk_image.read()

# Function to generate a SHA-256 hash for a file
def generate_sha256_hash(file_path):

    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    
    # Open the file in binary mode and read in chunks
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):  
            sha256_hash.update(chunk)
    
    # Return the hexadecimal digest of the hash
    return sha256_hash.hexdigest()

# Function to generate a Hexdump style output from the dd file binary data.
def hexdump(data, width=16):

    # Split the data into lines of the specified width
    lines = []

    # Loop through the data and format it into hex and ASCII parts, iterating by width.
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{byte:02X}' for byte in chunk)
        ascii_part = ''.join(chr(byte) if 32 <= byte < 127 else '.' for byte in chunk)
        lines.append(f"{i:08X}  {hex_part:<{width * 3}}  {ascii_part}")
    return '\n'.join(lines)

# Function to check if a located directory entry is likely valid based on ASCII name and extension
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

# Function to find directory entries in the disk image data
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


# Generate the hexdump string
hexdump_string = hexdump(data)

# Write the hexdump to a text file
with open('Project-3/Outputs/hexdump_output.txt', 'w') as output_file:
    output_file.write(hexdump_string)
print("Hexdump output has been saved to 'hexdump_output.txt'.\n")



# Define the file extensions we arew looking for.
common_extensions = [b'JPG', b'PNG', b'GIF', b'AVI', b'PDF']

file_names = find_directory_entries(data)

# Hex Representation of the File Signatures.
# 
# File Signatures:

#     'PDF': '0x25 0x50 0x44 0x46',
#     'GIF_87a': '0x47 0x49 0x46 0x38 0x37 0x61',
#     'GIF_89a': '0x47 0x49 0x46 0x38 0x39 0x61',
#     'JPG': '0xFF 0xD8 0xFF 0xE0',
#     'AVI': '0x52 0x49 0x46 0x46 0x41 0x56 0x49 0x20',
#     'PNG': '0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A',
#
# Define the file signatures for the files to be recovered
file_signatures = {
    'PDF': b'%PDF',
    'GIF': b'GIF89a',
    # 'GIF_89a': b'GIF89a',
    'JPG': b'\xFF\xD8', # Already in Hex.
    'AVI': b'RIFF', 
    'PNG': b'\x89PNG\r\n\x1a\n',
    
}

# Define the end of file signatures for the files to be recovered
file_end = {
    'PDF': b'%%EOF',
    'GIF': b'\x00\x3B',
    'JPG': b'\xFF\xD9',
    'AVI': b'',
    'PNG': b'IEND',
}

# list to store the names of the files recovered.
files = []



# Loop through the file signatures and find the files in the data
for sig_name, sig_bytes in file_signatures.items():
    print(f"Searching for file signature '{sig_name}'...")
    # Find the file signature in the data
    start = data.find(sig_bytes)


    if start == -1:
        print(f"File signature '{sig_name}' not found.")
    else:
        print(f"File signature '{sig_name}' found at offset {start}.")
        
        # Find the end of the file offset, if it exists
        end = -1

        if sig_name == 'AVI':
            # Offset for the 4-byte size after "RIFF"
            size_offset = start + 4  
            avi_size_bytes = data[size_offset:size_offset + 4]
            avi_size = int.from_bytes(avi_size_bytes, byteorder='little')

            # Calculate the end of the AVI file based on this size
            # Add 8 for the "RIFF" and size fields
            end = start + avi_size + 8  

            print(f"AVI file size (from header): {avi_size} bytes.")
            print(f"End of file calculated at offset {end}.")
        else:
            # Find the end of the file signature in the data, if not an AVI file
            if file_end[sig_name]:
                end = data.find(file_end[sig_name], start)
                end += len(file_end[sig_name])
                print(f"End of file signature '{sig_name}' found at offset {end}.")
        
            else:
                print(f"End of file signature '{sig_name}' not found.")
                continue

        # Write the file to a new file
        with open(f'Project-3/recovered-files/{file_names[sig_name]}.{sig_name.lower()}', 'wb') as output_file:
            output_file.write(data[start:end])
        files.append(f'{file_names[sig_name]}.{sig_name.lower()}')


        print(f"File '{file_names[sig_name]}.{sig_name.lower()}' has been saved.")
        print()

# Generate SHA-256 hashes for the recovered files
hashes = {}
for name in files:
    file_path = f'Project-3/recovered-files/{name}'
    hash_value = generate_sha256_hash(file_path)
    hashes[name] = hash_value
    print(f"{name}: {hash_value}")