from tabla_simbolos import TablaSimbolos, Simbolo

class AnalizadorSemantico:
    """Analizador semántico completo con verificación de tipos y manejo de ámbitos"""
    
    def __init__(self):
        self.tabla = TablaSimbolos()
        self.tokens_originales = []
        self.funciones_definidas = set()
        self.en_funcion = None
        self.tipo_retorno_esperado = None
        
    def construir_tabla_simbolos(self, tokens, arbol):
        """
        Construye la tabla de símbolos y realiza análisis semántico completo
        """
        try:
            # Guardar tokens originales para obtener información de línea
            self.tokens_originales = tokens
            
            # Paso 1: Primera pasada - Recolectar declaraciones
            print("Realizando primera pasada: recolectando declaraciones...")
            self._primera_pasada(arbol)
            
            # Paso 2: Segunda pasada - Verificar tipos y referencias
            print("Realizando segunda pasada: verificando tipos y referencias...")
            self._segunda_pasada(arbol)
            
            # Paso 3: Validaciones finales
            self.tabla.validar_tabla()
            
            return self.tabla
            
        except Exception as e:
            import traceback
            print(f"Error en analisis semantico: {e}")
            traceback.print_exc()
            return None
    
    def _primera_pasada(self, nodo, nivel=0):
        """Primera pasada: recolecta todas las declaraciones"""
        if not nodo:
            return
            
        # Manejo del nodo programa
        if nodo.symbol == 'PROGRAMA':
            for hijo in nodo.children:
                self._primera_pasada(hijo, nivel)
                
        # Declaración de variable
        elif self._es_declaracion_variable(nodo):
            self._procesar_declaracion_variable(nodo)
            
        # Definición de función
        elif self._es_definicion_funcion(nodo):
            self._procesar_definicion_funcion(nodo)
            
        # Bloques (entrar/salir de ámbito)
        elif nodo.symbol == 'bloque':
            self.tabla.entrar_ambito()
            for hijo in nodo.children:
                self._primera_pasada(hijo, nivel + 1)
            self.tabla.salir_ambito()
            
        # Otros nodos
        else:
            for hijo in nodo.children:
                self._primera_pasada(hijo, nivel)
    
    def _segunda_pasada(self, nodo):
        """Segunda pasada: verifica tipos, referencias y semántica"""
        if not nodo:
            return
            
        # Manejo del nodo programa
        if nodo.symbol == 'PROGRAMA':
            for hijo in nodo.children:
                self._segunda_pasada(hijo)
                
        # Asignaciones
        elif self._es_asignacion(nodo):
            self._verificar_asignacion(nodo)
            
        # Llamadas a función
        elif self._es_llamada_funcion(nodo):
            self._verificar_llamada_funcion(nodo)
            
        # Referencias a variables
        elif nodo.symbol == 'IDENTIFICADOR' and nodo.token:
            self._verificar_referencia_variable(nodo)
            
        # Expresiones
        elif nodo.symbol.startswith('exp_') or nodo.symbol == 'expresion':
            self._verificar_expresion(nodo)
            
        # Sentencias de control
        elif nodo.symbol == 'si_sentencia':
            self._verificar_sentencia_si(nodo)
        elif nodo.symbol == 'mientras_sentencia':
            self._verificar_sentencia_mientras(nodo)
        elif nodo.symbol == 'para_sentencia':
            self._verificar_sentencia_para(nodo)
            
        # Retorno
        elif nodo.symbol == 'RETORNAR':
            self._verificar_retorno(nodo)
            
        # Bloques
        elif nodo.symbol == 'bloque':
            self.tabla.entrar_ambito()
            for hijo in nodo.children:
                self._segunda_pasada(hijo)
            self.tabla.salir_ambito()
            
        # Otros nodos
        else:
            for hijo in nodo.children:
                self._segunda_pasada(hijo)
    
    def _es_declaracion_variable(self, nodo):
        """Determina si un nodo es una declaración de variable"""
        if nodo.symbol != 'sentencia':
            return False
        return any(hijo.symbol == 'VAR' for hijo in nodo.children)
    
    def _es_definicion_funcion(self, nodo):
        """Determina si un nodo es una definición de función"""
        return nodo.symbol == 'funcion_def'
    
    def _es_asignacion(self, nodo):
        """Determina si un nodo es una asignación"""
        if nodo.symbol != 'sentencia':
            return False
        # Buscar patrón: IDENTIFICADOR IGUAL expresion
        for i, hijo in enumerate(nodo.children):
            if hijo.symbol == 'IDENTIFICADOR' and i + 1 < len(nodo.children):
                siguiente = nodo.children[i + 1]
                if siguiente.symbol == 'asignacion_o_llamada':
                    for nieto in siguiente.children:
                        if nieto.symbol == 'IGUAL':
                            return True
        return False
    
    def _es_llamada_funcion(self, nodo):
        """Determina si un nodo es una llamada a función"""
        if nodo.symbol == 'IMPRIMIR':
            return True
        # Buscar patrón en asignacion_o_llamada con paréntesis
        if nodo.symbol == 'asignacion_o_llamada':
            return any(hijo.symbol == 'PAR_IZQ' for hijo in nodo.children)
        return False
    
    def _procesar_declaracion_variable(self, nodo):
        """Procesa una declaración de variable"""
        nombre = None
        tipo_inferido = 'unknown'
        linea = None
        
        # Extraer información de la declaración
        for i, hijo in enumerate(nodo.children):
            if hijo.symbol == 'IDENTIFICADOR' and hijo.token:
                nombre = hijo.token
                linea = hijo.linea
            elif hijo.symbol == 'expresion':
                tipo_inferido = self._inferir_tipo_expresion(hijo)
        
        if not nombre:
            self.tabla.errores.append("Error: Declaracion de variable sin nombre")
            return
            
        # Crear símbolo
        simbolo = Simbolo('variable', tipo_inferido, nombre, self.tabla.ambito_actual(), linea)
        self.tabla.agregar(simbolo)
    
    def _procesar_definicion_funcion(self, nodo):
        """Procesa una definición de función"""
        nombre_funcion = None
        parametros = []
        linea = None
        
        # Extraer nombre de función
        for hijo in nodo.children:
            if hijo.symbol == 'IDENTIFICADOR' and hijo.token:
                nombre_funcion = hijo.token
                linea = hijo.linea
                break
                
        if not nombre_funcion:
            self.tabla.errores.append("Error: Funcion sin nombre")
            return
            
        # Extraer parámetros
        for hijo in nodo.children:
            if hijo.symbol == 'parametros':
                parametros = self._extraer_parametros(hijo)
                break
        
        # Crear símbolo de función (tipo de retorno se inferirá después)
        simbolo_funcion = Simbolo('funcion', 'void', nombre_funcion, 'global', linea)
        simbolo_funcion.parametros = parametros
        simbolo_funcion.tipo_retorno = 'void'  # Por defecto
        
        if not self.tabla.agregar(simbolo_funcion):
            return
        
        # Entrar al ámbito de la función
        self.tabla.entrar_ambito(nombre_funcion)
        self.en_funcion = nombre_funcion
        self.funciones_definidas.add(nombre_funcion)
        
        # Agregar parámetros como variables locales
        for nombre_param, tipo_param in parametros:
            simbolo_param = Simbolo('parametro', tipo_param, nombre_param, nombre_funcion, linea)
            self.tabla.agregar(simbolo_param)
        
        # Procesar cuerpo de la función
        for hijo in nodo.children:
            if hijo.symbol == 'bloque':
                self._primera_pasada(hijo)
                break
        
        # Salir del ámbito
        self.tabla.salir_ambito()
        self.en_funcion = None
    
    def _extraer_parametros(self, nodo_parametros):
        """Extrae la lista de parámetros de una función"""
        parametros = []
        
        def recorrer_parametros(nodo):
            for hijo in nodo.children:
                if hijo.symbol == 'IDENTIFICADOR' and hijo.token:
                    # Por defecto asignamos tipo 'any', se puede mejorar con análisis de tipos
                    parametros.append((hijo.token, 'any'))
                elif hijo.children:
                    recorrer_parametros(hijo)
        
        recorrer_parametros(nodo_parametros)
        return parametros
    
    def _verificar_asignacion(self, nodo):
        """Verifica una asignación de variable"""
        nombre_var = None
        expresion = None
        linea = None
        
        # Extraer información de la asignación
        for i, hijo in enumerate(nodo.children):
            if hijo.symbol == 'IDENTIFICADOR' and hijo.token:
                nombre_var = hijo.token
                linea = hijo.linea
            elif hijo.symbol == 'asignacion_o_llamada':
                for nieto in hijo.children:
                    if nieto.symbol == 'expresion':
                        expresion = nieto
                        break
        
        if not nombre_var or not expresion:
            return
            
        # Verificar tipo de la expresión
        tipo_expresion = self._inferir_tipo_expresion(expresion)
        
        # Verificar la asignación
        self.tabla.verificar_asignacion(nombre_var, tipo_expresion, linea)
    
    def _verificar_llamada_funcion(self, nodo):
        """Verifica una llamada a función"""
        if nodo.symbol == 'IMPRIMIR':
            # Llamada a función imprimir - verificar argumentos
            argumentos = []
            for hijo in nodo.children:
                if hijo.symbol == 'lista_argumentos':
                    argumentos = self._extraer_tipos_argumentos(hijo)
                    break
            self.tabla.verificar_llamada_funcion('imprimir', argumentos, nodo.linea)
            return
            
        # Otras llamadas a función
        nombre_funcion = None
        argumentos = []
        linea = None
        
        # Buscar en el contexto padre para encontrar el identificador
        # Esto es una simplificación - en un compilador real sería más complejo
        
    def _verificar_referencia_variable(self, nodo):
        """Verifica una referencia a variable"""
        if nodo.token and nodo.linea:
            self.tabla.buscar(nodo.token, nodo.linea)
    
    def _verificar_expresion(self, nodo):
        """Verifica una expresión y sus tipos"""
        tipo = self._inferir_tipo_expresion(nodo)
        return tipo
    
    def _verificar_sentencia_si(self, nodo):
        """Verifica una sentencia SI"""
        # Verificar que la condición sea booleana
        for hijo in nodo.children:
            if hijo.symbol == 'expresion':
                tipo_condicion = self._inferir_tipo_expresion(hijo)
                if tipo_condicion != 'boolean' and tipo_condicion != 'unknown':
                    self.tabla.errores.append(
                        f"Error de tipos: Condicion de SI debe ser booleana, encontrado {tipo_condicion}"
                    )
                break
    
    def _verificar_sentencia_mientras(self, nodo):
        """Verifica una sentencia MIENTRAS"""
        # Verificar que la condición sea booleana
        for hijo in nodo.children:
            if hijo.symbol == 'expresion':
                tipo_condicion = self._inferir_tipo_expresion(hijo)
                if tipo_condicion != 'boolean' and tipo_condicion != 'unknown':
                    self.tabla.errores.append(
                        f"Error de tipos: Condicion de MIENTRAS debe ser booleana, encontrado {tipo_condicion}"
                    )
                break
    
    def _verificar_sentencia_para(self, nodo):
        """Verifica una sentencia PARA"""
        # Verificar condición
        expresiones = []
        for hijo in nodo.children:
            if hijo.symbol == 'expresion':
                expresiones.append(hijo)
        
        # La segunda expresión debe ser la condición (booleana)
        if len(expresiones) >= 2:
            tipo_condicion = self._inferir_tipo_expresion(expresiones[1])
            if tipo_condicion != 'boolean' and tipo_condicion != 'unknown':
                self.tabla.errores.append(
                    f"Error de tipos: Condicion de PARA debe ser booleana, encontrado {tipo_condicion}"
                )
    
    def _verificar_retorno(self, nodo):
        """Verifica una sentencia de retorno"""
        if not self.en_funcion:
            self.tabla.errores.append("Error: RETORNAR fuera de una funcion")
            return
        
        # Verificar tipo de retorno
        tipo_retorno = 'void'
        for hijo in nodo.children:
            if hijo.symbol == 'expresion':
                tipo_retorno = self._inferir_tipo_expresion(hijo)
                break
        
        # Actualizar tipo de retorno de la función
        simbolo_funcion = self.tabla.buscar(self.en_funcion)
        if simbolo_funcion:
            if simbolo_funcion.tipo_retorno == 'void':
                simbolo_funcion.tipo_retorno = tipo_retorno
            elif simbolo_funcion.tipo_retorno != tipo_retorno:
                self.tabla.errores.append(
                    f"Error de tipos: Tipo de retorno inconsistente en funcion {self.en_funcion}"
                )
    
    def _inferir_tipo_expresion(self, nodo):
        """Infiere el tipo de una expresión"""
        if not nodo:
            return 'unknown'
        
        # Literales
        if nodo.symbol == 'NUMERO':
            return 'number'
        elif nodo.symbol == 'CADENA':
            return 'string'
        elif nodo.symbol == 'VERDADERO' or nodo.symbol == 'FALSO':
            return 'boolean'
        
        # Variables
        elif nodo.symbol == 'IDENTIFICADOR' and nodo.token:
            simbolo = self.tabla.buscar(nodo.token)
            if simbolo:
                return simbolo.tipo
            return 'unknown'
        
        # Operadores aritméticos
        elif nodo.symbol in ['SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION']:
            return 'number'
        
        # Operadores de comparación
        elif nodo.symbol in ['MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL', 'IGUAL_IGUAL', 'DIFERENTE']:
            return 'boolean'
        
        # Operadores lógicos
        elif nodo.symbol in ['Y', 'O', 'NO']:
            return 'boolean'
        
        # Expresiones compuestas
        elif nodo.symbol == 'expresion' or nodo.symbol.startswith('exp_'):
            tipos = []
            for hijo in nodo.children:
                tipo = self._inferir_tipo_expresion(hijo)
                if tipo != 'unknown':
                    tipos.append(tipo)
            
            # Inferir tipo basado en el operador
            if nodo.children:
                for hijo in nodo.children:
                    if hijo.symbol in ['SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION']:
                        return 'number'
                    elif hijo.symbol in ['MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL', 'IGUAL_IGUAL', 'DIFERENTE']:
                        return 'boolean'
                    elif hijo.symbol in ['Y', 'O', 'NO']:
                        return 'boolean'
            
            # Si no hay operadores, usar el tipo del primer operando
            if tipos:
                return tipos[0]
        
        # Llamadas a función
        elif nodo.symbol == 'IMPRIMIR':
            return 'void'
        
        # Recursión para otros nodos
        else:
            for hijo in nodo.children:
                tipo = self._inferir_tipo_expresion(hijo)
                if tipo != 'unknown':
                    return tipo
        
        return 'unknown'
    
    def _extraer_tipos_argumentos(self, nodo):
        """Extrae los tipos de los argumentos de una llamada a función"""
        tipos = []
        
        def recorrer_argumentos(nodo):
            for hijo in nodo.children:
                if hijo.symbol == 'expresion':
                    tipo = self._inferir_tipo_expresion(hijo)
                    tipos.append(tipo)
                elif hijo.children:
                    recorrer_argumentos(hijo)
        
        recorrer_argumentos(nodo)
        return tipos
    
    def mostrar_errores(self):
        """Muestra todos los errores encontrados"""
        if self.tabla.errores:
            print("\n=== ERRORES SEMANTICOS ===")
            for error in self.tabla.errores:
                print(f"- {error}")
        else:
            print("\n=== ANALISIS SEMANTICO EXITOSO ===")
            print("No se encontraron errores semánticos")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del análisis"""
        print(f"\n=== ESTADISTICAS ===")
        print(f"Símbolos totales: {len(self.tabla.simbolos)}")
        print(f"Funciones definidas: {len(self.funciones_definidas)}")
        print(f"Errores encontrados: {len(self.tabla.errores)}")
        print(f"Ámbitos creados: {len(self.tabla.pila_ambitos)}")
