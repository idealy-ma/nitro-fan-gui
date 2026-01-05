"""
Configuration et constantes de l'application.
"""


class Config:
    """Constantes de configuration de l'application."""
    # Dimensions de la fenêtre
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 750
    WINDOW_TITLE = "Nitro Fan Control"
    
    # Configuration des températures
    TEMP_UPDATE_INTERVAL_MS = 1000  # Mise à jour toutes les 1 seconde
    TEMP_HISTORY_SIZE = 60  # Nombre de points dans l'historique (60 secondes à 1s/point)
    TEMP_CHART_HEIGHT = 150  # Hauteur des graphiques en pixels
    TEMP_MIN = 0  # Température minimale affichée
    TEMP_MAX = 100  # Température maximale affichée
    
    # Configuration du titre
    TITLE_TEXT = "Acer Nitro Fan Control"
    TITLE_FONT = "Inter"
    TITLE_FONT_SIZE = 14
    
    # Configuration des ventilateurs
    CPU_FAN_ID = 0
    GPU_FAN_ID = 1
    SLIDER_MIN = 30
    SLIDER_MAX = 100
    SLIDER_DEFAULT = 50
    TURBO_SPEED = 100
    
    # Thème sombre
    DARK_THEME = """
    QWidget {
        background-color: #121212;
        color: #ffffff;
    }
    QSlider::groove:horizontal {
        height: 6px;
        background: #2c2c2c;
    }
    QSlider::handle:horizontal {
        background: #ff4d4d;
        width: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }
    QPushButton {
        background-color: #1f1f1f;
        padding: 8px;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #ff4d4d;
    }
    QGroupBox {
        border: 1px solid #2c2c2c;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    """
