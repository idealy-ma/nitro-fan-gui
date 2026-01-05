"""
Module pour lire les températures CPU et GPU en temps réel.
"""
import subprocess
import re
from typing import Optional


class TemperatureReader:
    """Gère la lecture des températures CPU et GPU."""
    
    @staticmethod
    def get_cpu_temperature() -> Optional[float]:
        """
        Récupère la température du CPU en degrés Celsius.
        
        Returns:
            Température du CPU en °C, ou None si impossible à lire
        """
        try:
            # Méthode 1: Utiliser sensors (lm-sensors)
            result = subprocess.run(
                ["sensors"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2
            )
            
            if result.returncode == 0:
                # Chercher la température CPU (généralement "Core 0" ou "Package id 0")
                lines = result.stdout.split('\n')
                for line in lines:
                    # Chercher des patterns comme "Core 0: +45.0°C" ou "Package id 0: +45.0°C"
                    match = re.search(r'(?:Core|Package id \d+):\s*\+?([\d.]+)°C', line)
                    if match:
                        return float(match.group(1))
                
                # Fallback: chercher n'importe quelle température avec "°C"
                for line in lines:
                    match = re.search(r'\+?([\d.]+)°C', line)
                    if match:
                        temp = float(match.group(1))
                        if 20 <= temp <= 100:  # Plage raisonnable pour CPU
                            return temp
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
        
        try:
            # Méthode 2: Lire depuis /sys/class/thermal/
            # Chercher dans les zones thermiques
            result = subprocess.run(
                ["find", "/sys/class/thermal", "-name", "temp", "-type", "f"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2
            )
            
            if result.returncode == 0:
                temp_files = result.stdout.strip().split('\n')
                for temp_file in temp_files:
                    if temp_file and 'thermal_zone' in temp_file:
                        try:
                            with open(temp_file, 'r') as f:
                                temp_millidegrees = int(f.read().strip())
                                temp_celsius = temp_millidegrees / 1000.0
                                # Filtrer les températures raisonnables
                                if 20 <= temp_celsius <= 100:
                                    return temp_celsius
                        except (IOError, ValueError):
                            continue
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    @staticmethod
    def get_gpu_temperature() -> Optional[float]:
        """
        Récupère la température du GPU en degrés Celsius.
        
        Returns:
            Température du GPU en °C, ou None si impossible à lire
        """
        # Méthode 1: NVIDIA GPU avec nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2
            )
            
            if result.returncode == 0:
                temp_str = result.stdout.strip()
                if temp_str:
                    return float(temp_str)
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
        
        # Méthode 2: AMD GPU avec sensors
        try:
            result = subprocess.run(
                ["sensors"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2
            )
            
            if result.returncode == 0:
                # Chercher des patterns pour GPU AMD (comme "radeon" ou "amdgpu")
                lines = result.stdout.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['gpu', 'radeon', 'amdgpu']):
                        match = re.search(r'\+?([\d.]+)°C', line)
                        if match:
                            temp = float(match.group(1))
                            if 20 <= temp <= 100:
                                return temp
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
        
        # Méthode 3: Lire depuis /sys/class/drm/ pour certains GPUs
        try:
            result = subprocess.run(
                ["find", "/sys/class/drm", "-name", "temp*_input", "-type", "f"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2
            )
            
            if result.returncode == 0:
                temp_files = result.stdout.strip().split('\n')
                for temp_file in temp_files:
                    if temp_file:
                        try:
                            with open(temp_file, 'r') as f:
                                temp_millidegrees = int(f.read().strip())
                                temp_celsius = temp_millidegrees / 1000.0
                                if 20 <= temp_celsius <= 100:
                                    return temp_celsius
                        except (IOError, ValueError):
                            continue
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
