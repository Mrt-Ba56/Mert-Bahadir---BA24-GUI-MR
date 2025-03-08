from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTextEdit
from models import PulseModel



class MainController:
    def __init__(self, pulse_file_model, pulse_model, view):
        self.pulse_file_model = pulse_file_model
        self.pulse_model = pulse_model
        self.view = view
        self.pulse_file_created = False  # Neu: Variable, die prüft, ob eine Datei erstellt wurde
        # Beispiel: Debugging
        print(f"DEBUG: PulseFileModel verbunden mit View: {self.view.pulse_file_model}")
        print(f"DEBUG: MainController using PulseModel: {id(self.pulse_model)}")  # Debug instance ID
        print(f"DEBUG: Controller-View Verbindung: {self.view}, Typ: {type(self.view)}")

    def load_pulse_file(self):
        try:
            # Datei auswählen
            filepath, _ = QFileDialog.getOpenFileName(self.view, "Pulse-Datei öffnen", "", "Textdateien (*.txt)")
            if not filepath:
                print("DEBUG: Kein Dateipfad ausgewählt.")
                return

            print(f"DEBUG: Datei ausgewählt: {filepath}")

            # Datei laden
            content = self.pulse_file_model.load_file(filepath)
            print(f"DEBUG: PulseFileModel.file_content:\n{self.pulse_file_model.file_content}")

            # Überprüfen, ob Datei existiert und nicht leer ist
            import os
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                QMessageBox.warning(self.view, "Fehler", "Die ausgewählte Datei ist leer oder existiert nicht.")
                return

            # Dateipfad speichern
            self.pulse_file_model.file_path = filepath
            print(f"DEBUG: PulseFileModel.file_path = {self.pulse_file_model.file_path}")

            # Validierung des Inhalts
            if not self.pulse_file_model.is_valid_pulse_file(content):
                QMessageBox.warning(self.view, "Fehler", "Die Datei enthält keine gültige PULSE_PROGRAM-Deklaration.")
                return

            # Aktualisiere den Texteditor über die View
            self.view.update_text_editor(content)
            self.view.update_status(f"Datei erfolgreich geladen: {filepath}")

            # Parsing und Model-Update
            parameters, first_pulse, second_pulse, read_data = self.pulse_file_model.parse_content(content)
            self.pulse_model.update_from_data(parameters, first_pulse, second_pulse, read_data)

            # Debugging der Parsing-Ergebnisse
            print("DEBUG: Parsed parameters:", parameters)
            print("DEBUG: Parsed first_pulse:", first_pulse)
            print("DEBUG: Parsed second_pulse:", second_pulse)
            print("DEBUG: Parsed read_data:", read_data)

            # View mit den neuen Werten synchronisieren
            if self.view.pulse_control_controller:
                self.view.pulse_control_controller.load_parameters_to_view(
                    inputs=self.view.pulse_control_view.inputs,
                    first_pulse_inputs=self.view.pulse_control_view.first_pulse_inputs,
                    second_pulse_inputs=self.view.pulse_control_view.second_pulse_inputs,
                    read_data_inputs=self.view.pulse_control_view.read_data_inputs
                )
            else:
                print("WARNING: PulseControlController ist nicht korrekt verbunden.")

        except Exception as e:
            import traceback
            print(f"ERROR: Fehler beim Laden der Datei:\n{traceback.format_exc()}")
            QMessageBox.critical(self.view, "Fehler", f"Fehler beim Laden der Datei: {str(e)}")


class PulseControlController:

    def __init__(self, model, pulse_file_model, view):
        self.model = model
        self.pulse_file_model = pulse_file_model
        self.view = view  # View-Objekt wird hier gespeichert
        print(f"DEBUG: PulseControlController using PulseModel: {id(self.model)}")
        print(f"DEBUG: PulseFileModel initialized: {id(self.pulse_file_model)}")
        print(f"DEBUG: PulseControlController initialized with view: {type(self.view)}")

    def save_parameters_to_new_file(self):
        """Speichert die aktualisierten Parameter in einer neuen Datei."""

        if not self.model or not isinstance(self.model, PulseModel):
            QMessageBox.warning(None, "Warnung", "Kein gültiges Modell geladen, um Parameter zu speichern.")
            return

        if not self.pulse_file_model.file_path or not self.pulse_file_model.file_content:
            QMessageBox.warning(None, "Warnung", "Keine ursprüngliche Datei geladen, um eine Kopie zu erstellen.")
            return

        original_content = self.pulse_file_model.file_content.splitlines()
        new_file_path = 'pulse_program.txt'
        self.pulse_file_model.file_path = new_file_path

        # **Datei speichern (ganz wichtig, sonst kann compile() die nicht finden!)**
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(self.pulse_file_model.file_content)

        print(f"DEBUG: Neuer Dateipfad: {new_file_path}")

        # NEU: Markiere, dass eine Datei erstellt wurde
        if hasattr(self.view, "controller"):
            self.view.controller.pulse_file_created = True
            print("DEBUG: pulse_file_created wurde auf True gesetzt.")

        key_mapping = {
            "Frequenz in Hz": "frequency",
            "Polarisationszeit in ms": "polarization_time",
            "90° RF-Zyklus": "90_half_cycles",
            "Echo Delay in ms": "echo_delay",
            "180° RF-Zyklus": "180_half_cycles",
            "Receiver Delay in ms": "receiver_delay",
            "Datenabtastung (ADC)": "num_points",
            "Versuchswiederholung Delay in ms": "repetition_delay",
        }

        try:
            modified_lines = []

            for line in original_content:
                stripped_line = line.strip()
                if stripped_line.startswith("%"):
                    key = stripped_line.split("=")[0].strip("% ")
                    for gui_key, file_key in key_mapping.items():
                        if key == file_key and gui_key in self.model.parameters:
                            value = self.model.parameters[gui_key]
                            modified_lines.append(f"%{file_key} = {value}")
                            break
                    else:
                        modified_lines.append(line)
                elif stripped_line.startswith("PULSE 0 90"):
                    modified_lines.append(f"PULSE {' '.join(map(str, self.model.first_pulse))} %90_half_cycles")
                elif stripped_line.startswith("PULSE 0 180"):
                    modified_lines.append(f"PULSE {' '.join(map(str, self.model.second_pulse))} %180_half_cycles")
                elif stripped_line.startswith("READ_DATA"):
                    modified_lines.append(f"READ_DATA {' '.join(map(str, self.model.read_data))} %num_points")
                else:
                    modified_lines.append(line)

            with open(new_file_path, 'w', encoding='utf-8') as file:
                file.write("\n".join(modified_lines))

            # Aktualisieren der Datei im PulseFileModel
            self.pulse_file_model.file_path = new_file_path
            self.pulse_file_model.file_content = "\n".join(modified_lines)

            # Aktualisierung im Texteditor
            if hasattr(self.view, 'text_editor') and isinstance(self.view.text_editor, QTextEdit):
                self.view.text_editor.clear()
                self.view.text_editor.setPlainText(self.pulse_file_model.file_content)
                print(f"DEBUG: Texteditor erfolgreich mit neuem Inhalt aktualisiert.")
            else:
                print("ERROR: Texteditor ist nicht verfügbar oder ungültig.")
                QMessageBox.critical(None, "Fehler",
                                     "Die Aktualisierung des Texteditors konnte nicht durchgeführt werden.")

            QMessageBox.information(None, "Erfolg", f"Parameter erfolgreich gespeichert in: {new_file_path}")
            print(f"DEBUG: Datei erfolgreich gespeichert: {new_file_path}")

        except Exception as e:
            print(f"ERROR: Fehler beim Speichern der Datei: {str(e)}")
            QMessageBox.critical(None, "Fehler", f"Fehler beim Speichern der Datei: {e}")

    def update_parameters(self, inputs, first_pulse_inputs, second_pulse_inputs, read_data_inputs):
        """Aktualisiert das Modell basierend auf den Eingaben."""
        print("DEBUG: Aktualisiere Modell mit den Werten aus den Eingabefeldern.")

        for key, input_field in inputs.items():
            value = input_field.value()
            print(f"DEBUG: Setze Modell-Parameter {key} = {value}")
            self.model.parameters[key] = value

        first_pulse_values = [inp.value() for inp in first_pulse_inputs]
        print(f"DEBUG: Setze first_pulse = {first_pulse_values}")
        self.model.first_pulse = first_pulse_values

        second_pulse_values = [inp.value() for inp in second_pulse_inputs]
        print(f"DEBUG: Setze second_pulse = {second_pulse_values}")
        self.model.second_pulse = second_pulse_values

        read_data_values = [inp.value() for inp in read_data_inputs]
        print(f"DEBUG: Setze read_data = {read_data_values}")
        self.model.read_data = read_data_values

    def load_parameters_to_view(self, inputs, first_pulse_inputs, second_pulse_inputs, read_data_inputs):
        """Setzt Werte in die GUI oder setzt sie auf 0 und erzwingt ein vollständiges Neuladen."""

        if not self.pulse_file_model.file_path:  # Wenn keine Datei geladen ist
            print("DEBUG: Keine Datei geladen – Setze Werte auf 0.")

            for key, input_field in inputs.items():
                print(f"DEBUG: Vorher {key}: {input_field.value()}")  # Zeigt den alten Wert
                input_field.blockSignals(True)  # Blockiere Qt-Signale, um ungewollte Änderungen zu vermeiden
                input_field.setValue(0)
                input_field.blockSignals(False)
                print(f"DEBUG: Nachher {key}: {input_field.value()}")  # Sollte 0 sein

            for inp in first_pulse_inputs + second_pulse_inputs + read_data_inputs:
                print(f"DEBUG: Vorher Eingabe {inp.value()}")  # Alter Wert
                inp.blockSignals(True)
                inp.setValue(0)
                inp.blockSignals(False)
                print(f"DEBUG: Nachher Eingabe {inp.value()}")  # Sollte 0 sein

            # 🟢 Punkt 3: Erzwingen der GUI-Neuzeichnung
            self.view.repaint()
            self.view.update()

            # 🟢 Punkt 4: GUI kurz deaktivieren und wieder aktivieren (erzwingt Neuladen aller Komponenten)
            self.view.setEnabled(False)
            self.view.setEnabled(True)

            return  # Abbrechen, um alte Werte nicht erneut zu laden

        print("DEBUG: Aktualisiere Eingabefelder mit den Werten aus dem Modell.")

        # Aktualisiere Hauptparameter
        for key, input_field in inputs.items():
            value = self.model.parameters.get(key, 0)
            print(f"DEBUG: Setze Eingabefeld {key} = {value}")
            input_field.setValue(value)

        # Aktualisiere Pulse-Daten
        for i, val in enumerate(self.model.first_pulse):
            if i < len(first_pulse_inputs):
                print(f"DEBUG: Setze First Pulse Eingabefeld {i} = {val}")
                first_pulse_inputs[i].setValue(val)

        for i, val in enumerate(self.model.second_pulse):
            if i < len(second_pulse_inputs):
                print(f"DEBUG: Setze Second Pulse Eingabefeld {i} = {val}")
                second_pulse_inputs[i].setValue(val)

        for i, val in enumerate(self.model.read_data):
            if i < len(read_data_inputs):
                print(f"DEBUG: Setze Read Data Eingabefeld {i} = {val}")
                read_data_inputs[i].setValue(val)

class ExperimentController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def run_until_start_experiment(self):
        """Führt automatisch alle Schritte bis einschließlich step_start_experiment aus."""
        print("DEBUG: run_until_start_experiment wurde aufgerufen.")
        self.model.current_step = 0  # Immer von Schritt 0 starten
        target_step_index = self.model.get_step_index("step_start_experiment")
        if target_step_index == -1:
            self.view.update_output("Fehler: Zielschritt 'step_start_experiment' nicht gefunden!")
            print("DEBUG: Ziel-Schritt nicht gefunden, breche ab.")
            return
        print(f"DEBUG: Ziel-Schritt-Index: {target_step_index}")

        def execute_next_step_with_timer():
            if self.model.current_step <= target_step_index:
                print(f"DEBUG: Aktueller Schritt-Index: {self.model.current_step}")
                self.execute_next_step()
                QTimer.singleShot(2000, execute_next_step_with_timer)# Nächster Schritt nach kurzer Verzögerung
            else:
                print("DEBUG: Alle vorbereitenden Schritte abgeschlossen.")
                self.view.update_output(
                    "Beobachte die PULSE-Abfolge auf dem Oszilloskop" + "\n" + "Warte vor ADC-Wiedergabe")

        execute_next_step_with_timer()  # Starte direkt den ersten Schritt

    def execute_next_step(self):
        """Führt den aktuellen Schritt aus und bewegt sich zum nächsten."""
        if self.model.current_step < len(self.model.steps):
            try:
                step_function = self.model.steps[self.model.current_step]
                self.view.update_output(
                    f"Schritt {self.model.current_step + 1}: {step_function.__name__} wird ausgeführt."
                )
                result = step_function()

                # Zeige Diagramme und relevante Statistiken nur bei Schritt 7
                if self.model.current_step == self.model.get_step_index("step_visualize_results"):
                    if result and "plots" in result:
                        self.view.main_window.update_diagrams(result["plots"])
                    if result and "stats" in result:
                        self.view.update_output(result["stats"])

                # Zeige die Ausgabe nur, wenn sie nicht None ist und nicht Rohdaten enthält
                if result and not isinstance(result, dict):
                    self.view.update_output(f"{step_function.__name__} abgeschlossen: {result}")

                 # DEBUG nur ausgeben, wenn es nicht Schritt 7 ist
                if self.model.current_step != self.model.get_step_index("step_visualize_results"):
                    print(f"DEBUG: Schritt {self.model.current_step + 1} abgeschlossen mit Ergebnis: {result}")

                self.model.current_step += 1
            except Exception as e:
                error_message = f"Fehler bei Schritt {self.model.current_step + 1}: {e}"
                self.view.update_output(error_message)
                print(f"DEBUG: {error_message}")
        else:
            self.view.update_output("Keine weiteren Schritte auszuführen.")

    def restart_experiment(self):
        """
        Setzt das Experiment zurück und startet neu.
        """
        self.view.update_output("Experiment wird zurückgesetzt...")

        # Serielle Verbindung schließen, falls offen
        if self.model.ardSer:
            self.model.ardSer.close()
            self.model.ardSer = None
            self.view.update_output("Serielle Verbindung geschlossen.")

        # Experiment zurücksetzen
        self.model.reset()  # Ruft die Reset-Methode des Models auf
        self.model.current_step = 0
        self.view.update_output("Experiment wurde zurückgesetzt. Starte vorbereitende Schritte...")

        # Automatische Durchführung der ersten Schritte
        self.run_until_start_experiment()

    def step_visualize_results(self):
        """Visualisiert die Ergebnisse und aktualisiert das Diagramm."""
        try:
            result = self.model.step_visualize_results()
            if result and "plots" in result:
                self.view.update_diagrams(result["plots"])  # Aktualisiert die Diagramme in MainWindow
            if result and "stats" in result:
                self.view.update_output(result["stats"])
            return "Visualisierung abgeschlossen."
        except Exception as e:
            return f"Fehler bei der Visualisierung: {e}"

    def reset_model(self):
        """Setzt das Experiment-Modell und den Zustand zurück."""
        self.model.current_step = 0  # Zurücksetzen des Schritts
        print(f"DEBUG: current_step wurde zurückgesetzt: {self.model.current_step}")
        self.model.reset()
        print("DEBUG: ExperimentModel vollständig zurückgesetzt.")