from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
import random as rd
import sys

app=QApplication(sys.argv)
ventana = QWidget()
ventana.setWindowTitle('Virus Spread Game')
ventana.setGeometry(500, 100, 500, 500)
ventana.setStyleSheet("background-color: #f5e8c9;")

grid_layout = QGridLayout()
matriz_botones=[]
posiciones_infectadas = set()  # Almacena bloques infectados por el virus
posiciones_bloqueadas = set()  # Almacena bloques del jugador
turno_inicial_realizado = False  # Control para el primer turno

timer = QTimer()  # Mover el timer al ámbito global

def iniciar_juego():
    """Inicia el juego con una infección aleatoria"""
    x, y = rd.randint(0, 9), rd.randint(0, 9)
    infectar_celda(x, y)
    # timer.timeout.connect(propagar_automaticamente)
    # timer.start(2000)  # Propagación cada 2 segundos
#--Usarlo para los niveles


def infectar_celda(x:int,y:int) -> bool:
    """Infecta una celda si está disponible
    
        Args:
            x (int): coordenada x
            y (int): coordenada y

        Returns:
            bool: Retorna 'True' si esta disponible, por el contrario 'False'
    """
    print(f'X:{x} Y:{y}') #para depurar las coordenadas
    if (x, y) not in posiciones_bloqueadas and (x, y) not in posiciones_infectadas:
        boton = matriz_botones[y][x]
        boton.setText("🦠")
        boton.setStyleSheet("""
            background-color: #f5e8c9;  
            border: 2px inset #f5e8c9;  
            font-size: 40px;
        """)
        posiciones_infectadas.add((x, y))
        return True
    return False

def propagar_virus():
    """Este método propaga el virus a una sola celda adyacente aleatoria
    """
    celdas_disponibles = []
    coordenadas_adyacentes=((0,1), (1,0), (0,-1), (-1,0))
    for (x, y) in posiciones_infectadas:
        for desplazamiento_x, desplazamiento_y in coordenadas_adyacentes:  # 4 direcciones
            vecinos_x, vecinos_y = x + desplazamiento_x, y + desplazamiento_y
            if (0 <= vecinos_x < 10 and 0 <= vecinos_y < 10 and 
                (vecinos_x, vecinos_y) not in posiciones_infectadas and 
                (vecinos_x, vecinos_y) not in posiciones_bloqueadas):
                celdas_disponibles.append((vecinos_x, vecinos_y))
    
    if celdas_disponibles:
        vecinos_x, vecinos_y = rd.choice(celdas_disponibles)  # Elige una aleatoria
        infectar_celda(vecinos_x, vecinos_y)


def boton_Usr(x=0,y=0):
    """Maneja el clic del jugador para colocar bloques"""
    print(f'X:{x} Y:{y}') # Solo para depurar
    if (x, y) not in posiciones_infectadas:
        # Colocar bloque
        boton = matriz_botones[y][x]
        boton.setText("🧱")
        boton.setStyleSheet("""
        background-color: #f5e8c9;  
        border: 2px inset #f5e8c9;  
        font-size: 40px;
        """)
        posiciones_bloqueadas.add((x, y))
        propagar_virus()


    


def crear_Matriz(grid_layout):
    for y in range(10):
        fila_botones = []
        for x in range(10):
            boton = QPushButton()  
            boton.setFixedSize(50, 50)
            boton.setStyleSheet("font-size: 40px; border: 2px outset #a8e6ad;""border-style: outset; background: #a8e6ad;")
            boton.clicked.connect(lambda _, px=x, py=y: boton_Usr(px, py))
            grid_layout.addWidget(boton, y, x)
            fila_botones.append(boton)

        matriz_botones.append(fila_botones)

crear_Matriz(grid_layout)
ventana.setLayout(grid_layout)
ventana.show()
iniciar_juego()
sys.exit(app.exec())