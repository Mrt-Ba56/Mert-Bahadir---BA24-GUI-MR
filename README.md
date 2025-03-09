README - Steuerung des Magnetresonanz-Experiments

Projektbeschreibung
Dieses Projekt umfasst die Steuerung eines Magnetresonanz-Experiments durch die Kommunikation zwischen einem Python-Programm und einem Mikrocontroller (Arduino). 
Der Mikrocontroller übernimmt dabei zentrale Aufgaben wie Pulsgenerierung, Audiofrequenz-Synthese und Digitalisierung der Messsignale.

-Ablauf des Experiments

1.Verbindungsaufbau: Der Rechner stellt eine Verbindung zum Mikrocontroller her, um das Experiment zu steuern.

2.Aktivierung der Polarisationsschaltung: Die Polarisationsspule wird mit Energie versorgt, um ein starkes inhomogenes Magnetfeld zu erzeugen, das die Kernspins der Protonen ausrichtet.

3.Erzeugung der Hochfrequenzpulse (RF-Pulse): Die Senderplatine wandelt die Pulssignale des Mikrocontrollers in präzise Sinussignale um, die der Larmorfrequenz der Protonen entsprechen.

4.Signalaufnahme: Nach der Anregung durch die RF-Pulse senden die Protonen während der Relaxation ein FID-Signal, das von der Empfangsspule aufgenommen wird.

5.Signalverarbeitung: Das empfangene Signal wird verstärkt, von Störkomponenten befreit und zur Digitalisierung an den Mikrocontroller zurückgeleitet.

6.Datenübertragung und Analyse: Die digitalisierten Signale werden an den Rechner zurückgesendet, wo sie weiter analysiert werden.

-Aufbau des Codes

Das Experiment basiert auf einer Kombination aus Python- und Arduino-Code. Der Python-Code steuert die Pulssequenzen und sendet sie an den Arduino, der die Sequenzen verarbeitet und die Hardware steuert.

Wichtige Code-Dateien
1.anmr_compiler.py: Übersetzt Befehle in Byte-Sequenzen für den Mikrocontroller.
2.commandsFullEcho.txt: Enthält die vollständigen Befehle und zugehörigen Arduino-Pins zur Steuerung des Experiments.
3.anmr_common.py: Definiert allgemeine Funktionen für die Kommunikation zwischen Python und dem Mikrocontroller, einschließlich Befehlsübermittlung und Rückgabewerte.
4.anmr_com.ipynb: Importiert die vorherigen Python-Skripte und steuert die Experimentabläufe. Integriert die Eingabedatei, führt die Kompilierung durch und sendet die Befehle an den Arduino.

-Kommunikation zwischen Python und Arduino

Die serielle Schnittstelle wird mithilfe der Python-Bibliothek serial genutzt, um den Datenaustausch zwischen dem Rechner und dem Mikrocontroller zu ermöglichen.   
Der ursprüngliche Arduino-Code wurde 2010 von Carl A. Michal entwickelt und bleibt unverändert.

-Anforderungen

Python 3.x
Arduino mit unterstützter Firmware
Abhängigkeiten: pyserial, numpy, matplotlib, jupyter

-Nutzung

1.Vorbereitung: Sicherstellen, dass der Arduino mit dem Rechner verbunden ist.
2.Start des Jupyter Notebooks: anmr_com.ipynb öffnen und ausführen.
3.Kompilierung der Befehle: anmr_compiler.py übersetzt die Befehle.
4.Experiment starten: Die Steuerung erfolgt über die im Notebook definierten Befehle.
5.Ergebnisse auswerten: Empfangene Signale werden analysiert und grafisch dargestellt.

-Lizenz
Der ursprüngliche Arduino-Code stammt von Carl A. Michal (2010). Der Python-Code wurde entsprechend angepasst und erweitert.
