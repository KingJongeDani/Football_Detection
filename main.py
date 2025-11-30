from pathlib import Path
from typing import Generator
import cv2, asyncio
from fastapi.responses import StreamingResponse, FileResponse
from nicegui import ui, app
from ultralytics import YOLO
import yt_dlp
from moviepy import VideoFileClip

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

# "Streamt" das hochgeladene Video mit YOLO-Predictions
def stream() -> Generator[bytes, None, None]:
    cap = cv2.VideoCapture(str(uploaded_video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    while True:
        ok, frame = cap.read()
        if not ok:
            print('Videoende erreicht')
            break
        result = model(frame, conf=CONF_THRESH, verbose=False)[0]
        frame = draw(result, frame)
        ok, jpg = cv2.imencode('.jpg', frame)
        if not ok:
            continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
               + jpg.tobytes() + b'\r\n')
    cap.release()

@app.get('/yolo_stream')
def yolo_stream():
    return StreamingResponse(stream(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get('/yolo_image')
def yolo_image():
    img = cv2.imread(str(uploaded_image_path))
    if img is None:
        return {'error': 'Kein Bild hochgeladen oder konnte nicht geladen werden'}
    result = model(img, conf=CONF_THRESH, verbose=False)[0]
    img = draw(result, img)
    output_path = Path('predicted_image.jpg')
    cv2.imwrite(str(output_path), img)
    return FileResponse(str(output_path), media_type='image/jpeg')

# Hilfsfunktion: YouTube-Video herunterladen und zuschneiden
def download_and_cut_youtube(url: str, start: str, end: str, output_path: Path):
    def to_seconds(t: str) -> int:
        m, s = map(int, t.split(":"))
        return m*60 + s

    start_sec = to_seconds(start)
    end_sec = to_seconds(end)
    if end_sec - start_sec > 15:
        end_sec = start_sec + 15

    # Download mit yt-dlp
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'youtube_video.%(ext)s',
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Zuschneiden mit moviepy (neue Version → subclipped)
    clip = VideoFileClip('youtube_video.mp4').subclipped(start_sec, end_sec)
    clip.write_videofile(str(output_path), codec='libx264')

    return output_path

# --- Neue Seite für Bildanzeige ---
@ui.page('/yolo_image_page')
def yolo_image_page():
    ui.markdown('## YOLO Bildausgabe')
    ui.image('/yolo_image').classes('w-full max-w-md rounded-xl shadow mt-4')
    ui.button('Zurück zur Hauptseite',
              on_click=lambda: ui.run_javascript('window.location.href="/"')).classes('mt-4')

# --- Hauptseite ---
@ui.page('/')
def index():
    ui.markdown('#Football Detection')
    ui.label('Lade ein MP4-Video oder ein Bild hoch, oder nutze YouTube:')

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
        ui.button('Gehe zu YOLO-Bildseite',
                  on_click=lambda: ui.run_javascript('window.location.href="/yolo_image_page"')
                 ).classes('mt-4')

    ui.upload(on_upload=handle_video_upload,
              label='MP4-Datei hochladen',
              auto_upload=True).props('accept=.mp4').classes('max-w-md mt-4')

    ui.upload(on_upload=handle_image_upload,
              label='Bild hochladen',
              auto_upload=True).props('accept=.jpg,.jpeg,.png').classes('max-w-md mt-4')

    # --- YouTube Bereich ---
    ui.separator()
    ui.markdown('## YouTube-Ausschnitt für Prediction')

    link_input = ui.input('YouTube Link')
    start_input = ui.input('Startzeit (mm:ss)', value='00:00')
    end_input = ui.input('Endzeit (mm:ss)', value='00:10')

    async def handle_youtube():
        ui.notify('YouTube-Video wird heruntergeladen und zugeschnitten...')
        await asyncio.sleep(0.5)
        download_and_cut_youtube(link_input.value, start_input.value, end_input.value, uploaded_video_path)
        ui.notify('Clip gespeichert, YOLO-Analyse startet!')
        await asyncio.sleep(0.5)
        ui.image('/yolo_stream').classes('w-full max-w-4xl rounded-xl shadow mt-4')

    ui.button('YouTube-Clip analysieren', on_click=handle_youtube).classes('mt-2')

ui.run(host='0.0.0.0', port=9000, reload=False)
