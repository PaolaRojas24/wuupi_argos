import cv2
import mediapipe as mp
import numpy as np
import time
import socket
import struct
import sys
from registro_usuarios import guardar_usuario

if len(sys.argv) >= 3:
    username = sys.argv[1]
    password = sys.argv[2]
    cam_option = sys.argv[3]
    droidcam_ip = sys.argv[4]
    guardar_usuario(username, password)
else:
    print("No se recibieron usuario y contraseña.")

# Inicializar MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)
mp_drawing = mp.solutions.drawing_utils

if cam_option == "Integrada":
    cap = cv2.VideoCapture(0)
elif cam_option == "DroidCam":
    cap = cv2.VideoCapture(f'http://{droidcam_ip}:4747/video')
else:
    print("Opción de cámara no válida")
    sys.exit(1)

# Variables para el modo de ajuste de sensibilidad
umbral_mov = 20     # Sensibilidad inicial
umbral_min = 5
umbral_max = 80
posicion_inicial = None

# Confirmación en zona 1 (con pie izquierdo)
tiempo_confirmacion = 2  # segundos
inicio_en_zona_1 = None
confirmado = False
modo_ajuste_sensibilidad = True

# Una vez detectada la persona, guardaremos estas líneas y no las volveremos a calcular
zone_lines_static = None

# Tiempo para esperar 10 segundos mostrando cámara antes de procesar lógica
#inicio_espera = time.time()
#tiempo_espera = 10  # segundos

def compute_zone_lines(landmarks, w):
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    x_left = int(left_knee.x * w)
    x_right = int(right_knee.x * w)
    x_mid = (x_left + x_right) // 2

    zone_width = int(w * 0.1)
    offsets = [-2, -1, 1, 2]
    return [x_mid + offset * zone_width for offset in offsets]

def draw_static_zones(image, zone_lines, h):
    for x in zone_lines:
        cv2.line(image, (x, 0), (x, h), (0, 255, 0), 2)

    x_neutral_left = zone_lines[1]
    x_neutral_right = zone_lines[2]
    overlay = image.copy()
    cv2.rectangle(overlay, (x_neutral_left, 0), (x_neutral_right, h), (0, 255, 255), -1)
    alpha = 0.2
    image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

    cv2.putText(image, "Zona Neutral", (x_neutral_left + 10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
    return image

# Crear socket TCP para enviar video a Unity
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8000))  # Cambia IP si lo corres desde otro dispositivo
server_socket.listen(1)
print("Esperando conexión desde Unity...")
client_socket, addr = server_socket.accept()
print(f"Conectado a Unity en {addr}")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)
        annotated_image = frame.copy()

        # Siempre dibujamos landmarks y zonas si están disponibles
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            if zone_lines_static is None:
                zone_lines_static = compute_zone_lines(landmarks, w)

            mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )
            annotated_image = draw_static_zones(annotated_image, zone_lines_static, h)

        # Mostrar imagen con landmarks siempre
        cv2.imshow('Pose y Zonas', annotated_image)

        # Aquí continúa la lógica que tenías de detección y ajuste
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            zona_actual = None

            right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]

            if right_ankle.visibility > 0.5:
                ankle_x_right = int(right_ankle.x * w)
                if ankle_x_right < zone_lines_static[0]:
                    zona_actual = 1
                elif ankle_x_right < zone_lines_static[1]:
                    zona_actual = 2

            if left_ankle.visibility > 0.5:
                ankle_x_left = int(left_ankle.x * w)
                if zone_lines_static[2] < ankle_x_left <= zone_lines_static[3]:
                    zona_actual = 3
                elif ankle_x_left > zone_lines_static[3]:
                    zona_actual = 4

            if zona_actual:
                cv2.putText(annotated_image, f"Zona detectada: {zona_actual}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

            if modo_ajuste_sensibilidad:
                if right_ankle.visibility > 0.5:
                    x_mov = ankle_x_right
                    if posicion_inicial is None:
                        posicion_inicial = x_mov
                    else:
                        desplazamiento = x_mov - posicion_inicial
                        if abs(desplazamiento) > umbral_min:
                            if desplazamiento > 0 and umbral_mov < umbral_max:
                                umbral_mov += 1
                            elif desplazamiento < 0 and umbral_mov > umbral_min:
                                umbral_mov -= 1
                            posicion_inicial = x_mov

                if left_ankle.visibility > 0.5:
                    ankle_x_left = int(left_ankle.x * w)
                    if ankle_x_left < zone_lines_static[0]:
                        if inicio_en_zona_1 is None:
                            inicio_en_zona_1 = time.time()
                        elif time.time() - inicio_en_zona_1 >= tiempo_confirmacion:
                            confirmado = True
                            modo_ajuste_sensibilidad = False
                            print(f"✅ Sensibilidad confirmada: {umbral_mov}")
                    else:
                        inicio_en_zona_1 = None

                barra_x = int(w * 0.75)
                barra_y = int(h * 0.2)
                barra_ancho = int(w * 0.2)
                barra_alto = 20
                barra_llena = int((umbral_mov / 100) * barra_ancho)

                cv2.rectangle(annotated_image, (barra_x, barra_y), (barra_x + barra_ancho, barra_y + barra_alto), (100,100,100), 2)
                cv2.rectangle(annotated_image, (barra_x, barra_y), (barra_x + barra_llena, barra_y + barra_alto), (0,255,0), -1)
                cv2.putText(annotated_image, "Sensibilidad", (barra_x, barra_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

                cv2.imshow('Pose y Zonas', annotated_image)
                # Codificar el frame como JPEG
                _, jpeg_frame = cv2.imencode('.jpg', annotated_image)
                frame_data = jpeg_frame.tobytes()

                # Enviar tamaño y luego frame
                client_socket.sendall(struct.pack(">L", len(frame_data)))
                client_socket.sendall(frame_data)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
            break

except KeyboardInterrupt:
    print("Captura detenida manualmente.")

pose.close()
cap.release()
cv2.destroyAllWindows()

