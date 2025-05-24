import os
import numpy as np
import librosa

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

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                with open(input_path, 'r') as f:
                    line = f.read().strip()
                    opcodes = [int(val) for val in line.split() if val.isdigit()]
                if len(opcodes) < 100:
                    print(f"[!] Skipped (too short): {filename}")
                    continue

                opcodes = np.array(opcodes)
                vector = compute_lpc_error_vector(opcodes)

                # Debug: Show first vector summary
                if len(vector) > 0:
                    print(f"[✓] {filename}: LPC Vector (first 5 values): {vector[:5]}")

                with open(output_path, 'w') as f_out:
                    f_out.write(','.join(map(str, vector)))
                print(f"[✓] Saved: {output_path}")
            except Exception as e:
                print(f"[✗] Error processing {filename}: {e}")

if __name__ == "__main__":
    folders = [
        ("./opcodes/malware", "./lpc_vectors/malware"),
        ("./opcodes/benign", "./lpc_vectors/benign")
    ]
    for in_path, out_path in folders:
        process_folder(in_path, out_path)
