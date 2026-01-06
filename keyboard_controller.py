"""
Contrôleur pour gérer le clavier RGB via le module kernel acer.
"""
from pathlib import Path
from typing import List, Optional
import os

PAYLOAD_SIZE = 16
CHARACTER_DEVICE = "/dev/acer-gkbbl-0"

PAYLOAD_SIZE_STATIC_MODE = 4
CHARACTER_DEVICE_STATIC = "/dev/acer-gkbbl-static-0"

CONFIG_DIRECTORY = str(Path.home()) + "/.config/predator/saved profiles"
path = Path(CONFIG_DIRECTORY)
path.mkdir(parents=True, exist_ok=True)


class KeyboardController:
    """Gère le contrôle du clavier RGB."""
    
    @staticmethod
    def is_available() -> bool:
        """
        Vérifie si le module kernel est disponible.
        
        Returns:
            True si les devices character existent, False sinon
        """
        return os.path.exists(CHARACTER_DEVICE) and os.path.exists(CHARACTER_DEVICE_STATIC)
    
    @staticmethod
    def set_static_mode(zone: int, red: int, green: int, blue: int, brightness: int = 100) -> bool:
        """
        Définit le mode statique pour une zone spécifique.
        
        Args:
            zone: ID de la zone (1-4)
            red: Composante rouge (0-255)
            green: Composante verte (0-255)
            blue: Composante bleue (0-255)
            brightness: Luminosité (0-100)
        
        Returns:
            True si réussi, False sinon
        """
        if not KeyboardController.is_available():
            return False
        
        if zone < 1 or zone > 4:
            return False
        
        try:
            # Mode statique
            payload = [0] * PAYLOAD_SIZE_STATIC_MODE
            payload[0] = 1 << (zone - 1)
            payload[1] = max(0, min(255, red))
            payload[2] = max(0, min(255, green))
            payload[3] = max(0, min(255, blue))
            
            with open(CHARACTER_DEVICE_STATIC, 'wb') as cd:
                cd.write(bytes(payload))
            
            # Activer le mode statique
            payload = [0] * PAYLOAD_SIZE
            payload[2] = max(0, min(100, brightness))
            payload[9] = 1
            
            with open(CHARACTER_DEVICE, 'wb') as cd:
                cd.write(bytes(payload))
            
            return True
        except (IOError, PermissionError):
            return False
    
    @staticmethod
    def set_dynamic_mode(
        mode: int,
        speed: int = 4,
        brightness: int = 100,
        direction: int = 1,
        red: int = 50,
        green: int = 255,
        blue: int = 50
    ) -> bool:
        """
        Définit un mode dynamique pour le clavier.
        
        Args:
            mode: Mode (0=Static, 1=Breath, 2=Neon, 3=Wave, 4=Shifting, 5=Zoom)
            speed: Vitesse (0-9, 0=statique)
            brightness: Luminosité (0-100)
            direction: Direction (1=Right to Left, 2=Left to Right)
            red: Composante rouge (0-255)
            green: Composante verte (0-255)
            blue: Composante bleue (0-255)
        
        Returns:
            True si réussi, False sinon
        """
        if not KeyboardController.is_available():
            return False
        
        if mode == 0:
            return False  # Utiliser set_static_mode pour le mode statique
        
        try:
            payload = [0] * PAYLOAD_SIZE
            payload[0] = mode
            payload[1] = max(0, min(255, speed))
            payload[2] = max(0, min(100, brightness))
            payload[3] = 8 if mode == 3 else 0  # Wave mode
            payload[4] = direction
            payload[5] = max(0, min(255, red))
            payload[6] = max(0, min(255, green))
            payload[7] = max(0, min(255, blue))
            payload[9] = 1
            
            with open(CHARACTER_DEVICE, 'wb') as cd:
                cd.write(bytes(payload))
            
            return True
        except (IOError, PermissionError):
            return False
    
    @staticmethod
    def get_saved_profiles() -> List[str]:
        """
        Récupère la liste des profils sauvegardés.
        
        Returns:
            Liste des noms de profils
        """
        profiles = []
        if os.path.exists(CONFIG_DIRECTORY):
            for filepath in Path(CONFIG_DIRECTORY).glob('*.json'):
                profiles.append(filepath.stem)
        return sorted(profiles)
    
    @staticmethod
    def save_profile(name: str, mode: int, zone: int = 1, speed: int = 4,
                     brightness: int = 100, direction: int = 1,
                     red: int = 50, green: int = 255, blue: int = 50) -> bool:
        """
        Sauvegarde un profil.
        
        Args:
            name: Nom du profil
            mode: Mode RGB
            zone: Zone (pour mode statique)
            speed: Vitesse
            brightness: Luminosité
            direction: Direction
            red: Rouge
            green: Vert
            blue: Bleu
        
        Returns:
            True si réussi, False sinon
        """
        import json
        try:
            profile_data = {
                'mode': mode,
                'zone': zone,
                'speed': speed,
                'brightness': brightness,
                'direction': direction,
                'red': red,
                'green': green,
                'blue': blue
            }
            
            profile_path = Path(CONFIG_DIRECTORY) / f"{name}.json"
            with open(profile_path, 'wt') as f:
                json.dump(profile_data, f, indent=4)
            
            return True
        except (IOError, json.JSONDecodeError):
            return False
    
    @staticmethod
    def save_static_profile(name: str, brightness: int, zone_colors: dict) -> bool:
        """
        Sauvegarde un profil statique avec les 4 zones.
        
        Args:
            name: Nom du profil
            brightness: Luminosité globale
            zone_colors: Dictionnaire avec les couleurs de chaque zone
                        Format: {'zone_1': {'red': int, 'green': int, 'blue': int}, ...}
        
        Returns:
            True si réussi, False sinon
        """
        import json
        try:
            profile_data = {
                'mode': 0,  # RGB_MODE_STATIC
                'brightness': brightness
            }
            
            # Ajouter les couleurs de chaque zone
            for zone_key, colors in zone_colors.items():
                profile_data[zone_key] = colors
            
            profile_path = Path(CONFIG_DIRECTORY) / f"{name}.json"
            with open(profile_path, 'wt') as f:
                json.dump(profile_data, f, indent=4)
            
            return True
        except (IOError, json.JSONDecodeError):
            return False
    
    @staticmethod
    def load_profile(name: str) -> Optional[dict]:
        """
        Charge un profil sauvegardé.
        
        Args:
            name: Nom du profil
        
        Returns:
            Dictionnaire avec les paramètres du profil ou None
        """
        import json
        try:
            profile_path = Path(CONFIG_DIRECTORY) / f"{name}.json"
            if not profile_path.exists():
                return None
            
            with open(profile_path, 'rt') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
