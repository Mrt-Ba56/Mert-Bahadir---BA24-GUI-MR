from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QGroupBox, QTextEdit,
    QPushButton, QTabWidget, QScrollArea, QSpinBox, QHBoxLayout, QSplitter, QSizePolicy,
    QAction, QStatusBar, QPlainTextEdit, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from models import PulseModel, PulseFileModel, ExperimentModel
from controller import PulseControlController, ExperimentController
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class TitleScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Hauptlayout
        layout = QVBoxLayout()

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("S04_HTW_Berlin_Logo_pos_FARBIG_RGB.jpg")
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Titel und Name
        title_label = QLabel("Grafische Benutzeroberfläche zur Ansteuerung eines Magnetresonanzexperimentes")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        name_label = QLabel("Mert Bahadir - Matrikelnummer: 583483")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(name_label)

        # Buttons
        explanation_button = QPushButton("Versuchserklärung")
        explanation_button.clicked.connect(self.show_explanation)
        layout.addWidget(explanation_button)

        experiment_button = QPushButton("Versuchsdurchführung")
        experiment_button.clicked.connect(self.show_experiment)
        layout.addWidget(experiment_button)

        self.setLayout(layout)

    def show_explanation(self):
        """Wechselt zur Versuchserklärung."""
        self.stacked_widget.setCurrentIndex(1)  # Index der Versuchserklärung

    def show_experiment(self):
        """Wechselt zur Versuchsdurchführung."""
        self.stacked_widget.setCurrentIndex(2)  # Index der Versuchsdurchführung


class ExplanationDialog(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Hauptlayout
        layout = QVBoxLayout()

        # Splitter für Bild und Text
        splitter = QSplitter(Qt.Vertical)

        # Bild
        image_label = QLabel()
        pixmap = QPixmap("Experiment2.png")
        pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        splitter.addWidget(image_label)

        # Text
        explanation_text = QTextEdit()
        explanation_text.setReadOnly(True)  # Mach das Textfeld nur lesbar
        explanation_text.setHtml("""
            <style>
                p {
                    line-height: 1.8;  /* Zeilenabstand */
                }
            </style>
            <p>
                Zu Beginn des Experiments stellt der Rechner mithilfe eines Python-Programmes (1) eine Verbindung zum Mikrocontroller (2) her, wodurch es zum Steuern des Experiments genutzt werden kann.
                Der Mikrocontroller (2) stellt die zentrale Einheit für die Steuerung und Signalverarbeitung des Experimentes dar. Es dient als Pulsgenerator, Audiofrequenz-Synthesizer und als Digitalisierer der eingehenden Messignale.
            </p>
            <p>
                Nach der Verbindung zwischen Rechner (1) und Mikrocontroller (2), wird die Polarisationsschaltung (3) aktiviert, um die Polarisationsspule (4) mit Energie zu versorgen. Dabei wird ein starkes inhomogenes Magnetfeld erzeugt,
                was zur Folge hat, dass sich die Kernspins der Protonen im Probematerial (5) in eine gewünschte Richtung ausrichten. Das ist notwendig, damit eine messbare Magnetisierung besteht, da die natürliche Ausrichtung der Protonen
                im Erdmagnetfeld einfach zu schwach ist, um eine direkte Signalaufnahme zu ermöglichen. Die Polarisationsspule (4) wird jedoch nur kurz angeschaltet, wodurch die Protonen in das homogene Magnetfeld der Erde zurückkehren.
                Dies führt dazu, dass eine überschüssige Magnetisierung besteht, welche grundlegend für unseren Versuch ist.
            </p>
            <p>
                Anschließend werden durch die Senderplatine (6) die Hochfrequenzpulse (RF-Pulse) erzeugt, indem die Pulssignale des Mikrocontrollers (2) in präzise Sinussignale umgewandelt werden. Die folgenden Sinussignale müssen entsprechend
                den Prinzipien der Resonanzabsorption exakt mit der Larmorfrequenz der Probe übereinstimmen. Zunächst werden die RF-Pulse an den Transmitter/Receiver-Schalter (T/R-Switch) (7) weitergeleitet, wo sie zu der Sender- und
                Empfängerspule (8) übertragen werden, um die Protonen zu beeinflussen.
            </p>
            <p>
                Grundlegend hat der T/R-Switch (7) die Funktion, zwischen Sendemodus und Empfangsmodus zu wechseln. Bei den Protonen handelt es sich um Wasserstoffprotonen, welche als Probematerial (5) sehr gut geeignet sind.
                Denn einerseits ist die Larmorfrequenz gut bekannt und andererseits liefert es starke Signale aufgrund der hohen Protonendichte.
            </p>
            <p>
                Nach der gezielten Anregung der Protonen durch die RF-Pulse, kehren sie in ihren Gleichgewichtszustand entlang des Erdmagnetfeldes zurück. Das während der Relaxation gesonderte magnetische Resonanzsignal (FID-Signal)
                wird durch die Empfangsspule (8) aufgenommen und über den T/R-Switch (7) an die Empfängerplatine (9) gereicht. Hier wird das Signal verstärkt, von Störkomponenten befreit und zur Digitalisierung zurück an den Mikrocontroller (2)
                weitergeleitet. Aufgrund der schwachen Signale ist die Verstärkung durch die Empfängerplatine (9) entscheidend, um das schwache Signal in eine nutzbare Form umzuwandeln.
            </p>
        """)
        splitter.addWidget(explanation_text)

        splitter.setStretchFactor(0, 1)  # Bild weniger Stretch
        splitter.setStretchFactor(1, 3)  # Text mehr Stretch

        layout.addWidget(splitter)

        # Zurück-Button
        back_button = QPushButton("Zurück zum Titelbildschirm")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)  # Zurück zum Titelbildschirm

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.text_editor = QPlainTextEdit()
        self.setWindowTitle("Signalsteuerung und Datenvisualisierung")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)

        # Debug: Start der Initialisierung
        print("DEBUG: Initialisiere MainWindow...")

        # Initialisierung von Modellen
        self.pulse_model = PulseModel()
        self.pulse_file_model = PulseFileModel()
        self.experiment_model = ExperimentModel()

        # Debug: Modelle initialisiert
        print(f"DEBUG: PulseModel: {id(self.pulse_model)}")
        print(f"DEBUG: PulseFileModel: {id(self.pulse_file_model)}")
        print(f"DEBUG: ExperimentModel: {id(self.experiment_model)}")

        # Tab-Widget für Parameter und Experiment
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tabs hinzufügen
        self.param_tab = QWidget()
        self.param_tab_layout = QVBoxLayout()
        self.param_tab.setLayout(self.param_tab_layout)
        # Standardansicht (Parameter-Tab)
        self.tab_widget.addTab(self.param_tab, "Parameter")

        # ScrollArea für Parameterliste
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        param_widget = QWidget()
        param_layout = QVBoxLayout(param_widget)

        # ScrollArea konfigurieren
        self.scroll_area.setWidget(param_widget)

        # Füge ScrollArea zum Layout hinzu
        self.param_tab_layout.addWidget(self.scroll_area)

        # Debug: ScrollArea und Parameterlayout erstellt
        print(f"DEBUG: ScrollArea: {id(self.scroll_area)}")
        print(f"DEBUG: Parameterlayout: {id(param_layout)}")

        # Initialisiere PulseControlController
        self.pulse_control_controller = PulseControlController(self.pulse_model, self.pulse_file_model, self)

        # Debug: PulseControlController initialisiert
        print(f"DEBUG: PulseControlController: {id(self.pulse_control_controller)}")

        # Initialisiere PulseControl und füge es zur Parameterliste hinzu
        self.pulse_control_view = PulseControl(self.pulse_control_controller)
        param_layout.addWidget(self.pulse_control_view)

        # Debug: Überprüfe Parent-Hierarchie
        print(f"DEBUG: Parent von pulse_control_view: {self.pulse_control_view.parent()}")
        print(f"DEBUG: Typ des Parents: {type(self.pulse_control_view.parent())}")

        # Initialisiere GUI-Eingabefelder mit Model-Werten
        self.pulse_control_controller.load_parameters_to_view(
            inputs=self.pulse_control_view.inputs,
            first_pulse_inputs=self.pulse_control_view.first_pulse_inputs,
            second_pulse_inputs=self.pulse_control_view.second_pulse_inputs,
            read_data_inputs=self.pulse_control_view.read_data_inputs
        )

        # Debug: PulseControl erstellt und hinzugefügt
        print(f"DEBUG: PulseControl View: {id(self.pulse_control_view)}")

        # Debug: Texteditor initialisiert
        print(f"DEBUG: Texteditor-Instanz: {self.text_editor}, Typ: {type(self.text_editor)}")

        # Texteditor direkt unterhalb der Parameterliste
        self.text_editor = QTextEdit()
        self.text_editor.clear()  # Editor sicher leer halten
        self.text_editor.setReadOnly(True)
        self.text_editor.setMinimumHeight(200)
        self.param_tab_layout.addWidget(self.text_editor)

        # Debug: TextEditor erstellt
        print(f"DEBUG: TextEditor: {id(self.text_editor)}")

        # Setze das Layout für den Parameter-Tab
        self.param_tab.setLayout(self.param_tab_layout)

        # Debug: Parameter-Tab Layout gesetzt
        print(f"DEBUG: Parameter-Tab Layout: {id(self.param_tab_layout)}")

        # ExperimentExecutionView hinzufügen
        self.experiment_controller = ExperimentController(
            model=self.experiment_model,
            view=None  # View wird später gesetzt
        )

        self.experiment_execution_view = ExperimentExecutionView(
            controller=self.experiment_controller,
            tab_widget=self.tab_widget,
            main_window=self

        )
        self.experiment_controller.view = self.experiment_execution_view  # View wird nachträglich verbunden

        # Debug: ExperimentExecutionView und Controller verbunden
        print(f"DEBUG: ExperimentExecutionView: {id(self.experiment_execution_view)}")
        print(f"DEBUG: ExperimentController: {id(self.experiment_controller)}")

        # Menü einrichten
        self.setup_menu()

        # Statusbar für Statuslabel
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Bereit...")  # Initiale Statusmeldung

        # Debug: MainWindow Initialisierung abgeschlossen
        print("DEBUG: MainWindow erfolgreich initialisiert.")

    def update_status(self, message):
        """Zeigt eine Statusmeldung in der Statusleiste an."""
        self.status_bar.showMessage(message)

    def setup_menu(self):
        """Initialisiert das Hauptmenü."""
        if not self.controller:
            print("WARNING: Controller wurde nicht zugewiesen. Menü wird nicht vollständig eingerichtet.")
            return

        menu_bar = self.menuBar()

        # Datei-Menü
        file_menu = menu_bar.addMenu("Datei")

        open_action = QAction("Pulse-Datei öffnen", self)
        open_action.triggered.connect(self.controller.load_pulse_file)
        file_menu.addAction(open_action)

        # Experiment-Menü
        self.experiment_menu = menu_bar.addMenu("Experiment")
        self.start_action = QAction("Start", self)
        self.start_action.triggered.connect(self.start_experiment)
        self.leave_action = QAction("Verlassen", self)
        self.leave_action.triggered.connect(self.leave_experiment)

        # Standardmäßig "Start" hinzufügen
        self.experiment_menu.addAction(self.start_action)

        # Beenden-Menü
        quit_menu = menu_bar.addMenu("Beenden")

        quit_action = QAction("Beenden", self)
        quit_action.triggered.connect(self.close_application)
        quit_menu.addAction(quit_action)

    def start_experiment(self):
        """Startet das Experiment nur, wenn eine Pulse-Datei existiert."""
        if not self.controller.pulse_file_created:
            QMessageBox.warning(self, "Fehler",
                                "Bitte zuerst die Parameter speichern, bevor das Experiment gestartet wird!")
            return

        # Entferne den Parameter-Tab
        param_tab_index = self.tab_widget.indexOf(self.param_tab)
        if param_tab_index != -1:
            self.tab_widget.removeTab(param_tab_index)

        # Entferne vorhandene Tabs für Versuchsschritte und Messdiagramme, falls sie existieren
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) in ["Versuchsschritte", "Messdiagramme"]:
                self.tab_widget.removeTab(i)

        # Textfelder und Diagramme leeren
        if hasattr(self, "experiment_execution_view"):
            self.experiment_execution_view.output_area.clear()
        if hasattr(self, "figure") and self.figure:
            self.figure.clear()
            self.canvas.draw()

        # Fügt den Tab für Versuchsschritte hinzu
        self.tab_widget.addTab(self.experiment_execution_view, "Versuchsschritte")
        # Erstellt und fügt den Messdiagramme-Tab hinzu
        self.diagrams_tab = QWidget()
        self.diagrams_layout = QVBoxLayout()
        self.diagrams_tab.setLayout(self.diagrams_layout)

        # Fügt das Matplotlib-Canvas hinzu
        self.figure = Figure(figsize=(6, 4))  # Kleinere Diagrammgröße
        self.canvas = FigureCanvas(self.figure)
        self.diagrams_layout.addWidget(self.canvas)
        # Fügt den Messdiagramme-Tab hinzu
        self.tab_widget.addTab(self.diagrams_tab, "Messdiagramme")

        # Setzt den aktuellen Tab auf Versuchsschritte
        self.tab_widget.setCurrentWidget(self.experiment_execution_view)

        # Menü aktualisieren
        self.experiment_menu.clear()
        self.experiment_menu.addAction(self.leave_action)

        # Startet die ersten Schritte des Experiments
        print(f"DEBUG: Experiment startet von Schritt {self.experiment_model.current_step}")
        # **Direkter Aufruf der Methode**
        self.experiment_controller.run_until_start_experiment()

    def update_diagrams(self, plots):
        """Zeichnet die Diagramme in den Messdiagramme-Tab."""
        if not hasattr(self, "figure") or not self.figure:
            return  # Falls kein Diagramm vorhanden ist, abbrechen

        self.figure.clear()  # Löscht alte Diagramme
        for i, plot in enumerate(plots, start=1):
            subplot = self.figure.add_subplot(len(plots), 1, i)
            subplot.plot(plot["x"], plot["y"])
            subplot.set_title(plot["title"], fontsize=10)
            subplot.set_xlabel(plot["xlabel"], fontsize=8)
            subplot.set_ylabel(plot["ylabel"], fontsize=8)
            subplot.grid(True)

        self.figure.tight_layout(pad=2.0)  # Verhindert Überlappungen
        self.canvas.draw()

    def leave_experiment(self):
        """Wechselt zurück zum Parameter-Tab und setzt das Experiment zurück."""
        try:
            # Tabs entfernen
            if self.tab_widget.indexOf(self.experiment_execution_view) != -1:
                self.tab_widget.removeTab(self.tab_widget.indexOf(self.experiment_execution_view))

            if hasattr(self, "diagrams_tab") and self.tab_widget.indexOf(self.diagrams_tab) != -1:
                self.tab_widget.removeTab(self.tab_widget.indexOf(self.diagrams_tab))

            # Parameter-Tab hinzufügen, falls nicht vorhanden
            if self.tab_widget.indexOf(self.param_tab) == -1:
                self.tab_widget.addTab(self.param_tab, "Parameter")

            # ExperimentController zurücksetzen
            if hasattr(self.experiment_controller, "reset") and callable(self.experiment_controller.reset):
                self.experiment_controller.reset()

            # Texteditor leeren
            if hasattr(self.text_editor, "clear") and callable(self.text_editor.clear):
                self.text_editor.clear()

            # PulseModel zurücksetzen
            self.pulse_model.reset()

            # **Parameter im Modell zurücksetzen**
            if hasattr(self.pulse_model, "parameters"):
                for key in self.pulse_model.parameters.keys():
                    self.pulse_model.parameters[key] = 0  # Setze alle Werte auf 0
                self.pulse_model.first_pulse = [0, 0, 0]
                self.pulse_model.second_pulse = [0, 0, 0]
                self.pulse_model.read_data = [0, 0, 0]

            print("DEBUG: Model nach Reset:")
            print(self.pulse_model.parameters)
            print(self.pulse_model.first_pulse)
            print(self.pulse_model.second_pulse)
            print(self.pulse_model.read_data)

            # Auch PulseFileModel zurücksetzen
            self.pulse_file_model.file_path = None
            self.pulse_file_model.file_content = ""
            print("DEBUG: PulseFileModel wurde geleert.")

            # **Überprüfung: Wurde eine Datei geladen?**
            if self.pulse_file_model.file_path:  # Nur aktualisieren, wenn eine Datei existiert
                print("DEBUG: Es existiert eine geladene Datei – lade Werte in die GUI.")
                self.pulse_control_controller.load_parameters_to_view(
                    inputs=self.pulse_control_view.inputs,
                    first_pulse_inputs=self.pulse_control_view.first_pulse_inputs,
                    second_pulse_inputs=self.pulse_control_view.second_pulse_inputs,
                    read_data_inputs=self.pulse_control_view.read_data_inputs
                )
            else:
                print("DEBUG: Keine Datei geladen – GUI bleibt leer.")

            # Menü zurücksetzen
            self.experiment_menu.clear()
            self.experiment_menu.addAction(self.start_action)

            # Status aktualisieren
            self.update_status("Zurück zum Parameter-Tab.")

            # Setze Experimentzustand zurück
            self.experiment_controller.reset_model()
            self.text_editor.clear()  # Textfeld leeren
            print("DEBUG: ExperimentModel wurde zurückgesetzt.")

            print("DEBUG: leave_experiment erfolgreich ausgeführt.")
        except Exception as e:
            print(f"ERROR: Fehler in leave_experiment: {e}")

    def update_text_editor(self, content: str):
        """Aktualisiert den Inhalt des Texteditors."""
        if hasattr(self, 'text_editor') and isinstance(self.text_editor, QTextEdit):
            self.text_editor.clear()
            self.text_editor.setPlainText(content)
            print("DEBUG: Texteditor erfolgreich aktualisiert.")
        else:
            print("ERROR: Texteditor ist nicht verfügbar oder ungültig.")

    def close_application(self):
        """Beendet die Anwendung vollständig."""
        print("DEBUG: Anwendung wird beendet...")
        QApplication.quit()  # Beendet das gesamte Programm


class PulseControl(QGroupBox):
    def __init__(self, controller=None, model=None, main_window=None):
        super().__init__("Pulse Steuerung")
        self.controller = controller
        self.model = model
        self.main_window = main_window  # MainWindow speichern

        layout = QVBoxLayout()

        # Parameter-Eingaben erstellen
        parameter_names = [
            "Frequenz in Hz", "Polarisationszeit in ms", "90° RF-Zyklus",
            "Echo Delay in ms", "180° RF-Zyklus", "Receiver Delay in ms",
            "Datenabtastung (ADC)",  "Versuchswiederholung Delay in ms"
        ]
        self.inputs = self._create_inputs(layout, parameter_names, is_group=False)

        # First Pulse, Second Pulse, and Read Data erstellen (jetzt vertikal mit Erklärungen)
        self.first_pulse_inputs = self._create_group_with_explanations(
            layout, "First Pulse:", [
                "Startphase (°)",
                "Phasenschritt (°)",
                "Schritte bis zum Schritt"
            ]
        )

        self.second_pulse_inputs = self._create_group_with_explanations(
            layout, "Second Pulse:", [
                "Startphase (°)",
                "Phasenschritt (°)",
                "Schritte bis zum Schritt"
            ]
        )
        self.read_data_inputs = self._create_group_with_explanations(
            layout, "Read Data:", [
                "Startphase (°)",
                "Phasenschritt (°)",
                "Schritte bis zum Schritt"
            ]
        )

        # Speichern-Button hinzufügen
        self.save_button = QPushButton("Parameter speichern")
        layout.addWidget(self.save_button)

        if self.controller:
            self.save_button.clicked.connect(lambda: self.controller.update_parameters(
                inputs=self.inputs,
                first_pulse_inputs=self.first_pulse_inputs,
                second_pulse_inputs=self.second_pulse_inputs,
                read_data_inputs=self.read_data_inputs,
            ))
            self.save_button.clicked.connect(self.controller.save_parameters_to_new_file)
        else:
            print("Kein Controller gefunden!")

        self.setLayout(layout)

        # Debugging-Ausgabe für inputs
        print(f"DEBUG: PulseControl inputs initialisiert: {self.inputs}")
        print(f"DEBUG: First Pulse inputs: {self.first_pulse_inputs}")
        print(f"DEBUG: Second Pulse inputs: {self.second_pulse_inputs}")
        print(f"DEBUG: Read Data inputs: {self.read_data_inputs}")

    def _create_inputs(self, layout, labels, is_group=False):
        """
        Universelle Methode zur Erstellung von Eingabefeldern mit Labels.

        :param layout: Das Layout, in das die Widgets eingefügt werden.
        :param labels: Eine Liste von Labels (z. B. ["Frequenz", "Polarisationszeit"]) oder ein einzelner Text für Gruppen (z. B. "First Pulse").
        :param is_group: Falls True, werden die Eingabefelder in einer Zeile zurückgegeben (z. B. für Pulse-Daten).
        """
        if is_group:
            inputs = []
            group_layout = QVBoxLayout()  # Vertikales Layout für Label und Eingabefelder
            label = QLabel(labels)
            group_layout.addWidget(label, alignment=Qt.AlignLeft)  # Label links ausrichten

            for _ in range(3):  # Drei Eingabefelder für Gruppen wie "First Pulse"
                input_field = QSpinBox()
                input_field.setRange(0, 100000)
                input_field.setFixedWidth(100)
                group_layout.addWidget(input_field)  # Eingabefelder vertikal angeordnet
                inputs.append(input_field)

            layout.addLayout(group_layout)  # Das gesamte Layout hinzufügen
            return inputs
        else:
            inputs = {}
            for label_text in labels:
                param_layout = QHBoxLayout()
                label = QLabel(f"{label_text}:")
                input_field = QSpinBox()
                input_field.setRange(0, 100000)
                input_field.setFixedWidth(100)
                inputs[label_text] = input_field  # Speichert Eingabefelder mit Label als Key
                param_layout.addWidget(label)
                param_layout.addWidget(input_field)
                layout.addLayout(param_layout)
            return inputs

    def _create_group_with_explanations(self, layout, group_name, explanations):
        """
        Erstellt Eingabefelder mit Beschreibungen und einem Titel.

        :param layout: Das Hauptlayout, in das die Gruppe eingefügt wird.
        :param group_name: Name der Gruppe (z. B. "First Pulse").
        :param explanations: Liste der Beschreibungen für jede Eingabe.
        """
        group_layout = QVBoxLayout()

        # Überschrift der Gruppe in schwarzem Text
        group_title = QLabel(group_name)
        group_title.setStyleSheet("font-weight: bold; color: black;")  # Überschrift hervorheben
        group_layout.addWidget(group_title)

        inputs = []
        for explanation in explanations:
            # Layout für jede Eingabe
            param_layout = QHBoxLayout()

            # Beschreibung der Eingabe
            description = QLabel(explanation)
            description.setAlignment(Qt.AlignLeft)  # Links ausrichten

            # Eingabefeld
            input_field = QSpinBox()
            input_field.setRange(0, 100000)
            input_field.setFixedWidth(100)  # Einheitliche Breite

            # Beide Widgets in das horizontale Layout einfügen
            param_layout.addWidget(description)
            param_layout.addWidget(input_field)

            # Das horizontale Layout zum Gruppen-Layout hinzufügen
            group_layout.addLayout(param_layout)

            # Eingabefeld zur Liste hinzufügen
            inputs.append(input_field)

        # Füge das Gruppenlayout zum Hauptlayout hinzu
        layout.addLayout(group_layout)
        return inputs

class ExperimentExecutionView(QWidget):
    def __init__(self, controller, tab_widget, main_window):
        super().__init__()
        self.controller = controller
        self.tab_widget = tab_widget
        self.main_window = main_window  # Referenz auf MainWindow

        # Hauptlayout
        self.layout = QVBoxLayout(self)

        # Textbereich für Ausgaben
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)

        # Steuerungsbuttons
        self.start_button = QPushButton("Nächster Schritt")
        self.start_button.clicked.connect(self.controller.execute_next_step)

        self.restart_button = QPushButton("Experiment neustarten")
        self.restart_button.clicked.connect(self.controller.restart_experiment)

        # Widgets hinzufügen
        self.layout.addWidget(self.output_area)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.restart_button)

    def update_output(self, message):
        """Aktualisiert den Ausgabe-Bereich der GUI."""
        if isinstance(message, list) or isinstance(message, dict):
            print("DEBUG: Überspringe das Anzeigen von Rohdaten im Textfeld.")
            return
        self.output_area.append(message)
        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())
