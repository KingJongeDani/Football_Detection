from pathlib import Path
from typing import Generator
import cv2, asyncio
from fastapi.responses import StreamingResponse, FileResponse
from nicegui import ui, app
from ultralytics import YOLO

# Modell-Pfad
MODEL_PATH = 'best_football.pt'
model = YOLO(MODEL_PATH)
CONF_THRESH = 0.1

# Pfade für Uploads
uploaded_video_path = Path('uploaded_video.mp4')
uploaded_image_path = Path('uploaded_image.jpg')

# Malt nur Bounding Boxes ins Bild/Frame (ohne Label)
def draw(result, frame):

    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return frame

# "Streamt" das hochgeladene Video mit 25 FPS
def stream() -> Generator[bytes, None, None]:
    """Stream YOLO-Frames aus hochgeladenem Video"""
    cap = cv2.VideoCapture(str(uploaded_video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    while True:
        ok, frame = cap.read()
        if not ok:
            print('Videoende erreicht')
            break

        result = model(frame, conf=CONF_THRESH, verbose=False)[0]
        frame = draw(result, frame) #Malt Bounding Box drüber
        ok, jpg = cv2.imencode('.jpg', frame) 
        if not ok:
            continue

        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
               + jpg.tobytes() + b'\r\n')   #Statt alle Frames auf einmal zurückzugeben, liefert sie Frame für Frame nacheinander (Muss dann nd so viel laden)

    cap.release()


# Endpunkt wo das Video abgespielt wird
@app.get('/yolo_stream')
def yolo_stream():
    """Streaming-Endpunkt für YOLO-Frames"""
    return StreamingResponse(stream(), media_type='multipart/x-mixed-replace; boundary=frame')


# Endpunkt wo das Bild mit bounding boxes angezeigt wird
@app.get('/yolo_image')
def yolo_image():
    """Endpunkt für YOLO-Bild"""
    img = cv2.imread(str(uploaded_image_path))
    if img is None:
        return {'error': 'Kein Bild hochgeladen oder konnte nicht geladen werden'}

    result = model(img, conf=CONF_THRESH, verbose=False)[0]
    print("Erkannte Objekte:", len(result.boxes))  # Debug-Ausgabe

    img = draw(result, img)
    output_path = Path('predicted_image.jpg')
    cv2.imwrite(str(output_path), img)

    return FileResponse(str(output_path), media_type='image/jpeg')

# Endpunkt, wenn man die Website öffnet. Zeigt einerseits eine Überschrift
# Und auch die Boxen "Lade ein Video (.mp4) hoch" bzw auch mit Bild
@ui.page('/')
def index():
    ui.markdown('#Football Detection')
    ui.label('Lade ein MP4-Video oder ein Bild hoch, um es mit YOLO zu analysieren:')

    async def handle_video_upload(e):
        file_bytes = await e.file.read()
        with open(uploaded_video_path, 'wb') as f:
            f.write(file_bytes)
        ui.notify('Video erfolgreich hochgeladen!')
        await asyncio.sleep(0.5)
        ui.image('/yolo_stream').classes('w-full max-w-4xl rounded-xl shadow mt-4')

    async def handle_image_upload(e):
        file_bytes = await e.file.read()
        with open(uploaded_image_path, 'wb') as f:
            f.write(file_bytes)
        ui.notify('Bild erfolgreich hochgeladen!')
        await asyncio.sleep(0.5)
        ui.image('/yolo_image').classes('w-full max-w-md rounded-xl shadow mt-4')

    ui.upload(on_upload=handle_video_upload,
              label='MP4-Datei hochladen',
              auto_upload=True).props('accept=.mp4').classes('max-w-md mt-4')

    ui.upload(on_upload=handle_image_upload,
              label='Bild hochladen',
              auto_upload=True).props('accept=.jpg,.jpeg,.png').classes('max-w-md mt-4')


# Server starten
ui.run(host='0.0.0.0', port=9000, reload=False)
