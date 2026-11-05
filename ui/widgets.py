from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath
from PyQt6.QtCore import Qt

class WaveformCanvas(QWidget):
    ROW_H = 24
    LABEL_W = 150
    TIME_H = 20

    def __init__(self, is_input=True, parent=None):
        super().__init__(parent)
        self.is_input = is_input
        self.signals = []
        self.history = {}
        self.max_time = 600.0
        self.px_per_ns = 1.0
        self.setStyleSheet("background: #1e1e1e;")
        self.setMouseTracking(True)

    def set_data(self, signals, history, max_time, px_per_ns):
        self.signals = signals
        self.history = history
        self.max_time = max_time
        self.px_per_ns = px_per_ns
        needed_h = self.TIME_H + (len(self.signals) * self.ROW_H)
        self.setMinimumHeight(needed_h if needed_h > 0 else 100)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        for i, sig in enumerate(self.signals):
            y = self.TIME_H + (i * self.ROW_H)
            self._draw_row(painter, sig, y)

        painter.fillRect(0, 0, self.width(), self.TIME_H, QColor("#2d2d2d"))
        painter.setPen(QPen(QColor("#444444"), 1))
        painter.drawLine(0, self.TIME_H - 1, self.width(), self.TIME_H - 1)
        
        painter.setPen(QColor("#888"))
        painter.setFont(QFont("Consolas", 10)) # Aumentado de 8 a 10
        painter.drawText(10, 14, "Time (ns)")

        t = 0
        while t <= self.max_time:
            x = self.LABEL_W + t * self.px_per_ns
            painter.setPen(QPen(QColor("#555555"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(int(x), 0, int(x), self.height())
            if t % 100 == 0:
                painter.setPen(QColor("#aaa"))
                painter.drawText(int(x) + 2, 14, str(int(t)))
            t += 100

        if self.max_time > 0:
            cursor_x = self.LABEL_W + self.max_time * self.px_per_ns
            painter.setPen(QPen(QColor("#ffffff"), 1, Qt.PenStyle.SolidLine))
            painter.drawLine(int(cursor_x), 0, int(cursor_x), self.height())

    def _draw_row(self, painter, sig, y):
        name = sig["name"]
        is_bus = sig["is_bus"]
        radix = sig.get("radix", "Binario")
        
        painter.fillRect(0, y, self.width(), self.ROW_H, QColor("#1e1e1e"))
        painter.fillRect(0, y, self.LABEL_W, self.ROW_H, QColor("#2d2d2d"))
        
        painter.setPen(QColor("#dddddd"))
        painter.setFont(QFont("Consolas", 11)) # Aumentado de 9 a 11
        painter.drawText(10, y + 16, name)

        painter.setPen(QPen(QColor("#444444"), 1))
        painter.drawLine(self.LABEL_W, y, self.LABEL_W, y + self.ROW_H)
        painter.drawLine(0, y + self.ROW_H - 1, self.width(), y + self.ROW_H - 1)

        painter.save()
        painter.setClipRect(self.LABEL_W, y, self.width() - self.LABEL_W, self.ROW_H)
        painter.translate(self.LABEL_W, y)

        hist = self.history.get(name, [])
        if not hist:
            painter.restore()
            return

        y_hi = 4
        y_lo = self.ROW_H - 4
        wave_color = QColor("#00ff7f")

        if not is_bus:
            painter.setPen(QPen(wave_color, 1.5))
            path = QPainterPath()
            t0, v0 = hist[0]
            path.moveTo(t0 * self.px_per_ns, y_hi if str(v0).strip() == "1" else y_lo)
            
            prev_y = path.currentPosition().y()
            for i in range(1, len(hist)):
                t_val, v = hist[i]
                x = t_val * self.px_per_ns
                y_val = y_hi if str(v).strip() == "1" else y_lo
                path.lineTo(x, prev_y)
                path.lineTo(x, y_val)
                prev_y = y_val
            path.lineTo(self.max_time * self.px_per_ns, prev_y)
            painter.drawPath(path)
        else:
            painter.setPen(QPen(wave_color, 1))
            y_mid = self.ROW_H / 2
            for i in range(len(hist)):
                t_val, v = hist[i]
                x_start = t_val * self.px_per_ns
                
                if i + 1 < len(hist):
                    x_end = hist[i + 1][0] * self.px_per_ns
                else:
                    x_end = self.max_time * self.px_per_ns
                
                if x_end - x_start < 4:
                    continue
                    
                path = QPainterPath()
                path.moveTo(x_start, y_mid)
                path.lineTo(x_start + 4, y_hi)
                path.lineTo(x_end - 4, y_hi)
                path.lineTo(x_end, y_mid)
                path.lineTo(x_end - 4, y_lo)
                path.lineTo(x_start + 4, y_lo)
                path.closeSubpath()
                painter.drawPath(path)
                
                display_text = str(v)
                if radix == "Decimal":
                    try: display_text = str(int(str(v), 2))
                    except: pass
                elif radix == "Hexadecimal":
                    try: display_text = format(int(str(v), 2), 'X')
                    except: pass
                
                if (x_end - x_start) > len(display_text) * 6 + 6:
                    painter.setPen(QPen(wave_color))
                    painter.setFont(QFont("Consolas", 10)) # Aumentado de 8 a 10
                    painter.drawText(int(x_start + 4), int(y_mid + 4), display_text)
                    painter.setPen(QPen(wave_color, 1))

        painter.restore()

class WaveformSection(QWidget):
    def __init__(self, title, is_input=True, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setStyleSheet("background: #333; border-bottom: 1px solid #444;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(6)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #ddd; font-weight: bold; font-family: 'Segoe UI'; font-size: 14px; border: none;") # Aumentado a 14px
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        self.buttons = {}
        self.header_layout = header_layout
        
        self.layout.addWidget(header_widget)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: #1e1e1e; border: none; }")
        
        self.canvas = WaveformCanvas(is_input)
        self.scroll.setWidget(self.canvas)
        
        self.layout.addWidget(self.scroll)

    def add_header_button(self, name, text, callback):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton { background: #444; color: #ddd; padding: 2px 8px; border: none; border-radius: 2px; font-size: 13px; } /* Aumentado a 13px */
            QPushButton:hover { background: #555; }
        """)
        btn.clicked.connect(callback)
        self.buttons[name] = btn
        self.header_layout.addWidget(btn)
        return btn

    def set_data(self, signals, history, max_time, px_per_ns):
        self.canvas.set_data(signals, history, max_time, px_per_ns)