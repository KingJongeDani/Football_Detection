from pathlib import Path
from typing import Generator
import cv2, asyncio, os
import numpy as np
from fastapi.responses import StreamingResponse
from nicegui import ui, app
from ultralytics import YOLO
import yt_dlp
from moviepy import VideoFileClip

# Modell-Pfad
MODEL_PATH = 'best_football.pt'
model = YOLO(MODEL_PATH)
CONF_THRESH = 0.1

uploaded_video_path = Path('uploaded_video.mp4')

# Bounding Boxes werden gezogen
def draw(result, frame):
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return frame

# Streaming vom Video mit Überprüfung ob das Ende erreicht wurde
def stream() -> Generator[bytes, None, None]:
    global video_done
    video_done = False
    cap = cv2.VideoCapture(str(uploaded_video_path))
    while True:
        ok, frame = cap.read()
        if not ok:
            print('Videoende erreicht')
            video_done = True
            break
        result = model(frame, conf=CONF_THRESH, verbose=False)[0]
        frame = draw(result, frame)
        ok, jpg = cv2.imencode('.jpg', frame)
        if ok:
            #Verwandelt funktion stream() in einen Generator welcher dann Frame für Frame die predictede Bilder an die Website geben kann, damit es weniger Wartezeit gibt, dass man etwas sieht
            # Problem: Es laggt dadurch, es wird nicht mehr "Maßstabsgetreu" (1sek != 1sek)
            # Kurz gesagt "pausiert" yield die Funktion an einer Stelle und kann sie genau dort wieder weiterführen
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n') 
    cap.release()

# Streaming Endpunkt, falls man das Video nochmal sehen möchte (Muss man manuell dann eingeben)
@app.get('/yolo_stream')
def yolo_stream():
    return StreamingResponse(stream(), media_type='multipart/x-mixed-replace; boundary=frame')

# Youtube Download und Schnitt
def download_and_cut_youtube(url: str, start: str, end: str, output_path: Path):
    def to_seconds(t: str) -> int:
        m, s = map(int, t.split(":"))
        return m*60 + s

    start_sec = to_seconds(start)
    end_sec = to_seconds(end)
    # Darf maximal 15sek lang sein
    if end_sec - start_sec > 15:
        end_sec = start_sec + 15

    # Alte Dateien löschen, damit es nicht zu Kompliklationen kommt und die prediction das falsche Video nimmt (war davor ein Problem)
    for fname in ['uploaded_video.mp4', 'youtube_video.mp4', 'youtube_video.webm', 'tmp_clip.mp4']:
        f = Path(fname)
        if f.exists():
            f.unlink()
    # Lädt das Video
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'youtube_video.%(ext)s',
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Hier wird das Video geschnitten, dass man nur den eingegebenen Zeitraum sieht
    clip = VideoFileClip('youtube_video.mp4').subclipped(start_sec, end_sec)
    clip.write_videofile(str(output_path), codec='libx264') # libx264 ist ein Kompressionsstandard für YT-Videos

    return output_path

# Hauptseite, hier kann man dann einen Link einfügen, Start und Endzeit (max 15sek lang), Knöpfe für "jetzt predicten" und "gehe zur prediction"
@ui.page('/')
def index():
    ui.markdown('#Football Detection')
    ui.markdown('##Analysiere einen YouTube-Ausschnitt mit YOLO:')
    ui.markdown("1.) Youtube Fußball Video mit Folgelperspektive von der Seitenlinie suchen")
    ui.markdown("2.) Link reinkopieren und Start- / Stoppzeit eingeben (mm:ss) - maximal 15 Sekunden Differenz ;  Video so kurz wie möglich wählen")
    ui.markdown("3.) Auf Clip Analysieren drücken und warten bis das Video geladen ist")
    ui.markdown("4.) Auf Zum Video drücken und genießen! :)")


    link_input = ui.input('YouTube Link')
    start_input = ui.input('Startzeit (mm:ss)', value='00:00')
    end_input = ui.input('Endzeit (mm:ss)', value='00:10')

    # Spinner Ladebalken
    spinner = ui.spinner(size='lg').classes('mt-4').style('display: none;')

    # Button "Zum Video" wird später eingefügt
    video_button = ui.button(
        'Zum Video',
        on_click=lambda: ui.run_javascript('window.location.href="/video"')
    ).classes('mt-4')
    video_button.disable()   # Startzustand: grau/deaktiviert

    async def handle_youtube():
        spinner.style('display: block;')   # Spinner einblenden
        ui.notify('Neues YouTube-Video wird heruntergeladen...')
        await asyncio.sleep(0.5)

        try:
            download_and_cut_youtube(link_input.value, start_input.value, end_input.value, uploaded_video_path)
            ui.notify('Clip gespeichert!')
            video_button.enable()   # Aktiviert den Button, sobald Video fertig ist
        except Exception as e:
            ui.notify('Es gab einen Fehler bei der Eingabe. Lade die Website neu und versuche es erneut.', type='warning')
            print(f'Fehler: {e}')
        finally:
            spinner.style('display: none;')    # Spinner ausblenden
            await asyncio.sleep(0.5)

    # Erst der Prediction-Button
    ui.button('YouTube-Clip analysieren', on_click=handle_youtube).classes('mt-2')

    # Danach der "Zum Video"-Button
    video_button


# Video-Seite, bekommt das Video von anderen Endpunkt (/yolo_stream)
@ui.page('/video')
def video_page():
    ui.markdown('## Predicted Video')
    ui.image('/yolo_stream').classes('w-full max-w-4xl rounded-xl shadow mt-4')

    status_label = ui.label('').classes('mt-2 text-lg')

    async def check_done():
        while True:
            await asyncio.sleep(1)
            if video_done:
                status_label.text = 'Video zu Ende'
                break

    ui.timer(1.0, check_done)  # prüft jede Sekunde, also fragt eigentlich ab "Ist es schon fertig?"
    ui.button('Zurück zur Startseite', on_click=lambda: ui.run_javascript('window.location.href="/"')).classes('mt-4')

ui.run(host='0.0.0.0', port=9000, reload=False)
