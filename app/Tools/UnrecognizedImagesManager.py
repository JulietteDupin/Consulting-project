from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, QComboBox, QFormLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os


class UnrecognizedImagesManager(QMainWindow):
    def __init__(self, image_directory, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Images Non Reconnues")
        self.image_directory = image_directory
        self.image_files = []
        self.current_index = 0

        # Charger les images au démarrage
        self.load_images()

        # Créer un widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Interface principale
        main_layout = QVBoxLayout()

        # Label pour afficher les images
        self.image_label = QLabel("Aucune image à afficher.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)  # Permet de redimensionner l'image
        main_layout.addWidget(self.image_label)

        # Formulaire pour sélectionner les informations sur l'animal
        form_layout = QFormLayout()

        self.type_selector = QComboBox()
        self.type_selector.addItems(["Bluetit", "Chaffinch", "Great Tit", "Robin", "Other"])
        form_layout.addRow("Type d'animal :", self.type_selector)

        self.eating_status_selector = QComboBox()
        self.eating_status_selector.addItems(["Mange", "Ne mange pas"])
        form_layout.addRow("Statut alimentaire :", self.eating_status_selector)

        main_layout.addLayout(form_layout)

        # Boutons pour naviguer entre les images
        navigation_layout = QHBoxLayout()

        self.prev_button = QPushButton("Précédent")
        self.prev_button.clicked.connect(self.show_previous_image)
        navigation_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Suivant")
        self.next_button.clicked.connect(self.show_next_image)
        navigation_layout.addWidget(self.next_button)

        main_layout.addLayout(navigation_layout)

        # Bouton pour enregistrer les annotations
        self.save_button = QPushButton("Enregistrer les informations")
        self.save_button.clicked.connect(self.save_annotation)
        main_layout.addWidget(self.save_button)

        central_widget.setLayout(main_layout)

        # Afficher la première image si disponible
        self.update_image_display()

    def load_images(self):
        """Charge les fichiers d'images depuis le répertoire spécifié."""
        if os.path.exists(self.image_directory):
            self.image_files = [
                os.path.join(self.image_directory, f)
                for f in os.listdir(self.image_directory)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ]
        else:
            self.image_files = []

    def update_image_display(self):
        """Met à jour l'affichage de l'image actuelle."""
        if self.image_files:
            image_path = self.image_files[self.current_index]
            pixmap = QPixmap(image_path).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Aucune image à afficher.")
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Met à jour l'état des boutons de navigation."""
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.image_files) - 1)

    def show_previous_image(self):
        """Affiche l'image précédente."""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image_display()

    def show_next_image(self):
        """Affiche l'image suivante."""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.update_image_display()

    def save_annotation(self):
        """Enregistre l'annotation pour l'image actuelle."""
        if self.image_files:
            image_path = self.image_files[self.current_index]
            animal_type = self.type_selector.currentText()
            eating_status = self.eating_status_selector.currentText()

            annotation = {
                "image_path": image_path,
                "animal_type": animal_type,
                "eating_status": eating_status,
            }

            # Enregistrer les annotations dans un fichier JSON
            annotations_path = os.path.join(self.image_directory, "annotations.json")
            if os.path.exists(annotations_path):
                with open(annotations_path, "r") as file:
                    data = json.load(file)
            else:
                data = []

            data.append(annotation)
            with open(annotations_path, "w") as file:
                json.dump(data, file, indent=4)

            self.image_label.setText("Annotation enregistrée avec succès.")
