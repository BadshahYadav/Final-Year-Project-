import os

def convert_hex_to_opcodes(input_folder, output_folder):
    for category in os.listdir(input_folder):  # 'benign' and 'malware'
        category_path = os.path.join(input_folder, category)
        if not os.path.isdir(category_path):
            continue

        output_category_path = os.path.join(output_folder, category)
        os.makedirs(output_category_path, exist_ok=True)

        for file in os.listdir(category_path):
            if file.endswith(".hex"):
                hex_path = os.path.join(category_path, file)
                opcode_output_path = os.path.join(output_category_path, os.path.splitext(file)[0] + "_opcode.txt")

                try:
                    with open(hex_path, 'r') as f:
                        hex_data = f.read().replace('\n', '').strip()

                    opcodes = []
                    for i in range(0, len(hex_data) - 3, 4):  # 4 hex characters = 16 bits
                        chunk = hex_data[i:i+4]
                        opcodes.append(str(int(chunk, 16)))  # Convert to integer

                    with open(opcode_output_path, 'w') as f_out:
                        f_out.write(' '.join(opcodes))  # write in a single row, space-separated

                    print(f"[✓] Saved: {opcode_output_path}")
                except Exception as e:
                    print(f"[✗] Failed to process: {hex_path} — {e}")

if __name__ == "__main__":
    input_base = "./hexdumps"      # Input: .hex files here
    output_base = "./opcodes"      # Output: .txt files with integers
    convert_hex_to_opcodes(input_base, output_base)




# import os

# def convert_hex_to_opcodes(input_folder, output_folder):
#     for category in os.listdir(input_folder):  # 'benign' and 'malware'
#         category_path = os.path.join(input_folder, category)
#         if not os.path.isdir(category_path):
#             continue

#         output_category_path = os.path.join(output_folder, category)
#         os.makedirs(output_category_path, exist_ok=True)

#         for file in os.listdir(category_path):
#             if file.endswith(".hex"):
#                 hex_path = os.path.join(category_path, file)
#                 opcode_output_path = os.path.join(output_category_path, os.path.splitext(file)[0] + "_opcode.txt")

#                 try:
#                     with open(hex_path, 'r') as f:
#                         hex_data = f.read().replace('\n', '').strip()

#                     opcodes = []
#                     for i in range(0, len(hex_data) - 3, 4):  # 4 hex characters = 16 bits
#                         chunk = hex_data[i:i+4]
#                         opcodes.append(str(int(chunk, 16)))  # Convert to integer

#                     with open(opcode_output_path, 'w') as f_out:
#                         f_out.write('\n'.join(opcodes))

#                     print(f"[✓] Saved: {opcode_output_path}")
#                 except Exception as e:
#                     print(f"[✗] Failed to process: {hex_path} — {e}")

# if __name__ == "__main__":
#     input_base = "./hexdumps"      # Input: .hex files here
#     output_base = "./opcodes"      # Output: .txt files with integers
#     convert_hex_to_opcodes(input_base, output_base)
