# Instalar librerias
```
pip install -r requirements.txt

```
# Modelos utilizados
## Modelo MLP
Un modelo mlp es habitual para comenzar las pruebas.
### Estructura
En este caso se elabora un modelo que recibe las 187 variables de entrada y posee 5 clases de salida, las cuales representan cada una de las clases. Esta elaborado por 3 capas de 187, 128 y 64, respectivamente, generando un total de 32645 parámetros.
<img width="907" height="927" alt="image" src="https://github.com/user-attachments/assets/dbd4f25a-640f-425f-80e0-e4bad0f68b3f" />
### Rendimiento
El rendimiento del modelo es prometedor, entra una precisión del 97%, con recalls sobre 70%. Eso quiere decir que, si bien la precisión es alta, la fiabilidad de los datos puede no ser lo suficientemente buena. Fue entrenada durante 200 epocas pero deja de aprender cerca de las 20. 

<img width="886" height="528" alt="image" src="https://github.com/user-attachments/assets/88947fdf-c7e2-4fea-b7ce-70350e1fe8ce" />

Este modelo puede ser utilizado pues el rendimiento en general está bien, pero se podría considerar opciones con mayor recall o fiabilidad.

```
Evaluando modelo...

Accuracy: 0.9799

Reporte de clasificación:

              precision    recall  f1-score   support

           0       0.99      0.99      0.99     18118
           1       0.86      0.73      0.79       556
           2       0.94      0.94      0.94      1448
           3       0.82      0.74      0.78       162
           4       0.98      0.98      0.98      1608

    accuracy                           0.98     21892
   macro avg       0.92      0.88      0.90     21892
weighted avg       0.98      0.98      0.98     21892
```

La matriz de confusión por su lado demuestra que el modelo se complica a las diferencias las clases 1 y 3: 

<img width="886" height="689" alt="image" src="https://github.com/user-attachments/assets/80f3fdb6-4c04-4648-802e-eb845513eade" />

### Resultados
El modelo mlp da resultados bastante buena pesar el recall presentdo en las clases 1 y 3: 
<img width="886" height="526" alt="image" src="https://github.com/user-attachments/assets/bb33c8b4-a442-4f6a-824a-a5c0bcf110bd" />

## Modelo CNN
Posteriormente se utiliza un modelo cnn, por su popularidad hoy en día.
### Estructura
Se establece una señal de entrada 1D de 187 puntos, por las 187 muestras del dataset. Cuenta con dos capas convolucionales, la primera aplica 16 filtros de tamaño 15 y utiliza una función de activación Tanh. La segunda aplica 32 filtros de tamaño 7 también con función de activación Tanh. Luego de cada una de las capas convolucionales se aplica un MaxPooling que permite condensar la información y mantener las características más relevantes. Finalmente se genera una salida 3D que se aplana a un vector 1D de un tamaño de 640, esto permite alimentar a las capas densas fully connected donde en la primera se reduce a 64 neuronas generando un total de 41.024 parámetros, y en la última sección, se define otra capa densa fully connected que permite asignar cada muestra a una de las 5 categorías.

<img width="886" height="351" alt="image" src="https://github.com/user-attachments/assets/9afad32e-a47c-4466-b9df-ac01c451ca8f" />

### Rendimiento
En cuanto al entrenamiento se utilizan 200 epocas para entrenar el modelo y al igual que con el modelo mlp ambas rectas divegen, aunque en cnn un poco menos.
<img width="886" height="528" alt="image" src="https://github.com/user-attachments/assets/8522d972-0670-4643-8989-56f1667f69a0" />

Este modelo logra resultados similares a los generados por el mlp pero mas fiables, en general posee menos precisión, pero más recall. Se intentan utilizar métodos típicos como smote y técnicas de balanceo de clases para mejorar el rendimiento.

```
Evaluando modelo...

Accuracy: 0.9684

Reporte de clasificación:

              precision    recall  f1-score   support

           0       0.99      0.97      0.98     18118
           1       0.64      0.81      0.72       556
           2       0.90      0.95      0.92      1448
           3       0.61      0.85      0.71       162
           4       0.97      0.99      0.98      1608

    accuracy                           0.97     21892
   macro avg       0.82      0.91      0.86     21892
weighted avg       0.97      0.97      0.97     21892
```
Por el lado de la matriz de confusión es muy similar a la mlp, el modelo le cuesta mas diferenciar las clases 1 y 3.

<img width="886" height="689" alt="image" src="https://github.com/user-attachments/assets/52d43044-5ba0-4796-bf22-6ab991d3554a" />

### Resultados
Los resultados del modelo cnn son bastante similares al mlp, logra predecir la mayoría de los valores normales de manera correcta, en este caso se ubican algunos valores en en la categoría 2, esto podría ser correcto y que algunos de los datos que presenta el sujeto de pruebas sean anómalos.

<img width="886" height="526" alt="image" src="https://github.com/user-attachments/assets/ce4a8ed4-696f-44ce-8760-a8a0bcf55eec" />

## Modelo Autoencoder
Para este caso, se busca cambiar el enfoque utilizado anteriormente. Con los modelos previos se buscar asignar o predecir una categoría a cada latido recibido, es decir, recibir los valores y que con un modelo aprenda a identificar cada una de las categorías para determinar a qué tipo pertenece en su mayoría.
En este que caso, debido a la disparidad en cuanto a la cantidad de datos, se decide entrenar un modelo solo con la mayor cantidad de datos, en este caso la categoría 0 que representa un corazón sano para luego comparar con señales distintas que en este caso serian el resto de las categorías y determinar según distintos umbrales a cuál pertenece.

### Estructura
El autoencoder elaborado cuenta con una capa de entrada de 187 elementos, en cuanto a las capas densas cuenta con 4 de encoder (128, 64, 23 y 16) y 4 de decoder (32, 64, 128 y 187) todas con la función de activación relu a excepción de la ultima que utiliza sigmoid pues los datos están normalizados con valore de 0 a 1.

<img width="892" height="745" alt="image" src="https://github.com/user-attachments/assets/82a5ecd5-2dc0-4219-bfff-83f50150f31a" />

### Rendimiento
En cuanto al entrenamiento parece haber aprendido correctamente, las curvas de perdida y validación convergen desde el principio de la gráfica hasta al final de las 200 épocas. El modelo fue entrenado para identificar únicamente los latidos normales y parece prometedor.

<img width="858" height="512" alt="image" src="https://github.com/user-attachments/assets/289046a5-562c-4016-a37b-da439c62b2a9" />

```
Especificidad (cat. 0, normales): 88.3%
Sensitividad (cat. 1, abnormales): 40.8%
Sensitividad (cat. 2, abnormales): 83.1%
Sensitividad (cat. 3, abnormales): 3.1%
Sensitividad (cat. 4, abnormales): 91.2%
```
Por el contrario, tanto la especificidad y sensitividad son bastante bajos sobre todo en comparación a los modelos anteriores, principalmente en las clases 1 y 3, cosa se podía visualizar claramente en las matrices de confusión de los modelos anteriores.
Se determina que estas confusiones y la razón que explica por qué estos modelos tienen un mal rendimiento es porque los datos de prueba y entrenamiento son demasiados similares en general por lo que compararlos mediante el resultado del calculo del MAE no da resultados lo suficientemente precisisos particularmente para las clases 1 y 3.

<img width="886" height="482" alt="image" src="https://github.com/user-attachments/assets/fa381287-69fc-4258-974f-03724f8e00d7" />

En esta grafica se puede visualizar que no se logra siquiera separar los datos de anormales 3 y 1 de los datos normales 0.
Para comprar clases normales vs anormales se presenta el siguiente grafico que demuestra que tanto la clase 1 como la 3 tienen un gran parecido a los datos normales.

<img width="886" height="707" alt="image" src="https://github.com/user-attachments/assets/29da2947-2f78-4da4-8fa9-e487bd7d40de" />


### Resultados
Por el lado del modelo de autoencoder, se obtiene lo esperado, que logre predecir que el sujeto de pruebas tiene un corazón sano, pero quizás las muestras asignadas sean reducidas debido a la similitud con algunos datos: 

```
Umbral usado: 0.0838
Conteo de categorías: Counter({'normal': 1128, 'anómalo': 23})
```
En este caso se tendria que complementar con un modelo que indique que tipo de anomalia se detectando, el modelo autoencoder permite determinar si existe o no una anomalia, para categorizar habria que complementar. 