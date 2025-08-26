import nbformat
import os
import sys
import json
import time
import shutil
import requests
import asyncio
from nbconvert.preprocessors import ExecutePreprocessor

def set_windows_event_loop_policy():
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def wait_for_file(path, timeout=120, poll=1.0):
    start = time.time()
    while time.time() - start <= timeout:
        if os.path.exists(path):
            print(f"[OK] Encontrado: {path}")
            return True
        time.sleep(poll)
    print(f"[TIMEOUT] No apareció: {path}")
    return False

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

set_windows_event_loop_policy()

# Comprobación del backend
urlNewData = "https://9ae744d74797.ngrok-free.app/newData"
urlECG    = "https://9ae744d74797.ngrok-free.app/ecg"

try:
    response = requests.get(urlNewData, timeout=15)
except Exception as e:
    print(f"ERROR solicitando {urlNewData}: {e}")
    sys.exit(1)

if response.status_code == 200:
    try:
        data = response.json()
        print("Response data:", data)
        if data.get("status") == "true":
            print("No new data to process")
            sys.exit(0)
        elif data.get("status") == "false":
            try:
                responseECG = requests.get(urlECG, timeout=30)
            except Exception as e:
                print(f"ERROR solicitando {urlECG}: {e}")
                sys.exit(1)

            if responseECG.status_code == 200:
                ecg_data = responseECG.json()
                if isinstance(ecg_data, list) and all(isinstance(d, dict) and "timestamp" in d and "value" in d for d in ecg_data):
                    folder = "processing_data"
                    ensure_dir(folder)
                    file_path = os.path.join(folder, "ecg_data_to_load.txt")
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(ecg_data, f, indent=4, ensure_ascii=False)
                    print("ECG DATA TO LOAD:", file_path)
                else:
                    print("ERROR: ECG data format is invalid")
                    sys.exit(1)
            else:
                print("ERROR WITH THE ECG RESPONSE")
                sys.exit(1)
        else:
            print("ERROR WITH THE BACKEND RESPONSE")
            sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR BAD JSON")
        sys.exit(1)
else:
    print("ERROR WITH THE BACKEND RESPONSE")
    sys.exit(1)

notebooks = [
    "processing_data/getNewData.ipynb",
    "processing_data/formatRawData.ipynb",
    "models_working/train_model_mlp.ipynb",
    "processing_data/predictCategorization_MLP_MODEL.ipynb", 
    "processing_data/loadNewModel.ipynb",
]

executor = ExecutePreprocessor(timeout=600, kernel_name='python3')

for nb_path in notebooks:
    if not os.path.exists(nb_path):
        print(f"[SKIP] Notebook no encontrado -> {nb_path}")
        continue

    print(f"\n===== RUNNING: {nb_path} =====")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    try:
        nb_dir = os.path.dirname(nb_path) or "."
        executor.preprocess(nb, {"metadata": {"path": nb_dir}})
        print(f"[DONE] {nb_path}")
    except Exception as e:
        print(f"[FAIL] {nb_path}: {e}")
        sys.exit(1)

    if nb_path == "models_working/train_model_mlp.ipynb":
        model_path  = os.path.join("processing_data", "ecg_model_mlp.pth")
        scaler_path = os.path.join("processing_data", "minmaxscaler.pkl")

        if not wait_for_file(model_path, timeout=240):
            print(f"[FAIL] No se encontró el modelo en {model_path}")
            sys.exit(1)

        if not wait_for_file(scaler_path, timeout=240):
            print(f"[FAIL] No se encontró el scaler en {scaler_path}")
            sys.exit(1)

to_delete = [
    "processing_data/predicted_data.csv",
    "processing_data/ecg_segmentado_187.csv",
    "processing_data/ecg_data_to_load.txt",
]
for p in to_delete:
    try:
        if os.path.exists(p):
            os.remove(p)
            print(f"[CLEAN] {p} eliminado")
        else:
            print(f"[CLEAN] {p} no encontrado (ok)")
    except Exception as e:
        print(f"[CLEAN] error eliminando {p}: {e}")
