from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, 
                           QGridLayout, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt
import random as rd
import sys

def centrar_ventana(ventana):
    """Centra la ventana en la pantalla"""
    frame = ventana.frameGeometry()
    centro = ventana.screen().availableGeometry().center()
    frame.moveCenter(centro)
    ventana.move(frame.topLeft())

app = QApplication(sys.argv)

# Configuración de ventanas
ventana_juego = QWidget()
ventana_juego.setWindowTitle('Virus Spread Game')
ventana_juego.setStyleSheet("background-color: #f5e8c9;")

ventana_menu = QWidget()
ventana_menu.setWindowTitle("Virus Spread Game - Menú Principal")
ventana_menu.setStyleSheet("background-color: #f0f0f0; font-family: Arial;")

ventana_niveles = QWidget()
ventana_niveles.setWindowTitle("Selección de Nivel")
ventana_niveles.setStyleSheet("background-color: #f0f0f0;")

# Variables globales
grid_layout = QGridLayout()
matriz_botones = []
posiciones_infectadas = set()
posiciones_bloqueadas = set()
filas_actual = 0
columnas_actual = 0


nivel_actual={"Facil":10,
         "Medio":15,
         "Dificil":20}

def mostrar_menu_principal():
    """Muestra el menú principal centrado"""
    layout = QVBoxLayout()
    
    titulo = QLabel("Menú Principal")
    titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    titulo.setStyleSheet("""
        font-size: 28px; 
        font-weight: bold; 
        color: #333;
        margin-bottom: 30px;
    """)
    
    btn_juego = QPushButton("Jugar Virus Spread")
    btn_salir = QPushButton("Salir del Juego")
    
    estilo_boton = """
        QPushButton {
            font-size: 20px; padding: 15px; margin: 10px;
            background-color: #269e30; color: #000000;
            border: 2px solid #a8e6ad; border-radius: 8px;
            min-width: 200px;
        }
        QPushButton:hover { background-color: #a8e6ad; }
    """
    
    for boton in [btn_juego, btn_salir]:
        boton.setStyleSheet(estilo_boton)
    
    btn_juego.clicked.connect(mostrar_menu_niveles)
    btn_salir.clicked.connect(ventana_menu.close)
    
    layout.addWidget(titulo)
    layout.addStretch(1)
    layout.addWidget(btn_juego)
    layout.addWidget(btn_salir)
    layout.addStretch(1)
    
    ventana_menu.setLayout(layout)
    ventana_menu.resize(500, 400)  # Tamaño fijo para el menú
    centrar_ventana(ventana_menu)
    ventana_menu.show()

def mostrar_menu_niveles():
    """Muestra el menú de niveles centrado"""
    ventana_menu.hide()
    
    layout = QVBoxLayout()
    
    titulo = QLabel("Seleccione el Nivel")
    titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    titulo.setStyleSheet("""
        font-size: 24px; 
        font-weight: bold; 
        color: #333;
        margin-bottom: 30px;
    """)
    
    btn_nivel1 = QPushButton("Nivel Fácil (10x10)")
    btn_nivel2 = QPushButton("Nivel Medio (15x15)")
    btn_nivel3 = QPushButton("Nivel Difícil (20x20)")
    btn_volver = QPushButton("Volver al Menú")
    
    estilo_boton = """
        QPushButton {
            font-size: 18px; padding: 12px; margin: 8px;
            background-color: #269e30; color: #000000;
            border: 2px solid #a8e6ad; border-radius: 8px;
            min-width: 200px;
        }
        QPushButton:hover { background-color: #a8e6ad; }
    """
    
    for boton in [btn_nivel1, btn_nivel2, btn_nivel3, btn_volver]:
        boton.setStyleSheet(estilo_boton)
    
    btn_nivel1.clicked.connect(lambda: crear_Matriz(10, "Facil"))
    btn_nivel2.clicked.connect(lambda: crear_Matriz(15, "Medio")) 
    btn_nivel3.clicked.connect(lambda: crear_Matriz(20, "Dificil"))
    btn_volver.clicked.connect(lambda: [ventana_niveles.hide(), ventana_menu.show(), ventana_juego.hide()])
    
    layout.addWidget(titulo)
    layout.addStretch(1)
    layout.addWidget(btn_nivel1)
    layout.addWidget(btn_nivel2)
    layout.addWidget(btn_nivel3)
    layout.addStretch(2)
    layout.addWidget(btn_volver)
    
    ventana_niveles.setLayout(layout)
    ventana_niveles.resize(500, 400)  # Tamaño fijo para el menú de niveles
    centrar_ventana(ventana_niveles)
    ventana_niveles.show()

def crear_Matriz(tamano,nivel):
    """Crea la matriz de juego con el tamaño especificado"""
    global nivel_actual, filas_actual, columnas_actual, matriz_botones
    
    # Actualizar variables globales
    nivel_actual = nivel
    filas_actual = tamano
    columnas_actual = tamano
    
    
    # Limpiar estado anterior
    ventana_niveles.hide()
    matriz_botones.clear()
    posiciones_infectadas.clear()
    posiciones_bloqueadas.clear()


    # Limpiar layout existente
    for i in reversed(range(grid_layout.count())): 
        grid_layout.itemAt(i).widget().setParent(None)
    
     # Calcular tamaño de botón (fijo para simplificar)
    tamano_boton = 40 if tamano <= 15 else 30  # Más pequeño para nivel difícil

  

    # Crear matriz de botones
    for y in range(tamano):
        fila_botones = []
        for x in range(tamano):
            boton = QPushButton()
            boton.setFixedSize(tamano_boton, tamano_boton)
            boton.setStyleSheet("""
                font-size: {int(tamano_boton*0.6)}px; 
                border: 2px outset #a8e6ad;
                background: #a8e6ad;
            """)
            boton.clicked.connect(lambda _, px=x, py=y: boton_Usr(px, py))
            grid_layout.addWidget(boton, y, x)
            fila_botones.append(boton)
        matriz_botones.append(fila_botones)
    
    
    # Botón para volver
    btn_volver = QPushButton("Volver al Menú")
    btn_volver.setStyleSheet("""
        font-size: 16px; padding: 10px;
        background-color: #269e30; color: #000000;
        border: 2px solid #a8e6ad;
    """)
    btn_volver.clicked.connect(lambda: [ventana_juego.hide(), ventana_menu.show()])
    
    # Configurar layout principal
    main_layout = QVBoxLayout()
    main_layout.addLayout(grid_layout)
    main_layout.addWidget(btn_volver)
    
    # Asignar layout a la ventana (esto faltaba)
    ventana_juego.setLayout(main_layout)
    
    # Ajustar tamaño de ventana
    ventana_juego.setFixedSize(tamano_boton * tamano + 50, tamano_boton * tamano + 100)
    
    # Iniciar juego con posición aleatoria
    x, y = rd.randint(0, tamano-1), rd.randint(0, tamano-1)
    infectar_celda(x, y)
    
    centrar_ventana(ventana_juego)
    ventana_juego.show()


def infectar_celda(x: int, y: int) -> bool:
    """Infecta una celda si está disponible"""
    if (x, y) not in posiciones_bloqueadas and (x, y) not in posiciones_infectadas:
        boton = matriz_botones[y][x]
        boton.setText("🦠")
        boton.setStyleSheet(f"""
            background-color: #f5e8c9;  
            border: 2px inset #f5e8c9;  
            font-size: {int(boton.width()*0.6)}px;
        """)
        posiciones_infectadas.add((x, y))
        return True
    return False

def boton_Usr(x, y):
    """Maneja el clic del jugador para colocar bloques"""
    if (x, y) not in posiciones_infectadas and (x, y) not in posiciones_bloqueadas:
        boton = matriz_botones[y][x]
        boton.setText("🧱")
        boton.setStyleSheet(f"""
            background-color: #f5e8c9;  
            border: 2px inset #f5e8c9;  
            font-size: {int(boton.width()*0.6)}px;
        """)
        posiciones_bloqueadas.add((x, y))
        propagar_virus()


def propagar_virus():
    """Propaga el virus a celdas adyacentes"""
    celdas_a_infectar=set()
    coordenadas_adyacentes = ((0,1), (1,0), (0,-1), (-1,0))
    
    for (x, y) in posiciones_infectadas:
        for dx, dy in coordenadas_adyacentes:
            nx, ny = x + dx, y + dy
            if (0 <= nx < len(matriz_botones)) and (0 <= ny < len(matriz_botones[0]) and 
                (nx, ny) not in posiciones_infectadas and 
                (nx, ny) not in posiciones_bloqueadas):
                celdas_a_infectar.add((nx, ny))
    
    # Aplicamos la lógica según el nivel
    if nivel_actual == "Facil":
        if celdas_a_infectar:
            infectar_celda(*rd.choice(list(celdas_a_infectar)))
    
    elif nivel_actual == "Medio":
        if len(celdas_a_infectar) >= 2:
            # Infectamos 2 celdas aleatorias diferentes
            infectadas = rd.sample(list(celdas_a_infectar), 2)
            for celda in infectadas:
                infectar_celda(*celda)
        elif celdas_a_infectar:
            # Si hay menos de 2, infectamos las que haya
            for celda in celdas_a_infectar:
                infectar_celda(*celda)
    
    elif nivel_actual == "Dificil":
        # Infectamos todas las celdas adyacentes disponibles
        for celda in celdas_a_infectar:
            infectar_celda(*celda)


def niveles():
    global niveles

    for nivel in niveles:
        if nivel == "Facil":
            pass
        elif nivel == "Medio":
            pass
        elif nivel == "Dificil":
            pass
            


    pass
# Iniciar la aplicación
mostrar_menu_principal()
sys.exit(app.exec())