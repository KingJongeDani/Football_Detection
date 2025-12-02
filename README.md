# Projektbeschreibung
Dieses Projekt stellt eine Weboberfläche (GUI) für ein YOLOv8-Modell bereit, das Fußballspieler und Bälle in Videos erkennt.
Über die NiceGUI-Webseite können Benutzer:
1. Einen Youtube-Link einfügen + Start-/Stopp-Zeit eingeben
2. Bounding Boxes der erkannten Personen & Bälle ansehen

Das gesamte Setup läuft als Webserver, den man im Browser öffnen kann.

# Installation
Bevor das Projekt gestartet werden kann, müssen alle benötigten Bibliotheken installiert werden.
Dafür gibt es eine requirements.txt, die alle notwendigen Abhängigkeiten enthält.
Dazu wird eine VM (venv) empfohlen. Falls diese bereits vorhanden ist, diesen Schritt einfach überspringen.

## Venv Installation
1. Repository / Projekt herunterladen
2. Terminal vom Projekt öffnen und "python -m venv *Name*_venv" eingeben
3. Um die venv zu starten muss man folgendes im Terminal eingeben:
    - Windows: *Name*_venv\Scripts\activate
    - MAC/Linux: source *Name*_venv/bin/activate

## Requirements
Nachdem die venv gestartet wurde, muss folgendes eingegeben werden, um alle requirements zu installieren: "**pip install -r requirements.txt**"

# Starten des Webservers
1. Öffne ein Terminal in VS Code
2. In das Projektverzeichnis welchseln
3. Starte die Anwendung mit "python main.py"
4. Öffne im Browser: "**http://127.0.0.1:9000/**" bzw. jene Adresse, die festgelegt wurde
5. Ein Youtube Link von einem Fußballspiel aus der selben Perspektive wie die Beispielvideos einfügen und dann eine Start-/Stopp-Zeit (mm:ss) eingeben (max 15sek Differenz)
6. Danach auf "YouTube-Clip analysieren" drücken und warten, bis der Ladebalken nicht mehr zusehen ist
7. Anschließend auf "Zum Video" drücken, um das vorhergesagte Ergebnis zu sehen
6. Wenn "Videoende erreicht" angezeigt wird, kann man nach beliebe auf den Knopf "Zurück zur Startseite" drücken und den gesamten Vorgang wiederholen.

