import anmr_compiler as anmr
import anmr_common
import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import os

class PulseModel:
    def __init__(self):
        self.parameters = {
            "Frequenz in Hz": 0,
            "Polarisationszeit in ms": 0,
            "90° RF-Zyklus": 0,
            "Echo Delay in ms": 0,
            "180° RF-Zyklus": 0,
            "Receiver Delay in ms": 0,
            "Datenabtastung (ADC)": 0,
            "Versuchswiederholung Delay in ms": 0,
        }
        self.first_pulse = [0, 0, 0]
        self.second_pulse = [0, 0, 0]
        self.read_data = [0, 0, 0]
        print(f"PulseModel initialized: {id(self)}")  # Debug instance ID

    def update_from_data(self, parameters, first_pulse, second_pulse, read_data):
        print(f"Updating model with parameters: {parameters}")
        print(f"Updating model with first_pulse: {first_pulse}")
        print(f"Updating model with second_pulse: {second_pulse}")
        print(f"Updating model with read_data: {read_data}")
        self.parameters.update(parameters)
        self.first_pulse = first_pulse
        self.second_pulse = second_pulse
        self.read_data = read_data

    def reset(self):
        """Setzt alle Parameterwerte auf 0 zurück."""
        for key in self.parameters.keys():
            self.parameters[key] = 0
        self.first_pulse = [0, 0, 0]
        self.second_pulse = [0, 0, 0]
        self.read_data = [0, 0, 0]
        print("DEBUG: PulseModel wurde zurückgesetzt.")

class PulseFileModel:
    def __init__(self):
        self.file_path = None
        self.file_content = ""

    def is_valid_pulse_file(self, content):
        return content.strip().startswith("PULSE_PROGRAM")

    def load_file(self, filepath):
        """Lädt die Datei und gibt ihren Inhalt zurück."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                self.file_content = file.read()
                self.file_path = filepath
            return self.file_content
        except Exception as e:
            raise IOError(f"Fehler beim Laden der Datei: {str(e)}")

    def parse_content(self, content):
        """Parses the file content and returns parameters, first pulse, second pulse, and read data."""
        parameters = {}
        first_pulse = []
        second_pulse = []
        read_data = []

        for line in content.split("\n"):
            stripped_line = line.strip()
            if "=" in stripped_line and stripped_line.startswith("%"):
                try:
                    key, value = stripped_line.strip("% ").split("=")
                    key, value = key.strip(), value.strip()
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass  # Value remains a string
                    # Zuordnung neuer Parameterbezeichnungen
                    if key == "frequency":
                        parameters["Frequenz in Hz"] = value
                    elif key == "polarization_time":
                        parameters["Polarisationszeit in ms"] = value
                    elif key == "90_half_cycles":
                        parameters["90° RF-Zyklus"] = value
                    elif key == "echo_delay":
                        parameters["Echo Delay in ms"] = value
                    elif key == "180_half_cycles":
                        parameters["180° RF-Zyklus"] = value
                    elif key == "receiver_delay":
                        parameters["Receiver Delay in ms"] = value
                    elif key == "num_points":
                        parameters["Datenabtastung (ADC)"] = value
                    elif key == "repetition_delay":
                        parameters["Versuchswiederholung Delay in ms"] = value
                except Exception as e:
                    print(f"Error parsing parameter '{line}': {e}")

            elif stripped_line.startswith("PULSE 0 90"):
                first_pulse = [int(v) if v.isdigit() else 0 for v in stripped_line.split()[1:4]]
                print(f"DEBUG: Geparste First Pulse: {first_pulse}")
            elif stripped_line.startswith("PULSE 0 180"):
                second_pulse = [int(v) if v.isdigit() else 0 for v in stripped_line.split()[1:4]]
                print(f"DEBUG: Geparste Second Pulse: {second_pulse}")
            elif stripped_line.startswith("READ_DATA"):
                read_data = [int(v) if v.isdigit() else 0 for v in stripped_line.split()[1:4]]
                print(f"DEBUG: Geparste Read Data: {read_data}")

        print(f"Parsed parameters: {parameters}")
        print(f"Parsed first_pulse: {first_pulse}")
        print(f"Parsed second_pulse: {second_pulse}")
        print(f"Parsed read_data: {read_data}")
        return parameters, first_pulse, second_pulse, read_data

class ExperimentModel:
    def __init__(self, view=None):
        self.view = view
        self.serial = serial
        self.anmr = anmr
        self.anmr_common = anmr_common
        self.serial = serial
        self.time = time
        self.np = np
        self.plt = plt
        self.fft = fft
        self.fftfreq = fftfreq
        self.steps = [
            self.step_compile_command_list,
            self.step_setup_serial_connection,
            self.step_check_arduino_readiness,
            self.step_transfer_compiled_program,
            self.step_start_experiment,
            self.step_data_acquisition_and_processing,
            self.step_visualize_results,
        ]
        self.current_step = 0
        self.target_step = self.get_step_index("self.step_data_acquisition_and_processing")

    def get_step_index(self, step_name):
        """Gibt den Index eines Schrittes zurück oder -1, wenn nicht gefunden."""
        print(f"DEBUG: Schritte im Modell: {[step.__name__ for step in self.steps]}")
        for i, step in enumerate(self.steps):
            if step.__name__ == step_name:
                return i
        print(f"DEBUG: Schritt '{step_name}' nicht gefunden!")
        return -1

    def reset(self):
        """Setzt den Zustand des Experimentmodells vollständig zurück."""
        self.current_step = 0
        self.steps = [
            self.step_compile_command_list,
            self.step_setup_serial_connection,
            self.step_check_arduino_readiness,
            self.step_transfer_compiled_program,
            self.step_start_experiment,
            self.step_data_acquisition_and_processing,
            self.step_visualize_results,
        ]
        # Setzt alle Schritte zurück
        self.ardSer = None  # Schließt ggf. serielle Verbindungen
        print(f"DEBUG: Schritte nach Reset: {[step.__name__ for step in self.steps]}")

    def step_compile_command_list(self):
        try:
            print("DEBUG: step_compile_command_list wird ausgeführt.")

            # Setze den Dateinamen fest
            pulse_file_name = "pulse_program.txt"

            # Debug: Prüfen, ob die Datei existiert
            if not os.path.exists(pulse_file_name):
                print(f"ERROR: Datei {pulse_file_name} existiert nicht!")
            else:
                print(f"DEBUG: Datei {pulse_file_name} existiert, starte Compile-Prozess...")

            # Rufe compile nur auf, wenn die Datei wirklich existiert
            if os.path.exists(pulse_file_name):
                self.anmr.compile(pulse_file_name, "output.bin")

            return "step_compile_command_list erfolgreich."

        except Exception as e:
            return f"Fehler in step_compile_command_list: {e}"

    def step_setup_serial_connection(self):
        try:
            self.ardSer = self.serial.Serial('COM3', 1000000)
            self.ardSer.setRTS(True)
            self.ardSer.setDTR(True)
            self.ardSer.bytesize = self.serial.EIGHTBITS
            self.ardSer.parity = self.serial.PARITY_NONE
            self.ardSer.stopbits = self.serial.STOPBITS_ONE
            return "Serielle Verbindung erfolgreich hergestellt."
        except Exception as e:
            return f"Fehler bei der seriellen Verbindung: {e}"

    def step_check_arduino_readiness(self):
        try:
            self.ardSer.reset_input_buffer()
            self.ardSer.write(bytearray([14]))  # 14 is QUERY
            self.time.sleep(1)
            response = self.ardSer.readline()
            if response.strip():
                return f"Antwort vom Arduino: {response.decode().strip()}"
            else:
                return "Keine Antwort vom Arduino."
        except Exception as e:
            return f"Fehler beim Prüfen der Arduino-Bereitschaft: {e}"

    def step_transfer_compiled_program(self):
        try:
            self.anmr_common.downloadProgram('output.bin', self.ardSer)
            return "Programm erfolgreich übertragen."
        except Exception as e:
            return f"Fehler beim Übertragen des Programms: {e}"

    def step_start_experiment(self):
        try:
            self.ardSer.write(bytearray([9]))  # 9 is GO
            response = self.ardSer.readline()
            return f"Experiment gestartet: {response.decode().strip()}"
        except Exception as e:
            return f"Fehler beim Starten des Experiments: {e}"

    def step_data_acquisition_and_processing(self):
        # Exakter Codeblock zur Datenaufnahme und Verarbeitung
        try:
            def read_int_from_serial(bytesize, signed=False):
                """
                Liest eine Ganzzahl von der seriellen Schnittstelle mit der gegebenen Bytegröße.
                """
                bytes_read = self.ardSer.read(bytesize)
                return int.from_bytes(bytes_read, byteorder='little', signed=signed)

            def read_and_process_adc_data():
                """
                Liest und verarbeitet ADC-Daten, die vom Arduino gesendet wurden.
                """
                timeout_duration = 5  # Timeout in Sekunden
                last_data_time = self.time.time()  # Aktuelle Zeit speichern
                program_running = True  # Zustandsvariable für den Betriebsstatus des Programms
                adc_values = []  # Eine Liste für ADC-Werte

                while program_running:
                    if self.ardSer.in_waiting > 0:
                        header = self.ardSer.readline().decode().strip()
                        last_data_time = self.time.time()

                        if header == 'DAT':
                            # Aufruf von read_int_from_serial für die Anzahl der Datenpunkte
                            num_points = read_int_from_serial(4, signed=True)
                            for _ in range(num_points):
                                # Aufruf von read_int_from_serial für ADC-Werte
                                adc_value = read_int_from_serial(2, signed=True)
                                adc_values.append(adc_value)
                                print("ADC-Wert:", adc_value)

                        else:
                            print(f"Erhaltene Nachricht: {header}")

                    elif (self.time.time() - last_data_time) > timeout_duration:
                        print("Timeout: Keine Daten empfangen.")
                        if adc_values:  # Überprüfung, ob Daten vorhanden sind
                            adc_array = self.np.array(adc_values)  # Konvertiere die Liste in ein NumPy-Array
                            self.np.save("adc_data.npy", adc_array)
                            print(f"Daten gespeichert. {len(adc_values)} Werte.")
                        else:
                            print("Keine ADC-Daten zum Speichern.")
                        program_running = False

                    else:
                        print("Warte auf Daten...")
                        self.time.sleep(0.1)

            print("Daten werden aufgenommen und verarbeitet...")

            # Stelle sicher, dass die Funktion wirklich aufgerufen wird
            read_and_process_adc_data()

        except Exception as e:
            return f"Fehler während der Datenaufnahme: {e}"

        finally:
            self.ardSer.close()
            return "Datenaufnahme und Verarbeitung abgeschlossen" "\n" "Serielle Verbindung geschlossen nach ADC-Wertewiedergabe."

    def step_visualize_results(self):
        try:
            data = self.np.load('adc_data.npy')

            # Daten für Diagramm 1
            adc_plot = {
                "x": list(range(len(data))),
                "y": data.tolist(),
                "title": "ADC Data",
                "xlabel": "Measurement No.",
                "ylabel": "ADC Value"
            }

            # Daten für Diagramm 2 (FFT)
            sampling_rate = 9615.0
            N = len(data)
            yf = self.fft(data)
            xf = self.fftfreq(N, 1 / sampling_rate)
            fft_plot = {
                "x": xf[:N // 2].tolist(),
                "y": self.np.abs(yf[:N // 2]).tolist(),
                "title": "Frequency Spectrum",
                "xlabel": "Frequency (Hz)",
                "ylabel": "Amplitude"
            }

            stats = (
                f"Min Value: {self.np.min(data)}\n"
                f"Max Value: {self.np.max(data)}\n"
                f"Mean Value: {self.np.mean(data)}"
            )

            print("Visualisierung abgeschlossen." "\n" + stats)

            return {
                "Visualisierung abgeschlossen." "\n" "stats": stats,
                "plots": [adc_plot, fft_plot]
            }
        except Exception as e:
            return {
                "stats": f"Fehler bei der Visualisierung: {e}",
                "plots": []
            }