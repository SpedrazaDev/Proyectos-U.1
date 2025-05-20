from collections import deque
import os
import pickle
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, 
                           QGridLayout, QVBoxLayout, QLabel, QInputDialog,
                            QLineEdit, QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox as QMBox

import random as rd
import sys
import json
from datetime import datetime



def centrar_ventana(ventana):
    """Centra la ventana en la pantalla"""
    frame = ventana.frameGeometry()
    centro = ventana.screen().availableGeometry().center()
    frame.moveCenter(centro)
    ventana.move(frame.topLeft())

app = QApplication(sys.argv)
app.setStyleSheet("""
    QMessageBox, QInputDialog {
        background-color: #f0f0f0;
    }
    QMessageBox QLabel, QInputDialog QLabel, QLineEdit {
        color: black;
    }
    QMessageBox QPushButton, QInputDialog QPushButton {
        color: black;
        background-color: #e0e0e0;
    }
    QComboBox, QComboBox QAbstractItemView {
        color: black;
        background-color: white;
    }
                  
""")

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
posiciones_infectadas = set()     # Posiciones infectadas
posiciones_bloqueadas = set()     # Posiciones con bloques
posiciones_inhabilitadas = set()  # Posiciones no seleccionables
filas_actual = 0
columnas_actual = 0
nivel_actual = "Facil"  # Valor por defecto

def mostrar_menu_principal():
    """Muestra el menú principal"""
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
    btn_cargar = QPushButton("Cargar Partida")
    btn_salir = QPushButton("Salir del Juego")
    
    estilo_boton = """
        QPushButton {
            font-size: 20px; 
            padding: 15px; 
            margin: 10px;
            background-color: #269e30; 
            color: #000000;
            border: 2px solid #a8e6ad; 
            border-radius: 8px;
            min-width: 200px;
        }
        QPushButton:hover { 
            background-color: #a8e6ad; 
        }
    """
    
    for boton in [btn_juego, btn_cargar, btn_salir]:
        boton.setStyleSheet(estilo_boton)
    
    btn_juego.clicked.connect(mostrar_menu_niveles)
    btn_cargar.clicked.connect(cargar_partida_interfaz)
    btn_salir.clicked.connect(ventana_menu.close)
    
    layout.addWidget(titulo)
    layout.addStretch(1)
    layout.addWidget(btn_juego)
    layout.addWidget(btn_cargar)
    layout.addWidget(btn_salir)
    layout.addStretch(1)
    
    ventana_menu.setLayout(layout)
    ventana_menu.resize(500, 400)
    centrar_ventana(ventana_menu)
    ventana_menu.show()

def mostrar_menu_niveles():
    """Muestra el menú de niveles"""
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
    ventana_niveles.resize(500, 400)
    centrar_ventana(ventana_niveles)
    ventana_niveles.show()

def crear_Matriz(tamano, nivel, cargando_partida=False):
    """Crea la matriz de juego con el tamaño especificado
    cargando_partida: Indica si estamos cargando una partida guardada"""
    global nivel_actual, filas_actual, columnas_actual, matriz_botones
    
    nivel_actual = nivel
    filas_actual = tamano
    columnas_actual = tamano
    
    # Limpieza de estado anterior
    ventana_niveles.hide()
    matriz_botones.clear()
    posiciones_infectadas.clear()
    posiciones_bloqueadas.clear()
    posiciones_inhabilitadas.clear()

    # Limpiar layout existente
    while grid_layout.count():
        child = grid_layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
    
    # Tamaño de botones según nivel
    tamano_boton = 40 if tamano <= 15 else 30

    # Crear matriz de botones
    for y in range(tamano):
        fila_botones = []
        for x in range(tamano):
            boton = QPushButton()
            boton.setFixedSize(tamano_boton, tamano_boton)
            boton.setStyleSheet(f"""
                font-size: {int(tamano_boton*0.6)}px; 
                border: 2px outset #a8e6ad;
                background: #a8e6ad;
            """)
            boton.clicked.connect(lambda _, px=x, py=y: boton_Usr(px, py))
            grid_layout.addWidget(boton, y, x)
            fila_botones.append(boton)
        matriz_botones.append(fila_botones)
    
    # Botones inferiores
    btn_volver = QPushButton("Volver al Menú")
    btn_volver.setStyleSheet("""
        font-size: 16px; padding: 10px;
        background-color: #269e30; color: #000000;
        border: 2px solid #a8e6ad;
    """)
    btn_volver.clicked.connect(lambda: [ventana_juego.hide(), ventana_menu.show()])
    
    btn_guardar_partida = QPushButton("Guardar Partida")
    btn_guardar_partida.setStyleSheet("""
        font-size: 16px; padding: 10px;
        background-color: #269e30; color: #000000;
        border: 2px solid #a8e6ad;
    """)
    btn_guardar_partida.clicked.connect(guardar_partida_interfaz)
    
    # Configurar layout principal
    main_layout = QVBoxLayout()
    main_layout.addLayout(grid_layout)
    main_layout.addWidget(btn_volver)
    main_layout.addWidget(btn_guardar_partida)
    
    ventana_juego.setLayout(main_layout)
    ventana_juego.setFixedSize(tamano_boton * tamano + 50, tamano_boton * tamano + 100)
    
    # Solo agregar virus aleatorio si no estamos cargando una partida
    if not cargando_partida:
        x, y = rd.randint(0, tamano-1), rd.randint(0, tamano-1)
        infectar_celda(x, y)
    
    centrar_ventana(ventana_juego)
    ventana_juego.show()

def infectar_celda(x: int, y: int) -> bool:
    """Infecta una celda si está disponible"""
    if (x, y) not in posiciones_bloqueadas and (x, y) not in posiciones_infectadas:
        boton = matriz_botones[y][x]
        tamano_boton = boton.width()
        boton.setText("🦠")
        boton.setStyleSheet(f"""
            background-color: #f5e8c9;  
            border: 2px inset #f5e8c9;  
            font-size: {int(tamano_boton*0.6)}px;
        """)
        posiciones_infectadas.add((x, y))
        
        return True
    return False

def boton_Usr(x, y):
    """Maneja el clic del jugador para colocar bloques"""
    # Verificar si la posición es válida
    if (x, y) in posiciones_infectadas \
       or (x, y) in posiciones_bloqueadas \
       or (x, y) in posiciones_inhabilitadas:
        return
    
    # Si crea isla, la función ya marca la celda como inhabilitada y muestra mensaje
    if evitar_islas(x, y):
        return    
        
    boton = matriz_botones[y][x]
    tamano_boton = boton.width()
    boton.setText("🧱")
    boton.setStyleSheet(f"""
        background-color: #f5e8c9;  
        border: 2px inset #f5e8c9;  
        font-size: {int(tamano_boton*0.6)}px;
    """)
    posiciones_bloqueadas.add((x, y))
    
    # Verificar estado después de colocar el bloque
    estado = verificar_estado_juego()
    if estado == "victoria":
        msg = QMessageBox()
        msg.setWindowTitle("¡Ganaste!")
        msg.setText("¡Has contenido el virus completamente!")
        msg.exec()
        return
    elif estado == "derrota":
        msg = QMessageBox()
        msg.setWindowTitle("¡Perdiste!")
        msg.setText("¡El virus te ha contenido completamente!")
        msg.exec()
        return
    
    # Solo propagar si el juego no ha terminado
    propagar_virus()
    
    # Verificar estado nuevamente después de la propagación
    estado = verificar_estado_juego()
    if estado == "victoria":
        msg = QMessageBox()
        msg.setWindowTitle("¡Ganaste!")
        msg.setText("¡Has contenido el virus completamente!")
        msg.exec()
    elif estado == "derrota":
        msg = QMessageBox()
        msg.setWindowTitle("¡Perdiste!")
        msg.setText("¡El virus te ha contenido completamente!")
        msg.exec()
    

def propagar_virus():
    """Propaga el virus a celdas adyacentes según el nivel"""
    celdas_a_infectar = set()
    coordenadas_adyacentes = ((0,1), (1,0), (0,-1), (-1,0))
    
    for (x, y) in posiciones_infectadas:
        for dx, dy in coordenadas_adyacentes:
            nx, ny = x + dx, y + dy
            if (0 <= nx < columnas_actual and 0 <= ny < filas_actual and 
                (nx, ny) not in posiciones_infectadas and 
                (nx, ny) not in posiciones_bloqueadas):
                celdas_a_infectar.add((nx, ny))
    
    if not celdas_a_infectar:
        return
    
    # Infectar según nivel de dificultad
    if nivel_actual == "Facil":
        infectar_celda(*rd.choice(list(celdas_a_infectar)))
    
    elif nivel_actual == "Medio":
        infectadas = rd.sample(list(celdas_a_infectar), min(2, len(celdas_a_infectar)))
        for celda in infectadas:
            infectar_celda(*celda)
    
    elif nivel_actual == "Dificil":
        infectadas = rd.sample(list(celdas_a_infectar), min(3, len(celdas_a_infectar)))
        for celda in infectadas:
            infectar_celda(*celda)

     # Verificar estado después de propagación
    estado = verificar_estado_juego()
    if estado == "victoria":
        msg = QMessageBox()
        msg.setWindowTitle("¡Ganaste!")
        msg.setText("¡Has contenido el virus completamente!")
        msg.exec()
    elif estado == "derrota":
        msg = QMessageBox()
        msg.setWindowTitle("¡Perdiste!")
        msg.setText("¡El virus te ha contenido completamente!")
        msg.exec()



def estado_matriz(filas, columnas, infectadas, bloqueadas):
    """Crea una representación del estado del juego"""
    return {
        'filas': filas,
        'columnas': columnas,
        'infectadas': infectadas,
        'bloqueadas': bloqueadas,
        'nivel': nivel_actual
    }

def guardar_partida_interfaz():
    """Muestra diálogo para guardar partida"""
    nombre_partida, ok = QInputDialog.getText(
        ventana_juego,
        "Guardar Partida",
        "Ingrese un nombre para la partida:",
        QLineEdit.EchoMode.Normal,
        f"partida_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    if ok and nombre_partida:
        estado = estado_matriz(filas_actual, columnas_actual, 
                             posiciones_infectadas, posiciones_bloqueadas)
        if guardar_PartidasBin(nombre_partida, estado):
            msg = QMessageBox(ventana_juego)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Éxito")
            msg.setText("Partida guardada correctamente")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: black;
                }
                QPushButton {
                    color: black;
                    background-color: #e0e0e0;
                }
            """)
            msg.exec()  # Cambiado de exec_() a exec()

def cargar_partida_interfaz():
    """Muestra diálogo para cargar partida"""
    try:
        partidas = []
        if os.path.exists("Partidas"):
            partidas = [f[:-4] for f in os.listdir("Partidas") if f.endswith(".bin")]
        
        if not partidas:
            msg = QMessageBox(ventana_menu)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Información")
            msg.setText("No hay partidas guardadas")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: black;
                }
                QPushButton {
                    color: black;
                    background-color: #e0e0e0;
                }
            """)
            msg.exec()
            return
        
        # Versión simplificada que funciona correctamente
        partida, ok = QInputDialog.getItem(
            ventana_menu,
            "Cargar Partida",
            "Seleccione una partida:",
            partidas,
            0, 
            False
        )
        
        # Aplicar estilo solo al QInputDialog
        for child in ventana_menu.findChildren(QInputDialog):
            child.setStyleSheet("""
                QInputDialog {
                    background-color: #f0f0f0;
                }
                QLabel {
                    color: black;
                }
                
                QComboBox QAbstractItemView {
                    color: black;
                    background-color: white;
                    selection-background-color: #a8e6ad;
                }
                QPushButton {
                    color: black;
                    background-color: #e0e0e0;
                }
            """)
        
        if ok and partida:
            estado = cargar_PartidaBin(partida)
            if estado:
                crear_Matriz(estado['filas'], estado['nivel'], cargando_partida=True)
                
                global posiciones_infectadas, posiciones_bloqueadas
                posiciones_infectadas = estado['infectadas']
                posiciones_bloqueadas = estado['bloqueadas']
                
                for y in range(estado['filas']):
                    for x in range(estado['columnas']):
                        if (x, y) in posiciones_infectadas:
                            matriz_botones[y][x].setText("🦠")
                            matriz_botones[y][x].setStyleSheet(f"""
                                background-color: #f5e8c9;
                                border: 2px inset #f5e8c9;
                                font-size: {int(matriz_botones[y][x].width()*0.6)}px;
                            """)
                        elif (x, y) in posiciones_bloqueadas:
                            matriz_botones[y][x].setText("🧱")
                            matriz_botones[y][x].setStyleSheet(f"""
                                background-color: #f5e8c9;
                                border: 2px inset #f5e8c9;
                                font-size: {int(matriz_botones[y][x].width()*0.6)}px;
                            """)
                
                ventana_menu.hide()
                ventana_juego.show()
            
    except Exception as e:
        msg = QMessageBox(ventana_menu)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.setText(f"Error al cargar:\n{str(e)}")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                color: black;
                background-color: #e0e0e0;
            }
        """)
        msg.exec()


def guardar_PartidasBin(nombre_partida, estado_juego):
    """Guarda la partida en binario según las especificaciones"""
    try:
        os.makedirs("Partidas", exist_ok=True)
        
        filas = estado_juego['filas']
        columnas = estado_juego['columnas']
        
        nivel_juego = {"Facil": 0, "Medio": 1, "Dificil": 2}
        nivel_num = nivel_juego.get(estado_juego['nivel'], 0)
        
        # Preparar matriz en base 3
        matriz_base3 = []
        for y in range(filas):
            fila = []
            for x in range(columnas):
                if (x, y) in estado_juego['infectadas']:
                    fila.append(1)
                elif (x, y) in estado_juego['bloqueadas']:
                    fila.append(2)
                else:
                    fila.append(0)
            matriz_base3.append(fila)
        
        # Convertir cada fila a bytes
        with open(os.path.join("Partidas", f"{nombre_partida}.bin"), 'wb') as f:
            # Escribir cabecera (filas, columnas, nivel)
            f.write(filas.to_bytes(2, byteorder='big'))
            f.write(columnas.to_bytes(2, byteorder='big'))
            f.write(nivel_num.to_bytes(1, byteorder='big'))
            
            # Escribir cada fila como número en base 3
            for fila in matriz_base3:
                num = 0
                for i, val in enumerate(fila):
                    num += val * (3 ** (len(fila) - i - 1))
                
                # Calcular bytes necesarios y escribir
                bytes_necesarios = (len(fila) * 2 + 7) // 8  # Calcula bytes necesarios
                f.write(num.to_bytes(bytes_necesarios, byteorder='big'))
        
        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False
    
def cargar_PartidaBin(nombre_partida):
    """Carga partida desde archivo binario"""
    try:
        ruta = os.path.join("Partidas", f"{nombre_partida}.bin")
        if not os.path.exists(ruta):
            return None

        with open(ruta, 'rb') as f:
            # Leer cabecera
            filas = int.from_bytes(f.read(2), 'big')
            columnas = int.from_bytes(f.read(2), 'big')
            nivel_num = int.from_bytes(f.read(1), 'big')
            nivel_map = {0: "Facil", 1: "Medio", 2: "Dificil"}
            nivel = nivel_map.get(nivel_num, "Facil")
            
            # Calcular bytes por fila
            bytes_por_fila = (columnas * 2 + 7) // 8
            
            # Leer y reconstruir cada fila
            matriz_base3 = []
            for _ in range(filas):
                num = int.from_bytes(f.read(bytes_por_fila), 'big')
                fila = []
                for _ in range(columnas):
                    fila.insert(0, num % 3)
                    num = num // 3
                # Asegurar longitud correcta
                fila = [0]*(columnas - len(fila)) + fila
                matriz_base3.append(fila)
        
        # Reconstruir posiciones
        pos_infectadas = {(x,y) for y in range(filas) for x in range(columnas) if matriz_base3[y][x] == 1}
        pos_bloqueadas = {(x,y) for y in range(filas) for x in range(columnas) if matriz_base3[y][x] == 2}
        
        return {
            'filas': filas,
            'columnas': columnas,
            'nivel': nivel,
            'infectadas': pos_infectadas,
            'bloqueadas': pos_bloqueadas
        }
    except Exception as e:
        print(f"Error al cargar: {e}")
        return None


def evitar_islas(x_sel: int, y_sel: int) -> bool:
    """
    Comprueba si colocar un muro crea islas de celdas NO infectadas.
    Versión corregida que ignora el área contenida del virus.
    """

     # Simular bloqueo temporal
    bloqueadas_temp = set(posiciones_bloqueadas)
    bloqueadas_temp.add((x_sel, y_sel))

    filas, columnas = filas_actual, columnas_actual
    visitado = set()
    queue = deque()

    # Agregamos todos los bordes que sean celdas transitables (no bloqueadas ni infectadas)
    for x in range(columnas):
        for y in [0, filas-1]:  # Borde superior e inferior
            if (x, y) not in bloqueadas_temp and (x, y) not in posiciones_infectadas:
                queue.append((x, y))
                visitado.add((x, y))
    for y in range(filas):
        for x in [0, columnas-1]:  # Borde izquierdo y derecho
            if (x, y) not in bloqueadas_temp and (x, y) not in posiciones_infectadas:
                queue.append((x, y))
                visitado.add((x, y))

    # Propagación desde los bordes
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < columnas and 0 <= ny < filas
                and (nx, ny) not in bloqueadas_temp
                and (nx, ny) not in posiciones_infectadas
                and (nx, ny) not in visitado):
                visitado.add((nx, ny))
                queue.append((nx, ny))

    # Verificar si hay celdas no alcanzadas
    for y in range(filas):
        for x in range(columnas):
            if (x, y) not in bloqueadas_temp and (x, y) not in posiciones_infectadas:
                if (x, y) not in visitado:
                    # Celda no infectada aislada -> jugada inválida
                    posiciones_inhabilitadas.add((x_sel, y_sel))
                    boton = matriz_botones[y_sel][x_sel]
                    boton.setStyleSheet(f"""
                        font-size: {int(boton.width()*0.6)}px;
                        border: 2px outset #a4dbc7;
                        background: #a4dbc7;
                    """)
                    mostrar_ventana_celdaBloqueada()
                    return True

    return False


def mostrar_ventana_celdaBloqueada():
    """Muestra mensaje de celda bloqueada"""
    msg = QMessageBox()
    msg.setWindowTitle("Jugada no permitida")
    try:
        pixmap = QPixmap("Imagenes/isla.png")
        pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
        msg.setIconPixmap(pixmap)
    except:
        pass  # Si no encuentra la imagen, muestra el mensaje sin ella
    
    msg.setText("¡Esta jugada no es válida!")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()





def verificar_estado_juego() -> str:
    """Retorna el estado del juego: 'victoria', 'derrota' o 'en progreso'"""
    # Verificar si el virus puede expandirse
    puede_expandirse = False
    celdas_libres = 0
    
    # Contar celdas libres y verificar expansión posible
    for y in range(filas_actual):
        for x in range(columnas_actual):
            if (x, y) not in posiciones_bloqueadas and (x, y) not in posiciones_infectadas:
                celdas_libres += 1
                
            if (x, y) in posiciones_infectadas:
                # Verificar si el virus puede expandirse desde esta celda
                for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < columnas_actual and 0 <= ny < filas_actual and
                        (nx, ny) not in posiciones_bloqueadas and 
                        (nx, ny) not in posiciones_infectadas):
                        puede_expandirse = True
                        break
                if puede_expandirse:
                    break
    
    if not puede_expandirse:
        if celdas_libres > 0:
            return "victoria"  # Virus contenido y quedan celdas libres
        else:
            return "derrota"   # Virus contenido pero no quedan celdas libres
    return "en progreso"       # El juego continúa

# Iniciar la aplicación
mostrar_menu_principal()
sys.exit(app.exec())