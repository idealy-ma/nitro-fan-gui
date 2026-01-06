"""
Écran de contrôle des ventilateurs.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QSlider, QPushButton, QHBoxLayout, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from collections import deque
from datetime import datetime
from typing import Any

from config import Config
from fan_controller import FanController
from temperature_reader import TemperatureReader


class FanScreen(QWidget):
    """Écran de contrôle des ventilateurs."""
    
    def __init__(self, fan_controller: FanController, temperature_reader: TemperatureReader):
        """Initialise l'écran des ventilateurs."""
        super().__init__()
        self._fan_controller = fan_controller
        self._temperature_reader = temperature_reader
        
        # Historique des températures
        self._cpu_temp_history = deque(maxlen=Config.TEMP_HISTORY_SIZE)
        self._gpu_temp_history = deque(maxlen=Config.TEMP_HISTORY_SIZE)
        self._time_history = deque(maxlen=Config.TEMP_HISTORY_SIZE)
        self._start_time = datetime.now()
        
        self._init_ui()
        self._setup_temperature_timer()
    
    def _init_ui(self) -> None:
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Titre
        title = self._create_title()
        layout.addWidget(title)
        
        # Section de sélection d'appareil
        device_section = self._create_device_selection_section()
        layout.addWidget(device_section)
        
        # Section des températures
        temp_section = self._create_temperature_section()
        layout.addWidget(temp_section)
        
        # Section CPU
        cpu_section = self._create_fan_section("CPU", Config.CPU_FAN_ID)
        layout.addWidget(cpu_section)
        
        # Section GPU
        gpu_section = self._create_fan_section("GPU", Config.GPU_FAN_ID)
        layout.addWidget(gpu_section)
        
        # Boutons globaux
        global_button_layout = self._create_global_button_layout()
        layout.addLayout(global_button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_title(self) -> QLabel:
        """Crée le label de titre."""
        title = QLabel("Contrôle des Ventilateurs")
        title.setFont(QFont(Config.TITLE_FONT, Config.TITLE_FONT_SIZE, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        return title
    
    def _create_device_selection_section(self) -> QGroupBox:
        """Crée la section de sélection d'appareil."""
        group = QGroupBox("Appareil")
        layout = QVBoxLayout()
        
        label = QLabel("Sélectionner l'appareil:")
        label.setAlignment(Qt.AlignLeft)
        layout.addWidget(label)
        
        self._device_combo = QComboBox()
        self._device_combo.setEditable(False)
        
        recommended = self._fan_controller.get_recommended_devices()
        current = self._fan_controller.get_current_device()
        
        for device in recommended:
            self._device_combo.addItem(device)
        
        if current and current in recommended:
            index = self._device_combo.findText(current)
            if index >= 0:
                self._device_combo.setCurrentIndex(index)
        elif recommended:
            self._device_combo.setCurrentIndex(0)
        
        self._device_combo.currentTextChanged.connect(self._on_device_changed)
        layout.addWidget(self._device_combo)
        group.setLayout(layout)
        return group
    
    def _on_device_changed(self, device_name: str) -> None:
        """Gère le changement d'appareil sélectionné."""
        if device_name:
            success = self._fan_controller.apply_device(device_name)
            if success:
                self._fan_controller.stop()
                self._fan_controller.start()
    
    def _create_temperature_section(self) -> QGroupBox:
        """Crée la section d'affichage des températures."""
        group = QGroupBox("Températures")
        layout = QVBoxLayout()
        
        label_layout = QHBoxLayout()
        self._cpu_temp_label = QLabel("CPU: --°C")
        self._cpu_temp_label.setAlignment(Qt.AlignCenter)
        self._cpu_temp_label.setFont(QFont(Config.TITLE_FONT, 11, QFont.Bold))
        self._cpu_temp_label.setTextFormat(Qt.RichText)
        label_layout.addWidget(self._cpu_temp_label)
        
        self._gpu_temp_label = QLabel("GPU: --°C")
        self._gpu_temp_label.setAlignment(Qt.AlignCenter)
        self._gpu_temp_label.setFont(QFont(Config.TITLE_FONT, 11, QFont.Bold))
        self._gpu_temp_label.setTextFormat(Qt.RichText)
        label_layout.addWidget(self._gpu_temp_label)
        layout.addLayout(label_layout)
        
        cpu_chart_view = self._create_temperature_chart("CPU", QColor("#4CAF50"))
        layout.addWidget(cpu_chart_view)
        
        gpu_chart_view = self._create_temperature_chart("GPU", QColor("#2196F3"))
        layout.addWidget(gpu_chart_view)
        
        group.setLayout(layout)
        return group
    
    def _create_temperature_chart(self, name: str, color: QColor) -> QChartView:
        """Crée un graphique de température."""
        series = QLineSeries()
        series.setName(name)
        series.setColor(color)
        series.setPen(QColor(color))
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Température {name}")
        chart.setTheme(QChart.ChartThemeDark)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QColor("#121212"))
        
        axis_x = QValueAxis()
        axis_x.setRange(0, Config.TEMP_HISTORY_SIZE)
        axis_x.setTitleText("Temps (s)")
        axis_x.setLabelsColor(QColor("#ffffff"))
        axis_x.setLinePenColor(QColor("#ffffff"))
        axis_x.setGridLineColor(QColor("#2c2c2c"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(Config.TEMP_MIN, Config.TEMP_MAX)
        axis_y.setTitleText("Température (°C)")
        axis_y.setLabelsColor(QColor("#ffffff"))
        axis_y.setLinePenColor(QColor("#ffffff"))
        axis_y.setGridLineColor(QColor("#2c2c2c"))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setFixedHeight(Config.TEMP_CHART_HEIGHT)
        
        if name == "CPU":
            self._cpu_chart_series = series
            self._cpu_chart = chart
        else:
            self._gpu_chart_series = series
            self._gpu_chart = chart
        
        return chart_view
    
    def _create_fan_section(self, fan_name: str, fan_id: int) -> QGroupBox:
        """Crée une section de contrôle pour un ventilateur."""
        group = QGroupBox(f"{fan_name} Fan")
        layout = QVBoxLayout()
        
        speed_label = QLabel(f"{fan_name} speed: {Config.SLIDER_DEFAULT}%")
        speed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(speed_label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(Config.SLIDER_MIN, Config.SLIDER_MAX)
        slider.setValue(Config.SLIDER_DEFAULT)
        
        slider.valueChanged.connect(
            lambda value: self._on_slider_changed(value, fan_id, speed_label, fan_name)
        )
        layout.addWidget(slider)
        
        button_layout = QHBoxLayout()
        
        auto_btn = QPushButton("AUTO")
        auto_btn.clicked.connect(
            lambda: self._fan_controller.set_auto_mode(fan_id)
        )
        
        turbo_btn = QPushButton("TURBO")
        turbo_btn.clicked.connect(
            lambda: self._on_turbo_clicked(fan_id, slider, speed_label, fan_name)
        )
        
        button_layout.addWidget(auto_btn)
        button_layout.addWidget(turbo_btn)
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        group.slider = slider
        group.speed_label = speed_label
        
        return group
    
    def _create_global_button_layout(self) -> QHBoxLayout:
        """Crée la disposition des boutons globaux."""
        layout = QHBoxLayout()
        
        start_btn = QPushButton("START")
        start_btn.clicked.connect(self._fan_controller.start)
        
        stop_btn = QPushButton("STOP")
        stop_btn.clicked.connect(self._fan_controller.stop)
        
        layout.addWidget(start_btn)
        layout.addWidget(stop_btn)
        
        return layout
    
    def _on_slider_changed(self, value: int, fan_id: int, label: QLabel, fan_name: str) -> None:
        """Gère le changement de valeur du slider."""
        label.setText(f"{fan_name} speed: {value}%")
        self._fan_controller.set_speed(fan_id, value)
    
    def _on_turbo_clicked(self, fan_id: int, slider: QSlider, label: QLabel, fan_name: str) -> None:
        """Gère le clic sur le bouton TURBO."""
        speed = Config.TURBO_SPEED
        slider.setValue(speed)
        label.setText(f"{fan_name} speed: {speed}%")
        self._fan_controller.set_speed(fan_id, speed)
    
    def _setup_temperature_timer(self) -> None:
        """Configure le timer pour mettre à jour les températures."""
        self._temp_timer = QTimer(self)
        self._temp_timer.timeout.connect(self._update_temperatures)
        self._temp_timer.start(Config.TEMP_UPDATE_INTERVAL_MS)
        self._update_temperatures()
    
    def _update_temperatures(self) -> None:
        """Met à jour l'affichage des températures."""
        if not hasattr(self, '_cpu_chart_series') or not hasattr(self, '_gpu_chart_series'):
            return
        
        current_time = datetime.now()
        elapsed_seconds = (current_time - self._start_time).total_seconds()
        
        cpu_temp = self._temperature_reader.get_cpu_temperature()
        gpu_temp = self._temperature_reader.get_gpu_temperature()
        
        self._time_history.append(elapsed_seconds)
        
        if cpu_temp is not None:
            color = self._get_temperature_color(cpu_temp)
            self._cpu_temp_label.setText(f'CPU: <span style="color: {color};">{cpu_temp:.1f}°C</span>')
            self._cpu_temp_history.append(cpu_temp)
        else:
            self._cpu_temp_label.setText("CPU: --°C")
            self._cpu_temp_history.append(None)
        
        if gpu_temp is not None:
            color = self._get_temperature_color(gpu_temp)
            self._gpu_temp_label.setText(f'GPU: <span style="color: {color};">{gpu_temp:.1f}°C</span>')
            self._gpu_temp_history.append(gpu_temp)
        else:
            self._gpu_temp_label.setText("GPU: --°C")
            self._gpu_temp_history.append(None)
        
        self._update_chart(self._cpu_chart_series, self._cpu_temp_history, self._time_history)
        self._update_chart(self._gpu_chart_series, self._gpu_temp_history, self._time_history)
    
    def _update_chart(self, series: QLineSeries, temp_history: deque, time_history: deque) -> None:
        """Met à jour un graphique de température."""
        series.clear()
        
        if len(temp_history) == 0 or len(time_history) == 0:
            return
        
        for i, temp_val in enumerate(temp_history):
            if temp_val is not None:
                x = i
                series.append(x, temp_val)
    
    def _get_temperature_color(self, temp: float) -> str:
        """Retourne une couleur en fonction de la température."""
        if temp < 50:
            return "#4CAF50"  # Vert
        elif temp < 70:
            return "#FFC107"  # Jaune
        elif temp < 85:
            return "#FF9800"  # Orange
        else:
            return "#F44336"  # Rouge
