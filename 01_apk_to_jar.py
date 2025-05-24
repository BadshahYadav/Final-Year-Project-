import os
import subprocess

def convert_apks_to_jars(input_folders, output_base="./jarfiles"):
    for category_path in input_folders:
        if not os.path.isdir(category_path):
            print(f"[!] Invalid folder: {category_path}")
            continue

        category_name = os.path.basename(category_path)  # 'malware' or 'benign'
        output_folder = os.path.join(output_base, category_name)
        os.makedirs(output_folder, exist_ok=True)

        for file in os.listdir(category_path):
            if file.endswith(".apk"):
                apk_path = os.path.join(category_path, file)
                jar_name = os.path.splitext(file)[0] + ".jar"
                jar_output_path = os.path.join(output_folder, jar_name)

                try:
                    print(f"[*] Converting: {apk_path}")
                    command = f"/home/king/Documents/code/folder/python/dex-tools/d2j-dex2jar.sh \"{apk_path}\" -o \"{jar_output_path}\""
                    subprocess.run(command, shell=True, check=True)
                    print(f"[✓] Saved: {jar_output_path}")
                except subprocess.CalledProcessError:
                    print(f"[✗] Failed to convert: {apk_path}")

if __name__ == "__main__":
    folders = ["./Applications/malware", "./Applications/benign"]
    convert_apks_to_jars(folders)
