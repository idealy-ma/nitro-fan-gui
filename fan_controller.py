"""
Contrôleur pour gérer les commandes système du ventilateur.
"""
import subprocess
from typing import List, Optional


class FanController:
    """Gère les commandes système pour contrôler le ventilateur."""
    
    @staticmethod
    def _run_command(command: List[str], use_sudo: bool = True) -> None:
        """
        Exécute une commande système en masquant la sortie.
        
        Args:
            command: Liste des arguments de la commande
            use_sudo: Si True, essaie avec sudo, sinon essaie sans sudo d'abord
        """
        if use_sudo:
            # Essayer d'abord sans sudo
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            # Si ça échoue, essayer avec sudo
            if result.returncode != 0:
                sudo_command = ["sudo"] + command
                subprocess.run(
                    sudo_command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
        else:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
    
    @staticmethod
    def set_speed(fan_id: int, speed: int) -> None:
        """
        Définit la vitesse du ventilateur.
        
        Args:
            fan_id: ID du ventilateur (0 pour CPU, 1 pour GPU)
            speed: Vitesse en pourcentage (0-100)
        """
        FanController._run_command([
            "nbfc-safe", "set",
            "--fan", str(fan_id),
            "--speed", str(speed)
        ])
    
    @staticmethod
    def set_auto_mode(fan_id: int) -> None:
        """
        Active le mode automatique du ventilateur.
        
        Args:
            fan_id: ID du ventilateur (0 pour CPU, 1 pour GPU)
        """
        FanController._run_command([
            "nbfc-safe", "set",
            "--fan", str(fan_id),
            "--auto"
        ])
    
    @staticmethod
    def start() -> None:
        """Démarre le contrôle du ventilateur."""
        FanController._run_command([
            "nbfc-safe", "start"
        ])
    
    @staticmethod
    def stop() -> None:
        """Arrête le contrôle du ventilateur."""
        FanController._run_command([
            "nbfc-safe", "stop"
        ])
    
    @staticmethod
    def get_available_devices() -> List[str]:
        """
        Récupère la liste des appareils nbfc disponibles.
        
        Returns:
            Liste des noms d'appareils disponibles
        """
        try:
            result = subprocess.run(
                ["nbfc", "config", "-l"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5
            )
            
            if result.returncode == 0:
                devices = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                return devices
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return []
    
    @staticmethod
    def get_recommended_devices() -> List[str]:
        """
        Récupère la liste des appareils nbfc recommandés pour ce système.
        
        Returns:
            Liste des noms d'appareils recommandés
        """
        try:
            result = subprocess.run(
                ["nbfc", "config", "-r"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5
            )
            
            if result.returncode == 0:
                devices = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                return devices
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return []
    
    @staticmethod
    def get_current_device() -> Optional[str]:
        """
        Récupère l'appareil nbfc actuellement configuré.
        
        Returns:
            Nom de l'appareil actuel ou None
        """
        try:
            result = subprocess.run(
                ["nbfc", "config", "-l"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5
            )
            
            if result.returncode == 0:
                # Chercher l'appareil actuel (généralement marqué avec un astérisque ou autre)
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '*' in line or '(current)' in line.lower() or '(applied)' in line.lower():
                        device = line.strip().replace('*', '').replace('(current)', '').replace('(applied)', '').strip()
                        return device
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    @staticmethod
    def apply_device(device_name: str) -> bool:
        """
        Applique un appareil nbfc spécifique.
        
        Args:
            device_name: Nom de l'appareil à appliquer
        
        Returns:
            True si l'application a réussi, False sinon
        """
        try:
            result = subprocess.run(
                ["nbfc", "config", "-a", device_name],
                capture_output=True,
                text=True,
                check=False,
                timeout=5
            )
            
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False