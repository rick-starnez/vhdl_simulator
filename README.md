# VHDL Simulator 🚀

Un simulador y editor gráfico de VHDL desarrollado en Python con PyQt6. 
Permite extraer señales de una entidad, configurar sus entradas (arbitrarias, aleatorias o de reloj) y visualizar los resultados en un lienzo de formas de onda al estilo ModelSim.

## Características
- Editor de código VHDL integrado.
- Extracción automática de puertos (entradas y salidas).
- Motor de simulación paso a paso (Time-Step) con soporte para procesos (`process`).
- Configuración de Radix (Binario, Decimal, Hexadecimal) para visualización.
- Lienzo gráfico con zoom, rejilla y líneas de tiempo.
- Manejo de archivos completo (Nuevo, Abrir, Guardar, Guardar como).

## Requisitos
- Python 3.9 o superior.
- PyQt6.

## Instalación
1. Clona este repositorio:
   git clone https://github.com/TU_USUARIO/vhdl_simulator.git
   cd vhdl_simulator

2. Crea un entorno virtual e instala las dependencias:
    python -m venv venv
    source venv/bin/activate  # En Mac/Linux
    # venv\Scripts\activate   # En Windows
    pip install -r requirements.txt

3. Ejecuta la aplicación:
    python main.py

### 4. Sube el proyecto a GitHub
Si aún no tienes el repositorio creado en GitHub, créalo (sin inicializar con README para evitar conflictos). Luego, en tu terminal, ejecuta:

```bash
git init
git add .
git commit -m "Primera versión del simulador VHDL con PyQt6"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/vhdl_simulator.git
git push -u origin main