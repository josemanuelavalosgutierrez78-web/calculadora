"""
Calculadora Científica ACCESIBLE - Optimizada para Discapacidad Visual
=======================================================================
Autor: Asistente IA
Fecha: 2025
Descripción: Calculadora científica completamente accesible con síntesis de voz,
             navegación optimizada, atajos de teclado y feedback auditivo completo
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import statistics
import math
import subprocess
import platform
import threading
import queue


class CalculadoraAccesible:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Científica Accesible")
        self.root.geometry("950x800")
        self.root.resizable(False, False)
        self.x = sp.Symbol('x')
        self.buffer = ""
        self.modo_actual = "DEG"
        self.historial = []
        self.indice_historial = -1
        self.style = ttkb.Style(theme="darkly")
        self.voz_activada = True
        self.sistema_operativo = platform.system()
        self.cola_voz = queue.Queue()
        self.hilo_voz_activo = True
        self.todos_botones = []
        self.indice_foco = 0
        self.matriz_botones = []
        self.ultimo_resultado = 0
        self.ventana_stats = None
        self.ventana_grafico = None
        self.ventana_historial = None
        self.crear_interfaz()
        self.configurar_atajos()
        self.iniciar_hilo_voz()
        self.hablar("Calculadora científica accesible iniciada. Presione F1 para ayuda", prioridad=True)

    def iniciar_hilo_voz(self):
        def procesar_cola():
            while self.hilo_voz_activo:
                try:
                    texto = self.cola_voz.get(timeout=0.1)
                    self._hablar_sistema(texto)
                except queue.Empty:
                    continue
        hilo = threading.Thread(target=procesar_cola, daemon=True)
        hilo.start()

    def crear_interfaz(self):
        main_frame = tk.Frame(self.root, bg="#1a2332", padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=YES)
        barra_estado = tk.Frame(main_frame, bg="#2a3a4a", relief=RIDGE, bd=2, padx=10, pady=5)
        barra_estado.pack(fill=X, pady=(0, 10))
        tk.Label(barra_estado, text="♿ MODO ACCESIBLE", font=("Arial", 10, "bold"), bg="#2a3a4a", fg="#00ff00").pack(side=LEFT, padx=5)
        self.label_modo = tk.Label(barra_estado, text="DEG", font=("Arial", 10, "bold"), bg="#2a3a4a", fg="yellow")
        self.label_modo.pack(side=LEFT, padx=10)
        self.label_voz = tk.Label(barra_estado, text="🔊 VOZ ON", font=("Arial", 10, "bold"), bg="#2a3a4a", fg="#00ff00")
        self.label_voz.pack(side=RIGHT, padx=5)
        lcd_frame = tk.Frame(main_frame, bg="#3a4a5a", padx=10, pady=10, relief=RIDGE, bd=3)
        lcd_frame.pack(fill=X, pady=(0, 10))
        self.lcd_superior = tk.Label(lcd_frame, text="", font=("Courier New", 14, "bold"), bg="#a8b8a0", fg="#1a3a1a", height=2, anchor=E, padx=10)
        self.lcd_superior.pack(fill=X, pady=(0, 5))
        self.lcd_principal = tk.Label(lcd_frame, text="0", font=("Courier New", 28, "bold"), bg="#a8b8a0", fg="#000000", height=2, anchor=E, padx=10, relief=SUNKEN, bd=2)
        self.lcd_principal.pack(fill=X)
        self.label_foco = tk.Label(lcd_frame, text="Posición: Inicio", font=("Arial", 9), bg="#3a4a5a", fg="white")
        self.label_foco.pack(fill=X, pady=(5, 0))
        acceso_frame = tk.Frame(main_frame, bg="#1a2332")
        acceso_frame.pack(fill=X, pady=(0, 10))
        botones_acceso = [
            ("F1\nAYUDA", self.mostrar_ayuda, "#2a6a2a"),
            ("F2\nLEER", self.leer_pantalla, "#2a5a6a"),
            ("F3\nHISTORIAL", self.abrir_historial, "#5a4a2a"),
            ("F4\nTEXTO", self.modo_entrada_texto, "#4a2a6a"),
            ("F5\nVOZ", self.toggle_voz, "#6a2a2a")
        ]
        for texto, comando, color in botones_acceso:
            btn = tk.Button(acceso_frame, text=texto, command=comando, font=("Arial", 9, "bold"), bg=color, fg="white", relief=RAISED, bd=3, cursor="hand2", width=10, height=3)
            btn.pack(side=LEFT, padx=3, expand=YES, fill=BOTH)
        botones_frame = tk.Frame(main_frame, bg="#1a2332")
        botones_frame.pack(fill=BOTH, expand=YES)
        izq_frame = tk.Frame(botones_frame, bg="#1a2332")
        izq_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))
        der_frame = tk.Frame(botones_frame, bg="#1a2332")
        der_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        funciones_cientificas = [
            [("2nd", self.segunda_funcion, "#4a5a6a"), ("MODE", self.cambiar_modo, "#4a5a6a"), ("DEL", self.borrar_ultimo, "#8a3a3a"), ("AC", self.limpiar_todo, "#aa4a4a")],
            [("x²", lambda: self.insertar("**2"), "#2a4a5a"), ("√", lambda: self.insertar("sqrt("), "#2a4a5a"), ("^", lambda: self.insertar("**"), "#2a4a5a"), ("log", lambda: self.insertar("log("), "#2a4a5a")],
            [("ln", lambda: self.insertar("ln("), "#2a4a5a"), ("e^x", lambda: self.insertar("exp("), "#2a4a5a"), ("(", lambda: self.insertar("("), "#2a4a5a"), (")", lambda: self.insertar(")"), "#2a4a5a")],
            [("sin", lambda: self.insertar("sin("), "#1a3a4a"), ("cos", lambda: self.insertar("cos("), "#1a3a4a"), ("tan", lambda: self.insertar("tan("), "#1a3a4a"), ("π", lambda: self.insertar("pi"), "#2a4a5a")],
            [("sin⁻¹", lambda: self.insertar("asin("), "#1a3a4a"), ("cos⁻¹", lambda: self.insertar("acos("), "#1a3a4a"), ("tan⁻¹", lambda: self.insertar("atan("), "#1a3a4a"), ("x", lambda: self.insertar("x"), "#2a4a5a")],
            [("d/dx", self.calcular_derivada, "#3a5a3a"), ("∫dx", self.calcular_integral, "#3a5a3a"), ("STATS", self.abrir_stats, "#5a4a3a"), ("GRAPH", self.abrir_grafico, "#3a4a5a")]
        ]
        for fila in funciones_cientificas:
            f = tk.Frame(izq_frame, bg="#1a2332")
            f.pack(fill=X, pady=2)
            fila_botones = []
            for texto, comando, bg in fila:
                btn = tk.Button(f, text=texto, command=comando, font=("Arial", 11, "bold"), bg=bg, fg="white", activebackground=self.color_mas_claro(bg), relief=RAISED, bd=4, width=7, height=2, cursor="hand2")
                btn.pack(side=LEFT, padx=2, expand=YES, fill=BOTH)
                self.todos_botones.append(btn)
                fila_botones.append(btn)
            self.matriz_botones.append(fila_botones)
        botones_numericos = [
            [("7", lambda: self.insertar("7"), "#3a4a5a"), ("8", lambda: self.insertar("8"), "#3a4a5a"), ("9", lambda: self.insertar("9"), "#3a4a5a"), ("÷", lambda: self.insertar("/"), "#5a4a3a")],
            [("4", lambda: self.insertar("4"), "#3a4a5a"), ("5", lambda: self.insertar("5"), "#3a4a5a"), ("6", lambda: self.insertar("6"), "#3a4a5a"), ("×", lambda: self.insertar("*"), "#5a4a3a")],
            [("1", lambda: self.insertar("1"), "#3a4a5a"), ("2", lambda: self.insertar("2"), "#3a4a5a"), ("3", lambda: self.insertar("3"), "#3a4a5a"), ("-", lambda: self.insertar("-"), "#5a4a3a")],
            [("0", lambda: self.insertar("0"), "#3a4a5a"), (".", lambda: self.insertar("."), "#3a4a5a"), ("EXP", lambda: self.insertar("E"), "#3a4a5a"), ("+", lambda: self.insertar("+"), "#5a4a3a")],
            [("ANS", self.usar_resultado_anterior, "#4a5a4a"), ("=", self.calcular, "#2a6a2a")]
        ]
        for fila in botones_numericos:
            f = tk.Frame(der_frame, bg="#1a2332")
            f.pack(fill=BOTH, expand=YES, pady=2)
            fila_botones = []
            for item in fila:
                texto, comando, bg = item
                ancho = 25 if texto == "=" else 8
                btn = tk.Button(f, text=texto, command=comando,
                    font=("Arial", 18, "bold") if texto == "=" else (("Arial", 16, "bold") if texto.isdigit() or texto == "." else ("Arial", 12, "bold")),
                    bg=bg, fg="white", activebackground=self.color_mas_claro(bg), relief=RAISED, bd=4, width=ancho, height=2, cursor="hand2")
                btn.pack(side=LEFT, padx=2, expand=YES, fill=BOTH)
                self.todos_botones.append(btn)
                fila_botones.append(btn)
            self.matriz_botones.append(fila_botones)

    def configurar_atajos(self):
        self.root.bind('<Tab>', self.siguiente_boton)
        self.root.bind('<Shift-Tab>', self.boton_anterior)
        self.root.bind('<Return>', self.activar_boton_actual)
        self.root.bind('<KP_Enter>', self.activar_boton_actual)
        self.root.bind('<Up>', self.navegar_arriba)
        self.root.bind('<Down>', self.navegar_abajo)
        self.root.bind('<Left>', self.navegar_izquierda)
        self.root.bind('<Right>', self.navegar_derecha)
        self.root.bind('<F1>', lambda e: self.mostrar_ayuda())
        self.root.bind('<F2>', lambda e: self.leer_pantalla())
        self.root.bind('<F3>', lambda e: self.abrir_historial())
        self.root.bind('<F4>', lambda e: self.modo_entrada_texto())
        self.root.bind('<F5>', lambda e: self.toggle_voz())
        self.root.bind('<Escape>', lambda e: self.limpiar_todo())
        self.root.bind('<BackSpace>', lambda e: self.borrar_ultimo())
        self.root.bind('<Delete>', lambda e: self.borrar_ultimo())
        for i in range(10):
            self.root.bind(str(i), lambda e, n=i: self.insertar(str(n)))
        self.root.bind('+', lambda e: self.insertar("+"))
        self.root.bind('-', lambda e: self.insertar("-"))
        self.root.bind('*', lambda e: self.insertar("*"))
        self.root.bind('/', lambda e: self.insertar("/"))
        self.root.bind('.', lambda e: self.insertar("."))
        self.root.bind('(', lambda e: self.insertar("("))
        self.root.bind(')', lambda e: self.insertar(")"))
        self.root.bind('=', lambda e: self.calcular())

    def color_mas_claro(self, color_hex):
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        return f'#{min(255,int(r*1.3)):02x}{min(255,int(g*1.3)):02x}{min(255,int(b*1.3)):02x}'

    def hablar(self, texto, prioridad=False):
        if not self.voz_activada:
            return
        if prioridad:
            while not self.cola_voz.empty():
                try: self.cola_voz.get_nowait()
                except: break
        self.cola_voz.put(texto)

    def _hablar_sistema(self, texto):
        try:
            if self.sistema_operativo == "Windows":
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = 4; $s.Speak(\'{texto}\')"'
                subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
            elif self.sistema_operativo == "Darwin":
                subprocess.run(['say', '-v', 'Monica', '-r', '300', texto], capture_output=True, timeout=2)
            else:
                subprocess.run(['espeak', '-v', 'es', '-s', '200', texto], capture_output=True, timeout=2)
        except: pass

    def toggle_voz(self):
        self.voz_activada = not self.voz_activada
        if self.voz_activada:
            self.label_voz.config(text="🔊 VOZ ON", fg="#00ff00")
            self.hablar("Voz activada", prioridad=True)
        else:
            self.label_voz.config(text="🔇 VOZ OFF", fg="red")

    def siguiente_boton(self, event=None):
        if not self.todos_botones: return "break"
        while not self.cola_voz.empty():
            try: self.cola_voz.get_nowait()
            except: break
        if self.indice_foco < len(self.todos_botones):
            self.todos_botones[self.indice_foco].config(relief=RAISED, bd=4)
        self.indice_foco = (self.indice_foco + 1) % len(self.todos_botones)
        btn = self.todos_botones[self.indice_foco]
        btn.config(relief=SUNKEN, bd=2)
        btn.focus_set()
        self.label_foco.config(text=f"Botón {self.indice_foco+1} de {len(self.todos_botones)}")
        self.leer_boton_rapido(btn.cget("text"))
        return "break"

    def boton_anterior(self, event=None):
        if not self.todos_botones: return "break"
        while not self.cola_voz.empty():
            try: self.cola_voz.get_nowait()
            except: break
        if self.indice_foco < len(self.todos_botones):
            self.todos_botones[self.indice_foco].config(relief=RAISED, bd=4)
        self.indice_foco = (self.indice_foco - 1) % len(self.todos_botones)
        btn = self.todos_botones[self.indice_foco]
        btn.config(relief=SUNKEN, bd=2)
        btn.focus_set()
        self.label_foco.config(text=f"Botón {self.indice_foco+1} de {len(self.todos_botones)}")
        self.leer_boton_rapido(btn.cget("text"))
        return "break"

    def activar_boton_actual(self, event=None):
        if self.todos_botones and self.indice_foco < len(self.todos_botones):
            self.todos_botones[self.indice_foco].invoke()
        return "break"

    def navegar_arriba(self, event=None):
        while not self.cola_voz.empty():
            try: self.cola_voz.get_nowait()
            except: break
        self.boton_anterior(); return "break"

    def navegar_abajo(self, event=None):
        while not self.cola_voz.empty():
            try: self.cola_voz.get_nowait()
            except: break
        self.siguiente_boton(); return "break"

    def navegar_izquierda(self, event=None):
        while not self.cola_voz.empty():
            try: self.cola_voz.get_nowait()
            except: break
        self.boton_anterior(); return "break"

    def navegar_derecha(self, event=None):
        while not self.cola_voz.empty():
            try: self.cola_voz.get_nowait()
            except: break
        self.siguiente_boton(); return "break"

    def leer_boton_rapido(self, texto):
        p = {"2nd":"segunda","MODE":"modo","DEL":"borrar","AC":"limpiar","x²":"cuadrado","√":"raíz","^":"potencia","log":"log","ln":"ene natural","e^x":"exponencial","(":"abre",")":"cierra","sin":"seno","cos":"coseno","tan":"tangente","π":"pi","sin⁻¹":"arco seno","cos⁻¹":"arco coseno","tan⁻¹":"arco tangente","x":"equis","d/dx":"derivada","∫dx":"integral","STATS":"estadísticas","GRAPH":"gráfico","0":"cero","1":"uno","2":"dos","3":"tres","4":"cuatro","5":"cinco","6":"seis","7":"siete","8":"ocho","9":"nueve","÷":"dividir","×":"por","-":"menos","+":"más",".":"punto","EXP":"exponencial","ANS":"anterior","=":"igual"}
        self.hablar(p.get(texto, texto), prioridad=True)

    def insertar(self, valor):
        self.buffer += str(valor)
        self.actualizar_lcd()
        p = {"+":"más","-":"menos","*":"por","/":"dividido","**":"elevado a","sqrt(":"raíz cuadrada de","sin(":"seno de","cos(":"coseno de","tan(":"tangente de","log(":"logaritmo de","ln(":"logaritmo natural de","exp(":"exponencial de","pi":"pi","x":"equis","(":"abre paréntesis",")":"cierra paréntesis",".":"punto","E":"por diez elevado a","asin(":"arco seno de","acos(":"arco coseno de","atan(":"arco tangente de","**2":"al cuadrado"}
        self.hablar(p.get(str(valor), str(valor)))

    def actualizar_lcd(self):
        self.lcd_superior.config(text=self.buffer if self.buffer else "")

    def limpiar_todo(self):
        self.buffer = ""
        self.lcd_principal.config(text="0")
        self.lcd_superior.config(text="")
        self.hablar("Calculadora limpiada", prioridad=True)

    def borrar_ultimo(self):
        if self.buffer:
            c = self.buffer[-1]
            self.buffer = self.buffer[:-1]
            self.actualizar_lcd()
            self.hablar(f"Borrado {c}")
        else:
            self.hablar("No hay nada que borrar")

    def segunda_funcion(self):
        self.hablar("Segunda función, en desarrollo")

    def cambiar_modo(self):
        self.modo_actual = "RAD" if self.modo_actual == "DEG" else "DEG"
        self.label_modo.config(text=self.modo_actual)
        self.hablar("Modo " + ("radianes" if self.modo_actual=="RAD" else "grados"), prioridad=True)

    def calcular(self):
        if not self.buffer:
            self.hablar("No hay expresión para calcular"); return
        try:
            expr_str = self.buffer.replace("pi", str(math.pi)).replace("E","e")
            self.historial.append(f"{self.buffer} = ")
            if 'x' in expr_str:
                expr = sp.sympify(expr_str)
                resultado = str(expr)
                self.lcd_principal.config(text=resultado[:25])
                self.historial[-1] += resultado
                self.hablar(f"Expresión simbólica: {resultado}", prioridad=True)
            else:
                expr = sp.sympify(expr_str)
                resultado = float(expr.evalf())
                self.ultimo_resultado = resultado
                txt = f"{resultado:.6e}" if abs(resultado)<0.0001 or abs(resultado)>9999999 else f"{resultado:.8g}"
                self.lcd_principal.config(text=txt)
                self.historial[-1] += txt
                r_str = f"{resultado:.4f}".rstrip('0').rstrip('.')
                self.hablar(f"El resultado es {r_str}", prioridad=True)
            if len(self.historial) > 50:
                self.historial = self.historial[-50:]
        except Exception as e:
            self.lcd_principal.config(text="ERROR")
            self.hablar(f"Error: {str(e)}", prioridad=True)

    def usar_resultado_anterior(self):
        if self.ultimo_resultado != 0:
            self.insertar(str(self.ultimo_resultado))
        else:
            self.hablar("No hay resultado anterior")

    def calcular_derivada(self):
        if not self.buffer:
            self.hablar("No hay expresión para derivar"); return
        try:
            d = sp.diff(sp.sympify(self.buffer), self.x)
            self.buffer = str(d)
            self.actualizar_lcd()
            self.lcd_principal.config(text=f"d/dx: {str(d)[:15]}")
            self.hablar(f"La derivada es: {str(d)}", prioridad=True)
        except Exception as e:
            self.lcd_principal.config(text="ERROR")
            self.hablar(f"Error derivada: {str(e)}", prioridad=True)

    def calcular_integral(self):
        if not self.buffer:
            self.hablar("No hay expresión para integrar"); return
        try:
            i = sp.integrate(sp.sympify(self.buffer), self.x)
            self.buffer = str(i)
            self.actualizar_lcd()
            self.lcd_principal.config(text=f"∫: {str(i)[:15]}")
            self.hablar(f"La integral es: {str(i)}", prioridad=True)
        except Exception as e:
            self.lcd_principal.config(text="ERROR")
            self.hablar(f"Error integral: {str(e)}", prioridad=True)

    def mostrar_ayuda(self):
        ayuda = "Ayuda Calculadora Accesible.\nTab: siguiente botón. Shift+Tab: anterior.\nFlechas: navegar. Enter: activar.\nF1: ayuda. F2: leer pantalla. F3: historial.\nF4: entrada texto. F5: voz. Escape: limpiar."
        self.hablar(ayuda, prioridad=True)
        messagebox.showinfo("Ayuda - Calculadora Accesible", ayuda)

    def leer_pantalla(self):
        expr = self.buffer if self.buffer else "vacía"
        res = self.lcd_principal.cget("text")
        self.hablar(f"Modo {self.modo_actual}. Expresión: {expr}. Resultado: {res}", prioridad=True)

    def modo_entrada_texto(self):
        v = tk.Toplevel(self.root)
        v.title("Entrada de Texto")
        v.geometry("500x200")
        v.configure(bg="#2a3a4a")
        tk.Label(v, text="Escriba su expresión matemática:", font=("Arial",12), bg="#2a3a4a", fg="white").pack(pady=10)
        e = tk.Entry(v, font=("Courier New",16), bg="white", fg="black", width=40)
        e.pack(pady=5, padx=20)
        e.insert(0, self.buffer)
        e.focus_set()
        def aceptar():
            self.buffer = e.get()
            self.actualizar_lcd()
            self.hablar(f"Expresión: {self.buffer}")
            v.destroy()
        def cancelar():
            self.hablar("Cancelado"); v.destroy()
        f = tk.Frame(v, bg="#2a3a4a"); f.pack(pady=10)
        tk.Button(f, text="ACEPTAR (Enter)", command=aceptar, font=("Arial",11,"bold"), bg="#2a6a2a", fg="white", width=14, height=2).pack(side=LEFT, padx=8)
        tk.Button(f, text="CANCELAR (Esc)", command=cancelar, font=("Arial",11,"bold"), bg="#6a2a2a", fg="white", width=14, height=2).pack(side=LEFT, padx=8)
        e.bind('<Return>', lambda ev: aceptar())
        e.bind('<Escape>', lambda ev: cancelar())
        self.hablar("Modo texto abierto. Escriba y presione Enter")

    def abrir_historial(self):
        if self.ventana_historial and self.ventana_historial.winfo_exists():
            self.ventana_historial.lift(); return
        self.ventana_historial = tk.Toplevel(self.root)
        self.ventana_historial.title("Historial")
        self.ventana_historial.geometry("600x500")
        self.ventana_historial.configure(bg="#2a3a4a")
        fr = tk.Frame(self.ventana_historial, bg="#2a3a4a", padx=20, pady=20)
        fr.pack(fill=BOTH, expand=YES)
        tk.Label(fr, text="📜 HISTORIAL DE CÁLCULOS", font=("Arial",16,"bold"), bg="#2a3a4a", fg="white").pack(pady=(0,10))
        self.text_historial = scrolledtext.ScrolledText(fr, height=20, font=("Consolas",11), bg="#1a2a3a", fg="#00ff00", wrap=tk.WORD)
        self.text_historial.pack(fill=BOTH, expand=YES, pady=10)
        if self.historial:
            for i, e in enumerate(self.historial, 1):
                self.text_historial.insert(tk.END, f"{i}. {e}\n\n")
            self.hablar(f"Historial: {len(self.historial)} cálculos")
        else:
            self.text_historial.insert(tk.END, "No hay cálculos aún.\n")
            self.hablar("Historial vacío")
        bf = tk.Frame(fr, bg="#2a3a4a"); bf.pack(pady=10)
        tk.Button(bf, text="LEER HISTORIAL", command=self.leer_historial, font=("Arial",11,"bold"), bg="#2a5a6a", fg="white", width=18, height=2).pack(side=LEFT, padx=5)
        tk.Button(bf, text="LIMPIAR HISTORIAL", command=self.limpiar_historial, font=("Arial",11,"bold"), bg="#6a2a2a", fg="white", width=18, height=2).pack(side=LEFT, padx=5)

    def leer_historial(self):
        if not self.historial:
            self.hablar("Historial vacío"); return
        texto = f"Historial de {len(self.historial)} cálculos. "
        for i, e in enumerate(self.historial[-5:], 1):
            texto += f"Cálculo {i}: {e}. "
        self.hablar(texto, prioridad=True)

    def limpiar_historial(self):
        self.historial.clear()
        if hasattr(self, 'text_historial') and self.text_historial:
            self.text_historial.delete(1.0, tk.END)
            self.text_historial.insert(1.0, "Historial limpiado.\n")
        self.hablar("Historial limpiado", prioridad=True)

    def abrir_stats(self):
        if self.ventana_stats and self.ventana_stats.winfo_exists():
            self.ventana_stats.lift(); return
        self.hablar("Modo estadístico", prioridad=True)
        self.ventana_stats = tk.Toplevel(self.root)
        self.ventana_stats.title("Estadísticas")
        self.ventana_stats.geometry("600x550")
        self.ventana_stats.configure(bg="#2a3a4a")
        fr = tk.Frame(self.ventana_stats, bg="#2a3a4a", padx=20, pady=20)
        fr.pack(fill=BOTH, expand=YES)
        tk.Label(fr, text="📊 MODO ESTADÍSTICO", font=("Arial",16,"bold"), bg="#2a3a4a", fg="white").pack(pady=(0,10))
        tk.Label(fr, text="Datos separados por comas:", font=("Arial",12), bg="#2a3a4a", fg="white").pack(anchor=W)
        self.entry_stats = scrolledtext.ScrolledText(fr, height=6, font=("Consolas",12), bg="#3a4a5a", fg="white", insertbackground="white", wrap=tk.WORD)
        self.entry_stats.pack(fill=BOTH, pady=10)
        self.entry_stats.insert(1.0, "1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
        bf = tk.Frame(fr, bg="#2a3a4a"); bf.pack(pady=10)
        tk.Button(bf, text="CALCULAR", command=self.calcular_estadisticas, font=("Arial",12,"bold"), bg="#2a6a2a", fg="white", width=18, height=2).pack(side=LEFT, padx=5)
        tk.Button(bf, text="LEER RESULTADOS", command=self.leer_estadisticas, font=("Arial",12,"bold"), bg="#2a5a6a", fg="white", width=18, height=2).pack(side=LEFT, padx=5)
        self.text_resultado_stats = scrolledtext.ScrolledText(fr, height=14, font=("Consolas",11), bg="#1a2a3a", fg="#00ff00", wrap=tk.WORD)
        self.text_resultado_stats.pack(fill=BOTH, expand=YES)
        self.stats_resultado = None

    def calcular_estadisticas(self):
        try:
            datos = [float(x.strip()) for x in self.entry_stats.get(1.0, tk.END).split(',') if x.strip()]
            if not datos:
                self.hablar("No hay datos válidos"); return
            media = statistics.mean(datos)
            mediana = statistics.median(datos)
            varianza = statistics.variance(datos) if len(datos)>1 else 0
            desv = statistics.stdev(datos) if len(datos)>1 else 0
            self.stats_resultado = {'n':len(datos),'suma':sum(datos),'media':media,'mediana':mediana,'varianza':varianza,'desv_std':desv,'minimo':min(datos),'maximo':max(datos),'rango':max(datos)-min(datos)}
            r = self.stats_resultado
            res = f"{'='*50}\n📊 RESULTADOS ESTADÍSTICOS\n{'='*50}\nn:                 {r['n']}\nΣx:                {r['suma']:.4f}\nMedia:             {r['media']:.6f}\nMediana:           {r['mediana']:.6f}\nVarianza:          {r['varianza']:.6f}\nDesv. estándar:    {r['desv_std']:.6f}\nMínimo:            {r['minimo']:.4f}\nMáximo:            {r['maximo']:.4f}\nRango:             {r['rango']:.4f}\n{'='*50}\n"
            self.text_resultado_stats.delete(1.0, tk.END)
            self.text_resultado_stats.insert(1.0, res)
            self.hablar(f"Calculado. {len(datos)} datos. Media: {media:.2f}. Desviación: {desv:.2f}", prioridad=True)
        except Exception as e:
            self.hablar(f"Error: {str(e)}")

    def leer_estadisticas(self):
        if not self.stats_resultado:
            self.hablar("Calcule primero las estadísticas"); return
        r = self.stats_resultado
        self.hablar(f"Datos: {r['n']}. Media: {r['media']:.2f}. Mediana: {r['mediana']:.2f}. Desviación: {r['desv_std']:.2f}. Mínimo: {r['minimo']:.2f}. Máximo: {r['maximo']:.2f}.", prioridad=True)

    def abrir_grafico(self):
        if self.ventana_grafico and self.ventana_grafico.winfo_exists():
            self.ventana_grafico.lift(); return
        self.hablar("Modo gráfico", prioridad=True)
        self.ventana_grafico = tk.Toplevel(self.root)
        self.ventana_grafico.title("Graficador")
        self.ventana_grafico.geometry("900x750")
        self.ventana_grafico.configure(bg="#2a3a4a")
        cf = tk.Frame(self.ventana_grafico, bg="#2a3a4a", padx=15, pady=15)
        cf.pack(fill=tk.X)
        tk.Label(cf, text="📈 GRAFICADOR DE FUNCIONES", font=("Arial",16,"bold"), bg="#2a3a4a", fg="white").pack(pady=(0,10))
        ff = tk.Frame(cf, bg="#2a3a4a"); ff.pack(fill=tk.X, pady=5)
        tk.Label(ff, text="f(x) =", font=("Arial",13,"bold"), bg="#2a3a4a", fg="white").pack(side=LEFT, padx=5)
        self.entry_funcion = tk.Entry(ff, font=("Consolas",13), bg="#3a4a5a", fg="white", insertbackground="white")
        self.entry_funcion.pack(side=LEFT, fill=tk.X, expand=YES, padx=5)
        self.entry_funcion.insert(0, self.buffer if self.buffer else "x**2")
        rf = tk.Frame(cf, bg="#2a3a4a"); rf.pack(fill=tk.X, pady=5)
        tk.Label(rf, text="x mín:", font=("Arial",11), bg="#2a3a4a", fg="white").pack(side=LEFT, padx=5)
        self.entry_xmin = tk.Entry(rf, width=8, font=("Arial",11), bg="#3a4a5a", fg="white"); self.entry_xmin.pack(side=LEFT); self.entry_xmin.insert(0,"-10")
        tk.Label(rf, text="x máx:", font=("Arial",11), bg="#2a3a4a", fg="white").pack(side=LEFT, padx=5)
        self.entry_xmax = tk.Entry(rf, width=8, font=("Arial",11), bg="#3a4a5a", fg="white"); self.entry_xmax.pack(side=LEFT); self.entry_xmax.insert(0,"10")
        of = tk.Frame(cf, bg="#2a3a4a"); of.pack(fill=tk.X, pady=5)
        self.var_derivada = tk.BooleanVar(value=False)
        self.var_integral = tk.BooleanVar(value=False)
        tk.Checkbutton(of, text="Derivada f'(x)", variable=self.var_derivada, font=("Arial",11), bg="#2a3a4a", fg="white", selectcolor="#3a4a5a", activebackground="#2a3a4a", activeforeground="white").pack(side=LEFT, padx=10)
        tk.Checkbutton(of, text="Integral ∫f(x)dx", variable=self.var_integral, font=("Arial",11), bg="#2a3a4a", fg="white", selectcolor="#3a4a5a", activebackground="#2a3a4a", activeforeground="white").pack(side=LEFT, padx=10)
        bf = tk.Frame(cf, bg="#2a3a4a"); bf.pack(pady=10)
        tk.Button(bf, text="🎨 GRAFICAR", command=self.graficar, font=("Arial",13,"bold"), bg="#2a5a6a", fg="white", width=18, height=2).pack(side=LEFT, padx=5)
        tk.Button(bf, text="🔊 DESCRIBIR", command=self.describir_grafico, font=("Arial",13,"bold"), bg="#5a4a2a", fg="white", width=18, height=2).pack(side=LEFT, padx=5)
        self.grafico_frame = tk.Frame(self.ventana_grafico, bg="#2a3a4a")
        self.grafico_frame.pack(fill=BOTH, expand=YES, padx=15, pady=(0,15))
        self.ultimo_grafico = None

    def graficar(self):
        try:
            for w in self.grafico_frame.winfo_children(): w.destroy()
            expr_str = self.entry_funcion.get()
            xmin = float(self.entry_xmin.get())
            xmax = float(self.entry_xmax.get())
            expr = sp.sympify(expr_str)
            f = sp.lambdify(self.x, expr, 'numpy')
            xv = np.linspace(xmin, xmax, 500)
            yv = f(xv)
            self.ultimo_grafico = {'expr':str(expr),'x_min':xmin,'x_max':xmax,'y_min':float(np.min(yv)),'y_max':float(np.max(yv))}
            fig = Figure(figsize=(10,6), dpi=90, facecolor='#2a3a4a')
            ax = fig.add_subplot(111, facecolor='#1a2a3a')
            ax.plot(xv, yv, 'cyan', linewidth=3, label=f'f(x)={expr}')
            if self.var_derivada.get():
                d = sp.lambdify(self.x, sp.diff(expr,self.x), 'numpy')
                ax.plot(xv, d(xv), 'yellow', linewidth=2.5, linestyle='--', label="f'(x)")
            if self.var_integral.get():
                ig = sp.lambdify(self.x, sp.integrate(expr,self.x), 'numpy')
                ax.plot(xv, ig(xv), 'lime', linewidth=2.5, linestyle='-.', label="∫f(x)dx")
            ax.set_xlabel('x',fontsize=14,color='white',fontweight='bold')
            ax.set_ylabel('y',fontsize=14,color='white',fontweight='bold')
            ax.set_title(f'Gráfica de {expr}',fontsize=16,fontweight='bold',color='white')
            ax.grid(True,alpha=0.4,color='gray',linestyle='--')
            ax.legend(loc='best',fontsize=11,facecolor='#2a3a4a',edgecolor='white',labelcolor='white')
            ax.axhline(y=0,color='white',linewidth=1.2,alpha=0.7)
            ax.axvline(x=0,color='white',linewidth=1.2,alpha=0.7)
            ax.tick_params(colors='white',labelsize=10)
            for s in ax.spines.values(): s.set_color('white'); s.set_linewidth(1.5)
            c = FigureCanvasTkAgg(fig, self.grafico_frame)
            c.draw(); c.get_tk_widget().pack(fill=BOTH, expand=YES)
            self.hablar("Gráfico generado. Presione describir para información", prioridad=True)
        except Exception as e:
            tk.Label(self.grafico_frame, text=f"❌ Error: {str(e)}", font=("Arial",13), bg="#2a3a4a", fg="red").pack(pady=50)
            self.hablar(f"Error al graficar: {str(e)}", prioridad=True)

    def describir_grafico(self):
        if not self.ultimo_grafico:
            self.hablar("No hay gráfico. Genere uno primero"); return
        g = self.ultimo_grafico
        desc = f"Función: {g['expr']}. x: {g['x_min']} a {g['x_max']}. y: {g['y_min']:.2f} a {g['y_max']:.2f}."
        if self.var_derivada.get(): desc += " Con derivada en amarillo."
        if self.var_integral.get(): desc += " Con integral en verde."
        self.hablar(desc, prioridad=True)


def main():
    root = ttkb.Window(themename="darkly")
    app = CalculadoraAccesible(root)
    root.mainloop()

if __name__ == "__main__":
    main()
