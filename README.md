# 🧮 Calculadora Científica Accesible

Calculadora científica con síntesis de voz y navegación por teclado, optimizada para personas con discapacidad visual.

## ♿ Características de Accesibilidad

- 🔊 **Síntesis de voz** en español para todas las acciones
- ⌨️ **Navegación completa con teclado** (Tab, flechas, Enter)
- 🎯 **Atajos de teclado** para funciones comunes (F1–F5)
- 📢 **Confirmaciones auditivas** de cada operación
- 📜 **Historial de cálculos** con lectura por voz
- 📝 **Modo de entrada de texto** libre

## 📦 Instalación

```bash
pip install ttkbootstrap sympy numpy matplotlib pyttsx3
```

## ▶️ Ejecución

```bash
python calculadora_accesible.py
```

## ⌨️ Atajos de Teclado

| Tecla | Función |
|-------|---------|
| `F1` | Ayuda vocal |
| `F2` | Leer pantalla |
| `F3` | Abrir historial |
| `F4` | Modo entrada de texto |
| `F5` | Activar / desactivar voz |
| `Tab` | Siguiente botón |
| `Shift+Tab` | Botón anterior |
| `↑ ↓ ← →` | Navegación direccional |
| `Enter` | Activar botón enfocado |
| `Escape` | Limpiar todo |
| `Backspace` | Borrar último carácter |
| `0–9`, `+`, `-`, `*`, `/` | Entrada directa |

## 🔬 Funciones Científicas

- Trigonometría: `sin`, `cos`, `tan` y sus inversas
- Logaritmos: `log` (base 10), `ln` (natural)
- Exponencial, raíz cuadrada, potencias
- Derivadas e integrales simbólicas (con SymPy)
- Modo estadístico: media, mediana, desviación estándar
- Graficador de funciones con derivada e integral

## 🖥️ Compatibilidad de Voz

| Sistema Operativo | Motor de voz |
|-------------------|-------------|
| Windows | PowerShell / SAPI |
| macOS | `say` (Monica, español) |
| Linux | `espeak -v es` |

## 📄 Licencia

MIT — libre uso y modificación.
