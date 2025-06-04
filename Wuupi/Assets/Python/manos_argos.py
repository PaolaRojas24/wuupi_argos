import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
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

def draw_landmarks_on_image(rgb_image, detection_result, zone_status):
    hand_landmarks_list = detection_result.hand_landmarks
    annotated_image = np.copy(rgb_image)

    height, width, _ = annotated_image.shape
    section_width = width // 4
    zona_segura_inicio_y = int(0.7 * height)

    # Colores por sección (azul, verde, amarillo, rojo)
    colores = [(72, 232, 248), (61, 198, 68), (255, 232, 74), (253, 148, 232)]
    
    # Grosor de líneas negras que delimitan zonas
    black_thickness = 3

    # Dibujar líneas divisorias negras más gruesas
    for i in range(1, 4):
        x = i * section_width
        cv2.line(annotated_image, (x, 0), (x, zona_segura_inicio_y), (0, 0, 0), black_thickness)
    cv2.line(annotated_image, (0, zona_segura_inicio_y), (width, zona_segura_inicio_y), (0, 0, 0), black_thickness)
    cv2.rectangle(annotated_image, (0, zona_segura_inicio_y), (width, height), (0, 0, 0), black_thickness)

    # Dibujar cuadrados de 20x20 en medio de cada sección arriba
    for i in range(4):
        center_x = i * section_width + section_width // 2
        top_left = (center_x - 35, 0)
        bottom_right = (center_x + 10, 70)
        cv2.rectangle(annotated_image, top_left, bottom_right, colores[i], -1)

    # Pintar zonas activas (si se cumplió tiempo), excepto zona 5
    for zone_idx, status in zone_status.items():
        if status['active']:
            if zone_idx < 4:  # Secciones 1-4
                x_start = zone_idx * section_width
                x_end = (zone_idx + 1) * section_width
                y_start = 0
                y_end = zona_segura_inicio_y

                # Overlay con color y opacidad
                overlay = annotated_image.copy()
                color = colores[zone_idx]

                cv2.rectangle(overlay, (x_start, y_start), (x_end, y_end), color, -1)
                alpha = 0.6
                cv2.addWeighted(overlay, alpha, annotated_image, 1 - alpha, 0, annotated_image)

                # Perímetro del color, sin sobreponer las líneas negras (dentro del rectángulo)
                offset = black_thickness  # Para que no se superponga
                cv2.rectangle(annotated_image,
                              (x_start + offset, y_start + offset),
                              (x_end - offset, y_end - offset),
                              color, black_thickness)

            # Para zona 5 (index 4), no color de fondo, solo perímetro punteado verde
            # (aunque la zona no se active por tiempo, si la mano entra se dibuja el perímetro punteado)
            # Esto se controla más abajo fuera de este bloque

    # Procesar cada mano para detección y zona dominante
    zones_touched = set()
    for landmarks in hand_landmarks_list:
        section_counts = [0, 0, 0, 0, 0]  # 4 secciones + zona segura

        for landmark in landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)

            if y < zona_segura_inicio_y:
                section_index = min(x // section_width, 3)
            else:
                section_index = 4

            section_counts[section_index] += 1
            cv2.circle(annotated_image, (x, y), 4, (255, 0, 0), -1)

        # Conexiones de la mano
        for connection in mp.solutions.hands.HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            cv2.line(annotated_image,
                     (int(start.x * width), int(start.y * height)),
                     (int(end.x * width), int(end.y * height)),
                     (0, 255, 255), 2)

        zona_dominante = section_counts.index(max(section_counts))
        zones_touched.add(zona_dominante)
        wrist = landmarks[0]
        cx = int(wrist.x * width)
        cy = int(wrist.y * height)
        cv2.putText(annotated_image, f'Zona {zona_dominante + 1}', (cx, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Llevar un set de zonas activas en este frame
    zonas_activas_este_frame = set()

    for landmarks in hand_landmarks_list:
        section_counts = [0, 0, 0, 0, 0]

        for landmark in landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)

            if y < zona_segura_inicio_y:
                section_index = min(x // section_width, 3)
            else:
                section_index = 4

            section_counts[section_index] += 1
            cv2.circle(annotated_image, (x, y), 4, (255, 0, 0), -1)

        for connection in mp.solutions.hands.HAND_CONNECTIONS:
            start_idx, end_idx = connection
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            cv2.line(annotated_image,
                     (int(start.x * width), int(start.y * height)),
                     (int(end.x * width), int(end.y * height)),
                     (0, 255, 255), 2)

        zona_dominante = section_counts.index(max(section_counts))
        zones_touched.add(zona_dominante)
        zonas_activas_este_frame.add(zona_dominante)

        wrist = landmarks[0]
        cx = int(wrist.x * width)
        cy = int(wrist.y * height)
        cv2.putText(annotated_image, f'Zona {zona_dominante + 1}', (cx, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Actualizar contadores de zona solo si fueron tocadas en este frame
    for idx in zone_status.keys():
        if idx in zonas_activas_este_frame and idx != 4:
            zone_status[idx]['count'] += 1
        elif idx != 4:
            zone_status[idx]['count'] = 0
            zone_status[idx]['active'] = False

    # Dibujar perímetro punteado verde en zona 5 si la mano está ahí (sin color de fondo)
    if 4 in zones_touched:
        x_start = 0
        x_end = width
        y_start = zona_segura_inicio_y
        y_end = height
        offset = black_thickness

        # Dibujar líneas punteadas verdes (separado en segmentos para simular punteado)
        gap = 10
        line_color = (0, 255, 0)
        thickness = 2

        # Top border punteado
        for x in range(x_start + offset, x_end - offset, gap*2):
            cv2.line(annotated_image, (x, y_start + offset), (x + gap, y_start + offset), line_color, thickness)
        # Bottom border punteado
        for x in range(x_start + offset, x_end - offset, gap*2):
            cv2.line(annotated_image, (x, y_end - offset), (x + gap, y_end - offset), line_color, thickness)
        # Left border punteado
        for y in range(y_start + offset, y_end - offset, gap*2):
            cv2.line(annotated_image, (x_start + offset, y), (x_start + offset, y + gap), line_color, thickness)
        # Right border punteado
        for y in range(y_start + offset, y_end - offset, gap*2):
            cv2.line(annotated_image, (x_end - offset, y), (x_end - offset, y + gap), line_color, thickness)

    return annotated_image, zone_status


# Crear detector
base_options = python.BaseOptions(model_asset_path=r'Assets\Documents\hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

if cam_option == "Integrada":
    cap = cv2.VideoCapture(0)
elif cam_option == "DroidCam":
    cap = cv2.VideoCapture(f'http://{droidcam_ip}:4747/video')
else:
    print("Opción de cámara no válida")
    sys.exit(1)

# Estado de zonas: contador de frames y activo (colorado)
zone_status = {
    0: {'count': 0, 'active': False},  # Sección 1
    1: {'count': 0, 'active': False},  # Sección 2
    2: {'count': 0, 'active': False},  # Sección 3
    3: {'count': 0, 'active': False},  # Sección 4
    4: {'count': 0, 'active': False}   # Zona segura
}

FRAME_RATE = 30  # Ajusta si tu cámara tiene diferente fps
FRAMES_TO_ACTIVE = 2 * FRAME_RATE  # 2 segundos * fps

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

        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        result = detector.detect(mp_img)

        # Dibujar y actualizar zona_status
        annotated, zone_status = draw_landmarks_on_image(img_rgb, result, zone_status)

        # Activar zona si se cumplió el tiempo requerido (solo zonas 0-3)
        for zone_idx, status in zone_status.items():
            if zone_idx != 4 and status['count'] >= FRAMES_TO_ACTIVE:
                status['active'] = True
                print(zone_idx + 1)

        cv2.imshow("Webcam", cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

        _, img_encoded = cv2.imencode('.jpg', cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
        data = img_encoded.tobytes()

        # Enviar longitud primero (4 bytes)
        client_socket.sendall(struct.pack(">L", len(data)))
        # Enviar los datos de la imagen
        client_socket.sendall(data)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Captura detenida manualmente.")

finally:
    client_socket.close()
    server_socket.close()
    cap.release()
    cv2.destroyAllWindows()

cap.release()
cv2.destroyAllWindows()