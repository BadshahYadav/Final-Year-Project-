import os
import csv

def create_dataset(benign_folder, malware_folder, output_csv):
    dataset = []
    max_length = 0

    # Process both classes
    for label, folder in [(0, benign_folder), (1, malware_folder)]:
        for filename in os.listdir(folder):
            if filename.endswith("_opcode.txt"):
                path = os.path.join(folder, filename)
                try:
                    with open(path, 'r') as f:
                        content = f.read().replace('\n', '').strip()
                        if ',' in content:
                            values = [float(x) for x in content.split(',') if x.strip()]
                        else:
                            values = [float(x) for x in content.split() if x.strip()]
                        
                        if not values:
                            continue

                        dataset.append(values + [label])
                        max_length = max(max_length, len(values))
                except Exception as e:
                    print(f"[!] Error reading {filename}: {e}")

    # Normalize length (pad with zeros)
    for row in dataset:
        row[:max_length]  # trim if too long
        while len(row) < max_length + 1:  # +1 for label
            row.insert(-1, 0.0)

    # Write to CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        header = [f'feature_{i}' for i in range(max_length)] + ['label']
        writer.writerow(header)
        writer.writerows(dataset)

    print(f"[✓] Dataset saved to: {output_csv}")

if __name__ == "__main__":
    create_dataset("./lpc_vectors/benign", "./lpc_vectors/malware", "dataset.csv")
