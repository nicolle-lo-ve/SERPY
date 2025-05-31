import csv
import sys
import io
# Configuración universal de codificación
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
class Node:
    def __init__(self, symbol, children=None, token=None, linea=None, columna=None):
        """
        Clase para representar nodos del árbol sintáctico.
        """
        self.symbol = symbol
        self.children = children if children is not None else []
        self.token = token  # Solo para nodos terminales
        self.linea = linea  # Información de ubicación
        self.columna = columna  # Información de ubicación
        self.id = id(self)  # Identificador único para graphviz
    
    def add_child(self, child_node):
        """Añade un nodo hijo"""
        self.children.append(child_node)
    
    def __repr__(self):
        ubicacion = f" [{self.linea}:{self.columna}]" if self.linea and self.columna else ""
        return f"{self.symbol} ({self.token}){ubicacion}" if self.token else f"{self.symbol}{ubicacion}"
class AnalizadorSintacticoLL:
    def __init__(self, archivo_tabla):
        self.tabla = self.cargar_tabla_csv(archivo_tabla)
        self.raiz = None  # Raíz del árbol sintáctico
        # Estadísticas de análisis (silenciosas)
        self.estadisticas = {
            'nodos_creados': 0,
            'tokens_procesados': 0,
            'producciones_aplicadas': 0,
            'pasos_total': 0
        }
    
    def cargar_tabla_csv(self, archivo):
        tabla = {}
        with open(archivo, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=','))
            terminales = reader[0][1:]  # Saltar la primera columna vacía
            for fila in reader[1:]:
                no_terminal = fila[0]
                for i, celda in enumerate(fila[1:]):
                    produccion = celda.strip()
                    if produccion:  # Solo agregamos si hay producción
                        lado_derecho = produccion.split() if produccion != 'ε' else ['ε']
                        tabla[(no_terminal, terminales[i])] = lado_derecho
        return tabla
    def generar_graphviz(self, nodo_raiz):
        """
        Genera código DOT para visualizar en Graphviz Online.
        """
        if not nodo_raiz:
            return ""
        
        dot_code = "digraph ArbolSintactico {\n"
        dot_code += "    node [shape=box, style=filled, fillcolor=lightblue];\n"
        dot_code += "    rankdir=TB;\n\n"
        
        def agregar_nodo(nodo, padre_id=None):
            nonlocal dot_code
            
            # Crear etiqueta del nodo con información de ubicación si está disponible
            if nodo.token:
                ubicacion = f"\\n[{nodo.linea}:{nodo.columna}]" if nodo.linea and nodo.columna else ""
                etiqueta = f"{nodo.symbol}\\n'{nodo.token}'{ubicacion}"
            else:
                etiqueta = nodo.symbol
            
            dot_code += f'    "{nodo.id}" [label="{etiqueta}"];\n'
            
            if padre_id:
                dot_code += f'    "{padre_id}" -> "{nodo.id}";\n'
            
            for hijo in nodo.children:
                agregar_nodo(hijo, nodo.id)
        
        agregar_nodo(nodo_raiz)
        dot_code += "}\n"
        return dot_code
    def analizar(self, tokens):
        """
        Realiza el análisis sintáctico LL(1) de la entrada.
        VERSIÓN SILENCIOSA: Todo el proceso es interno, solo muestra resultado final.
        """
        # Reiniciar estadísticas
        self.estadisticas = {
            'nodos_creados': 0, 
            'tokens_procesados': 0, 
            'producciones_aplicadas': 0,
            'pasos_total': 0
        }
        
        # Añadir símbolo de fin de entrada
        tokens = tokens + ['$']
        
        # Inicializar pila con símbolo de fin y símbolo inicial
        pila = ['$', 'PROGRAMA']
        indice = 0
        token_actual = tokens[indice]
        
        # Estructuras para construir el árbol
        stack_arbol = []  # Pila para construcción del árbol
        self.raiz = Node('PROGRAMA')  # Nodo raíz inicial
        stack_arbol.append(self.raiz)
        self.estadisticas['nodos_creados'] += 1
        
        # PROCESO SILENCIOSO - Sin impresiones durante el análisis
        pasos = []
        paso_num = 1
        
        while pila[-1] != '$':
            X = pila[-1]
            nodo_actual = stack_arbol[-1] if stack_arbol else None
            
            # Preparar información para debugging (sin imprimir)
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            accion = ""
            
            if X == token_actual:
                # COINCIDENCIA: Emparejar terminal
                accion = f"Emparejar {X}"
                
                # Para nodos terminales, guardamos el token
                if nodo_actual:
                    nodo_actual.token = token_actual
                
                pila.pop()
                stack_arbol.pop()
                indice += 1
                self.estadisticas['tokens_procesados'] += 1
                
                if indice < len(tokens):
                    token_actual = tokens[indice]
                
            elif (X, token_actual) in self.tabla:
                # EXPANSIÓN: Aplicar regla gramatical
                produccion = self.tabla[(X, token_actual)]
                produccion_str = ' '.join(produccion) if produccion != ['ε'] else 'ε'
                accion = f"{X} -> {produccion_str}"
                
                pila.pop()
                stack_arbol.pop()
                self.estadisticas['producciones_aplicadas'] += 1
                
                if produccion != ['ε']:
                    # Crear nodos hijos y agregarlos al árbol
                    nuevos_nodos = []
                    for simbolo in produccion:
                        nuevo_nodo = Node(simbolo)
                        nuevos_nodos.append(nuevo_nodo)
                        nodo_actual.add_child(nuevo_nodo)
                        self.estadisticas['nodos_creados'] += 1
                    
                    # Agregar en orden inverso a la pila y stack_arbol
                    for simbolo in reversed(produccion):
                        pila.append(simbolo)
                    
                    for nodo in reversed(nuevos_nodos):
                        stack_arbol.append(nodo)
                
            else:
                # ERROR: No hay regla para la combinación
                error_msg = f"ERROR: No hay regla para ({X}, {token_actual})"
                
                return {
                    'CONCLUSION': "RECHAZADO :(",
                    'mensaje': error_msg,
                    'pasos': pasos,
                    'arbol': None,
                    'graphviz_code': None,
                    'estadisticas': self.estadisticas
                }
            
            # Guardar paso para posible debugging (sin imprimir)
            pasos.append((paso_num, pila_actual, entrada_restante, accion))
            paso_num += 1
            self.estadisticas['pasos_total'] += 1
        
        # RESULTADO FINAL: Solo aquí se imprime algo
        graphviz_code = self.generar_graphviz(self.raiz)
        
        return {
            'CONCLUSION': "ACEPTADO :)",
            'mensaje': "La entrada pertenece al lenguaje definido por la gramática",
            'pasos': pasos,
            'arbol': self.raiz,
            'graphviz_code': graphviz_code,
            'estadisticas': self.estadisticas
        }
def formatear_celda(contenido, ancho):
    """Formatea el contenido de una celda con el ancho especificado"""
    contenido_str = str(contenido)
    if len(contenido_str) > ancho:
        return contenido_str[:ancho-3] + "..."
    return contenido_str.ljust(ancho)
def imprimir_tabla(datos, titulos, anchos):
    """
    Imprime una tabla formateada.
    Compatible con la versión original.
    """
    # Imprimir encabezados
    linea = "|"
    for i, titulo in enumerate(titulos):
        ancho = anchos[i] if i < len(anchos) else 15
        linea += " " + formatear_celda(titulo, ancho) + " |"
    print(linea)
    
    # Imprimir separador
    linea_sep = "|"
    for ancho in anchos:
        linea_sep += "-" * (ancho + 2) + "|"
    print(linea_sep)
    
    # Imprimir datos
    for fila in datos:
        linea = "|"
        for i, valor in enumerate(fila):
            ancho = anchos[i] if i < len(anchos) else 15
            linea += " " + formatear_celda(valor_str := str(valor), ancho) + " |"
        print(linea)
def mostrar_instrucciones():
    """Muestra instrucciones para visualizar el árbol"""
    print("\n" + "="*60)
    print("INSTRUCCIONES PARA VISUALIZAR EL ÁRBOL SINTÁCTICO")
    print("="*60)
    print("1. Copia el código DOT generado arriba")
    print("2. Ve a https://dreampuf.github.io/GraphvizOnline/")
    print("3. Pega el código en el editor")
    print("4. ¡Disfruta de la visualización de tu árbol sintáctico!")
    print("="*60)
# FUNCIONES DE COMPATIBILIDAD (mantener para no romper imports existentes)
def crear_nodo(symbol, children=None, token=None):
    """Función de compatibilidad para crear nodos"""
    return Node(symbol, children, token)
def crear_analizador(archivo_tabla):
    """Función de compatibilidad para crear analizador"""
    return AnalizadorSintacticoLL(archivo_tabla)