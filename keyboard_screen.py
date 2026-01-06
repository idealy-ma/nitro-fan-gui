"""
Écran de contrôle du clavier RGB.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider, QPushButton,
    QHBoxLayout, QGroupBox, QComboBox, QSpinBox, QMessageBox, QInputDialog, QColorDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

from config import Config
from keyboard_controller import KeyboardController


class KeyboardScreen(QWidget):
    """Écran de contrôle du clavier RGB."""
    
    def __init__(self):
        """Initialise l'écran du clavier."""
        super().__init__()
        self._keyboard_controller = KeyboardController()
        self._init_ui()
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Vérifie si le module kernel est disponible."""
        if not self._keyboard_controller.is_available():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Module non disponible")
            msg.setText("Le module kernel acer-gkbbl n'est pas disponible.")
            msg.setInformativeText(
                "Assurez-vous que le module kernel est installé et chargé.\n\n"
                "Les devices /dev/acer-gkbbl-0 et /dev/acer-gkbbl-static-0 doivent exister."
            )
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Titre
        title = QLabel("Contrôle du Clavier RGB")
        title.setFont(QFont(Config.TITLE_FONT, Config.TITLE_FONT_SIZE, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Section mode
        mode_section = self._create_mode_section()
        layout.addWidget(mode_section)
        
        # Section paramètres statiques (4 zones)
        self._static_params_section = self._create_static_params_section()
        layout.addWidget(self._static_params_section)
        self._static_params_section.setVisible(False)
        
        # Section paramètres dynamiques
        self._dynamic_params_section = self._create_dynamic_params_section()
        layout.addWidget(self._dynamic_params_section)
        
        # Section couleur dynamique
        self._dynamic_color_section = self._create_dynamic_color_section()
        layout.addWidget(self._dynamic_color_section)
        
        # Boutons d'action
        action_section = self._create_action_section()
        layout.addWidget(action_section)
        
        # Section profils
        profile_section = self._create_profile_section()
        layout.addWidget(profile_section)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_mode_section(self) -> QGroupBox:
        """Crée la section de sélection du mode."""
        group = QGroupBox("Mode RGB")
        layout = QVBoxLayout()
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("Static", Config.RGB_MODE_STATIC)
        self._mode_combo.addItem("Breath", Config.RGB_MODE_BREATH)
        self._mode_combo.addItem("Neon", Config.RGB_MODE_NEON)
        self._mode_combo.addItem("Wave", Config.RGB_MODE_WAVE)
        self._mode_combo.addItem("Shifting", Config.RGB_MODE_SHIFTING)
        self._mode_combo.addItem("Zoom", Config.RGB_MODE_ZOOM)
        
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        layout.addWidget(self._mode_combo)
        
        group.setLayout(layout)
        return group
    
    def _on_mode_changed(self, index: int) -> None:
        """Gère le changement de mode."""
        mode = self._mode_combo.currentData()
        is_static = (mode == Config.RGB_MODE_STATIC)
        self._static_params_section.setVisible(is_static)
        self._dynamic_params_section.setVisible(not is_static)
        self._dynamic_color_section.setVisible(not is_static)
    
    def _create_static_params_section(self) -> QGroupBox:
        """Crée la section des paramètres statiques avec 4 zones."""
        group = QGroupBox("Zones du Clavier (Mode Statique)")
        layout = QVBoxLayout()
        
        # Luminosité globale pour le mode statique
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Luminosité globale:")
        brightness_layout.addWidget(brightness_label)
        self._static_brightness_slider = QSlider(Qt.Horizontal)
        self._static_brightness_slider.setRange(Config.RGB_BRIGHTNESS_MIN, Config.RGB_BRIGHTNESS_MAX)
        self._static_brightness_slider.setValue(Config.RGB_BRIGHTNESS_DEFAULT)
        self._static_brightness_value_label = QLabel(f"{Config.RGB_BRIGHTNESS_DEFAULT}%")
        self._static_brightness_value_label.setMinimumWidth(40)
        self._static_brightness_slider.valueChanged.connect(
            lambda v: self._static_brightness_value_label.setText(f"{v}%")
        )
        brightness_layout.addWidget(self._static_brightness_slider)
        brightness_layout.addWidget(self._static_brightness_value_label)
        layout.addLayout(brightness_layout)
        
        # Stocker les contrôles de couleur pour chaque zone
        self._zone_colors = []
        
        # Zone 1
        zone1_layout = self._create_zone_color_controls(1, "Zone 1 (Gauche)")
        layout.addLayout(zone1_layout)
        
        # Zone 2
        zone2_layout = self._create_zone_color_controls(2, "Zone 2")
        layout.addLayout(zone2_layout)
        
        # Zone 3
        zone3_layout = self._create_zone_color_controls(3, "Zone 3")
        layout.addLayout(zone3_layout)
        
        # Zone 4
        zone4_layout = self._create_zone_color_controls(4, "Zone 4 (Droite)")
        layout.addLayout(zone4_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_zone_color_controls(self, zone_num: int, zone_label_text: str) -> QHBoxLayout:
        """Crée les contrôles de couleur pour une zone."""
        layout = QHBoxLayout()
        
        # Label de la zone
        zone_label = QLabel(zone_label_text)
        zone_label.setMinimumWidth(100)
        layout.addWidget(zone_label)
        
        # Aperçu de couleur
        color_preview = QLabel()
        color_preview.setMinimumSize(40, 30)
        color_preview.setMaximumSize(40, 30)
        color_preview.setStyleSheet("background-color: rgb(50, 255, 50); border: 1px solid #2c2c2c; border-radius: 4px;")
        color_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(color_preview)
        
        # Bouton color picker
        color_picker_btn = QPushButton("🎨")
        color_picker_btn.setToolTip("Ouvrir le sélecteur de couleur")
        color_picker_btn.setMinimumWidth(35)
        color_picker_btn.setMaximumWidth(35)
        layout.addWidget(color_picker_btn)
        
        # Rouge
        red_label = QLabel("R:")
        red_label.setMinimumWidth(20)
        layout.addWidget(red_label)
        red_spinbox = QSpinBox()
        red_spinbox.setRange(Config.RGB_COLOR_MIN, Config.RGB_COLOR_MAX)
        red_spinbox.setValue(50)
        red_spinbox.setMinimumWidth(60)
        layout.addWidget(red_spinbox)
        
        # Vert
        green_label = QLabel("V:")
        green_label.setMinimumWidth(20)
        layout.addWidget(green_label)
        green_spinbox = QSpinBox()
        green_spinbox.setRange(Config.RGB_COLOR_MIN, Config.RGB_COLOR_MAX)
        green_spinbox.setValue(255)
        green_spinbox.setMinimumWidth(60)
        layout.addWidget(green_spinbox)
        
        # Bleu
        blue_label = QLabel("B:")
        blue_label.setMinimumWidth(20)
        layout.addWidget(blue_label)
        blue_spinbox = QSpinBox()
        blue_spinbox.setRange(Config.RGB_COLOR_MIN, Config.RGB_COLOR_MAX)
        blue_spinbox.setValue(50)
        blue_spinbox.setMinimumWidth(60)
        layout.addWidget(blue_spinbox)
        
        # Fonction pour mettre à jour l'aperçu
        def update_preview():
            r = red_spinbox.value()
            g = green_spinbox.value()
            b = blue_spinbox.value()
            color_preview.setStyleSheet(
                f"background-color: rgb({r}, {g}, {b}); "
                f"border: 1px solid #2c2c2c; border-radius: 4px;"
            )
        
        # Connecter les spinboxes pour mettre à jour l'aperçu
        red_spinbox.valueChanged.connect(update_preview)
        green_spinbox.valueChanged.connect(update_preview)
        blue_spinbox.valueChanged.connect(update_preview)
        
        # Connecter le color picker
        def open_color_picker():
            current_color = QColor(
                red_spinbox.value(),
                green_spinbox.value(),
                blue_spinbox.value()
            )
            color = QColorDialog.getColor(current_color, self, f"Sélectionner la couleur - {zone_label_text}")
            if color.isValid():
                red_spinbox.setValue(color.red())
                green_spinbox.setValue(color.green())
                blue_spinbox.setValue(color.blue())
                update_preview()
        
        color_picker_btn.clicked.connect(open_color_picker)
        
        # Mise à jour initiale de l'aperçu
        update_preview()
        
        # Stocker les références
        zone_data = {
            'zone': zone_num,
            'red': red_spinbox,
            'green': green_spinbox,
            'blue': blue_spinbox,
            'preview': color_preview,
            'update_preview': update_preview
        }
        self._zone_colors.append(zone_data)
        
        layout.addStretch()
        return layout
    
    def _create_dynamic_params_section(self) -> QGroupBox:
        """Crée la section des paramètres dynamiques."""
        group = QGroupBox("Paramètres (Modes Dynamiques)")
        layout = QVBoxLayout()
        
        # Vitesse
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Vitesse:")
        speed_layout.addWidget(speed_label)
        self._speed_slider = QSlider(Qt.Horizontal)
        self._speed_slider.setRange(Config.RGB_SPEED_MIN, Config.RGB_SPEED_MAX)
        self._speed_slider.setValue(Config.RGB_SPEED_DEFAULT)
        self._speed_value_label = QLabel(str(Config.RGB_SPEED_DEFAULT))
        self._speed_value_label.setMinimumWidth(30)
        self._speed_slider.valueChanged.connect(
            lambda v: self._speed_value_label.setText(str(v))
        )
        speed_layout.addWidget(self._speed_slider)
        speed_layout.addWidget(self._speed_value_label)
        layout.addLayout(speed_layout)
        
        # Luminosité
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Luminosité:")
        brightness_layout.addWidget(brightness_label)
        self._brightness_slider = QSlider(Qt.Horizontal)
        self._brightness_slider.setRange(Config.RGB_BRIGHTNESS_MIN, Config.RGB_BRIGHTNESS_MAX)
        self._brightness_slider.setValue(Config.RGB_BRIGHTNESS_DEFAULT)
        self._brightness_value_label = QLabel(f"{Config.RGB_BRIGHTNESS_DEFAULT}%")
        self._brightness_value_label.setMinimumWidth(40)
        self._brightness_slider.valueChanged.connect(
            lambda v: self._brightness_value_label.setText(f"{v}%")
        )
        brightness_layout.addWidget(self._brightness_slider)
        brightness_layout.addWidget(self._brightness_value_label)
        layout.addLayout(brightness_layout)
        
        # Direction (pour Wave et Shifting)
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Direction:")
        direction_layout.addWidget(direction_label)
        self._direction_combo = QComboBox()
        self._direction_combo.addItem("Droite → Gauche", Config.RGB_DIRECTION_RTL)
        self._direction_combo.addItem("Gauche → Droite", Config.RGB_DIRECTION_LTR)
        direction_layout.addWidget(self._direction_combo)
        layout.addLayout(direction_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_dynamic_color_section(self) -> QGroupBox:
        """Crée la section de sélection de couleur pour les modes dynamiques."""
        group = QGroupBox("Couleur RGB (Modes Dynamiques)")
        layout = QVBoxLayout()
        
        # Rouge
        red_layout = QHBoxLayout()
        red_label = QLabel("Rouge:")
        red_layout.addWidget(red_label)
        self._red_spinbox = QSpinBox()
        self._red_spinbox.setRange(Config.RGB_COLOR_MIN, Config.RGB_COLOR_MAX)
        self._red_spinbox.setValue(50)
        red_layout.addWidget(self._red_spinbox)
        layout.addLayout(red_layout)
        
        # Vert
        green_layout = QHBoxLayout()
        green_label = QLabel("Vert:")
        green_layout.addWidget(green_label)
        self._green_spinbox = QSpinBox()
        self._green_spinbox.setRange(Config.RGB_COLOR_MIN, Config.RGB_COLOR_MAX)
        self._green_spinbox.setValue(255)
        green_layout.addWidget(self._green_spinbox)
        layout.addLayout(green_layout)
        
        # Bleu
        blue_layout = QHBoxLayout()
        blue_label = QLabel("Bleu:")
        blue_layout.addWidget(blue_label)
        self._blue_spinbox = QSpinBox()
        self._blue_spinbox.setRange(Config.RGB_COLOR_MIN, Config.RGB_COLOR_MAX)
        self._blue_spinbox.setValue(50)
        blue_layout.addWidget(self._blue_spinbox)
        layout.addLayout(blue_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_action_section(self) -> QGroupBox:
        """Crée la section des boutons d'action."""
        group = QGroupBox("Actions")
        layout = QHBoxLayout()
        
        apply_btn = QPushButton("Appliquer")
        apply_btn.clicked.connect(self._apply_settings)
        layout.addWidget(apply_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_profile_section(self) -> QGroupBox:
        """Crée la section de gestion des profils."""
        group = QGroupBox("Profils")
        layout = QVBoxLayout()
        
        # ComboBox des profils
        profile_layout = QHBoxLayout()
        profile_label = QLabel("Profil:")
        profile_layout.addWidget(profile_label)
        self._profile_combo = QComboBox()
        self._refresh_profiles()
        profile_layout.addWidget(self._profile_combo)
        layout.addLayout(profile_layout)
        
        # Boutons profil
        profile_btn_layout = QHBoxLayout()
        load_btn = QPushButton("Charger")
        load_btn.clicked.connect(self._load_profile)
        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self._save_profile)
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self._refresh_profiles)
        
        profile_btn_layout.addWidget(load_btn)
        profile_btn_layout.addWidget(save_btn)
        profile_btn_layout.addWidget(refresh_btn)
        layout.addLayout(profile_btn_layout)
        
        group.setLayout(layout)
        return group
    
    def _apply_settings(self) -> None:
        """Applique les paramètres RGB."""
        mode = self._mode_combo.currentData()
        
        if mode == Config.RGB_MODE_STATIC:
            # Mode statique : appliquer chaque zone
            brightness = self._static_brightness_slider.value()
            success = True
            
            for zone_data in self._zone_colors:
                zone = zone_data['zone']
                red = zone_data['red'].value()
                green = zone_data['green'].value()
                blue = zone_data['blue'].value()
                
                zone_success = self._keyboard_controller.set_static_mode(
                    zone, red, green, blue, brightness
                )
                if not zone_success:
                    success = False
            
            if not success:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Erreur")
                msg.setText("Impossible d'appliquer certaines zones.")
                msg.setInformativeText("Vérifiez que le module kernel est chargé.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        else:
            # Mode dynamique
            speed = self._speed_slider.value()
            brightness = self._brightness_slider.value()
            direction = self._direction_combo.currentData()
            red = self._red_spinbox.value()
            green = self._green_spinbox.value()
            blue = self._blue_spinbox.value()
            
            success = self._keyboard_controller.set_dynamic_mode(
                mode, speed, brightness, direction, red, green, blue
            )
            
            if not success:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Erreur")
                msg.setText("Impossible d'appliquer les paramètres.")
                msg.setInformativeText("Vérifiez que le module kernel est chargé.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
    
    def _refresh_profiles(self) -> None:
        """Actualise la liste des profils."""
        self._profile_combo.clear()
        profiles = self._keyboard_controller.get_saved_profiles()
        for profile in profiles:
            self._profile_combo.addItem(profile)
    
    def _load_profile(self) -> None:
        """Charge un profil."""
        profile_name = self._profile_combo.currentText()
        if not profile_name:
            return
        
        profile = self._keyboard_controller.load_profile(profile_name)
        if profile:
            # Mettre à jour l'interface avec les valeurs du profil
            mode = profile.get('mode', Config.RGB_MODE_WAVE)
            index = self._mode_combo.findData(mode)
            if index >= 0:
                self._mode_combo.setCurrentIndex(index)
            
            if mode == Config.RGB_MODE_STATIC:
                # Charger les couleurs des zones
                brightness = profile.get('brightness', Config.RGB_BRIGHTNESS_DEFAULT)
                self._static_brightness_slider.setValue(brightness)
                
                # Charger les couleurs des zones si disponibles
                for zone_data in self._zone_colors:
                    zone = zone_data['zone']
                    zone_key = f'zone_{zone}'
                    if zone_key in profile:
                        zone_colors = profile[zone_key]
                        zone_data['red'].setValue(zone_colors.get('red', 50))
                        zone_data['green'].setValue(zone_colors.get('green', 255))
                        zone_data['blue'].setValue(zone_colors.get('blue', 50))
                    # Mettre à jour l'aperçu
                    if 'update_preview' in zone_data:
                        zone_data['update_preview']()
            else:
                # Mode dynamique
                self._speed_slider.setValue(profile.get('speed', Config.RGB_SPEED_DEFAULT))
                self._brightness_slider.setValue(profile.get('brightness', Config.RGB_BRIGHTNESS_DEFAULT))
                self._red_spinbox.setValue(profile.get('red', 50))
                self._green_spinbox.setValue(profile.get('green', 255))
                self._blue_spinbox.setValue(profile.get('blue', 50))
                
                if 'direction' in profile:
                    index = self._direction_combo.findData(profile['direction'])
                    if index >= 0:
                        self._direction_combo.setCurrentIndex(index)
            
            self._apply_settings()
    
    def _save_profile(self) -> None:
        """Sauvegarde un profil."""
        profile_name = self._profile_combo.currentText()
        if not profile_name:
            # Demander un nom
            name, ok = QInputDialog.getText(self, "Sauvegarder le profil", "Nom du profil:")
            if not ok or not name:
                return
            profile_name = name
        
        mode = self._mode_combo.currentData()
        
        if mode == Config.RGB_MODE_STATIC:
            # Sauvegarder les couleurs des 4 zones
            brightness = self._static_brightness_slider.value()
            zone_colors = {}
            for zone_data in self._zone_colors:
                zone = zone_data['zone']
                zone_colors[f'zone_{zone}'] = {
                    'red': zone_data['red'].value(),
                    'green': zone_data['green'].value(),
                    'blue': zone_data['blue'].value()
                }
            
            # Utiliser la méthode save_profile avec les données des zones
            # On doit adapter le contrôleur pour accepter les zones multiples
            success = self._keyboard_controller.save_static_profile(
                profile_name, brightness, zone_colors
            )
        else:
            # Mode dynamique
            speed = self._speed_slider.value()
            brightness = self._brightness_slider.value()
            direction = self._direction_combo.currentData()
            red = self._red_spinbox.value()
            green = self._green_spinbox.value()
            blue = self._blue_spinbox.value()
            
            success = self._keyboard_controller.save_profile(
                profile_name, mode, 1, speed, brightness, direction, red, green, blue
            )
        
        if success:
            self._refresh_profiles()
            index = self._profile_combo.findText(profile_name)
            if index >= 0:
                self._profile_combo.setCurrentIndex(index)
