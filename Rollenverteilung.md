# Rollenverteilung
## Daniel Kraxner
### GUI
- Gesamte Benutzeroberfläche
    - Upload von Bildern und Videos
    - Anzeigen der Predictions
    - Streaming von Frames
- Geschafft, dass die Webapplikation auch auf den KI-Server funktioniert 
- Zusäzlich nochmal auf eigenen Endgerät probiert

### Daten
- YOLO-Modell Trainiert + Preprocessing (Während Niklas weitere Datensätze gesucht hat um zu mergen)
    - Preprocessing:
        - Helligkeit
        - Blurring
        - Farbanpassung

## Niklas Gössler
### Daten
- Datensatz gesucht und für unsere Applikation angepasst
- Weitere Datensätze gesucht (Merging)
- Trainingsläufe vorbereitet
- Modellresultate auszuwerten und am Schulserver getestet, ob das Modell Predictions erstellt
- Daten zum Testen des Modells gesucht

## Gemeinsame Arbeiten

- Mehrere Testdurchläufe auf Bildern und Videos gemacht
- Verhalten des Modells im Browser und am Server analysiert
- Probiert ein **weiteres Modell** zu machen, welches 2 Teams erkennt
- Dieses zweite Modell hat in der Praxis jedoch nicht gut funktioniert,
    - Teams wurden nicht zuverlässig auseinandergehalten
    - Schiedsrichter wurden anhand der Farben oft falsch erkannt
- Deshalb haben wir entschieden, das Modell vorerst nicht weiter zu verwenden

## Probleme
- Webapplikation auf Server starten
- Genug Trainingsbilder finden
- Zweites Modell hat Zeit gekostet und trotzdem nicht gut funktioniert
- Modell funktioniert bei Videos besser als bei Bilder
- Confidence muss sehr weit runtergestellt werden

## Erkenntnisse
- YOLO ist sehr gut, aber kein "Wundermittel"
- Datensatz Qualität und Größe haben einen sehr wichtigen und großen Einfluss auf das Modell, wie gut es funktioniert
- Preprocessing verbessert teilweise die Ergebnisse
- Browser Applikationen

# History
## 1. Einheit
- Grundlagen YOLO
- Einteilung in Gruppen
- Projektfindung

## 2. Einheit
- Passende Datensätze in Roboflow gesucht
- Venv eingerichtet
- Überlegt wie das Training funktionieren könnte
- Angefangen zu trainieren

## 3. Einheit
- NiceGUI begonnen
- Datensätze gemerged
- Weiter trainiert
- Erste Testläufe

## 4. Einheit
- Neues Modell gemacht, welches zwei Teams unterscheiden soll
- Modell trainiert
- Datensatz gesucht
- NiceGUI auf KI-Server gebracht
- Video Erkennung begonnen

## 5. Einheit
- NiceGUI 
- Video Erkennung
- Modell weitertrainiert
- Testläufe für Modell
- (Nicht sehr effektive Einheit, aufgrund eines Defekts im KI-Server)

## 6. Einheit
- Preprocessing um beim 1. Modell bessere Ergebnisse zu erzielen
- NiceGUI Fertigstellung
- Fertig trainiert
- Letze Testläufe