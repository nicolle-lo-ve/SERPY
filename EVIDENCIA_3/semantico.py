from tabla_simbolos import TablaSimbolos, Simbolo

class Semantico:
    """Analizador semántico para el compilador"""
    
    def __init__(self):
        """Inicializa el analizador semántico"""
        self.tabla_simbolos = TablaSimbolos()
        self.ambito_actual = "global"
        self.errores = []
        self.advertencias = []
        self.estadisticas = {
            'declaraciones_procesadas': 0,
            'referencias_procesadas': 0,
            'errores_semanticos': 0,
            'advertencias_generadas': 0
        }
    
    def construir_tabla_simbolos(self, tokens, arbol):
        """
        Construye la tabla de símbolos a partir de los tokens y el árbol sintáctico.
        Compatible con la estructura del compilador existente.
        
        Args:
            tokens: Lista de objetos Valor con los tokens del análisis léxico
            arbol: Árbol sintáctico generado por el análisis sintáctico
            
        Returns:
            TablaSimbolos: Tabla de símbolos construida o None si hay errores
        """
        try:
            print("\n=== INICIANDO ANÁLISIS SEMÁNTICO ===")
            
            # Validar entradas
            if not self._validar_entradas(tokens, arbol):
                return None
            
            # Estrategia 1: Análisis por recorrido del árbol sintáctico
            print("🔍 Analizando estructura del árbol sintáctico...")
            self._analizar_arbol(arbol, tokens)
            
            # Estrategia 2: Análisis secuencial de tokens para validación
            print("🔍 Validando con análisis secuencial de tokens...")
            self._analizar_tokens_secuencial(tokens)
            
            # Estrategia 3: Análisis de referencias y uso de símbolos
            print("🔍 Analizando referencias y uso de símbolos...")
            self._analizar_referencias(tokens)
            
            # Validación final
            print("🔍 Validando consistencia de la tabla...")
            self._validar_consistencia()
            
            # Reportar resultados
            self._reportar_resultados()
            
            return self.tabla_simbolos
            
        except Exception as e:
            print(f"❌ Error crítico en análisis semántico: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _validar_entradas(self, tokens, arbol):
        """Valida que las entradas sean correctas"""
        if not tokens:
            self.errores.append("Lista de tokens vacía")
            return False
        
        if not arbol:
            self.errores.append("Árbol sintáctico vacío")
            return False
        
        return True
    
    def _analizar_arbol(self, nodo, tokens, ambito="global"):
        """Analiza el árbol sintáctico para construir la tabla de símbolos"""
        if not nodo:
            return
        
        # Cambiar ámbito si es necesario
        ambito_anterior = self.ambito_actual
        cambio_ambito = False
        
        try:
            # Procesar nodo actual según su tipo
            if nodo.symbol == "funcion_def":
                nombre_funcion = self._procesar_definicion_funcion(nodo, tokens)
                if nombre_funcion:
                    # Cambiar al ámbito de la función
                    self.tabla_simbolos.cambiar_ambito(nombre_funcion)
                    self.ambito_actual = nombre_funcion
                    cambio_ambito = True
                    print(f"   🔄 Entrando al ámbito de función: '{nombre_funcion}'")
            
            elif nodo.symbol == "sentencia" and self._es_declaracion_variable(nodo):
                self._procesar_declaracion_variable(nodo, tokens)
            
            elif nodo.symbol == "parametros":
                self._procesar_parametros(nodo, tokens)
            
            elif nodo.symbol == "bloque":
                # Los bloques pueden tener variables locales
                print(f"   🔍 Procesando bloque en ámbito: '{self.ambito_actual}'")
            
            # Procesar nodos hijos
            for hijo in nodo.children:
                self._analizar_arbol(hijo, tokens, self.ambito_actual)
                
        finally:
            # Restaurar ámbito anterior si cambió
            if cambio_ambito:
                self.tabla_simbolos.salir_ambito()
                self.ambito_actual = self.tabla_simbolos.ambito_actual
                print(f"   🔄 Saliendo del ámbito, regresando a: '{self.ambito_actual}'")
    
    def _procesar_definicion_funcion(self, nodo, tokens):
        """Procesa la definición de una función"""
        try:
            # Buscar el nombre de la función en los hijos
            nombre_funcion = None
            parametros = []
            nodo_parametros = None
            
            for hijo in nodo.children:
                if hijo.symbol == "IDENTIFICADOR" and hijo.token:
                    # El token contiene "IDENTIFICADOR", necesitamos obtener el lexema real
                    nombre_funcion = self._obtener_lexema_real(hijo, tokens)
                elif hijo.symbol == "parametros":
                    nodo_parametros = hijo
                    parametros = self._extraer_parametros(hijo, tokens)
            
            # En lugar de procesar aquí, marcar para procesamiento secuencial
            if nombre_funcion and nombre_funcion != "detectar_en_secuencial":
                print(f"   🔄 Detectada estructura de función (procesamiento secuencial)")
                return nombre_funcion
            else:
                print(f"   🔄 Estructura de función detectada (se procesará en análisis secuencial)")
                return "pendiente_secuencial"
            
        except Exception as e:
            self.errores.append(f"Error procesando definición de función: {e}")
            return None
    
    def _procesar_declaracion_variable(self, nodo, tokens):
        """Procesa la declaración de una variable"""
        try:
            # El análisis de variables se hace principalmente en análisis secuencial
            # Este método se mantiene para compatibilidad
            print(f"   🔍 Estructura de variable detectada (se procesa en análisis secuencial)")
            
        except Exception as e:
            self.errores.append(f"Error procesando declaración de variable: {e}")
    
    def _obtener_linea_nodo(self, nodo):
        """Obtiene la línea de declaración de un nodo"""
        try:
            if hasattr(nodo, 'linea') and nodo.linea:
                return nodo.linea
            elif hasattr(nodo, 'token') and nodo.token:
                # Intentar buscar en los tokens originales
                return None  # Se llenará por análisis secuencial
            else:
                return None
        except:
            return None
    
    def _obtener_lexema_real(self, nodo, tokens):
        """Obtiene el lexema real de un nodo - versión simplificada"""
        # Por simplicidad, usar el análisis secuencial como fuente principal
        # El análisis del árbol sirve principalmente para detectar estructura
        return "detectar_en_secuencial"
    
    def _procesar_parametros(self, nodo, tokens):
        """Procesa los parámetros de una función"""
        try:
            # Los parámetros se procesan en el análisis secuencial
            print(f"   🔍 Estructura de parámetros detectada (se procesa en análisis secuencial)")
            return []
            
        except Exception as e:
            self.errores.append(f"Error procesando parámetros: {e}")
            return []
    
    def _extraer_parametros(self, nodo_parametros, tokens):
        """Extrae los nombres de los parámetros de un nodo de parámetros"""
        # En la nueva implementación, esto se maneja en el análisis secuencial
        return []
    
    def _es_declaracion_variable(self, nodo):
        """Verifica si un nodo representa una declaración de variable"""
        # Buscar patrón VAR en los hijos
        for hijo in nodo.children:
            if hijo.symbol == "VAR":
                return True
        return False
    
    def _extraer_valor_expresion(self, nodo):
        """Extrae el valor de una expresión simple"""
        try:
            # Buscar nodos terminales con tokens
            def buscar_valor(n):
                if n.token:
                    # Intentar convertir a número
                    try:
                        if '.' in str(n.token):
                            return float(n.token)
                        else:
                            return int(n.token)
                    except (ValueError, TypeError):
                        # Si no es número, devolver como string
                        return str(n.token)
                
                # Buscar en hijos
                for hijo in n.children:
                    valor = buscar_valor(hijo)
                    if valor is not None:
                        return valor
                return None
            
            return buscar_valor(nodo)
        except:
            return None
    
    def _inferir_tipo(self, valor):
        """Infiere el tipo de dato basado en el valor"""
        if valor is None:
            return "unknown"
        elif isinstance(valor, int):
            return "int"
        elif isinstance(valor, float):
            return "float"
        elif isinstance(valor, str):
            # Si está entre comillas, es string
            if (valor.startswith('"') and valor.endswith('"')) or (valor.startswith("'") and valor.endswith("'")):
                return "string"
            # Si es 'verdadero' o 'falso', es boolean
            elif valor.lower() in ['verdadero', 'falso', 'true', 'false']:
                return "boolean"
            else:
                return "string"
        else:
            return "unknown"
    
    def _analizar_tokens_secuencial(self, tokens):
        """Análisis secuencial de tokens para validación y detección adicional"""
        i = 0
        ambito_contexto = "global"  # Seguimiento del ámbito actual basado en tokens
        stack_ambitos = ["global"]
        
        while i < len(tokens):
            token = tokens[i]
            
            # Detectar cambios de ámbito basado en estructura de tokens
            if token.getToken() == "DEFINIR" and i + 1 < len(tokens):
                siguiente = tokens[i + 1]
                if siguiente.getToken() == "IDENTIFICADOR":
                    nombre_funcion = siguiente.getLexema()
                    
                    # Crear función si no existe
                    if not self.tabla_simbolos.existe_simbolo(nombre_funcion, "global"):
                        simbolo_funcion = Simbolo(
                            categoria_lexica="funcion",
                            tipo="void",
                            lexema=nombre_funcion,
                            ambito="global",
                            declarada_en=token.getLinea()
                        )
                        
                        if self.tabla_simbolos.agregar_simbolo(simbolo_funcion):
                            print(f"   ✅ Función '{nombre_funcion}' detectada y agregada")
                            self.estadisticas['declaraciones_procesadas'] += 1
                    
                    # Detectar parámetros
                    parametros = self._extraer_parametros_de_tokens(tokens, i + 2)
                    if parametros:
                        print(f"   📝 Parámetros detectados: {', '.join(parametros)}")
                    
                    # Preparar para entrar al ámbito de la función
                    if self._encontrar_llave_apertura(tokens, i):
                        stack_ambitos.append(nombre_funcion)
                        ambito_contexto = nombre_funcion
                        print(f"   🔄 Contexto secuencial: entrando a función '{nombre_funcion}'")
                        
                        # Agregar parámetros al ámbito de la función
                        for param in parametros:
                            simbolo_param = Simbolo(
                                categoria_lexica="parametro",
                                tipo="unknown",
                                lexema=param,
                                ambito=nombre_funcion,
                                declarada_en=token.getLinea()
                            )
                            
                            if self.tabla_simbolos.agregar_simbolo(simbolo_param):
                                print(f"   📋 Parámetro '{param}' agregado al ámbito '{nombre_funcion}'")
                                self.estadisticas['declaraciones_procesadas'] += 1
            
            # Detectar salida de ámbito con llaves de cierre
            elif token.getToken() == "LLAVE_DER" and len(stack_ambitos) > 1:
                ambito_anterior = stack_ambitos.pop()
                ambito_contexto = stack_ambitos[-1]
                print(f"   🔄 Contexto secuencial: saliendo de '{ambito_anterior}' a '{ambito_contexto}'")
            
            # Detectar declaraciones VAR con ámbito correcto
            elif token.getToken() == "VAR" and i + 1 < len(tokens):
                siguiente = tokens[i + 1]
                if siguiente.getToken() == "IDENTIFICADOR":
                    nombre = siguiente.getLexema()
                    
                    # Buscar valor inicial
                    valor = None
                    tipo = "unknown"
                    
                    if (i + 3 < len(tokens) and 
                        tokens[i + 2].getToken() == "IGUAL"):
                        token_valor = tokens[i + 3]
                        valor = token_valor.getLexema()
                        tipo = self._inferir_tipo_por_token(token_valor)
                    
                    # Verificar si ya existe en el ámbito actual
                    simbolo_existente = self.tabla_simbolos.obtener_simbolo(nombre, ambito_contexto)
                    
                    if not simbolo_existente:
                        # Crear y agregar símbolo en el ámbito correcto
                        simbolo = Simbolo(
                            categoria_lexica="variable",
                            tipo=tipo,
                            lexema=nombre,
                            valor=valor,
                            ambito=ambito_contexto,
                            declarada_en=token.getLinea()
                        )
                        
                        if self.tabla_simbolos.agregar_simbolo(simbolo):
                            ambito_info = f"'{ambito_contexto}'" if ambito_contexto != "global" else "global"
                            print(f"   🔍 Variable '{nombre}' detectada en ámbito {ambito_info} (análisis secuencial)")
                    elif not simbolo_existente.declarada_en:
                        # Actualizar línea de declaración si no la tiene
                        simbolo_existente.declarada_en = token.getLinea()
            
            i += 1
    
    def _encontrar_llave_apertura(self, tokens, inicio):
        """Busca la llave de apertura después de una declaración de función"""
        for i in range(inicio, min(inicio + 10, len(tokens))):
            if tokens[i].getToken() == "LLAVE_IZQ":
                return True
        return False
    
    def _extraer_parametros_de_tokens(self, tokens, inicio):
        """Extrae los parámetros de una función de la secuencia de tokens"""
        parametros = []
        
        # Buscar paréntesis de apertura
        i = inicio
        while i < len(tokens) and tokens[i].getToken() != "PAR_IZQ":
            i += 1
        
        if i >= len(tokens):
            return parametros
        
        i += 1  # Pasar del PAR_IZQ
        
        # Extraer identificadores hasta PAR_DER
        while i < len(tokens) and tokens[i].getToken() != "PAR_DER":
            if tokens[i].getToken() == "IDENTIFICADOR":
                parametros.append(tokens[i].getLexema())
            i += 1
        
        return parametros
    
    def _inferir_tipo_por_token(self, token):
        """Infiere el tipo basado en el token"""
        if token.getToken() == "NUMERO":
            valor = token.getLexema()
            try:
                if '.' in str(valor):
                    return "float"
                else:
                    return "int"
            except:
                return "unknown"
        elif token.getToken() == "CADENA":
            return "string"
        elif token.getToken() in ["VERDADERO", "FALSO"]:
            return "boolean"
        else:
            return "unknown"
    
    def _analizar_referencias(self, tokens):
        """Analiza las referencias a símbolos para marcar su uso"""
        for token in tokens:
            if token.getToken() == "IDENTIFICADOR":
                nombre = token.getLexema()
                simbolo = self.tabla_simbolos.obtener_simbolo(nombre)
                
                if simbolo:
                    simbolo.agregar_referencia(token.getLinea(), token.getColumna())
                    self.estadisticas['referencias_procesadas'] += 1
                else:
                    # Símbolo usado pero no declarado
                    self.advertencias.append(f"Referencia a símbolo no declarado: '{nombre}' en línea {token.getLinea()}")
                    self.estadisticas['advertencias_generadas'] += 1
    
    def _validar_consistencia(self):
        """Valida la consistencia de la tabla de símbolos"""
        # Verificar variables no usadas
        for simbolo in self.tabla_simbolos.tabla.values():
            if not simbolo.usada and simbolo.categoria_lexica == "variable":
                self.advertencias.append(f"Variable '{simbolo.lexema}' declarada pero no usada")
                self.estadisticas['advertencias_generadas'] += 1
        
        # Más validaciones se pueden agregar aquí
        return True
    
    def _reportar_resultados(self):
        """Reporta los resultados del análisis semántico"""
        print(f"\n📊 RESULTADOS DEL ANÁLISIS SEMÁNTICO:")
        print(f"   • Símbolos encontrados: {len(self.tabla_simbolos.tabla)}")
        print(f"   • Declaraciones procesadas: {self.estadisticas['declaraciones_procesadas']}")
        print(f"   • Referencias procesadas: {self.estadisticas['referencias_procesadas']}")
        
        if self.errores:
            print(f"\n❌ ERRORES ({len(self.errores)}):")
            for error in self.errores:
                print(f"   • {error}")
            self.estadisticas['errores_semanticos'] = len(self.errores)
        
        if self.advertencias:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.advertencias)}):")
            for advertencia in self.advertencias:
                print(f"   • {advertencia}")
    
    def obtener_estadisticas(self):
        """Devuelve las estadísticas del análisis"""
        return self.estadisticas
    
    def obtener_errores(self):
        """Devuelve la lista de errores"""
        return self.errores
    
    def obtener_advertencias(self):
        """Devuelve la lista de advertencias"""
        return self.advertencias
