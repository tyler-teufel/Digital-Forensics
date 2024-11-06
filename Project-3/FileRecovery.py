'''
* Script for COMP-5350 Project 3
*
* This script reads the binary data from the disk dump file 'Project3.dd',
* with the goal of recovering several files from the disk image based on file signature.

'''




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

# Read the binary data from the disk dump file
with open('Project-3/disk-drives/Project3.dd', 'rb') as disk_image:
    data = disk_image.read()

# Generate the hexdump string
hexdump_string = hexdump(data)

# Write the hexdump to a text file
with open('Project-3/Outputs/hexdump_output.txt', 'w') as output_file:
    output_file.write(hexdump_string)

print("Hexdump output has been saved to 'hexdump_output.txt'.")



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
    'AVI': b'RIFFAVI ', 
    'PNG': b'\x89PNG\r\n\x1a\n',
    
}

file_end = {
    'PDF': b'%%EOF',
    'GIF': b'\x3B',
    # 'GIF_89a': b'\x3B',
    'JPG': b'\xFF\xD9',
    'AVI': b'',
    'PNG': b'IEND',
}

x = 1
for sig_name, sig_bytes in file_signatures.items():
    # Find the file signature in the data
    start = data.find(sig_bytes)


    if start == -1:
        print(f"File signature '{sig_name}' not found.")
    else:
        print(f"File signature '{sig_name}' found at offset {start}.")
        
        # Find the end of the file offset, if it exists
        end = -1
        if file_end[sig_name]:
            end = data.find(file_end[sig_name], start)
            end += len(file_end[sig_name])
            print(f"End of file signature '{sig_name}' found at offset {end}.")
        else:
            print(f"End of file signature '{sig_name}' not found.")
            continue

        # Write the file to a new file
        with open(f'Project-3/recovered-files/recovered_file{x}.{sig_name.lower()}', 'wb') as output_file:
            output_file.write(data[start:end])

        print(f"File 'recovered_file{x}.{sig_name.lower()}' has been saved.")
        print()
    x += 1

