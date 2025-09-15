from fastapi import FastAPI
import uvicorn
import threading
import nbformat
import os
import time
import json
import requests
from nbconvert.preprocessors import ExecutePreprocessor

app = FastAPI()

isProcessing = False 

def wait_for_file(path, timeout=120, poll=1.0):
    start = time.time()
    while time.time() - start <= timeout:
        if os.path.exists(path):
            print(f"[OK] FILE FOUND: {path}")
            return True
        time.sleep(poll)
    print(f"[TIMEOUT] FILE NOT FOUND: {path}")
    return False

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def run_notebooks():
    ruta = os.path.join(os.path.dirname(__file__), "ngrok_link.txt")
    if not os.path.exists(ruta):
        print(f"[ERROR] CANT FIND FILE: {ruta}")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        base_url = f.read().strip()

    urlNewData = f"{base_url}/newData"
    urlECG = f"{base_url}/ecg"
    try:
        response = requests.get(urlNewData, timeout=15)
        response.raise_for_status()
        data = response.json()
        print("[OK] RESPONSE DATA:", data)
    except Exception as e:
        print(f"[ERROR] ERROR FETCHING {urlNewData}: {e}")
        return

    newData = data.get("newData", False) is True

    if newData:
        try:
            responseECG = requests.get(urlECG, timeout=30)
            responseECG.raise_for_status()
            ecg_data = responseECG.json()
        except Exception as e:
            print(f"[ERROR] ERROR FETCHING {urlECG}: {e}")
            return

        if isinstance(ecg_data, list) and all(isinstance(d, dict) and "timestamp" in d and "value" in d for d in ecg_data):
            ensure_dir(".")
            file_path = "ecg_data_to_load.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(ecg_data, f, indent=4, ensure_ascii=False)
            print(f"[OK] ECG DATA SAVED: {file_path}")
        else:
            print("[ERROR] DATA FORMAT INVALID")
            return
    else:
        print("[OK] USING LOCAL MODEL")

    common_notebooks = ["getNewData.ipynb", "formatRawData.ipynb"]
    training_notebook = "../models_working/train_model_mlp.ipynb"
    prediction_notebooks = ["predictCategorization_MLP_MODEL.ipynb", "loadNewModel.ipynb"]

    executor = ExecutePreprocessor(timeout=600, kernel_name='python3')

    for nb_path in common_notebooks:
        if not os.path.exists(nb_path):
            print(f"[SKIP] CANT FIND -> {nb_path}")
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
            return

    if newData and os.path.exists(training_notebook):
        print(f"\n===== RUNNING TRAINING: {training_notebook} =====")
        with open(training_notebook, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        try:
            nb_dir = os.path.dirname(training_notebook) or "."
            executor.preprocess(nb, {"metadata": {"path": nb_dir}})
            print(f"[DONE] {training_notebook}")
        except Exception as e:
            print(f"[FAIL] {training_notebook}: {e}")
            return

        for path in ["ecg_model_mlp.pth", "minmaxscaler.pkl"]:
            if not wait_for_file(path, timeout=240):
                print(f"[FAIL] CANT FIND: {path}")
                return

    for nb_path in prediction_notebooks:
        if not os.path.exists(nb_path):
            print(f"[SKIP] CANT FIND -> {nb_path}")
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
            return

def polling_loop(base_url: str):
    global isProcessing
    while True:
        try:
            status_url = f"{base_url}/predictionStatus"
            response = requests.get(status_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            print("[POLL] STATUS:", data["status"]["ok"], "MESSAGE:", data["status"]["message"])

            if data["status"]["message"] == "Prediction sended" and not isProcessing:
                isProcessing = True
                print("[INFO] Prediction sended detected! Running notebooks...")
                run_notebooks()
                print("[OK] Cycle finished. Waiting 20s for next signal...")
                time.sleep(20)
                isProcessing = False
        except Exception as e:
            print("[ERROR] Polling loop:", e)
        time.sleep(5)

@app.on_event("startup")
def start_polling():
    threading.Thread(target=polling_loop, args=("http://localhost:3333",), daemon=True).start()

@app.post("/doPrediction")
async def do_prediction():
    return {"ok": True, "message": "Polling loop already running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
