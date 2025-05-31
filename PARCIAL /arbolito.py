# arbolito.py - VERSIÓN CON MANEJO COMPLETO DE ERRORES
# Analizador sintáctico LL(1) robusto con detección y reporte detallado de errores
import csv
import sys
import io
from error_manager import get_error_manager, ErrorType, ErrorSeverity
import traceback
import os
# Configuración universal de codificación
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
class Node:
    def __init__(self, symbol, children=None, token=None, linea=None, columna=None):
        """
        Clase para representar nodos del árbol sintáctico con validación.
        
        Args:
            symbol (str): Símbolo gramatical (terminal o no terminal)
            children (list[Node], optional): Nodos hijos. Defaults to None.
            token (str, optional): Token asociado si es terminal. Defaults to None.
            linea (int, optional): Línea del token en el código fuente.
            columna (int, optional): Columna del token en el código fuente.
        """
        self.error_mgr = get_error_manager()
        
        # Validar parámetros
        if not symbol:
            self.error_mgr.add_warning(
                "Nodo creado sin símbolo",
                "Constructor de nodos",
                suggestion="Especifica un símbolo válido para el nodo"
            )
            symbol = "NODO_SIN_SIMBOLO"
        
        self.symbol = symbol
        self.children = children if children is not None else []
        self.token = token
        self.linea = linea
        self.columna = columna
        self.id = id(self)  # Identificador único para graphviz
        
        # Validar children si se proporcionan
        if self.children:
            self._validar_hijos()
    
    def _validar_hijos(self):
        """Valida que los hijos sean nodos válidos."""
        try:
            hijos_validos = []
            for i, hijo in enumerate(self.children):
                if isinstance(hijo, Node):
                    hijos_validos.append(hijo)
                else:
                    self.error_mgr.add_warning(
                        f"Hijo inválido en posición {i} del nodo '{self.symbol}': no es un Node",
                        "Validador de nodos",
                        suggestion="Asegúrate de que todos los hijos sean objetos Node"
                    )
            
            self.children = hijos_validos
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error validando hijos del nodo '{self.symbol}': {str(e)}",
                "Validador de nodos"
            )
    
    def add_child(self, child_node):
        """Añade un nodo hijo con validación."""
        try:
            if not isinstance(child_node, Node):
                self.error_mgr.add_warning(
                    f"Intento de agregar hijo no válido al nodo '{self.symbol}'",
                    "Administrador de nodos",
                    suggestion="Solo agrega objetos Node como hijos"
                )
                return False
            
            self.children.append(child_node)
            return True
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error agregando hijo al nodo '{self.symbol}': {str(e)}",
                "Administrador de nodos"
            )
            return False
    
    def get_info(self):
        """Obtiene información detallada del nodo."""
        try:
            ubicacion = f" [{self.linea}:{self.columna}]" if self.linea and self.columna else ""
            return {
                'symbol': self.symbol,
                'token': self.token,
                'ubicacion': ubicacion,
                'num_hijos': len(self.children),
                'es_terminal': self.token is not None,
                'es_hoja': len(self.children) == 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def __repr__(self):
        try:
            ubicacion = f" [{self.linea}:{self.columna}]" if self.linea and self.columna else ""
            return f"{self.symbol} ({self.token}){ubicacion}" if self.token else f"{self.symbol}{ubicacion}"
        except Exception as e:
            return f"Node(ERROR: {str(e)})"
class AnalizadorSintacticoLL:
    def __init__(self, archivo_tabla):
        """Inicializa el analizador sintáctico con manejo de errores robusto."""
        self.error_mgr = get_error_manager()
        self.archivo_tabla = archivo_tabla
        self.tabla = {}
        self.raiz = None
        
        # Estadísticas detalladas
        self.estadisticas = {
            'nodos_creados': 0,
            'tokens_procesados': 0,
            'producciones_aplicadas': 0,
            'pasos_total': 0,
            'errores_sintacticos': 0,
            'tiempo_inicio': None,
            'tiempo_fin': None
        }
        
        # Cargar tabla LL1 con manejo de errores
        if not self._cargar_tabla_con_validacion():
            self.error_mgr.add_warning(
                "Analizador sintáctico creado sin tabla LL1 válida",
                "Constructor de analizador",
                suggestion="El análisis funcionará en modo limitado"
            )
    
    def _cargar_tabla_con_validacion(self):
        """Carga la tabla LL1 con validación exhaustiva."""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(self.archivo_tabla):
                self.error_mgr.add_file_error(
                    f"Archivo de tabla LL1 no encontrado: {self.archivo_tabla}",
                    self.archivo_tabla,
                    f"Crea el archivo {self.archivo_tabla} con la tabla LL1 válida"
                )
                return False
            
            # Verificar permisos de lectura
            if not os.access(self.archivo_tabla, os.R_OK):
                self.error_mgr.add_file_error(
                    f"Sin permisos para leer tabla LL1: {self.archivo_tabla}",
                    self.archivo_tabla,
                    f"Verifica los permisos del archivo {self.archivo_tabla}"
                )
                return False
            
            # Intentar cargar CSV
            tabla_cargada = self._cargar_tabla_csv()
            
            if not tabla_cargada:
                return False
            
            # Validar contenido de la tabla
            return self._validar_tabla_cargada()
            
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.ARCHIVO,
                ErrorSeverity.ERROR,
                f"Error cargando tabla LL1: {str(e)}",
                "Cargador de tabla",
                exception=e,
                suggestion="Verifica el formato del archivo de tabla LL1"
            )
            return False
    
    def _cargar_tabla_csv(self):
        """Carga la tabla CSV con manejo de errores detallado."""
        try:
            self.tabla = {}
            
            with open(self.archivo_tabla, newline='', encoding='utf-8') as csvfile:
                try:
                    reader = list(csv.reader(csvfile, delimiter=','))
                    
                    if not reader:
                        self.error_mgr.add_file_error(
                            "Archivo de tabla LL1 está vacío",
                            self.archivo_tabla,
                            "Agrega contenido válido al archivo de tabla"
                        )
                        return False
                    
                    if len(reader) < 2:
                        self.error_mgr.add_file_error(
                            "Archivo de tabla LL1 no tiene suficientes filas",
                            self.archivo_tabla,
                            "El archivo debe tener al menos una fila de encabezados y una de datos"
                        )
                        return False
                    
                    # Procesar encabezados (terminales)
                    terminales = reader[0][1:]  # Saltar la primera columna vacía
                    if not terminales:
                        self.error_mgr.add_file_error(
                            "No se encontraron terminales en la tabla LL1",
                            self.archivo_tabla,
                            "Verifica que la primera fila contenga los terminales"
                        )
                        return False
                    
                    # Procesar filas de datos
                    producciones_cargadas = 0
                    for fila_num, fila in enumerate(reader[1:], 2):
                        try:
                            if not fila:
                                continue  # Saltar filas vacías
                            
                            no_terminal = fila[0].strip()
                            if not no_terminal:
                                self.error_mgr.add_warning(
                                    f"Fila {fila_num} sin no-terminal en tabla LL1",
                                    "Parser de tabla",
                                    suggestion="Verifica que cada fila tenga un no-terminal"
                                )
                                continue
                            
                            # Procesar producciones para este no-terminal
                            for i, celda in enumerate(fila[1:]):
                                if i < len(terminales):
                                    terminal = terminales[i]
                                    produccion = celda.strip()
                                    
                                    if produccion:  # Solo agregar si hay producción
                                        try:
                                            lado_derecho = produccion.split() if produccion != 'ε' else ['ε']
                                            self.tabla[(no_terminal, terminal)] = lado_derecho
                                            producciones_cargadas += 1
                                        except Exception as e:
                                            self.error_mgr.add_warning(
                                                f"Error procesando producción '{produccion}' en fila {fila_num}: {str(e)}",
                                                "Parser de tabla"
                                            )
                                            
                        except Exception as e:
                            self.error_mgr.add_warning(
                                f"Error procesando fila {fila_num} de tabla LL1: {str(e)}",
                                "Parser de tabla"
                            )
                    
                    if producciones_cargadas == 0:
                        self.error_mgr.add_file_error(
                            "No se cargaron producciones válidas de la tabla LL1",
                            self.archivo_tabla,
                            "Verifica el contenido y formato de la tabla"
                        )
                        return False
                    
                    print(f"✅ Tabla LL1 cargada: {producciones_cargadas} producciones, {len(terminales)} terminales")
                    return True
                    
                except csv.Error as e:
                    self.error_mgr.add_file_error(
                        f"Error de formato CSV en tabla LL1: {str(e)}",
                        self.archivo_tabla,
                        "Verifica que el archivo sea un CSV válido"
                    )
                    return False
                    
        except FileNotFoundError:
            # Ya manejado en _cargar_tabla_con_validacion
            return False
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.ARCHIVO,
                ErrorSeverity.ERROR,
                f"Error inesperado cargando tabla CSV: {str(e)}",
                "Cargador CSV",
                exception=e
            )
            return False
    
    def _validar_tabla_cargada(self):
        """Valida la coherencia de la tabla LL1 cargada."""
        try:
            if not self.tabla:
                self.error_mgr.add_file_error(
                    "Tabla LL1 cargada está vacía",
                    self.archivo_tabla,
                    "Verifica que el archivo contenga producciones válidas"
                )
                return False
            
            # Obtener terminales y no-terminales únicos
            terminales = set()
            no_terminales = set()
            
            for (nt, t), produccion in self.tabla.items():
                no_terminales.add(nt)
                terminales.add(t)
            
            # Verificar que hay un símbolo inicial
            if 'PROGRAMA' not in no_terminales:
                self.error_mgr.add_warning(
                    "No se encontró símbolo inicial 'PROGRAMA' en la tabla LL1",
                    "Validador de tabla",
                    suggestion="Asegúrate de que 'PROGRAMA' esté en los no-terminales"
                )
            
            # Verificar producciones básicas
            if '$' not in terminales:
                self.error_mgr.add_warning(
                    "No se encontró símbolo de fin '$' en la tabla LL1",
                    "Validador de tabla",
                    suggestion="Agrega el símbolo de fin '$' a los terminales"
                )
            
            print(f"📊 Validación LL1: {len(no_terminales)} no-terminales, {len(terminales)} terminales")
            return True
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error validando tabla LL1: {str(e)}",
                "Validador de tabla"
            )
            return True  # No es crítico si la validación falla
    def generar_graphviz(self, nodo_raiz):
        """Genera código DOT para visualizar en Graphviz con manejo de errores."""
        try:
            if not nodo_raiz:
                self.error_mgr.add_warning(
                    "Intento de generar Graphviz sin nodo raíz",
                    "Generador Graphviz",
                    suggestion="Asegúrate de que el análisis sintáctico sea exitoso"
                )
                return ""
            
            dot_code = "digraph ArbolSintactico {\n"
            dot_code += "    node [shape=box, style=filled, fillcolor=lightblue];\n"
            dot_code += "    rankdir=TB;\n\n"
            
            nodos_procesados = set()
            
            def agregar_nodo(nodo, padre_id=None):
                nonlocal dot_code
                
                try:
                    # Evitar nodos duplicados
                    if nodo.id in nodos_procesados:
                        return
                    nodos_procesados.add(nodo.id)
                    
                    # Crear etiqueta del nodo con información segura
                    if hasattr(nodo, 'token') and nodo.token:
                        ubicacion = f"\\n[{nodo.linea}:{nodo.columna}]" if nodo.linea and nodo.columna else ""
                        etiqueta = f"{nodo.symbol}\\n'{nodo.token}'{ubicacion}"
                    else:
                        etiqueta = nodo.symbol
                    
                    # Escapar caracteres especiales
                    etiqueta = etiqueta.replace('"', '\\"').replace('\n', '\\n')
                    
                    dot_code += f'    "{nodo.id}" [label="{etiqueta}"];\n'
                    
                    if padre_id:
                        dot_code += f'    "{padre_id}" -> "{nodo.id}";\n'
                    
                    # Procesar hijos de forma segura
                    if hasattr(nodo, 'children'):
                        for hijo in nodo.children:
                            if isinstance(hijo, Node):
                                agregar_nodo(hijo, nodo.id)
                            else:
                                self.error_mgr.add_warning(
                                    f"Hijo inválido encontrado en nodo '{nodo.symbol}'",
                                    "Generador Graphviz"
                                )
                                
                except Exception as e:
                    self.error_mgr.add_warning(
                        f"Error procesando nodo para Graphviz: {str(e)}",
                        "Generador Graphviz"
                    )
            
            agregar_nodo(nodo_raiz)
            dot_code += "}\n"
            
            return dot_code
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error generando código Graphviz: {str(e)}",
                "Generador Graphviz",
                suggestion="Esto no afecta el análisis, solo la visualización"
            )
            return ""
    def analizar(self, tokens):
        """
        Realiza el análisis sintáctico LL(1) con manejo exhaustivo de errores.
        
        Args:
            tokens (list): Lista de tokens a analizar
            
        Returns:
            dict: Resultado del análisis con información completa
        """
        try:
            import time
            self.estadisticas['tiempo_inicio'] = time.time()
            
            # Validar entrada
            if not self._validar_entrada_analisis(tokens):
                return self._crear_resultado_error("Entrada inválida para análisis")
            
            # Reiniciar estadísticas
            self.estadisticas.update({
                'nodos_creados': 0,
                'tokens_procesados': 0,
                'producciones_aplicadas': 0,
                'pasos_total': 0,
                'errores_sintacticos': 0
            })
            
            # Preparar análisis
            tokens = tokens + ['$']  # Añadir símbolo de fin
            pila = ['$', 'PROGRAMA']
            indice = 0
            token_actual = tokens[indice]
            
            # Construir árbol
            stack_arbol = []
            self.raiz = Node('PROGRAMA')
            stack_arbol.append(self.raiz)
            self.estadisticas['nodos_creados'] += 1
            
            # Ejecutar análisis
            pasos = []
            paso_num = 1
            
            while pila[-1] != '$':
                try:
                    resultado_paso = self._procesar_paso_analisis(
                        pila, stack_arbol, tokens, indice, token_actual, paso_num
                    )
                    
                    if not resultado_paso['exito']:
                        return self._crear_resultado_error(
                            resultado_paso['mensaje'],
                            pasos,
                            resultado_paso.get('sugerencia')
                        )
                    
                    # Actualizar estado
                    indice = resultado_paso.get('nuevo_indice', indice)
                    if indice < len(tokens):
                        token_actual = tokens[indice]
                    
                    pasos.append(resultado_paso['paso_info'])
                    paso_num += 1
                    self.estadisticas['pasos_total'] += 1
                    
                except Exception as e:
                    self.estadisticas['errores_sintacticos'] += 1
                    error_msg = f"Error en paso {paso_num}: {str(e)}"
                    self.error_mgr.add_syntax_error(
                        error_msg,
                        suggestion="Verifica la estructura del código fuente"
                    )
                    return self._crear_resultado_error(error_msg, pasos)
            
            # Análisis exitoso
            self.estadisticas['tiempo_fin'] = time.time()
            return self._crear_resultado_exitoso(pasos)
            
        except Exception as e:
            self.estadisticas['errores_sintacticos'] += 1
            self.error_mgr.add_error(
                ErrorType.SINTACTICO,
                ErrorSeverity.CRITICO,
                f"Error crítico en análisis sintáctico: {str(e)}",
                "Analizador Sintáctico",
                exception=e,
                suggestion="Verifica la entrada y la tabla LL1"
            )
            return self._crear_resultado_error(f"Error crítico: {str(e)}")
    def _validar_entrada_analisis(self, tokens):
        """Valida la entrada para el análisis sintáctico."""
        try:
            if not tokens:
                self.error_mgr.add_syntax_error(
                    "Lista de tokens vacía para análisis sintáctico",
                    suggestion="Verifica que el análisis léxico haya sido exitoso"
                )
                return False
            
            if len(tokens) == 0:
                self.error_mgr.add_syntax_error(
                    "No hay tokens para analizar",
                    suggestion="Asegúrate de que el código fuente no esté vacío"
                )
                return False
            
            # Verificar que los tokens sean válidos
            for i, token in enumerate(tokens[:5]):  # Verificar primeros 5
                if not isinstance(token, str):
                    self.error_mgr.add_syntax_error(
                        f"Token inválido en posición {i}: {type(token)}",
                        suggestion="Verifica que todos los tokens sean strings"
                    )
                    return False
            
            if not self.tabla:
                self.error_mgr.add_warning(
                    "Análisis sintáctico sin tabla LL1 válida",
                    "Analizador Sintáctico",
                    suggestion="Se usará modo simulado"
                )
            
            return True
            
        except Exception as e:
            self.error_mgr.add_syntax_error(
                f"Error validando entrada: {str(e)}",
                suggestion="Verifica la estructura de los tokens"
            )
            return False
    def _procesar_paso_analisis(self, pila, stack_arbol, tokens, indice, token_actual, paso_num):
        """Procesa un paso individual del análisis sintáctico."""
        try:
            X = pila[-1]
            nodo_actual = stack_arbol[-1] if stack_arbol else None
            
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            
            if X == token_actual:
                # COINCIDENCIA: Emparejar terminal
                accion = f"Emparejar {X}"
                
                # Actualizar nodo terminal
                if nodo_actual:
                    nodo_actual.token = token_actual
                
                pila.pop()
                stack_arbol.pop()
                nuevo_indice = indice + 1
                self.estadisticas['tokens_procesados'] += 1
                
                return {
                    'exito': True,
                    'nuevo_indice': nuevo_indice,
                    'paso_info': (paso_num, pila_actual, entrada_restante, accion)
                }
                
            elif (X, token_actual) in self.tabla:
                # EXPANSIÓN: Aplicar regla gramatical
                produccion = self.tabla[(X, token_actual)]
                produccion_str = ' '.join(produccion) if produccion != ['ε'] else 'ε'
                accion = f"{X} -> {produccion_str}"
                
                pila.pop()
                stack_arbol.pop()
                self.estadisticas['producciones_aplicadas'] += 1
                
                if produccion != ['ε']:
                    # Crear nodos hijos
                    nuevos_nodos = []
                    for simbolo in produccion:
                        nuevo_nodo = Node(simbolo)
                        nuevos_nodos.append(nuevo_nodo)
                        if nodo_actual:
                            nodo_actual.add_child(nuevo_nodo)
                        self.estadisticas['nodos_creados'] += 1
                    
                    # Agregar en orden inverso
                    for simbolo in reversed(produccion):
                        pila.append(simbolo)
                    
                    for nodo in reversed(nuevos_nodos):
                        stack_arbol.append(nodo)
                
                return {
                    'exito': True,
                    'nuevo_indice': indice,  # No cambiar índice
                    'paso_info': (paso_num, pila_actual, entrada_restante, accion)
                }
                
            else:
                # ERROR: No hay regla
                error_msg = f"No hay regla para ({X}, {token_actual})"
                sugerencia = f"Verifica la sintaxis cerca del token '{token_actual}'"
                
                self.estadisticas['errores_sintacticos'] += 1
                self.error_mgr.add_syntax_error(
                    error_msg,
                    suggestion=sugerencia
                )
                
                return {
                    'exito': False,
                    'mensaje': error_msg,
                    'sugerencia': sugerencia
                }
                
        except Exception as e:
            error_msg = f"Error procesando paso {paso_num}: {str(e)}"
            self.error_mgr.add_syntax_error(
                error_msg,
                suggestion="Verifica la estructura del código"
            )
            return {
                'exito': False,
                'mensaje': error_msg
            }
    def _crear_resultado_exitoso(self, pasos):
        """Crea resultado exitoso del análisis."""
        try:
            graphviz_code = self.generar_graphviz(self.raiz)
            
            # Calcular tiempo de ejecución
            tiempo_ejecucion = None
            if (self.estadisticas.get('tiempo_inicio') and 
                self.estadisticas.get('tiempo_fin')):
                tiempo_ejecucion = self.estadisticas['tiempo_fin'] - self.estadisticas['tiempo_inicio']
            
            return {
                'CONCLUSION': "ACEPTADO :)",
                'mensaje': "La entrada pertenece al lenguaje definido por la gramática",
                'pasos': pasos,
                'arbol': self.raiz,
                'graphviz_code': graphviz_code,
                'estadisticas': self.estadisticas.copy(),
                'tiempo_ejecucion': tiempo_ejecucion
            }
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error creando resultado exitoso: {str(e)}",
                "Generador de resultados"
            )
            # Resultado mínimo en caso de error
            return {
                'CONCLUSION': "ACEPTADO :)",
                'mensaje': "Análisis exitoso (con advertencias)",
                'pasos': pasos,
                'arbol': self.raiz,
                'graphviz_code': "",
                'estadisticas': self.estadisticas.copy()
            }
    def _crear_resultado_error(self, mensaje, pasos=None, sugerencia=None):
        """Crea resultado de error del análisis."""
        try:
            return {
                'CONCLUSION': "RECHAZADO :(",
                'mensaje': mensaje,
                'pasos': pasos or [],
                'arbol': None,
                'graphviz_code': None,
                'estadisticas': self.estadisticas.copy(),
                'sugerencia': sugerencia
            }
            
        except Exception as e:
            # Resultado de fallback si hasta esto falla
            return {
                'CONCLUSION': "RECHAZADO :(",
                'mensaje': f"Error crítico: {str(e)}",
                'pasos': [],
                'arbol': None,
                'graphviz_code': None,
                'estadisticas': {}
            }
# Funciones de utilidad con manejo de errores
def formatear_celda(contenido, ancho):
    """Formatea el contenido de una celda con el ancho especificado."""
    try:
        contenido_str = str(contenido)
        if len(contenido_str) > ancho:
            return contenido_str[:ancho-3] + "..."
        return contenido_str.ljust(ancho)
    except Exception:
        return "ERROR".ljust(ancho)
def imprimir_tabla(datos, titulos, anchos):
    """Imprime una tabla formateada con manejo de errores."""
    try:
        error_mgr = get_error_manager()
        
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
        for fila_num, fila in enumerate(datos):
            try:
                linea = "|"
                for i, valor in enumerate(fila):
                    ancho = anchos[i] if i < len(anchos) else 15
                    linea += " " + formatear_celda(valor, ancho) + " |"
                print(linea)
            except Exception as e:
                error_mgr.add_warning(
                    f"Error imprimiendo fila {fila_num}: {str(e)}",
                    "Impresor de tabla"
                )
                print(f"| ERROR en fila {fila_num}: {str(e)}")
                
    except Exception as e:
        print(f"Error crítico imprimiendo tabla: {str(e)}")
def mostrar_instrucciones():
    """Muestra instrucciones para visualizar el árbol."""
    try:
        print("\n" + "="*60)
        print("INSTRUCCIONES PARA VISUALIZAR EL ÁRBOL SINTÁCTICO")
        print("="*60)
        print("1. Copia el código DOT generado")
        print("2. Ve a https://dreampuf.github.io/GraphvizOnline/")
        print("3. Pega el código en el editor")
        print("4. ¡Disfruta de la visualización de tu árbol sintáctico!")
        print("="*60)
    except Exception as e:
        print(f"Error mostrando instrucciones: {str(e)}")
# FUNCIONES DE COMPATIBILIDAD
def crear_nodo(symbol, children=None, token=None):
    """Función de compatibilidad para crear nodos."""
    try:
        return Node(symbol, children, token)
    except Exception as e:
        error_mgr = get_error_manager()
        error_mgr.add_warning(
            f"Error creando nodo con función de compatibilidad: {str(e)}",
            "Función de compatibilidad"
        )
        return None
def crear_analizador(archivo_tabla):
    """Función de compatibilidad para crear analizador."""
    try:
        return AnalizadorSintacticoLL(archivo_tabla)
    except Exception as e:
        error_mgr = get_error_manager()
        error_mgr.add_error(
            ErrorType.SISTEMA,
            ErrorSeverity.ERROR,
            f"Error creando analizador con función de compatibilidad: {str(e)}",
            "Función de compatibilidad",
            exception=e
        )
        return None
