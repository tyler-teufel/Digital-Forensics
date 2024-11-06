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
