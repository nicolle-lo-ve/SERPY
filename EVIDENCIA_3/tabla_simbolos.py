class Simbolo:
    """Clase para representar un símbolo en la tabla de símbolos"""
    
    def __init__(self, categoria, tipo, nombre, ambito, declarada_en=None, valor=None):
        """
        Inicializa un símbolo.
        
        Args:
            categoria (str): 'variable', 'funcion', 'parametro', 'constante'
            tipo (str): Tipo de dato ('int', 'float', 'string', 'boolean', 'void')
            nombre (str): Nombre del símbolo
            ambito (str): Ámbito donde se declara
            declarada_en (int): Línea de declaración
            valor: Valor inicial si es una constante
        """
        self.categoria = categoria
        self.tipo = tipo
        self.nombre = nombre
        self.ambito = ambito
        self.declarada_en = declarada_en
        self.valor = valor
        self.referencias = []
        self.inicializada = False
        self.usada = False
        self.parametros = [] if categoria == 'funcion' else None
        self.tipo_retorno = 'void' if categoria == 'funcion' else None
        
    def agregar_referencia(self, linea):
        """Registra una referencia al símbolo"""
        if linea not in self.referencias:
            self.referencias.append(linea)
        self.usada = True
        
    def agregar_parametro(self, nombre_param, tipo_param):
        """Agrega un parámetro a una función"""
        if self.categoria == 'funcion':
            self.parametros.append((nombre_param, tipo_param))
            
    def set_tipo_retorno(self, tipo):
        """Establece el tipo de retorno de una función"""
        if self.categoria == 'funcion':
            self.tipo_retorno = tipo
        
    def __str__(self):
        if self.categoria == 'funcion':
            params = f"({','.join([f'{p[0]}:{p[1]}' for p in self.parametros])})" if self.parametros else "()"
            return f"{self.nombre}: {self.categoria}<{self.tipo_retorno}>{params} @{self.ambito}"
        elif self.valor is not None:
            return f"{self.nombre}: {self.categoria}<{self.tipo}> = {self.valor} @{self.ambito}"
        else:
            return f"{self.nombre}: {self.categoria}<{self.tipo}> @{self.ambito}"

class TablaSimbolos:
    """Tabla de símbolos con manejo de ámbitos anidados"""
    
    def __init__(self):
        self.tabla = {}  # clave: "ambito::nombre" -> Simbolo
        self.pila_ambitos = ["global"]  # Pila de ámbitos
        self.errores = []
        self.advertencias = []
        self.contador_ambitos = 0
        
        # Funciones predefinidas del sistema
        self._agregar_funciones_predefinidas()
        
    def _agregar_funciones_predefinidas(self):
        """Agrega funciones predefinidas del sistema"""
        # Función imprimir
        imprimir = Simbolo('funcion', 'void', 'imprimir', 'global', 0)
        imprimir.parametros = [('valor', 'any')]  # Acepta cualquier tipo
        imprimir.tipo_retorno = 'void'
        self.tabla['global::imprimir'] = imprimir
        
    def entrar_ambito(self, nombre_ambito=None):
        """Entra a un nuevo ámbito"""
        if nombre_ambito is None:
            self.contador_ambitos += 1
            nombre_ambito = f"bloque_{self.contador_ambitos}"
        self.pila_ambitos.append(nombre_ambito)
        
    def salir_ambito(self):
        """Sale del ámbito actual"""
        if len(self.pila_ambitos) > 1:
            self.pila_ambitos.pop()
            
    def ambito_actual(self):
        """Obtiene el ámbito actual"""
        return self.pila_ambitos[-1]
        
    def obtener_clave_completa(self, nombre, ambito=None):
        """Genera la clave completa para un símbolo"""
        if ambito is None:
            ambito = self.ambito_actual()
        return f"{ambito}::{nombre}"
        
    def agregar(self, simbolo):
        """Agrega un símbolo a la tabla"""
        clave = self.obtener_clave_completa(simbolo.nombre, simbolo.ambito)
        
        # Verificar si ya existe en el mismo ámbito
        if clave in self.tabla:
            self.errores.append(
                f"Error semantico: Variable '{simbolo.nombre}' ya declarada en el ambito '{simbolo.ambito}'"
                + (f" (linea {simbolo.declarada_en})" if simbolo.declarada_en else "")
            )
            return False
            
        self.tabla[clave] = simbolo
        simbolo.inicializada = True
        return True
        
    def buscar(self, nombre, linea_referencia=None):
        """
        Busca un símbolo por nombre, siguiendo la cadena de ámbitos.
        Retorna el símbolo encontrado o None si no existe.
        """
        # Buscar en orden: ámbito actual hacia global
        for ambito in reversed(self.pila_ambitos):
            clave = self.obtener_clave_completa(nombre, ambito)
            if clave in self.tabla:
                simbolo = self.tabla[clave]
                if linea_referencia:
                    simbolo.agregar_referencia(linea_referencia)
                return simbolo
        
        # Si no se encuentra, agregar error
        if linea_referencia:
            self.errores.append(
                f"Error semantico: Variable '{nombre}' no declarada (linea {linea_referencia})"
            )
        return None
        
    def buscar_en_ambito_actual(self, nombre):
        """Busca un símbolo solo en el ámbito actual"""
        clave = self.obtener_clave_completa(nombre)
        return self.tabla.get(clave, None)
        
    def verificar_tipos_compatibles(self, tipo1, tipo2):
        """Verifica si dos tipos son compatibles para asignación"""
        if tipo1 == tipo2:
            return True
            
        # Promociones automáticas permitidas
        promociones = {
            ('int', 'float'): True,    # int puede promocionarse a float
            ('boolean', 'int'): True,  # boolean puede promocionarse a int
        }
        
        return promociones.get((tipo2, tipo1), False)
        
    def inferir_tipo_operacion(self, tipo1, tipo2, operador, linea=None):
        """
        Infiere el tipo resultado de una operación binaria.
        Retorna el tipo resultado o None si la operación es inválida.
        """
        tipos_numericos = {'int', 'float'}
        
        # Operaciones aritméticas
        if operador in {'+', '-', '*', '/', '^', 'MAS', 'MENOS', 'MULT', 'DIV', 'POTENCIA'}:
            if tipo1 in tipos_numericos and tipo2 in tipos_numericos:
                # Promoción de tipos: si uno es float, el resultado es float
                if 'float' in (tipo1, tipo2):
                    return 'float'
                return 'int'
            else:
                if linea:
                    self.errores.append(
                        f"Error de tipos en linea {linea}: Operacion aritmetica '{operador}' "
                        f"no valida entre {tipo1} y {tipo2}"
                    )
                return None
                
        # Operaciones de comparación
        elif operador in {'==', '!=', '<', '>', '<=', '>=', 'IGUAL_IGUAL', 'DIFERENTE', 
                         'MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL'}:
            if tipo1 in tipos_numericos and tipo2 in tipos_numericos:
                return 'boolean'
            elif tipo1 == tipo2:  # Mismos tipos se pueden comparar
                return 'boolean'
            else:
                if linea:
                    self.errores.append(
                        f"Error de tipos en linea {linea}: Comparacion '{operador}' "
                        f"no valida entre {tipo1} y {tipo2}"
                    )
                return None
                
        # Operaciones lógicas
        elif operador in {'&&', '||', 'Y_LOGICO', 'O_LOGICO'}:
            if tipo1 == 'boolean' and tipo2 == 'boolean':
                return 'boolean'
            else:
                if linea:
                    self.errores.append(
                        f"Error de tipos en linea {linea}: Operacion logica '{operador}' "
                        f"requiere operandos booleanos, encontrados {tipo1} y {tipo2}"
                    )
                return None
                
        return None
        
    def verificar_asignacion(self, nombre_var, tipo_expresion, linea):
        """Verifica que una asignación sea válida"""
        simbolo = self.buscar(nombre_var, linea)
        if not simbolo:
            return False
            
        if simbolo.categoria != 'variable' and simbolo.categoria != 'parametro':
            self.errores.append(
                f"Error semantico en linea {linea}: '{nombre_var}' no es una variable"
            )
            return False
            
        if not self.verificar_tipos_compatibles(simbolo.tipo, tipo_expresion):
            self.errores.append(
                f"Error de tipos en linea {linea}: No se puede asignar {tipo_expresion} "
                f"a variable '{nombre_var}' de tipo {simbolo.tipo}"
            )
            return False
            
        return True
        
    def verificar_llamada_funcion(self, nombre_funcion, tipos_argumentos, linea):
        """Verifica que una llamada a función sea válida"""
        funcion = self.buscar(nombre_funcion, linea)
        if not funcion:
            return None
            
        if funcion.categoria != 'funcion':
            self.errores.append(
                f"Error semantico en linea {linea}: '{nombre_funcion}' no es una funcion"
            )
            return None
            
        # Verificar número de argumentos
        if len(tipos_argumentos) != len(funcion.parametros):
            self.errores.append(
                f"Error semantico en linea {linea}: Funcion '{nombre_funcion}' "
                f"espera {len(funcion.parametros)} argumentos, se proporcionaron {len(tipos_argumentos)}"
            )
            return None
            
        # Verificar tipos de argumentos
        for i, (tipo_arg, (_, tipo_param)) in enumerate(zip(tipos_argumentos, funcion.parametros)):
            if tipo_param == 'any':  # Parámetros que aceptan cualquier tipo
                continue
            if not self.verificar_tipos_compatibles(tipo_param, tipo_arg):
                self.errores.append(
                    f"Error de tipos en linea {linea}: Argumento {i+1} de '{nombre_funcion}' "
                    f"esperado {tipo_param}, encontrado {tipo_arg}"
                )
                return None
                
        return funcion.tipo_retorno
        
    def imprimir_tabla(self):
        """Imprime la tabla de símbolos de forma organizada"""
        print("\n" + "="*130)
        print("TABLA DE SIMBOLOS")
        print("="*130)
        
        if not self.tabla:
            print("La tabla de simbolos esta vacia")
            return
        
        # Encabezados
        print(f"{'Nombre':<20} {'Categoria':<12} {'Tipo':<12} {'Ambito':<15} {'Linea':<8} {'Usado':<8} {'Detalles':<25}")
        print("-" * 130)
        
        # Organizar por ámbitos
        simbolos_por_ambito = {}
        for simbolo in self.tabla.values():
            if simbolo.ambito not in simbolos_por_ambito:
                simbolos_por_ambito[simbolo.ambito] = []
            simbolos_por_ambito[simbolo.ambito].append(simbolo)
        
        # Mostrar por ámbitos
        for ambito in sorted(simbolos_por_ambito.keys()):
            if ambito != 'global':
                print(f"\n--- Ambito: {ambito} ---")
            
            for simbolo in sorted(simbolos_por_ambito[ambito], key=lambda s: s.nombre):
                usado = "Si" if simbolo.usada else "No"
                linea = str(simbolo.declarada_en) if simbolo.declarada_en else "-"
                
                # Detalles adicionales
                detalles = ""
                if simbolo.categoria == 'funcion':
                    params = f"({len(simbolo.parametros)} params)" if simbolo.parametros else "(0 params)"
                    detalles = f"{params} -> {simbolo.tipo_retorno}"
                elif simbolo.valor is not None:
                    detalles = f"= {simbolo.valor}"
                elif simbolo.referencias:
                    detalles = f"refs: {len(simbolo.referencias)}"
                
                print(f"{simbolo.nombre:<20} {simbolo.categoria:<12} {simbolo.tipo:<12} "
                      f"{simbolo.ambito:<15} {linea:<8} {usado:<8} {detalles:<25}")
    
    def generar_reporte_errores(self):
        """Genera un reporte completo de errores y advertencias"""
        if not self.errores and not self.advertencias:
            print("\nNo se encontraron errores semanticos.")
            return True
            
        print(f"\n--- REPORTE DE ERRORES SEMANTICOS ---")
        print(f"Total de errores: {len(self.errores)}")
        print(f"Total de advertencias: {len(self.advertencias)}")
        
        if self.errores:
            print("\nERRORES:")
            for i, error in enumerate(self.errores, 1):
                print(f"  {i}. {error}")
                
        if self.advertencias:
            print("\nADVERTENCIAS:")
            for i, advertencia in enumerate(self.advertencias, 1):
                print(f"  {i}. {advertencia}")
                
        return len(self.errores) == 0
    
    def validar_tabla(self):
        """Valida la consistencia de la tabla de símbolos"""
        # Verificar variables no usadas
        for simbolo in self.tabla.values():
            if simbolo.categoria == 'variable' and not simbolo.usada and simbolo.ambito != 'global':
                self.advertencias.append(
                    f"Advertencia: Variable '{simbolo.nombre}' declarada pero no usada en ambito '{simbolo.ambito}'"
                )
        
        return len(self.errores) == 0
    
    def obtener_estadisticas(self):
        """Devuelve estadísticas detalladas de la tabla"""
        variables = sum(1 for s in self.tabla.values() if s.categoria == 'variable')
        funciones = sum(1 for s in self.tabla.values() if s.categoria == 'funcion')
        parametros = sum(1 for s in self.tabla.values() if s.categoria == 'parametro')
        constantes = sum(1 for s in self.tabla.values() if s.categoria == 'constante')
        
        variables_usadas = sum(1 for s in self.tabla.values() 
                              if s.categoria == 'variable' and s.usada)
        
        return {
            'total_simbolos': len(self.tabla),
            'variables': variables,
            'variables_usadas': variables_usadas,
            'funciones': funciones,
            'parametros': parametros,
            'constantes': constantes,
            'errores': len(self.errores),
            'advertencias': len(self.advertencias),
            'ambitos_totales': len(set(s.ambito for s in self.tabla.values()))
        }
