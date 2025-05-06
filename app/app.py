import sys
import os
import cv2
import torch
from torchvision import transforms
from PyQt5.QtCore import QTimer, QDateTime, QSize, QPropertyAnimation, QRect, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QMenu, QAction
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PIL import Image
from Tools.EatingHabits import EatingHabits
from Tools.VideoAnalyzer import VideoAnalyzer
from Tools.HabitsVisualization import HabitsVisualization
from Tools.UnrecognizedImagesManager import UnrecognizedImagesManager
from Tools.LiveAnalyzer import LiveAnalyzer
from pathlib import Path

class AnimalEatingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.menu_open = False

        # Charger le modèle
        self.model = torch.load('./../model_eating_classification.pth', map_location=torch.device('cpu'), weights_only=False)
        self.model.eval()

        # Transformations pour le modèle
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        # Habitudes alimentaires et gestion des images non reconnues
        self.habits = EatingHabits()
        self.unrecognized_images_manager = UnrecognizedImagesManager("C:\\Users\\julie\\Documents\\Birdfeeder images and video clips\\app\\unrecognized_images\\")

    def initUI(self):
        self.setWindowTitle("Animal Eating Detector")
        self.setGeometry(100, 100, 400, 300)

        # Menu
        self.menu_bar = self.menuBar()
        self.create_menu()

        layout = QVBoxLayout()

        self.label = QLabel("Par quoi souhaitez-vous commencer ?", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.alert = QLabel("", self)
        self.alert.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.alert)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Bouton de menu
        logo = QIcon('./datas/pictures/menu.png')
        self.menu_btn = QPushButton(logo, '', self)
        self.menu_btn.setToolTip('Cliquer pour afficher le menu')
        self.menu_btn.clicked.connect(self.toggle_menu)
        self.menu_btn.setGeometry(10, 10, 50, 50)
        self.menu_btn.setIconSize(QSize(50, 50))

    def toggle_menu(self):
        """Afficher ou masquer le menu avec une animation."""
        if not self.menu_open:
            # Position et dimensions de l'ouverture du menu
            self.menu.setGeometry(0, 0, 200, self.height())
            self.menu.show()
        else:
            self.menu.hide()

        self.menu_open = not self.menu_open


    def create_menu(self):
        self.menu = QMenu(self)

        live_analyze_action = QAction("Analyser en direct", self)
        live_analyze_action.triggered.connect(self.start_live_analysis)
        self.menu.addAction(live_analyze_action)

        visualize_habits_action = QAction("Visualiser les habitudes", self)
        visualize_habits_action.triggered.connect(self.visualize_habits_from_video)
        self.menu.addAction(visualize_habits_action)

        manage_unrecognized_images_action = QAction("Images Non Reconnues", self)
        manage_unrecognized_images_action.triggered.connect(self.show_unrecognized_images_page)
        self.menu.addAction(manage_unrecognized_images_action)

    def start_live_analysis(self):
        self.live_analyzer_window = LiveAnalyzer(self.model, self.transform, self.habits, self)
        self.live_analyzer_window.show()

    def visualize_habits_from_video(self):
        self.habits_window = HabitsVisualization()
        self.habits_window.show()

    def show_unrecognized_images_page(self):
        self.unrecognized_images_manager.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('./style/style.qss').read_text())
    main_window = AnimalEatingApp()
    main_window.setWindowIcon(QIcon("./datas/pictures/app logo.png"))
    main_window.show()
    sys.exit(app.exec_())
