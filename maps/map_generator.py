# maps/map_generator.py

from utils.node import Node
from utils.double_linked_list import DoubleLinkedList

class MatrizCuadrada:
    def __init__(self, tamaño):
        self.tamaño = tamaño
        self.inicializar_matriz()

    def inicializar_matriz(self):
        # Inicializamos la matriz con nodos vacíos
        self.matriz = []
        for _ in range(self.tamaño):
            fila = []
            for _ in range(self.tamaño):
                fila.append(Nodo())
            self.matriz.append(fila)

        # Establecemos las conexiones entre nodos
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if i > 0:
                    self.matriz[i][j].up = self.matriz[i - 1][j]  # Conexión hacia arriba
                if i < self.tamaño - 1:
                    self.matriz[i][j].down = self.matriz[i + 1][j]   # Conexión hacia abajo
                if j > 0:
                    self.matriz[i][j].prev = self.matriz[i][j - 1]  # Conexión hacia la izquierda
                if j < self.tamaño - 1:
                    self.matriz[i][j].next = self.matriz[i][j + 1]   # Conexión hacia la derecha

    def imprimir_matriz(self):
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                print(self.matriz[i][j].value, end="\t")
            print()

# Ejemplo de uso
tamaño_matriz = 8
matriz = MatrizCuadrada(tamaño_matriz)
matriz.imprimir_matriz()

