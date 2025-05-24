import os
import subprocess

def convert_jar_to_hexdump(input_folder, output_folder):
    for category in os.listdir(input_folder):  # 'benign' and 'malware'
        category_path = os.path.join(input_folder, category)
        if not os.path.isdir(category_path):
            continue

        output_category_path = os.path.join(output_folder, category)
        os.makedirs(output_category_path, exist_ok=True)

        for file in os.listdir(category_path):
            if file.endswith(".jar"):
                jar_path = os.path.join(category_path, file)
                hex_name = os.path.splitext(file)[0] + ".hex"
                hex_output_path = os.path.join(output_category_path, hex_name)

                try:
                    print(f"[*] Converting: {jar_path}")
                    command = f"xxd -p \"{jar_path}\" > \"{hex_output_path}\""
                    subprocess.run(command, shell=True, check=True)
                    print(f"[✓] Saved: {hex_output_path}")
                except subprocess.CalledProcessError:
                    print(f"[✗] Failed to convert: {jar_path}")

if __name__ == "__main__":
    input_base = "./jarfiles"  # This folder contains 'benign' and 'malware' folders
    output_base = "./hexdumps"  # The folder to save the hex files
    convert_jar_to_hexdump(input_base, output_base)
