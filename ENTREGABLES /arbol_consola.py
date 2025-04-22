import csv
import time
import sys
import io
from collections import deque

# Configuración universal de codificación
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class Node:
    def __init__(self, symbol, children=None, token=None):
        self.symbol = symbol
        self.children = children if children is not None else []
        self.token = token
        self.id = id(self)
    
    def add_child(self, child_node):
        self.children.append(child_node)
    
    def __repr__(self):
        return f"{self.symbol} ({self.token})" if self.token else self.symbol

class AnalizadorSintacticoLL:
    def __init__(self, archivo_tabla):
        self.tabla = self.cargar_tabla_csv(archivo_tabla)
        self.raiz = None
    
    def cargar_tabla_csv(self, archivo):
        tabla = {}
        with open(archivo, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';'))
            terminales = reader[0][1:]
            for fila in reader[1:]:
                no_terminal = fila[0]
                for i, celda in enumerate(fila[1:]):
                    produccion = celda.strip()
                    if produccion:
                        lado_derecho = produccion.split() if produccion != 'ε' else ['ε']
                        tabla[(no_terminal, terminales[i])] = lado_derecho
        return tabla

    def mostrar_pila(self, pila):
        print("\n┌─────── Pila Actual ───────┐")
        print("+-------+")
        for elemento in reversed(pila):
            print(f"| {elemento.center(5)} |")
            print("+-------+")
        print("└──────────────────────────┘")

    def mostrar_arbol_ascii(self, node=None, prefix=""):
        """Muestra el árbol sintáctico en formato ASCII art"""
        if node is None:
            if self.raiz is None:
                print("\nÁrbol vacío")
                return
            print("\n┌────────── Árbol Sintáctico ──────────┐")
            node = self.raiz
        
        # Determinar el símbolo a mostrar
        symbol = f"{node.symbol} [{node.token}]" if node.token else node.symbol
        
        if len(node.children) == 0:
            print(prefix + "└── " + symbol)
        else:
            print(prefix + "┌── " + symbol)
            
            for i, child in enumerate(node.children):
                if i == len(node.children) - 1:
                    new_prefix = prefix + "    "
                    self.mostrar_arbol_ascii(child, new_prefix)
                else:
                    new_prefix = prefix + "│   "
                    self.mostrar_arbol_ascii(child, new_prefix)
        
        if node == self.raiz:
            print("└──────────────────────────────────┘")

    def analizar(self, tokens):
        tokens.append('$')
        pila = ['$', 'E']
        indice = 0
        token_actual = tokens[indice]
        
        # Inicialización del árbol
        self.raiz = Node('E')
        stack_arbol = [self.raiz]
        
        print("\n════════ INICIANDO ANÁLISIS ════════")
        print("Pila inicial y árbol sintáctico vacío:")
        self.mostrar_pila(pila)
        self.mostrar_arbol_ascii()
        print(f"\n• Token inicial: '{token_actual}'")
        time.sleep(1.5)
        
        pasos = []
        paso_num = 1
        
        while pila[-1] != '$':
            X = pila[-1]
            nodo_actual = stack_arbol[-1] if stack_arbol else None
            
            print(f"\n═════════ PASO {paso_num} ═════════")
            print(f"• Tope de pila: '{X}'")
            print(f"• Token actual: '{token_actual}'")
            
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            accion = ""
            
            if X == token_actual:
                accion = f"Emparejar {X}"
                print(f"\n✓ Coincidencia: '{X}' == '{token_actual}'")
                print(f"• Acción: Sacar '{X}' de la pila y avanzar")
                
                if nodo_actual:
                    nodo_actual.token = token_actual
                
                pila.pop()
                stack_arbol.pop()
                indice += 1
                if indice < len(tokens):
                    token_actual = tokens[indice]
                
                self.mostrar_pila(pila)
                self.mostrar_arbol_ascii()
                print(f"• Nuevo token: '{token_actual}'")
                time.sleep(1.5)
                
            elif (X, token_actual) in self.tabla:
                produccion = self.tabla[(X, token_actual)]
                produccion_str = ' → '.join(produccion) if produccion != ['ε'] else 'ε'
                accion = f"{X} → {produccion_str}"
                print(f"\n↗ Expansión: Aplicando {accion}")
                print(f"• Sacamos '{X}' y agregamos producción")
                
                pila.pop()
                nodo_padre = stack_arbol.pop()
                
                for simbolo in reversed(produccion):
                    if simbolo != 'ε':
                        pila.append(simbolo)
                        nuevo_nodo = Node(simbolo)
                        nodo_padre.add_child(nuevo_nodo)
                        stack_arbol.append(nuevo_nodo)
                        print(f"  + Agregado '{simbolo}'")
                
                self.mostrar_pila(pila)
                self.mostrar_arbol_ascii()
                print(f"• Token actual: '{token_actual}' (no avanzamos)")
                time.sleep(1.5)
                
            else:
                print(f"\n✗ ERROR: No hay regla para ({X}, {token_actual})")
                print("Posibles causas:")
                print(f"- Falta producción para '{X}' con token '{token_actual}'")
                print(f"- Token inesperado en posición {indice}")
                pasos.append((paso_num, pila_actual, entrada_restante, "ERROR"))
                return {
                    "exito": False,
                    "mensaje": f"Error en token '{token_actual}' (posición {indice})",
                    "pasos": pasos,
                    "arbol": None
                }
            
            pasos.append((paso_num, pila_actual, entrada_restante, accion))
            paso_num += 1
        
        if token_actual == '$':
            print("\n═════════ ANÁLISIS EXITOSO ═════════")
            print("✓ Todos los tokens procesados correctamente")
            print("✓ Pila vaciada correctamente")
            
            self.limpiar_nodos_epsilon(self.raiz)
            self.mostrar_arbol_ascii()
            
            return {
                "exito": True,
                "mensaje": "La cadena pertenece al lenguaje",
                "pasos": pasos,
                "arbol": self.raiz
            }
        else:
            print("\n═════════ ERROR ═════════")
            print(f"✗ Token pendiente: '{token_actual}'")
            print("✗ La pila se vació pero quedaron tokens")
            
            return {
                "exito": False,
                "mensaje": f"Token '{token_actual}' no procesado",
                "pasos": pasos,
                "arbol": None
            }
    
    def limpiar_nodos_epsilon(self, node):
        for child in node.children[:]:
            if child.symbol == 'ε':
                node.children.remove(child)
            else:
                self.limpiar_nodos_epsilon(child)

def analizar_cadena(cadena):
    tokens = cadena.strip().split()
    analizador = AnalizadorSintacticoLL("tabla_sintactica.csv")
    return analizador.analizar(tokens)

if __name__ == "__main__":
    print("\n EJEMPLO DE ANÁLISIS ")
    resultado = analizar_cadena("int mas int")
    
    print("\n═════════ RESUMEN ═════════")
    print(f"Resultado: {'ÉXITO' if resultado['exito'] else 'FALLO'}")
    print(resultado['mensaje'])
