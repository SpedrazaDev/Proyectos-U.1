import os
import pickle
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, 
                           QGridLayout, QVBoxLayout, QLabel, QInputDialog,
                            QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

import random as rd
import sys
import json
import datetime


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
posiciones_inhabilitadas= set()
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
    posiciones_inhabilitadas.clear()


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
            boton.clicked.connect(lambda _,x=x, y=y: evitar_islas(x,y))
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
        estado = estado_matriz(filas_actual, columnas_actual,
                             posiciones_infectadas, posiciones_bloqueadas)
        # imprimir_estado_base3(estado)
        return True
    return False

def boton_Usr(x, y):
    """Maneja el clic del jugador para colocar bloques"""
    if (x, y) not in posiciones_infectadas and (x, y) not in posiciones_bloqueadas and (x,y) not in posiciones_inhabilitadas:
        boton = matriz_botones[y][x]
        boton.setText("🧱")
        boton.setStyleSheet(f"""
            background-color: #f5e8c9;  
            border: 2px inset #f5e8c9;  
            font-size: {int(boton.width()*0.6)}px;
        """)
        posiciones_bloqueadas.add((x, y))
        estado = estado_matriz(filas_actual, columnas_actual, 
                             posiciones_infectadas, posiciones_bloqueadas)
        # imprimir_estado_base3(estado)
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

# def guardar_estado_matriz(matriz):
#     for e in len(matriz):
#         posiciones_infectadas.

def estado_matriz(filas, columnas, posInfectadas, posBloqueadas):
    estado_Matriz=[]

    for y in range(filas):
        fila=[]
        for x in range(columnas):
            if (x, y) in posInfectadas:
                fila.append(1)  # Virus
            elif (x, y) in posBloqueadas:
                fila.append(2)  # Barrera
            else:
                fila.append(0)  # Libre
        estado_Matriz.append(fila)
    return estado_Matriz


def imprimir_estado_base3(matriz_estado):
    """Imprime la matriz en base 3 de forma legible"""
    print("\nEstado actual del tablero (Base 3):")
    for fila in matriz_estado:
        print(" ".join(map(str, fila)))
    print()


def evitar_islas(x: int, y:int):
    cont=0
    fueraDeMatriz=set()
    dentroDeMatriz=set()

    coordenadas_adyacentes = ((0,1), (1,0), (0,-1), (-1,0))
    if (x, y) not in posiciones_infectadas and (x, y) not in posiciones_bloqueadas:
        
        for xVecino, yVecino in coordenadas_adyacentes:                                                     #para celda adyacentes a la seleccion
            xVecino, yVecino = x + xVecino, y + yVecino                                                     
            cont=0                                                                                          
            for xAdyacente,yAdyacente in coordenadas_adyacentes:                                            #para cada celda adyacente a las adyacentes a la seleccion
                xAdyacente, yAdyacente = xAdyacente + xVecino, yAdyacente + yVecino                         #(estas son las celdas a validar si son un muro o no)
                                                                                                            
                if not (0 <= xAdyacente < columnas_actual and 0 <= yAdyacente < filas_actual) :             #se valida si las celdas vecinas a la seleccionada son parte de la matriz
                    fueraDeMatriz.add((xAdyacente, yAdyacente))                                             
                if (0 <= xVecino < columnas_actual and 0 <= yVecino < filas_actual):                        
                    dentroDeMatriz.add((xVecino,yVecino))                                                   
                                                                                                            
                if (xAdyacente,yAdyacente) in posiciones_bloqueadas:                                        #en condiciones normales se validan las celdas bloqueadas y se aumenta el contador
                    cont+=1                                                                                 
                elif (xAdyacente,yAdyacente) in fueraDeMatriz and (xVecino,yVecino) in dentroDeMatriz:      #si es un borde se toma las celdas fuera de la matriz como "bloqueadas" y se aumenta el contador
                    cont+=1                                                                                 
                                                                                                            
                if cont==3:                                                                                 #Si una celda tiene 3 posiciones bloqueadas adyacentes no puede tener una cuarta porque sería una isla
                    cont=0                                                                                  #
                    boton= matriz_botones[y][x]                                                             #se manipula el color del botón seleccionado a uno mas oscuro para mostrar que está "bloqueado"
                    boton.setStyleSheet("""
                        font-size: {int(tamano_boton*0.6)}px; 
                        border: 2px outset #a4dbc7;
                        background: #a4dbc7;
                    """)
                    posiciones_inhabilitadas.add((x, y))                                                    #Se inhabilita esa posicion para que no sea reemplazada por un muro
                    mostrar_ventana_celdaBloqueada()                                                        #se muestra un mensaje que dice que no es una jugada valida
                    
def mostrar_ventana_celdaBloqueada():
    msg = QMessageBox()
    msg.setWindowTitle("Jugada no permitida")
    pixmap = QPixmap("Imagenes\isla.png") 
    pixmap = pixmap.scaled(150, 150,aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
    msg.setIconPixmap(pixmap)
    msg.setText("¡Esta jugada no es valida!")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

def guardar_partida(nombre_partida, estado_juego) -> bool:
    """
    Guarda el estado del juego en archivo binario y actualiza el registro JSON
    Args:
        nombre_partida: Nombre personalizado que el usuario asigna
        estado_juego: Diccionario con el estado actual del juego
    Returns:
        bool: True si se guardó correctamente, False si hubo error
    """
    try:
        # Configurar rutas y directorios
        carpeta = "Partidas"
        os.makedirs(carpeta, exist_ok=True)
        
        # Sanitizar nombre del archivo
        nombre_archivo = f"{nombre_partida}.bin"
        ruta_bin = os.path.join(carpeta, nombre_archivo)
        ruta_json = os.path.join(carpeta, "registro_partidas.json")
        
        # Verificar si ya existe la partida
        if os.path.exists(ruta_bin):
            raise FileExistsError(f"Ya existe una partida con el nombre '{nombre_partida}'")

        # Convertir matriz a representación hexadecimal
        matriz_base3 = estado_matriz(
            estado_juego['filas'],
            estado_juego['columnas'],
            estado_juego['infectadas'],
            estado_juego['bloqueadas']
        )
        
        hex_lista = []
        for fila in matriz_base3:
            fila_str = ''.join(map(str, fila))
            num_decimal = int(fila_str, 3)
            hex_lista.append(hex(num_decimal))

        # Preparar datos con metadatos
        datos = {
            'nivel': estado_juego['nivel'],
            'hex_data': hex_lista,
            'datos_extra': {
                'nombre': nombre_partida,
                # 'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'filas': estado_juego['filas'],
                'columnas': estado_juego['columnas']
            }
        }

        # Guardar archivo binario
        with open(ruta_bin, 'wb') as file:
            pickle.dump(datos, file)
        
        # Actualizar registro JSON
        actualizar_registro_partidas(ruta_json, nombre_partida, ruta_bin, datos)
        
        return True
        
    except Exception as e:
        print(f"Error al guardar partida: {e}")
        return False

def actualizar_registro_partidas(ruta_json, nombre_partida, ruta_bin, datos):
    """
    Actualiza el archivo JSON con los datos extra de la partida
    Args:
        ruta_json: Ruta del archivo JSON de registro
        nombre_partida: Nombre personalizado de la partida
        ruta_bin: Ruta del archivo binario guardado
        datos: Datos de la partida a registrar
    """
    try:
        # Cargar registro existente o crear nuevo
        if os.path.exists(ruta_json):
            with open(ruta_json, 'r', encoding='utf-8') as file:
                registro = json.load(file)
        else:
            registro = {}
        
        # Actualizar registro
        registro[nombre_partida] = {
            'archivo': os.path.basename(ruta_bin),
            'nivel': datos['nivel'],
            # 'fecha': datos['metadata']['fecha'],
            'ruta_completa': ruta_bin
        }
        
        # Guardar registro
        with open(ruta_json, 'w', encoding='utf-8') as file:
            json.dump(registro, file, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error al actualizar registro: {e}")

def guardar_partida_interfaz():
    """
    Muestra diálogo para guardar partida y maneja la interacción con el usuario
    """
    nombre, ok = QInputDialog.getText(
        ventana_juego, 
        "Guardar partida",
        "Nombre para esta partida:",
        QLineEdit.EchoMode.Normal,
        # f"partida_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )
    
    if ok and nombre:
        estado_actual = {
            'nivel': nivel_actual,
            'filas': filas_actual,
            'columnas': columnas_actual,
            'infectadas': posiciones_infectadas,
            'bloqueadas': posiciones_bloqueadas
        }
        
        if guardar_partida(nombre, estado_actual):
            QMessageBox.information(ventana_juego, "Éxito", f"Partida '{nombre}' guardada correctamente")
        else:
            QMessageBox.warning(ventana_juego, "Error", "No se pudo guardar la partida")




# Iniciar la aplicación
mostrar_menu_principal()
sys.exit(app.exec())