import re
import random
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QToolBar,
    QPlainTextEdit, QMessageBox, QDialog, QFileDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from simulator import VHDLSimulator
from ui.widgets import WaveformSection
from ui.dialogs import EditDialog, OutputEditDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VHDL Simulator - Sin Título")
        self.resize(1400, 800)
        self.setStyleSheet("background-color: #1e1e1e;")

        self.max_sim_time = 600.0
        self.history = {}
        self.inputs_data = []
        self.outputs_data = []
        self.signal_configs = {}
        self.output_configs = {}
        
        self.current_file = None
        self.is_modified = False

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setStyleSheet("QSplitter::handle { background-color: #444; width: 4px; }")

        # AQUI SE AJUSTÓ EL TAMAÑO DE FUENTE A 12px
        toolbar_style = """
            QToolBar { background: #2b2b2b; border: none; padding: 2px; }
            QToolButton { color: #ddd; padding: 4px 8px; border: 1px solid transparent; font-size: 12px; }
            QToolButton:hover { background: #3a3a3a; border: 1px solid #555; }
            QToolButton:checked { background: #1e1e1e; border: 1px solid #555; }
            QToolButton:disabled { color: #666; }
        """

        # ================= COLUMNA IZQUIERDA: EDITOR =================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        toolbar_left = QToolBar("Archivo")
        toolbar_left.setMovable(False)
        toolbar_left.setStyleSheet(toolbar_style)

        self.act_new = QAction("Nuevo", self)
        self.act_new.triggered.connect(self.new_file)
        
        self.act_open = QAction("Abrir", self)
        self.act_open.triggered.connect(self.open_file)
        
        self.act_save = QAction("Guardar", self)
        self.act_save.triggered.connect(self.save_file)
        self.act_save.setEnabled(False)
        
        self.act_save_as = QAction("Guardar como...", self)
        self.act_save_as.triggered.connect(self.save_file_as)
        
        self.act_extract = QAction("Extraer señales", self)
        self.act_extract.triggered.connect(self.extract_signals)

        toolbar_left.addAction(self.act_new)
        toolbar_left.addAction(self.act_open)
        toolbar_left.addAction(self.act_save)
        toolbar_left.addAction(self.act_save_as)
        toolbar_left.addSeparator()
        toolbar_left.addAction(self.act_extract)

        left_layout.addWidget(toolbar_left)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("-- Escribe tu código VHDL aquí...")
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14pt;
                border: none;
            }
        """)
        
        self.editor.setPlainText(
            "entity sumador is\n"
            "  port (\n"
            "    a   : in  std_logic_vector(3 downto 0);\n"
            "    b   : in  std_logic_vector(3 downto 0);\n"
            "    cin : in  std_logic;\n"
            "    s   : out std_logic_vector(3 downto 0);\n"
            "    cout: out std_logic\n"
            "  );\n"
            "end entity;\n"
            "\n"
            "architecture behavioral of sumador is\n"
            "begin\n"
            "  process(a, b, cin)\n"
            "  begin\n"
            "    suma <= conv_integer(a) + conv_integer(b) + conv_integer(cin);\n"
            "    s <= conv_std_logic_vector(suma, 4);\n"
            "    if suma > 15 then\n"
            "      cout <= '1';\n"
            "    else\n"
            "      cout <= '0';\n"
            "    end if;\n"
            "  end process;\n"
            "end architecture;\n"
        )
        self.editor.textChanged.connect(self.on_text_changed)
        left_layout.addWidget(self.editor)

        # ================= COLUMNA DERECHA: SIMULADOR =================
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.sim_splitter = QSplitter(Qt.Orientation.Vertical)
        self.sim_splitter.setStyleSheet("QSplitter::handle { background-color: #444; height: 4px; }")

        self.input_section = WaveformSection("Inputs", is_input=True)
        self.output_section = WaveformSection("Outputs", is_input=False)
        
        self.input_section.add_header_button("edit", "Editar", self.open_edit_dialog)
        self.input_section.add_header_button("simulate", "Simular", self.set_simulate_mode)
        self.output_section.add_header_button("edit_out", "Editar", self.open_output_edit_dialog)

        self.sim_splitter.addWidget(self.input_section)
        self.sim_splitter.addWidget(self.output_section)
        self.sim_splitter.setSizes([300, 300])

        right_layout.addWidget(self.sim_splitter, 1)

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([450, 950])

        self.setCentralWidget(main_splitter)

        self.is_modified = True

    # =================================================================
    #  LÓGICA DE ARCHIVOS
    # =================================================================
    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self.act_save.setEnabled(True)
            self.update_window_title()

    def update_window_title(self):
        filename = os.path.basename(self.current_file) if self.current_file else "Sin Título"
        mod_star = "*" if self.is_modified else ""
        self.setWindowTitle(f"VHDL Simulator - {filename}{mod_star}")

    def maybe_save_changes(self):
        if not self.is_modified:
            return True
            
        reply = QMessageBox.question(
            self, "Cambios sin guardar",
            "El documento ha sido modificado. ¿Desea guardar los cambios?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif reply == QMessageBox.StandardButton.Cancel:
            return False
        return True

    def new_file(self):
        if not self.maybe_save_changes():
            return
            
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self.act_save.setEnabled(False)
        self.update_window_title()
        
        self.history = {}
        self.inputs_data = []
        self.outputs_data = []
        self._refresh_waves()

    def open_file(self):
        if not self.maybe_save_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Archivo VHDL", "", "Archivos VHDL (*.vhd *.vhdl);;Todos los archivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.current_file = file_path
                self.is_modified = False
                self.act_save.setEnabled(False)
                self.update_window_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{e}")

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
            
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.is_modified = False
            self.act_save.setEnabled(False)
            self.update_window_title()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")
            return False

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Archivo VHDL", "", "Archivos VHDL (*.vhd);;Todos los archivos (*)"
        )
        
        if file_path:
            if not file_path.lower().endswith(('.vhd', '.vhdl')):
                file_path += '.vhd'
                
            self.current_file = file_path
            return self.save_file()
        return False

    def closeEvent(self, event):
        if self.maybe_save_changes():
            event.accept()
        else:
            event.ignore()

    # =================================================================
    #  LÓGICA DE SIMULACIÓN
    # =================================================================
    def open_edit_dialog(self):
        self.editor.setReadOnly(False)
        
        if not self.inputs_data:
            QMessageBox.warning(self, "Editar", "Primero debes extraer las señales del código VHDL.")
            return

        dialog = EditDialog(self.inputs_data, self.signal_configs, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.signal_configs = dialog.configs
            for sig in self.inputs_data:
                name = sig["name"]
                if name in self.signal_configs:
                    sig["radix"] = self.signal_configs[name].get("radix", "Binario")
            self.update_inputs_only()

    def open_output_edit_dialog(self):
        if not self.outputs_data:
            QMessageBox.warning(self, "Editar", "Primero debes extraer las señales del código VHDL.")
            return

        dialog = OutputEditDialog(self.outputs_data, self.output_configs, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.output_configs = dialog.configs
            for sig in self.outputs_data:
                name = sig["name"]
                if name in self.output_configs:
                    sig["radix"] = self.output_configs[name].get("radix", "Binario")
            self._refresh_waves()

    def set_simulate_mode(self):
        self.editor.setReadOnly(True)
        self.run_full_simulation()

    def update_inputs_only(self):
        if not self.inputs_data:
            return

        self.history = {}
        for sig in self.inputs_data + self.outputs_data:
            self.history[sig["name"]] = []

        for sig in self.inputs_data:
            name = sig["name"]
            cfg = self.signal_configs.get(name, {"type": "Arbitraria", "value": "0", "radix": "Binario"})
            points = []
            
            if cfg["type"] == "Arbitraria":
                val_str = cfg["value"]
                points.append((0.0, val_str))
                
            elif cfg["type"] == "Aleatoria":
                interval = cfg["interval"]
                t = 0.0
                while t <= self.max_sim_time:
                    if sig["is_bus"]:
                        val_str = bin(random.randint(0, 15))[2:].zfill(4)
                    else:
                        val_str = str(random.randint(0, 1))
                    points.append((t, val_str))
                    t += interval
                    
            elif cfg["type"] == "Reloj":
                interval = cfg["interval"]
                start_val = cfg["start"]
                
                t = 0.0
                if sig["is_bus"]:
                    val_a, val_b = "0000", "1111"
                else:
                    val_a, val_b = "0", "1"
                    
                if start_val == "1" or start_val == "1111":
                    curr_val, next_val = val_b, val_a
                else:
                    curr_val, next_val = val_a, val_b
                    
                while t <= self.max_sim_time:
                    points.append((t, curr_val))
                    t += interval
                    curr_val, next_val = next_val, curr_val

            self.history[name] = points

        for sig in self.outputs_data:
            name = sig["name"]
            val = "0000" if sig["is_bus"] else "0"
            self.history[name] = [(0.0, val)]

        self._refresh_waves()

    def run_full_simulation(self):
        if not self.inputs_data:
            return

        input_waveforms = {} 

        for sig in self.inputs_data:
            name = sig["name"]
            cfg = self.signal_configs.get(name, {"type": "Arbitraria", "value": "0", "radix": "Binario"})
            input_waveforms[name] = []
            
            if cfg["type"] == "Arbitraria":
                input_waveforms[name].append((0.0, cfg["value"]))
                
            elif cfg["type"] == "Aleatoria":
                interval = cfg["interval"]
                t = 0.0
                while t <= self.max_sim_time:
                    if sig["is_bus"]:
                        val_str = bin(random.randint(0, 15))[2:].zfill(4)
                    else:
                        val_str = str(random.randint(0, 1))
                    input_waveforms[name].append((t, val_str))
                    t += interval
                    
            elif cfg["type"] == "Reloj":
                interval = cfg["interval"]
                start_val = cfg["start"]
                
                t = 0.0
                if sig["is_bus"]:
                    val_a, val_b = "0000", "1111"
                else:
                    val_a, val_b = "0", "1"
                    
                if start_val == "1" or start_val == "1111":
                    curr_val, next_val = val_b, val_a
                else:
                    curr_val, next_val = val_a, val_b
                    
                while t <= self.max_sim_time:
                    input_waveforms[name].append((t, curr_val))
                    t += interval
                    curr_val, next_val = next_val, curr_val

        code = self.editor.toPlainText()
        sim_engine = VHDLSimulator(code)

        bus_widths = {sig["name"]: 4 for sig in self.inputs_data if sig["is_bus"]}

        output_waveforms = {sig["name"]: [] for sig in self.outputs_data}
        
        t = 0.0
        step = 1.0 
        while t <= self.max_sim_time:
            current_inputs = {}
            for sig in self.inputs_data:
                name = sig["name"]
                val_str = "0"
                for t_val, v in input_waveforms[name]:
                    if t_val <= t:
                        val_str = v
                    else:
                        break
                
                if sig["is_bus"]:
                    current_inputs[name] = int(val_str, 2)
                else:
                    current_inputs[name] = int(val_str)

            outs = sim_engine.evaluate(t, current_inputs, bus_widths)
            
            for sig in self.outputs_data:
                name = sig["name"]
                if name in outs:
                    val = outs[name]
                    if sig["is_bus"]:
                        val_str = str(val) if isinstance(val, str) else format(val, '04b')
                    else:
                        val_str = str(val)
                        
                    if not output_waveforms[name] or output_waveforms[name][-1][1] != val_str:
                        output_waveforms[name].append((t, val_str))
                        
            t += step

        for sig in self.outputs_data:
            name = sig["name"]
            if output_waveforms[name]:
                if output_waveforms[name][-1][0] < self.max_sim_time:
                    output_waveforms[name].append((self.max_sim_time, output_waveforms[name][-1][1]))
            else:
                output_waveforms[name] = [(0.0, "0000" if sig["is_bus"] else "0"), 
                                          (self.max_sim_time, "0000" if sig["is_bus"] else "0")]

        self.history = {}
        for sig in self.inputs_data:
            self.history[sig["name"]] = input_waveforms[sig["name"]]
            
        for sig in self.outputs_data:
            self.history[sig["name"]] = output_waveforms[sig["name"]]

        self._refresh_waves()

    def extract_signals(self):
        code = self.editor.toPlainText()
        code_no_comments = re.sub(r"--[^\n]*", "", code)

        start_match = re.search(r"\bport\s*\(", code_no_comments, flags=re.IGNORECASE)
        if not start_match:
            QMessageBox.warning(self, "Extraer señales", "No se encontró un bloque 'port ('.")
            return

        start_idx = start_match.end()
        depth = 1
        end_idx = start_idx
        for i in range(start_idx, len(code_no_comments)):
            if code_no_comments[i] == '(':
                depth += 1
            elif code_no_comments[i] == ')':
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break

        port_block = code_no_comments[start_idx:end_idx]
        parts = self._split_top_level(port_block, ';')

        self.history = {}
        self.inputs_data = []
        self.outputs_data = []
        self.signal_configs = {}
        self.output_configs = {}

        for part in parts:
            part = part.strip()
            if not part or ':' not in part:
                continue

            names_str, rest = part.split(':', 1)
            rest = rest.strip()

            dir_match = re.match(r"(in|out|inout)\b\s*(.*)", rest, re.IGNORECASE | re.DOTALL)
            if not dir_match:
                continue
                
            direction = dir_match.group(1).lower()
            vhdl_type = dir_match.group(2).strip()
            is_bus = "vector" in vhdl_type.lower() or "unsigned" in vhdl_type.lower() or "signed" in vhdl_type.lower()

            names = [n.strip() for n in names_str.split(',') if n.strip()]
            for name in names:
                self.history[name] = []
                sig = {
                    "name": name, "type": vhdl_type,
                    "direction": direction, "is_bus": is_bus,
                    "radix": "Binario"
                }
                if direction in ("in", "inout"):
                    self.inputs_data.append(sig)
                    self.signal_configs[name] = {"type": "Arbitraria", "value": "0000" if is_bus else "0", "radix": "Binario"}
                else:
                    self.outputs_data.append(sig)
                    self.output_configs[name] = {"radix": "Binario"}

        self.reset_simulation()
        self._refresh_waves()

    def reset_simulation(self):
        for sig in self.inputs_data + self.outputs_data:
            name = sig["name"]
            val = "0000" if sig["is_bus"] else "0"
            self.history[name] = [(0.0, val)]

    def _refresh_waves(self):
        px_per_ns = 2.0
        if self.max_sim_time > 0:
            max_width = self.input_section.scroll.viewport().width() - self.input_section.canvas.LABEL_W
            px_per_ns = max(0.5, min(10.0, max_width / (self.max_sim_time + 50)))
            
        self.input_section.set_data(self.inputs_data, self.history, self.max_sim_time, px_per_ns)
        self.output_section.set_data(self.outputs_data, self.history, self.max_sim_time, px_per_ns)

    @staticmethod
    def _split_top_level(text: str, sep: str):
        result, buf, depth = [], [], 0
        for ch in text:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            if ch == sep and depth == 0:
                result.append(''.join(buf))
                buf = []
            else:
                buf.append(ch)
        if buf:
            result.append(''.join(buf))
        return result