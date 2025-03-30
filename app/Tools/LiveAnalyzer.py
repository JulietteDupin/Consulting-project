import os
import cv2
import torch
from torchvision import transforms
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PIL import Image


class LiveAnalyzer(QMainWindow):
    def __init__(self, model, transform, habits, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyse en Direct")
        self.model = model
        self.transform = transform
        self.habits = habits
        self.cap = None
        self.timer = QTimer(self)
        self.running = False

        # Stocke les alertes ignorées pour chaque oiseau
        self.suppressed_alerts = {}

        # Détection et statistiques
        self.eating_counts = {
            "eating_bluetit": 0,
            "eating_chaffinM": 0,
            "eating_greattit": 0,
            "eating_robin": 0
        }
        self.last_eating_time = {bird: None for bird in self.eating_counts}

        self.class_name = {
            0: 'eating_bluetit',
            1: 'eating_chaffinM',
            2: 'eating_greattit',
            3: 'eating_robin',
            4: 'not_eating_bluetit',
            5: 'not_eating_chaffinM',
            6: 'not_eating_greattit',
            7: 'not_eating_robin',
            8: 'not recognised'
        }

        self.timer.timeout.connect(self.process_frame)

        # Interface utilisateur
        self.label_image = QLabel(self)
        self.label_image.setFixedSize(640, 640)
        self.label = QLabel(self)
        self.alert = QLabel(self)
        self.alert.setStyleSheet("color: red; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.label_image)
        layout.addWidget(self.label)
        layout.addWidget(self.alert)

        start_btn = QPushButton("Start live analysis")
        start_btn.clicked.connect(self.start_analyzer)
        layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop live analysis")
        stop_btn.clicked.connect(self.stop_analyzer)
        layout.addWidget(stop_btn)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_analyzer(self):
        """Démarre l'analyse vidéo."""
        self.cap = cv2.VideoCapture("../consulting project vidéo birds.mp4")
        if not self.cap.isOpened():
            print("Impossible d'accéder à la caméra.")
            return

        self.running = True
        self.timer.start(30)  # Capture une frame toutes les 30 ms

    def process_frame(self):
        """Analyse une frame et déclenche une alerte si nécessaire."""
        ret, frame = self.cap.read()
        if not ret:
            self.stop_analyzer()
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        input_tensor = self.transform(frame_pil).unsqueeze(0)

        with torch.no_grad():
            output = self.model(input_tensor)
            softmax_probs = torch.nn.functional.softmax(output, dim=1)
            confidence, predicted = torch.max(softmax_probs, 1)

        result_text = self.class_name[predicted.item()]
        confidence_value = confidence.item()

        if predicted.item() < 4:  # Oiseau en train de manger
            current_time = QDateTime.currentDateTime()
            last_time = self.last_eating_time[result_text]

            if last_time is None or last_time.msecsTo(current_time) >= 60000:
                self.eating_counts[result_text] += 1
                self.last_eating_time[result_text] = current_time

        today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        self.habits.record_eating(today, QDateTime.currentDateTime().toString("h"), self.eating_counts)

        # Vérification des alertes
        alert, animal = self.habits.check_for_change()
        if alert:
            self.show_alert_popup(f"⚠️ Alerte : {animal} mange moins souvent que d'habitude !", animal)

        # Affichage
        frame_qt = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        self.update_frame_from_camera(frame_qt, f"{result_text} ({confidence_value:.2f})")

    def update_frame_from_camera(self, frame_qt, result_text):
        """Met à jour l'affichage."""
        if frame_qt.isNull():
            return

        pixmap = QPixmap.fromImage(frame_qt).scaled(
            self.label_image.width(), self.label_image.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.label_image.setPixmap(pixmap)
        self.label.setText(result_text)

        self.label.repaint()
        self.label_image.repaint()

    def stop_analyzer(self):
        """Arrête l'analyse vidéo."""
        self.running = False
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.close()

    def show_alert_popup(self, message, bird_type):
        """Affiche une pop-up avec un bouton 'J'ai compris' pour éviter les répétitions pendant 4h."""

        current_time = QDateTime.currentDateTime()

        # Vérifie si une alerte a déjà été ignorée récemment
        if bird_type in self.suppressed_alerts:
            last_suppressed = self.suppressed_alerts[bird_type]
            if last_suppressed.secsTo(current_time) < 14400:  # 14400 sec = 4h
                return  # Ne pas afficher l'alerte

        # Création de la pop-up
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Alerte Alimentaire")
        msg_box.setText(message)

        # Ajout d'un bouton "J'ai compris"
        btn_understood = msg_box.addButton("J'ai compris", QMessageBox.AcceptRole)
        msg_box.addButton(QMessageBox.Ok)  # Bouton par défaut

        msg_box.exec_()

        # Si "J'ai compris" est cliqué, enregistrer l'heure actuelle pour cet oiseau
        if msg_box.clickedButton() == btn_understood:
            self.suppressed_alerts[bird_type] = current_time
