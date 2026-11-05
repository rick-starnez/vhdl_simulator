from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, 
    QLineEdit, QSpinBox, QRadioButton, QStackedWidget, QGroupBox, 
    QPushButton, QDialogButtonBox, QWidget
)
from PyQt6.QtCore import Qt, QTimer

class EditDialog(QDialog):
    def __init__(self, input_signals, current_configs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Señales de Entrada")
        self.setStyleSheet("background-color: #1e1e1e; color: #ddd;")
        
        self.input_signals = input_signals
        self.configs = dict(current_configs) 
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(10)
        
        self.combo_signals = QComboBox()
        self.combo_signals.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555; min-width: 150px;")
        for sig in input_signals:
            self.combo_signals.addItem(sig["name"])
        form_layout.addRow("Señal:", self.combo_signals)
        
        self.combo_type = QComboBox()
        self.combo_type.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555; min-width: 150px;")
        self.combo_type.addItems(["Arbitraria", "Aleatoria", "Reloj"])
        form_layout.addRow("Tipo:", self.combo_type)
        
        layout.addLayout(form_layout)
        
        self.group_options = QGroupBox("Opciones de la Señal")
        self.group_options.setStyleSheet("""
            QGroupBox { color: #ddd; border: 1px solid #444; margin-top: 10px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
        """)
        self.options_layout = QVBoxLayout(self.group_options)
        self.options_layout.setContentsMargins(10, 10, 10, 10)
        
        self.stacked_options = QStackedWidget()
        
        # 1. Arbitraria
        self.page_arbitraria = QWidget()
        lay_arb = QVBoxLayout(self.page_arbitraria)
        lay_arb.setContentsMargins(0, 0, 0, 0)
        form_arb = QFormLayout()
        form_arb.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.input_bin = QLineEdit()
        self.input_bin.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555;")
        form_arb.addRow("Valor:", self.input_bin)
        
        self.combo_radix_arb = QComboBox()
        self.combo_radix_arb.addItems(["Binario", "Decimal", "Hexadecimal"])
        self.combo_radix_arb.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555;")
        form_arb.addRow("Radix:", self.combo_radix_arb)
        
        lay_arb.addLayout(form_arb)
        self.stacked_options.addWidget(self.page_arbitraria)
        
        # 2. Aleatoria
        self.page_aleatoria = QWidget()
        lay_ale = QVBoxLayout(self.page_aleatoria)
        lay_ale.setContentsMargins(0, 0, 0, 0)
        form_ale = QFormLayout()
        form_ale.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.spin_random_interval = QSpinBox()
        self.spin_random_interval.setRange(1, 100000)
        self.spin_random_interval.setValue(100)
        self.spin_random_interval.setSuffix(" ns")
        self.spin_random_interval.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 2px; border: 1px solid #555;")
        form_ale.addRow("Intervalo de cambio:", self.spin_random_interval)
        
        self.combo_radix_ale = QComboBox()
        self.combo_radix_ale.addItems(["Binario", "Decimal", "Hexadecimal"])
        self.combo_radix_ale.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555;")
        form_ale.addRow("Radix:", self.combo_radix_ale)
        
        lay_ale.addLayout(form_ale)
        self.stacked_options.addWidget(self.page_aleatoria)
        
        # 3. Reloj
        self.page_reloj = QWidget()
        lay_rel = QVBoxLayout(self.page_reloj)
        lay_rel.setContentsMargins(0, 0, 0, 0)
        form_rel = QFormLayout()
        form_rel.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.input_clock_start = QLineEdit()
        self.input_clock_start.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555;")
        form_rel.addRow("Valor inicial:", self.input_clock_start)
        
        self.combo_radix_clock = QComboBox()
        self.combo_radix_clock.addItems(["Binario", "Decimal", "Hexadecimal"])
        self.combo_radix_clock.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555;")
        form_rel.addRow("Radix:", self.combo_radix_clock)
        
        dir_layout = QHBoxLayout()
        self.radio_desc = QRadioButton("Descendente")
        self.radio_asc = QRadioButton("Ascendente")
        self.radio_asc.setChecked(True)
        
        radio_style = "QRadioButton { color: #ddd; } QRadioButton::indicator { width: 13px; height: 13px; }"
        self.radio_desc.setStyleSheet(radio_style)
        self.radio_asc.setStyleSheet(radio_style)
        
        dir_layout.addWidget(self.radio_asc)
        dir_layout.addWidget(self.radio_desc)
        form_rel.addRow("Dirección:", dir_layout)
        
        self.spin_clock_interval = QSpinBox()
        self.spin_clock_interval.setRange(1, 100000)
        self.spin_clock_interval.setValue(50)
        self.spin_clock_interval.setSuffix(" ns")
        self.spin_clock_interval.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 2px; border: 1px solid #555;")
        form_rel.addRow("Intervalo:", self.spin_clock_interval)
        
        lay_rel.addLayout(form_rel)
        self.stacked_options.addWidget(self.page_reloj)
        
        self.options_layout.addWidget(self.stacked_options)
        
        btn_save_layout = QHBoxLayout()
        btn_save_layout.addStretch()
        self.btn_save_signal = QPushButton("Guardar Señal")
        self.btn_save_signal.setStyleSheet("""
            QPushButton { background: #005a9e; color: white; padding: 5px 15px; border: none; border-radius: 3px; }
            QPushButton:hover { background: #0078d4; }
        """)
        self.btn_save_signal.clicked.connect(self.save_current_signal)
        btn_save_layout.addWidget(self.btn_save_signal)
        
        self.options_layout.addLayout(btn_save_layout)
        layout.addWidget(self.group_options)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.setStyleSheet("""
            QPushButton { background: #444; color: #ddd; padding: 5px 15px; border: none; border-radius: 2px; min-width: 70px; }
            QPushButton:hover { background: #555; }
        """)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        self.combo_type.currentIndexChanged.connect(self.on_type_changed)
        self.combo_signals.currentIndexChanged.connect(self.load_current_config)
        
        if self.combo_signals.count() > 0:
            self.load_current_config()
            
        self.adjustSize()

    def on_type_changed(self, index):
        self.stacked_options.setCurrentIndex(index)
        self.adjustSize()

    def load_current_config(self):
        sig_name = self.combo_signals.currentText()
        if sig_name in self.configs:
            cfg = self.configs[sig_name]
            self.combo_type.setCurrentText(cfg.get("type", "Arbitraria"))
            self.stacked_options.setCurrentIndex(self.combo_type.currentIndex())
            
            if cfg["type"] == "Arbitraria":
                self.input_bin.setText(str(cfg.get("value", "0")))
                self.combo_radix_arb.setCurrentText(cfg.get("radix", "Binario"))
            elif cfg["type"] == "Aleatoria":
                self.spin_random_interval.setValue(cfg.get("interval", 100))
                self.combo_radix_ale.setCurrentText(cfg.get("radix", "Binario"))
            elif cfg["type"] == "Reloj":
                self.input_clock_start.setText(str(cfg.get("start", "0")))
                self.combo_radix_clock.setCurrentText(cfg.get("radix", "Binario"))
                self.spin_clock_interval.setValue(cfg.get("interval", 50))
                if cfg.get("direction", "Ascendente") == "Ascendente":
                    self.radio_asc.setChecked(True)
                else:
                    self.radio_desc.setChecked(True)
        
        self.adjustSize()

    def convert_to_binary(self, value_str, radix):
        try:
            if radix == "Binario":
                return value_str.zfill(4)
            elif radix == "Decimal":
                return bin(int(value_str))[2:].zfill(4)
            elif radix == "Hexadecimal":
                return bin(int(value_str, 16))[2:].zfill(4)
        except:
            return "0000"

    def save_current_signal(self):
        sig_name = self.combo_signals.currentText()
        sig_type = self.combo_type.currentText()
        
        cfg = {"type": sig_type}
        
        if sig_type == "Arbitraria":
            cfg["value"] = self.convert_to_binary(self.input_bin.text(), self.combo_radix_arb.currentText())
            cfg["radix"] = self.combo_radix_arb.currentText()
        elif sig_type == "Aleatoria":
            cfg["interval"] = self.spin_random_interval.value()
            cfg["radix"] = self.combo_radix_ale.currentText()
        elif sig_type == "Reloj":
            cfg["start"] = self.convert_to_binary(self.input_clock_start.text(), self.combo_radix_clock.currentText())
            cfg["radix"] = self.combo_radix_clock.currentText()
            cfg["direction"] = "Ascendente" if self.radio_asc.isChecked() else "Descendente"
            cfg["interval"] = self.spin_clock_interval.value()
            
        self.configs[sig_name] = cfg
        
        self.btn_save_signal.setText("¡Guardado!")
        self.btn_save_signal.setStyleSheet("background: #107c10; color: white; padding: 5px 15px; border: none; border-radius: 3px;")
        
        QTimer.singleShot(1000, lambda: self.btn_save_signal.setText("Guardar Señal") or 
                                       self.btn_save_signal.setStyleSheet("""
                                           QPushButton { background: #005a9e; color: white; padding: 5px 15px; border: none; border-radius: 3px; }
                                           QPushButton:hover { background: #0078d4; }
                                       """))

    def accept(self):
        self.save_current_signal()
        super().accept()


class OutputEditDialog(QDialog):
    def __init__(self, output_signals, current_configs, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Señales de Salida")
        self.setStyleSheet("background-color: #1e1e1e; color: #ddd;")
        
        self.output_signals = output_signals
        self.configs = dict(current_configs) 
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(10)
        
        self.combo_signals = QComboBox()
        self.combo_signals.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555; min-width: 150px;")
        for sig in output_signals:
            self.combo_signals.addItem(sig["name"])
        form_layout.addRow("Señal:", self.combo_signals)
        
        self.combo_radix = QComboBox()
        self.combo_radix.addItems(["Binario", "Decimal", "Hexadecimal"])
        self.combo_radix.setStyleSheet("background: #2d2d2d; color: #ddd; padding: 4px; border: 1px solid #555; min-width: 150px;")
        form_layout.addRow("Radix:", self.combo_radix)
        
        layout.addLayout(form_layout)
        
        btn_save_layout = QHBoxLayout()
        btn_save_layout.addStretch()
        self.btn_save_signal = QPushButton("Guardar Señal")
        self.btn_save_signal.setStyleSheet("""
            QPushButton { background: #005a9e; color: white; padding: 5px 15px; border: none; border-radius: 3px; }
            QPushButton:hover { background: #0078d4; }
        """)
        self.btn_save_signal.clicked.connect(self.save_current_signal)
        btn_save_layout.addWidget(self.btn_save_signal)
        
        layout.addLayout(btn_save_layout)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.setStyleSheet("""
            QPushButton { background: #444; color: #ddd; padding: 5px 15px; border: none; border-radius: 2px; min-width: 70px; }
            QPushButton:hover { background: #555; }
        """)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        self.combo_signals.currentIndexChanged.connect(self.load_current_config)
        
        if self.combo_signals.count() > 0:
            self.load_current_config()
            
        self.adjustSize()

    def load_current_config(self):
        sig_name = self.combo_signals.currentText()
        if sig_name in self.configs:
            cfg = self.configs[sig_name]
            self.combo_radix.setCurrentText(cfg.get("radix", "Binario"))
        self.adjustSize()

    def save_current_signal(self):
        sig_name = self.combo_signals.currentText()
        if sig_name not in self.configs:
            self.configs[sig_name] = {}
        self.configs[sig_name]["radix"] = self.combo_radix.currentText()
        
        self.btn_save_signal.setText("¡Guardado!")
        self.btn_save_signal.setStyleSheet("background: #107c10; color: white; padding: 5px 15px; border: none; border-radius: 3px;")
        
        QTimer.singleShot(1000, lambda: self.btn_save_signal.setText("Guardar Señal") or 
                                       self.btn_save_signal.setStyleSheet("""
                                           QPushButton { background: #005a9e; color: white; padding: 5px 15px; border: none; border-radius: 3px; }
                                           QPushButton:hover { background: #0078d4; }
                                       """))

    def accept(self):
        self.save_current_signal()
        super().accept()