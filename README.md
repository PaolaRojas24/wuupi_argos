<h1>Proyecto con Wuupi</h1>
<p>Equipo Robonautas:</p>
Daniel Castillo López A01737357</br>
Emmanuel Lechuga Arreola A01736241</br>
Paola Rojas Domínguez A01737136</br>
</br>
Video de la demo: https://youtu.be/0E-hnjby2FA
<h2>Descripción general</h2>
Este proyecto permite que una interfaz hecha en Unity interactúe con dos scripts de Python (manos_argos.py y piernas_argos.py) que procesan video en tiempo real y detectan zonas tocadas por la mano o zonas relacionadas con piernas. Unity se encarga de gestionar el inicio de sesión, la selección del modo, la cámara a usar, y visualizar el video procesado.

<h2>Requisitos del sistema</h2>
<li>Sistema operativo: Windows 10 u 11</li>
<li>Procesador Mínimo: Intel core i3 (décima generación o superior) o AMD Ryzen 5 (2da generación o superior).</li>
<li>Memoría RAM: 8GB DDR4 Suficiente para cargar sistema operativo, las librerías (mas la de media pipe) y manejar stream de video en memoria sin agotar recursos.</li>
<li>Memoria gráfica: Integrada (intel iris Xe Graphics, AMD Radeon Graphics).</li>
<li>Cámara: Webcam HD (720p x 480p) recomendado: webcam full HD (1080p a 30 fps o 60 fps ) o celular con Droidcam</li>
<li>Unity 2022 o superior</li>
<li>Python 3.9 o superior</li>
<li>Conexión a internet si se usará cámara por IP (DroidCam)</li>

<h2>Librerías de Python usadas</h2>
<li>opencv-python: procesamiento de video</li>
<li>mediapipe: detección de manos/piernas</li>
<li>numpy: operaciones con arreglos</li>
<li>openpyxl: manipulación de archivos Excel</li>
<li>socket, struct, time, sys: librerías estándar para comunicación y control</li>

<h2>Instalación</h2>
<h3>1. Instalar Python y dependencias</h3>
1. Asegúrate de tener Python instalado. Puedes descargarlo desde: https://www.python.org/downloads/ </br>
2. Descargar los archivos de la carpeta librerías: https://github.com/PaolaRojas24/wuupi_argos/tree/main/Librerias</br>
3. Ejecuta el script setup_env.bat para instalar las librerías necesarias: </br>
<li>Doble clic en setup_env.bat</li>
<li>Espera a que finalice la instalación</li>
<h3>2. Abrir el proyecto en Unity</h3>
1. Descarga el proyecto de unity de la carpeta Wuupi (se sugiere utilizar DownGit): https://github.com/PaolaRojas24/wuupi_argos/tree/main/Wuupi </br>
2. Abre Unity Hub </br>
3. Selecciona "Add" y carga la carpeta del proyecto </br>
4. Abre la escena inicial: LoginScene.unity </br>

<h2>Uso del sistema</h2>
<h3>1. LoginScene</h3>
El usuario debe ingresar:

<li>Nombre de usuario</li>
<li>Contraseña</li>
<li>Tipo de procesamiento (Manos o Piernas)</li>
<li>Cámara a usar (Integrada o DroidCam)</li>
<li>Si escoge DroidCam, debe ingresar una IP (ej. 10.50.124.161)</li>

Al presionar el botón "Iniciar", se guarda la información y se carga la CamaraScene.
<h3>2. CamaraScene</h3>
Unity lanza el script correspondiente de Python (manos_argos.py o piernas_argos.py)
El script:
<li>Procesa el video</li>
<li>Detecta zonas de interacción (con MediaPipe)</li>
<li>Envia imágenes procesadas por socket a Unity</li>
Unity recibe y muestra el video en tiempo real en un RawImage.

<h2>Comunicación Unity ↔ Python</h2>
<li>Unity inicia el script Python con System.Diagnostics.Process.</li>
<li>El script Python actúa como servidor TCP (puerto 8000) y envía frames codificados.</li>
<li>Unity se conecta como cliente y visualiza los frames.</li>

<h2>manos_argos.py</h2>
Este script detecta manos humanas utilizando la librería MediaPipe y determina qué zonas de la pantalla están siendo tocadas por la mano. Funciona de la siguiente manera:
<li>Captura video desde una cámara (integrada o IP con DroidCam).</li>
<li>Usa MediaPipe Tasks para detectar manos y extraer landmarks (puntos clave).</li>
<li>Divide la imagen en zonas visuales (zona segura y cuatro zonas representando cada uno de los botones).</li>
<li>Determina qué zona está siendo activada por la mano y la envía en tiempo real a Unity mediante sockets.</li>
<li>También se visualiza la imagen procesada con anotaciones en tiempo real dentro de Unity.</li>
Este script es útil para sistemas de interacción sin contacto, interfaces gestuales o control de elementos con movimiento de la mano.</br>
En caso de querer modificar el tamaño de las zonas, se deben de modificar las siguentes líneas de código:

```
height, width, _ = annotated_image.shape
section_width = width // 4
zona_segura_inicio_y = int(0.7 * height)
```

<h2>piernas_argos.py</h2>
Este script está diseñado para el seguimiento de piernas u objetos similares. Su comportamiento es el siguiente:
<li>Captura video en tiempo real desde la cámara seleccionada.</li>
<li>Utiliza MediaPipe Pose para detectar posiciones clave de las piernas.</li>
<li>Calcula en qué zonas de la pantalla se encuentran los elementos detectados.</li>
<li>Envía la información a Unity, que puede utilizarla para visualización, interacción o toma de decisiones.</li>
Este script puede utilizarse para interfaces controladas por movimientos de pierna, análisis de postura o sistemas de detección de presencia en ciertas regiones del espacio visual.

<h2>registro_usuarios.py</h2>
Este script se encarga de registrar los usuarios que inician sesión.</br>
Almacena la información en un archivo Excel (usuarios.xlsx) con las columnas:
<li>Usuario</li>
<li>Contraseña</li>
