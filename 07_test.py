import os
import numpy as np
import librosa
import subprocess
import joblib

# Adjust LPC error vector to match model's expected feature size
def adjust_lpc_vector_size(lpc_vector, target_size=41246):
    current_size = len(lpc_vector)
    if current_size < target_size:
        # Pad with zeros
        lpc_vector = lpc_vector + [0.0] * (target_size - current_size)
    elif current_size > target_size:
        # Truncate to the target size
        lpc_vector = lpc_vector[:target_size]
    
    return lpc_vector

def compute_lpc_error_vector(opcodes, window_size=100, step_size=50, lpc_order=8):
    error_vector = []
    for start in range(0, len(opcodes) - window_size + 1, step_size):
        window = opcodes[start:start + window_size].astype(float)
        window -= np.mean(window)  # Zero-mean

        if len(window) <= lpc_order:
            error_vector.append(0.0)
            continue

        try:
            coeffs = librosa.lpc(window, order=lpc_order)
            predicted = np.convolve(window, -1 * coeffs[1:], mode='full')
            predicted = predicted[:len(window) - (len(coeffs) - 1)]  # Slice to match
            actual = window[len(coeffs)-1:]
            if len(actual) != len(predicted):
                raise ValueError(f"Length mismatch: actual({len(actual)}), predicted({len(predicted)})")

            residual = actual - predicted
            error_energy = np.sum(residual ** 2)
            error_vector.append(error_energy)
        except Exception as e:
            print(f"[!] LPC failed at window starting {start}: {e}")
            error_vector.append(0.0)
    return error_vector

def convert_apks_to_jars(input_folders, output_base="./jarfiles_test"):
    for category_path in input_folders:
        if not os.path.isfile(category_path):  # Fix to check file, not directory
            print(f"[!] Invalid file: {category_path}")
            continue

        output_folder = os.path.join(output_base)
        os.makedirs(output_folder, exist_ok=True)

        apk_path = category_path
        jar_name = os.path.splitext(os.path.basename(apk_path))[0] + ".jar"
        jar_output_path = os.path.join(output_folder, jar_name)

        try:
            print(f"[*] Converting: {apk_path}")
            command = f"/home/king/Documents/code/folder/python/dex-tools/d2j-dex2jar.sh \"{apk_path}\" -o \"{jar_output_path}\""
            subprocess.run(command, shell=True, check=True)
            print(f"[✓] Saved: {jar_output_path}")
        except subprocess.CalledProcessError:
            print(f"[✗] Failed to convert: {apk_path}")

def convert_jar_to_hexdump(input_folder, output_folder="./hexdumps_test"):
    for file in os.listdir(input_folder):
        if file.endswith(".jar"):
            jar_path = os.path.join(input_folder, file)
            hex_name = os.path.splitext(file)[0] + ".hex"
            hex_output_path = os.path.join(output_folder, hex_name)

            try:
                print(f"[*] Converting: {jar_path}")
                command = f"xxd -p \"{jar_path}\" > \"{hex_output_path}\""
                subprocess.run(command, shell=True, check=True)
                print(f"[✓] Saved: {hex_output_path}")
            except subprocess.CalledProcessError:
                print(f"[✗] Failed to convert: {jar_path}")

def convert_hex_to_opcodes(input_folder, output_folder="./opcodes_test"):
    os.makedirs(output_folder, exist_ok=True)  # Ensure the opcodes folder exists

    for file in os.listdir(input_folder):
        if file.endswith(".hex"):
            hex_path = os.path.join(input_folder, file)
            opcode_output_path = os.path.join(output_folder, os.path.splitext(file)[0] + "_opcode.txt")

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

def predict_malware_for_apk(apk_path, model):
    # Convert APK to JAR
    jar_name = os.path.splitext(os.path.basename(apk_path))[0] + ".jar"
    jar_output_path = os.path.join("./jarfiles_test", jar_name)
    print(f"[*] Converting APK: {apk_path} to JAR: {jar_output_path}")
    convert_apks_to_jars([apk_path], output_base="./jarfiles_test")

    # Convert JAR to Hex
    hex_name = os.path.splitext(os.path.basename(jar_name))[0] + ".hex"
    hex_output_path = os.path.join("./hexdumps_test", hex_name)
    os.makedirs("./hexdumps_test", exist_ok=True)  # Ensure the hexdumps folder exists
    convert_jar_to_hexdump("./jarfiles_test", "./hexdumps_test")

    # Convert Hex to Opcodes
    opcode_name = os.path.splitext(os.path.basename(hex_name))[0] + "_opcode.txt"
    opcode_output_path = os.path.join("./opcodes_test", opcode_name)
    os.makedirs("./opcodes_test", exist_ok=True)  # Ensure the opcodes folder exists
    convert_hex_to_opcodes("./hexdumps_test", "./opcodes_test")

    # Read Opcodes and Compute LPC Vector
    with open(opcode_output_path, 'r') as f:
        opcodes = [int(val) for val in f.read().strip().split()]
    
    lpc_vector = compute_lpc_error_vector(np.array(opcodes))

    # Debug: Print LPC vector size and a snippet of it
    print(f"LPC Vector Size: {len(lpc_vector)}")
    print(f"Sample LPC Vector: {lpc_vector[:10]}")  # Show first 10 values

    # Adjust the LPC vector size to match the model's expected feature count
    lpc_vector = adjust_lpc_vector_size(lpc_vector, target_size=41246)

    # Save the LPC vector to a file
    lpc_vector_output_path = os.path.join("./lpc_vectors_test", os.path.splitext(os.path.basename(apk_path))[0] + "_lpc_vector.txt")
    os.makedirs("./lpc_vectors_test", exist_ok=True)  # Ensure the lpc_vectors folder exists

    with open(lpc_vector_output_path, 'w') as f:
        f.write(' '.join(map(str, lpc_vector)))  # Write LPC vector in space-separated format

    print(f"[✓] Saved LPC Vector to: {lpc_vector_output_path}")

    # Make prediction
    prediction = model.predict([lpc_vector])

    return prediction

# Load the trained model
model = joblib.load("malware_classifier.pkl")

if __name__ == "__main__":
    apk_path = "./Test_apk/test1.apk"  # Path to the test APK
    result = predict_malware_for_apk(apk_path, model)
    print(f"Prediction result: {'Malware' if result[0] == 1 else 'Benign'}")
