import os
import cv2
import torch
from torchvision import transforms
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

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

        # Classes et compteurs
        self.eating_counts = {
            "eating_bluetit": 0,
            "eating_chaffinM": 0,
            "eating_greattit": 0,
            "eating_robin": 0
        }

        # Dernière détection pour éviter les doublons en moins d'une minute
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

        # Configurer le timer pour capturer des frames à intervalles réguliers
        self.timer.timeout.connect(self.process_frame)

        # Interface utilisateur
        self.label_image = QLabel(self)
        self.label_image.setText("Aucune image")
        self.label_image.setFixedSize(640, 480)

        self.label = QLabel(self)
        self.label.setText("Aucun résultat")

        self.alert = QLabel(self)
        self.alert.setText("")
        self.alert.setStyleSheet("color: red; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.label_image)
        layout.addWidget(self.label)
        layout.addWidget(self.alert)

        refresh_btn = QPushButton("Start live analysis")
        refresh_btn.clicked.connect(self.start_analyzer)
        layout.addWidget(refresh_btn)
        
        refresh_btn = QPushButton("Stop live analysis")
        refresh_btn.clicked.connect(self.stop_analyzer)
        layout.addWidget(refresh_btn)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_analyzer(self):
        """Démarre l'analyse en direct."""
        self.cap = cv2.VideoCapture(0)  # Webcam par défaut
        if not self.cap.isOpened():
            print("Impossible d'accéder à la caméra.")
            return

        self.running = True
        self.timer.start(30)  # Capture une frame toutes les 30 ms

    def process_frame(self, output_dir="C:\\Users\\julie\\Documents\\Birdfeeder images and video clips\\app\\unrecognized_images\\"):
        """Traite une frame de la caméra."""
        ret, frame = self.cap.read()
        if not ret:
            print("Aucun flux de la caméra.")
            self.stop_analyzer()
            return

        # Prétraitement
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        input_tensor = self.transform(frame_pil).unsqueeze(0)

        # Prédiction
        with torch.no_grad():
            output = self.model(input_tensor)
            softmax_probs = torch.nn.functional.softmax(output, dim=1)
            confidence, predicted = torch.max(softmax_probs, 1)

        # Sauvegarde si non reconnu
        if predicted == torch.tensor([8]):
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd_hh-mm-ss")
            image_name = f"unrecognized_{timestamp}.jpg"
            image_path = os.path.join(output_dir, image_name)
            cv2.imwrite(image_path, frame)

        # Mise à jour des statistiques
        result_text = self.class_name[predicted.item()]
        confidence_value = confidence.item()

        if predicted.item() < 4:  # Seulement si l'oiseau est en train de manger
            current_time = QDateTime.currentDateTime()

            # Vérifier si au moins une minute s'est écoulée depuis le dernier repas enregistré
            last_time = self.last_eating_time[result_text]
            if last_time is None or last_time.msecsTo(current_time) >= 60000:  # 60000 ms = 1 min
                self.eating_counts[result_text] += 1
                self.last_eating_time[result_text] = current_time  # Mettre à jour l'heure du dernier repas

        today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        self.habits.record_eating(today, QDateTime.currentDateTime().toString("h"), self.eating_counts)

        # Alertes
        alert_text = ""
        if self.habits.check_for_change():
            self.show_alert_popup("⚠️ Alerte : L'animal mange moins souvent que d'habitude !")

        # Convertir la frame pour l'affichage
        frame_qt = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)

        # Mettre à jour l'interface
        self.update_frame_from_camera(frame_qt, f"{result_text} ({confidence_value:.2f})", alert_text)

    def update_frame_from_camera(self, frame_qt, result_text, alert_text=""):
        """Met à jour l'affichage avec la frame et le texte."""
        if frame_qt.isNull():
            print("Erreur : Le QImage est vide.")
            return

        pixmap = QPixmap.fromImage(frame_qt)
        if pixmap.isNull():
            print("Erreur : La conversion QImage -> QPixmap a échoué.")
            return

        self.label_image.setPixmap(pixmap)
        self.label.setText(result_text)
        self.alert.setText(alert_text)

        self.label.repaint()
        self.label_image.repaint()
        self.alert.repaint()

    def stop_analyzer(self):
        """Arrête l'analyse en direct."""
        self.running = False
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.close()

    def show_alert_popup(self, message):
        """Affiche une pop-up d'alerte non bloquante (une seule à la fois)."""

        # Vérifie si une pop-up est déjà affichée
        if hasattr(self, "alert_shown") and self.alert_shown:
            return

        self.alert_shown = True  # Empêche l'affichage d'une autre pop-up

        # Création de la pop-up
        self.msg_box = QMessageBox()
        self.msg_box.setIcon(QMessageBox.Warning)
        self.msg_box.setWindowTitle("Alerte Alimentaire")
        self.msg_box.setText(message)
        self.msg_box.setStandardButtons(QMessageBox.Ok)

        # Quand l'utilisateur ferme la pop-up, réinitialiser `alert_shown`
        self.msg_box.finished.connect(lambda: setattr(self, "alert_shown", False))

        self.msg_box.show()  # Affiche la pop-up