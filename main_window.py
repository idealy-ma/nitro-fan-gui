"""
Fenêtre principale de l'application GUI.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import sys

from config import Config
from fan_controller import FanController
from temperature_reader import TemperatureReader
from fan_screen import FanScreen
from keyboard_screen import KeyboardScreen


class MainWindow(QWidget):
    """Fenêtre principale de l'application."""
    
    def __init__(self):
        """Initialise la fenêtre principale."""
        super().__init__()
        self._fan_controller = FanController()
        self._temperature_reader = TemperatureReader()
        
        # Vérifier les appareils recommandés avant de continuer
        recommended = self._fan_controller.get_recommended_devices()
        if not recommended:
            self._show_no_device_error()
            return
        
        self._init_ui()
        self._apply_theme()
    
    def _show_no_device_error(self) -> None:
        """Affiche un message d'erreur et quitte l'application."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Erreur - Aucun appareil recommandé")
        msg.setText("Aucun appareil nbfc recommandé trouvé pour ce système.")
        msg.setInformativeText(
            "L'application ne peut pas fonctionner sans un appareil compatible.\n\n"
            "Veuillez vérifier que nbfc est correctement installé et configuré."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        sys.exit(1)
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur."""
        self.setWindowTitle(Config.WINDOW_TITLE)
        self.setFixedSize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Layout horizontal principal
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Zone de contenu principal (à gauche)
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Titre principal
        title = self._create_title()
        content_layout.addWidget(title)
        
        # StackedWidget pour gérer les écrans
        self._stacked_widget = QStackedWidget()
        
        # Créer les écrans
        self._fan_screen = FanScreen(self._fan_controller, self._temperature_reader)
        self._keyboard_screen = KeyboardScreen()
        
        # Ajouter les écrans au stacked widget
        self._stacked_widget.addWidget(self._fan_screen)
        self._stacked_widget.addWidget(self._keyboard_screen)
        
        content_layout.addWidget(self._stacked_widget)
        content_widget.setLayout(content_layout)
        
        # Menu latéral (à droite)
        menu_widget = self._create_side_menu()
        
        # Ajouter au layout principal
        main_layout.addWidget(menu_widget, stretch=0)
        main_layout.addWidget(content_widget, stretch=1)
        
        self.setLayout(main_layout)
    
    def _create_title(self) -> QLabel:
        """Crée le label de titre."""
        title = QLabel(Config.TITLE_TEXT)
        title.setFont(QFont(Config.TITLE_FONT, Config.TITLE_FONT_SIZE, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        return title
    
    def _create_side_menu(self) -> QWidget:
        """Crée le menu latéral."""
        menu_widget = QWidget()
        menu_widget.setFixedWidth(Config.MENU_WIDTH)
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(10, 10, 10, 10)
        menu_layout.setSpacing(5)
        
        # Titre du menu
        menu_title = QLabel("Menu")
        menu_title.setFont(QFont(Config.TITLE_FONT, 12, QFont.Bold))
        menu_title.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(menu_title)
        
        # Liste des options
        self._menu_list = QListWidget()
        self._menu_list.addItem("Ventilateurs")
        self._menu_list.addItem("Clavier RGB")
        self._menu_list.setCurrentRow(0)  # Sélectionner le premier par défaut
        self._menu_list.currentRowChanged.connect(self._on_menu_item_changed)
        menu_layout.addWidget(self._menu_list)
        
        menu_layout.addStretch()
        menu_widget.setLayout(menu_layout)
        
        return menu_widget
    
    def _on_menu_item_changed(self, index: int) -> None:
        """Gère le changement d'élément du menu."""
        self._stacked_widget.setCurrentIndex(index)
    
    def _apply_theme(self) -> None:
        """Applique le thème sombre à la fenêtre."""
        self.setStyleSheet(Config.DARK_THEME)
