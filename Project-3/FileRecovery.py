'''
* Script for COMP-5350 Project 3
*
* This script reads the binary data from the disk dump file 'Project3.dd',
* with the goal of recovering several files from the disk image based on file signature.

'''

# Library needed for hashing the files.
import hashlib



# Read the binary data from the disk dump file for analysis.
with open('Project-3/disk-drives/Project3.dd', 'rb') as disk_image:
    data = disk_image.read()

# Function to generate a SHA-256 hash for a file
def generate_sha256_hash(file_path):

    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    
    # Open the file in binary mode (rb) and read in chunks
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
    # Output should look like the hexdumps in the linux machine, with ascii representation on the right.
    for i in range(0, len(data), width):

        # We iterate through the data 16 bytes at a time, from 0 to the end of the data.
        chunk = data[i:i+width]

        # Specifies each byte to be represented in 2-digit uppercase hex format, for each byte in the chunk.
        hex_part = ' '.join(f'{byte:02X}' for byte in chunk)

        # Specifies the ASCII representation of the bytes in the chunk.
        ascii_part = ''.join(chr(byte) if 32 <= byte < 127 else '.' for byte in chunk)

        # Append the hex and ASCII parts to the lines list, beginning with the 8 byte offset.
        lines.append(f"{i:08X}  {hex_part:<{width * 3}}  {ascii_part}")

    return '\n'.join(lines)

# Function to check if a located directory entry is likely valid based on ASCII name and extension.
def is_likely_directory_entry(entry):

    # Split the entry into name and extension parts, each 8 and 3 bytes long respectively.
    name_part = entry[:8]
    ext_part = entry[8:11]
    
    # Ensure name and extension are ASCII and non-empty, based on the ASCII values.
    if not all(32 <= byte < 127 for byte in name_part + ext_part):
        return False
    
    # Check if the extension is one of the known types
    if ext_part not in common_extensions:
        return False
    
    return True

# Function to find directory entries in the disk image data
def find_directory_entries(data):

    # Create a dictionary to store the file names based on extension types.
    files = {}

    # Scan through data to find potential directory entries, in 32 byte increments.
    for i in range(0, len(data) - 32, 32): 
        # Each entry being parsed is 32 bytes long.
        entry = data[i:i + 32]

        # Check if the entry is likely a directory entry based on the ASCII name and extension.
        if is_likely_directory_entry(entry):

            # Extract the file name and extension from the entry, and store in the dictionary.
            # Ignore any encoding errors and strip any whitespace.
            file_name = entry[:8].decode('ascii', errors='ignore').strip()
            file_ext = entry[8:11].decode('ascii', errors='ignore').strip()

            # Store the file name in the dictionary based on the extension.
            files[file_ext] = file_name

    return files


# Generate the hexdump string (if needed).
hexdump_string = hexdump(data)

# Write the hexdump to a text file
with open('Project-3/Outputs/hexdump_output.txt', 'w') as output_file:
    output_file.write(hexdump_string)
print("Hexdump output has been saved to 'hexdump_output.txt'.\n")



# Define the file extensions we are looking for, represented in bytes.
# This will be used to validate the directory entries found in the disk image.
common_extensions = [b'JPG', b'PNG', b'GIF', b'AVI', b'PDF']

# Find the directory entries in the disk image data, and populate a dictionary with the file names.
file_names = find_directory_entries(data)


# Define the file signatures for the files to be recovered.
file_signatures = {
    'PDF': b'%PDF',
    'GIF': b'GIF89a', # GIF87a not found, so using GIF89a.
    'JPG': b'\xFF\xD8', # Already in Hex.
    'AVI': b'RIFF', 
    'PNG': b'\x89PNG\r\n\x1a\n',
    
}

# Define the end of file signatures for the files to be recovered.
file_end = {
    'PDF': b'%%EOF',
    'GIF': b'\x00\x3B', 
    'JPG': b'\xFF\xD9',
    'AVI': b'', # AVI files are based on size, so no end signature.
    'PNG': b'IEND',
}

# list to store the names of the files recovered.
files = []



# Loop through the file signatures and find the files in the data.
for sig_name, sig_bytes in file_signatures.items():

    print(f"Searching for file signature '{sig_name}'...")
    
    # Find the file signature in the data
    start = data.find(sig_bytes)

    # If the signature is not found, print a message and continue to the next signature.
    if start == -1:
        print(f"File signature '{sig_name}' not found.")
    else:
        print(f"File signature '{sig_name}' found at offset {start}.")
        
        # Default the end of the file to -1, in case it is not found.
        end = -1

        # If the file is an AVI file, calculate the end based on the size in the header.
        if sig_name == 'AVI':

            # Offset for the 4-byte size located after "RIFF".
            size_offset = start + 4  
            avi_size_bytes = data[size_offset:size_offset + 4]
            avi_size = int.from_bytes(avi_size_bytes, byteorder='little')

            # Calculate the end of the AVI file based on this size.
            # Add 8 for the "RIFF" and size fields.
            end = start + avi_size + 8  

            print(f"AVI file size (from header): {avi_size} bytes.")
            print(f"End of file calculated at offset {end}.")
        else:

            # Find the end of the file signature in the data, if not an AVI file.
            if file_end[sig_name]:

                # Locate the end of the file signature in the data following the file signature.
                end = data.find(file_end[sig_name], start)

                # If the end of the file signature is found, update the end offset to encapsulate the file.
                end += len(file_end[sig_name])
                print(f"End of file signature '{sig_name}' found at offset {end}.")
        
            else:
                print(f"End of file signature '{sig_name}' not found.")
                continue

        # Write the file to a new file, add the name to the files list.
        with open(f'Project-3/recovered-files/{file_names[sig_name]}.{sig_name.lower()}', 'wb') as output_file:
            output_file.write(data[start:end])
        files.append(f'{file_names[sig_name]}.{sig_name.lower()}')


        print(f"File '{file_names[sig_name]}.{sig_name.lower()}' has been saved.")
        print()

# Generate SHA-256 hashes for the recovered files.
hashes = {}
for name in files:
    file_path = f'Project-3/recovered-files/{name}'
    hash_value = generate_sha256_hash(file_path)
    hashes[name] = hash_value
    print(f"{name}: {hash_value}")