import os
import subprocess

UI_FOLDER = "ui"
OUTPUT_FOLDER = "ui_gen"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for file in os.listdir(UI_FOLDER):
    if file.endswith(".ui"):

        input_path = os.path.join(UI_FOLDER, file)

        output_file = file.replace(".ui", "_ui.py")
        output_path = os.path.join(OUTPUT_FOLDER, output_file)

        print(f"Compilando {file} -> {output_file}")

        subprocess.run([
            "pyside6-uic",
            input_path,
            "-o",
            output_path
        ])

print("✔ Todos los UI fueron compilados")