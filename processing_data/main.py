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

ruta = os.path.join(os.path.dirname(__file__), "ngrok_link.txt")
if not os.path.exists(ruta):
    print(f"[ERROR] No se encontró el archivo: {ruta}")
    print("Por favor crea el archivo y coloca el enlace ngrok dentro.")
    sys.exit(1)

with open(ruta, "r", encoding="utf-8") as f:
    base_url = f.read().strip()

urlNewData = f"{base_url}/newData"
urlECG    = f"{base_url}/ecg"

try:
    response = requests.get(urlNewData, timeout=15)
    response.raise_for_status()
    data = response.json()
    print("Response data:", data)
except Exception as e:
    print(f"ERROR solicitando {urlNewData}: {e}")
    sys.exit(1)

newData = data.get("status") == "true"

if newData:
    try:
        responseECG = requests.get(urlECG, timeout=30)
        responseECG.raise_for_status()
        ecg_data = responseECG.json()
    except Exception as e:
        print(f"ERROR solicitando {urlECG}: {e}")
        sys.exit(1)

    if isinstance(ecg_data, list) and all(isinstance(d, dict) and "timestamp" in d and "value" in d for d in ecg_data):
        folder = "."
        ensure_dir(folder)
        file_path = os.path.join(folder, "ecg_data_to_load.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ecg_data, f, indent=4, ensure_ascii=False)
        print("ECG DATA TO LOAD:", file_path)
    else:
        print("ERROR: ECG data format is invalid")
        sys.exit(1)
else:
    print("No new data, solo se ejecutará predicción con modelo local")

# ---------- Definir notebooks ----------
common_notebooks = [
    "getNewData.ipynb",
    "formatRawData.ipynb",
]

training_notebook = "../models_working/train_model_mlp.ipynb"

prediction_notebooks = [
    "predictCategorization_MLP_MODEL.ipynb",
    "loadNewModel.ipynb",
]

executor = ExecutePreprocessor(timeout=600, kernel_name='python3')

for nb_path in common_notebooks:
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

if newData:
    if os.path.exists(training_notebook):
        print(f"\n===== RUNNING TRAINING: {training_notebook} =====")
        with open(training_notebook, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        try:
            nb_dir = os.path.dirname(training_notebook) or "."
            executor.preprocess(nb, {"metadata": {"path": nb_dir}})
            print(f"[DONE] {training_notebook}")
        except Exception as e:
            print(f"[FAIL] {training_notebook}: {e}")
            sys.exit(1)

        model_path  = os.path.join(".", "ecg_model_mlp.pth")
        scaler_path = os.path.join(".", "minmaxscaler.pkl")

        if not wait_for_file(model_path, timeout=240):
            print(f"[FAIL] No se encontró el modelo en {model_path}")
            sys.exit(1)

        if not wait_for_file(scaler_path, timeout=240):
            print(f"[FAIL] No se encontró el scaler en {scaler_path}")
            sys.exit(1)
    else:
        print(f"[SKIP] Notebook de entrenamiento no encontrado -> {training_notebook}")

for nb_path in prediction_notebooks:
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