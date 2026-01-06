"""
Configuration et constantes de l'application.
"""


class Config:
    """Constantes de configuration de l'application."""
    # Dimensions de la fenêtre
    WINDOW_WIDTH = 800
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
    
    # Configuration du clavier RGB
    RGB_MODE_STATIC = 0
    RGB_MODE_BREATH = 1
    RGB_MODE_NEON = 2
    RGB_MODE_WAVE = 3
    RGB_MODE_SHIFTING = 4
    RGB_MODE_ZOOM = 5
    
    RGB_SPEED_MIN = 0
    RGB_SPEED_MAX = 9
    RGB_SPEED_DEFAULT = 4
    
    RGB_BRIGHTNESS_MIN = 0
    RGB_BRIGHTNESS_MAX = 100
    RGB_BRIGHTNESS_DEFAULT = 100
    
    RGB_COLOR_MIN = 0
    RGB_COLOR_MAX = 255
    
    RGB_ZONE_MIN = 1
    RGB_ZONE_MAX = 4
    
    RGB_DIRECTION_RTL = 1  # Right to Left
    RGB_DIRECTION_LTR = 2  # Left to Right
    
    # Menu latéral
    MENU_WIDTH = 150
    
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
    QListWidget {
        background-color: #1a1a1a;
        border: none;
        outline: none;
    }
    QListWidget::item {
        padding: 12px;
        border-radius: 4px;
        margin: 2px;
    }
    QListWidget::item:selected {
        background-color: #ff4d4d;
    }
    QListWidget::item:hover {
        background-color: #2a2a2a;
    }
    QComboBox {
        background-color: #1f1f1f;
        border: 1px solid #2c2c2c;
        border-radius: 4px;
        padding: 4px;
    }
    QComboBox:hover {
        border: 1px solid #ff4d4d;
    }
    QSpinBox {
        background-color: #1f1f1f;
        border: 1px solid #2c2c2c;
        border-radius: 4px;
        padding: 4px;
    }
    QSpinBox:hover {
        border: 1px solid #ff4d4d;
    }
    """
