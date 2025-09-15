# Dispositivo predictor con mantenedor de versiones
Este dispositivo se encarga de recibir la informacion proveniente desde el [backend](https://github.com/Mati11111/ecg-back) para procesar las señales ECG y, si es necesario, entrenar el modelo predictor, devolviendo una carga API externa con los resultados de la prediccion.

## Dispositivo predictor
Sistema encargado de realizar proceso de prediccion y entrenamiento, una vez realiza el entrenamiento carga en API externa (cloudinary por defecto) el modelo, pesos y resultado de las predicciones.

### Instalar librerias
```bash
cd ./processing_data
pip install -r requirements.txt
```
### Ejecutar servidor
```bash
cd ./processing_data
python main.py
```
Una vez ejecutado el documento **main.py** se realiza el flujo de entrenamiento y prediccion de datos, es importante realizar la conversion de los archivos ipynb a py para poder leerlos, este flujo esta especificado dentro de [Data-Processing](https://github.com/Mati11111/ECG-Arrhythmia-Categorizator-/blob/main/docs/Data-Processing.md).

## Mantenedor de dispositivo
Sistema encargado de mantener actualizado el dispositivo, recibe webhook desde github para controlar enlaces dinamicos y nuevas versiones.

### Instalar dependencias
```bash
cd ./backend
npm install
```
### Ejecutar servidor
```bash
npm run dev
```
