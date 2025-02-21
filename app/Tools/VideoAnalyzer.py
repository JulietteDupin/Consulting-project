
import cv2  # Pour traiter les vidéos (lecture des frames)
import torch  # Pour les calculs liés au modèle d'apprentissage automatique
from torchvision import transforms  # Pour les transformations d'images
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime  # Pour gérer les threads, signaux et dates
from PIL import Image  # Pour manipuler les images

class VideoAnalyzer(QThread):
    analysis_complete = pyqtSignal(int)  # Signal pour transmettre le résultat à la fenêtre principale

    def __init__(self, video_path, model, transform, habits):
        super().__init__()
        self.video_path = video_path
        self.model = model
        self.transform = transform
        self.habits = habits
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
        self.eating_counts = {
            "eating_bluetit": 0,
            "eating_chaffinM": 0,
            "eating_greattit": 0,
            "eating_robin": 0
        }

    def run(self):
        eating_count = 0
        cap = cv2.VideoCapture(self.video_path)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Prétraitement de la frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            input_tensor = self.transform(frame_pil).unsqueeze(0)

            # Prédiction
            with torch.no_grad():
                output = self.model(input_tensor)
                _, predicted = torch.max(output, 1)

                # Vérification si l'animal mange
                if predicted.item() < 4:  # Assurez-vous que "0" est l'index de classe "eating"
                    self.eating_counts[self.class_name[predicted.item()]] += 1

        cap.release()

        # Enregistrer les habitudes alimentaires
        today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        hour = QDateTime.currentDateTime().toString("h")
        self.habits.record_eating(today, hour, eating_counts)

        # Émettre le signal lorsque l'analyse est terminée
        self.analysis_complete.emit(eating_counts)

        # Alerte si un changement est détecté
        if self.habits.check_for_change():
            alert_text = "⚠️ Alerte : Changement d'habitude alimentaire détecté !"
            self.frame_processed.emit(frame_qt, alert_text)

