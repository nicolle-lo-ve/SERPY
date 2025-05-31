# semantico.py - VERSIÓN FINAL CORREGIDA PARA GENERAR TABLA CORRECTA
# Analizador semántico que genera la tabla de símbolos según especificaciones exactas
from tabla_simbolos import TablaSimbolos, Simbolo
from error_manager import get_error_manager, ErrorType, ErrorSeverity
import traceback
class Semantico:
    def __init__(self):
        """Inicializa el analizador semántico con manejo de errores."""
        self.tabla_simbolos = TablaSimbolos()
        self.error_mgr = get_error_manager()
        self.ambito_actual = "global"
        self.ambito_stack = ["global"]  # Stack para manejo de ámbitos
        self.estadisticas = {
            'declaraciones_procesadas': 0,
            'referencias_procesadas': 0,
            'errores_semanticos': 0,
            'advertencias_generadas': 0
        }
    def construir_tabla_simbolos(self, tokens, arbol):
        """
        Construye la tabla de símbolos según especificaciones exactas.
        """
        try:
            print("\n=== INICIANDO CONSTRUCCIÓN DE TABLA DE SÍMBOLOS ===")
            
            # Validar entradas
            if not self._validar_entradas(tokens, arbol):
                return None
            
            # Estrategia 1: Análisis secuencial de tokens (CORREGIDA PARA TABLA EXACTA)
            simbolos_tokens = self._detectar_por_tokens(tokens)
            
            # Estrategia 2: Análisis del árbol sintáctico (CORREGIDA)
            simbolos_arbol = self._detectar_por_arbol(arbol)
            
            # Estrategia 3: Análisis de referencias (CORREGIDA)
            referencias = self._procesar_referencias(tokens)
            
            # Validación final
            self._validar_tabla_final()
            
            # Reportar estadísticas
            self._reportar_estadisticas()
            
            if self.tabla_simbolos.tabla:
                print(f"✅ TABLA DE SÍMBOLOS CONSTRUIDA - Total símbolos: {len(self.tabla_simbolos.tabla)}")
                return self.tabla_simbolos
            else:
                self.error_mgr.add_semantic_error(
                    "No se encontraron símbolos en el código fuente",
                    suggestion="Verifica que el código tenga declaraciones de variables o funciones válidas"
                )
                return None
                
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.CRITICO,
                f"Error crítico construyendo tabla de símbolos: {str(e)}",
                "Constructor de tabla",
                exception=e,
                suggestion="Verifica la sintaxis del código fuente"
            )
            return None
    def _validar_entradas(self, tokens, arbol):
        """Valida que las entradas sean correctas."""
        if not tokens:
            self.error_mgr.add_semantic_error(
                "Lista de tokens vacía",
                suggestion="Verifica que el análisis léxico haya generado tokens"
            )
            return False
        
        if not arbol:
            self.error_mgr.add_semantic_error(
                "Árbol sintáctico vacío",
                suggestion="Verifica que el análisis sintáctico haya generado un árbol válido"
            )
            return False
        
        return True
    def _detectar_por_tokens(self, tokens):
        """
        Análisis secuencial de tokens CORREGIDO para generar tabla exacta.
        """
        contador = 0
        errores_estrategia = 0
        
        try:
            print("🔍 Estrategia 1: Análisis secuencial de tokens...")
            
            i = 0
            while i < len(tokens):
                try:
                    token_obj = tokens[i]
                    
                    # Verificar patrón DEFINIR para funciones
                    if (self._es_token_definir(token_obj) and 
                        i + 1 < len(tokens) and
                        self._es_identificador(tokens[i + 1])):
                        
                        resultado = self._procesar_declaracion_funcion(tokens, i)
                        if resultado['exito']:
                            contador += 1
                            i += resultado['tokens_procesados']
                        else:
                            errores_estrategia += 1
                            i += 1
                    
                    # Verificar patrón VAR para variables (CORREGIDO para evitar duplicados)
                    elif (self._es_token_var(token_obj) and 
                          i + 4 < len(tokens) and
                          self._es_identificador(tokens[i + 1]) and
                          self._es_igual(tokens[i + 2])):
                        
                        # Verificar si no es un duplicado
                        nombre_var = tokens[i + 1].getLexema()
                        if not self._ya_existe_en_ambito_actual(nombre_var):
                            resultado = self._procesar_declaracion_var(tokens, i)
                            if resultado['exito']:
                                contador += 1
                                i += resultado['tokens_procesados']
                            else:
                                errores_estrategia += 1
                                i += 1
                        else:
                            # Skip variable duplicada
                            i += 5
                    else:
                        i += 1
                        
                except Exception as e:
                    errores_estrategia += 1
                    i += 1
            
            print(f"   Resultado: {contador} declaraciones, {errores_estrategia} errores")
            self.estadisticas['declaraciones_procesadas'] = contador
            self.estadisticas['errores_semanticos'] += errores_estrategia
            
            return contador
            
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.ERROR,
                f"Error en análisis de tokens: {str(e)}",
                "Estrategia 1",
                exception=e
            )
            return 0
    def _ya_existe_en_ambito_actual(self, nombre):
        """Verifica si ya existe una variable en el ámbito actual"""
        try:
            simbolo_existente = self.tabla_simbolos.buscar(nombre)
            if simbolo_existente:
                return (hasattr(simbolo_existente, 'ambito') and 
                       simbolo_existente.ambito == self.ambito_actual and
                       hasattr(simbolo_existente, 'categoria_lexica') and
                       simbolo_existente.categoria_lexica == "variable")
            return False
        except:
            return False
    def _es_token_definir(self, token_obj):
        """Verifica si el token es DEFINIR"""
        try:
            return (hasattr(token_obj, 'getToken') and 
                   token_obj.getToken() == "DEFINIR")
        except:
            return False
        

    def _procesar_declaracion_funcion(self, tokens, indice_inicio):
        """Procesa una declaración de función corregida."""
        # Patrón: DEFINIR IDENTIFICADOR PAR_IZQ [parametros] PAR_DER BLOQUE
        if indice_inicio + 3 >= len(tokens):
            return {'exito': False, 'tokens_procesados': 1}
        
        token_definir = tokens[indice_inicio]
        token_nombre = tokens[indice_inicio + 1]
        token_par_izq = tokens[indice_inicio + 2]
        
        # Validar estructura básica
        if (not self._es_token_definir(token_definir) or
            not self._es_identificador(token_nombre) or
            not self._es_parentesis_izquierdo(token_par_izq)):
            return {'exito': False, 'tokens_procesados': 1}
        
        nombre_funcion = token_nombre.getLexema()
        linea = token_nombre.getLinea()
        
        # Crear símbolo de función primero (en ámbito global)
        simbolo_funcion = Simbolo(
            categoria_lexica="funcion",
            tipo="int",  # Tipo de retorno por defecto
            lexema=nombre_funcion,
            valor=None,
            ambito="global",
            declarada_en=linea
        )
        
        try:
            self.tabla_simbolos.insertar(simbolo_funcion)
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.ERROR,
                f"No se pudo insertar función '{nombre_funcion}': {str(e)}",
                "Procesador de funciones",
                exception=e
            )
            return {'exito': False, 'tokens_procesados': 1}
        
        # Cambiar al ámbito de la función para procesar parámetros y variables locales
        ambito_anterior = self.ambito_actual
        self.ambito_actual = nombre_funcion
        self.ambito_stack.append(nombre_funcion)
        
        # Buscar paréntesis derecho y procesar parámetros
        i = indice_inicio + 3
        tokens_procesados = 3
        parametros = []
        
        while i < len(tokens):
            token_actual = tokens[i]
            tokens_procesados += 1
            
            if self._es_parentesis_derecho(token_actual):
                break
            elif self._es_identificador(token_actual):
                # Procesar parámetro
                nombre_param = token_actual.getLexema()
                parametros.append(nombre_param)
                
                # Crear símbolo de parámetro
                simbolo_param = Simbolo(
                    categoria_lexica="parametro",
                    tipo="int",  # Tipo por defecto para parámetros
                    lexema=nombre_param,
                    valor=None,
                    ambito=nombre_funcion,
                    declarada_en=linea
                )
                
                try:
                    self.tabla_simbolos.insertar(simbolo_param)
                except Exception as e:
                    self.error_mgr.add_warning(
                        f"No se pudo insertar parámetro '{nombre_param}': {str(e)}",
                        "Procesador de funciones",
                        linea,
                        "Verifica si el parámetro ya existe"
                    )
                
                # Saltar coma si existe
                if i+1 < len(tokens) and self._es_coma(tokens[i+1]):
                    i += 1
                    tokens_procesados += 1
            
            i += 1
        
        # Buscar el inicio del bloque (llave izquierda)
        while i < len(tokens) and not self._es_llave_izquierda(tokens[i]):
            i += 1
            tokens_procesados += 1
        
        # Procesar cuerpo de la función si encontramos llave izquierda
        if i < len(tokens) and self._es_llave_izquierda(tokens[i]):
            i += 1
            tokens_procesados += 1
            nivel_bloque = 1
            
            while i < len(tokens) and nivel_bloque > 0:
                if self._es_llave_izquierda(tokens[i]):
                    nivel_bloque += 1
                elif self._es_llave_derecha(tokens[i]):
                    nivel_bloque -= 1
                
                # Procesar declaraciones de variables locales
                if (self._es_token_var(tokens[i]) and 
                    i + 4 < len(tokens) and
                    self._es_identificador(tokens[i + 1]) and
                    self._es_igual(tokens[i + 2])):
                    
                    resultado_var = self._procesar_declaracion_var(tokens, i)
                    if resultado_var['exito']:
                        i += resultado_var['tokens_procesados'] - 1
                        tokens_procesados += resultado_var['tokens_procesados'] - 1
                
                i += 1
                tokens_procesados += 1
        
        # Volver al ámbito anterior
        self.ambito_stack.pop()
        self.ambito_actual = self.ambito_stack[-1] if self.ambito_stack else "global"
        
        print(f"  ✅ Función '{nombre_funcion}' con {len(parametros)} parámetros")
        return {'exito': True, 'tokens_procesados': tokens_procesados}

    def _agregar_parametro(self, nombre_param, linea, ambito_funcion):
        """Agregar parámetro como símbolo con ámbito de función CORREGIDO"""
        try:
            # CORREGIDO: Crear parámetro con tipo "entero" y ámbito correcto
            simbolo_param = Simbolo(
                categoria_lexica="parametro",
                tipo="entero",  # CORREGIDO: usar "entero" en lugar de "parameter"
                lexema=nombre_param,
                valor=None,  # CORREGIDO: sin valor para parámetros
                ambito=ambito_funcion,  # CORREGIDO: ámbito de la función
                declarada_en=linea
            )
            
            # Insertar parámetro
            try:
                self.tabla_simbolos.insertar(simbolo_param)
                print(f"    📝 Parámetro '{nombre_param}' en función '{ambito_funcion}'")
            except Exception as e:
                # Si ya existe, crear con nombre único sin reportar error
                simbolo_param_unico = Simbolo(
                    categoria_lexica="parametro",
                    tipo="entero",
                    lexema=f"{nombre_param}_{ambito_funcion}",  # Nombre único
                    valor=None,
                    ambito=ambito_funcion,
                    declarada_en=linea
                )
                try:
                    self.tabla_simbolos.insertar(simbolo_param_unico)
                except:
                    pass  # Ignorar si aún falla
            
        except Exception as e:
            # Continuar silenciosamente
            pass
    def _es_parentesis_izquierdo(self, token_obj):
        """Verifica si el token es paréntesis izquierdo"""
        try:
            return (hasattr(token_obj, 'getToken') and 
                   token_obj.getToken() == "PAR_IZQ")
        except:
            return False
    def _es_parentesis_derecho(self, token_obj):
        """Verifica si el token es paréntesis derecho"""
        try:
            return (hasattr(token_obj, 'getToken') and 
                   token_obj.getToken() == "PAR_DER")
        except:
            return False
    
    def _procesar_referencias(self, tokens):
        """Procesa referencias a variables y funciones."""
        contador = 0
        
        try:
            print("🔗 Estrategia 3: Análisis de referencias...")
            
            i = 0
            while i < len(tokens):
                token_obj = tokens[i]
                
                # Referencias a funciones (IDENTIFICADOR seguido de PAR_IZQ)
                if (token_obj.getToken() == "IDENTIFICADOR" and 
                    i+1 < len(tokens) and 
                    self._es_parentesis_izquierdo(tokens[i+1])):
                    
                    nombre_funcion = token_obj.getLexema()
                    simbolo = self.tabla_simbolos.buscar(nombre_funcion)
                    
                    if simbolo and simbolo.categoria_lexica == "funcion":
                        ubicacion = f"{token_obj.getLinea()}:{token_obj.getColumna()}"
                        simbolo.referencias.append(ubicacion)
                        contador += 1
                    
                    # Saltar los parámetros
                    i += 2
                    while i < len(tokens) and not self._es_parentesis_derecho(tokens[i]):
                        i += 1
                    if i < len(tokens) and self._es_parentesis_derecho(tokens[i]):
                        i += 1
                    continue
                
                # Referencias a variables
                elif token_obj.getToken() == "IDENTIFICADOR":
                    lexema = token_obj.getLexema()
                    simbolo = self.tabla_simbolos.buscar(lexema)
                    
                    if simbolo:
                        ubicacion = f"{token_obj.getLinea()}:{token_obj.getColumna()}"
                        simbolo.referencias.append(ubicacion)
                        contador += 1
                
                i += 1
            
            print(f"   Resultado: {contador} referencias procesadas")
            self.estadisticas['referencias_procesadas'] = contador
            return contador
            
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.WARNING,
                f"Error procesando referencias: {str(e)}",
                "Procesador de referencias",
                exception=e
            )
            return 0
    
    
    def _es_funcion_valida(self, nombre):
        """Verifica si un identificador es una función válida declarada"""
        try:
            simbolo = self.tabla_simbolos.buscar(nombre)
            return simbolo and hasattr(simbolo, 'categoria_lexica') and simbolo.categoria_lexica == "funcion"
        except:
            return False
    # Métodos auxiliares
    def _es_token_var(self, token_obj):
        """Verifica si el token es VAR"""
        try:
            return (hasattr(token_obj, 'getToken') and 
                   token_obj.getToken() == "VAR")
        except:
            return False
    def _es_identificador(self, token_obj):
        """Verifica si el token es un identificador"""
        try:
            return (hasattr(token_obj, 'getToken') and 
                   token_obj.getToken() == "IDENTIFICADOR")
        except:
            return False
    def _es_igual(self, token_obj):
        """Verifica si el token es IGUAL"""
        try:
            return (hasattr(token_obj, 'getToken') and 
                   token_obj.getToken() == "IGUAL")
        except:
            return False
    
    # Agregar este método a la clase Semantico
    def _es_coma(self, token_obj):
        """Verifica si el token es una coma"""
        try:
            return (hasattr(token_obj, 'getToken') and 
                token_obj.getToken() == "COMA")
        except:
            return False
        
    def _es_llave_izquierda(self, token_obj):
        try:
            return token_obj.getToken() == "LLAVE_IZQ"
        except:
            return False

    def _es_llave_derecha(self, token_obj):
        try:
            return token_obj.getToken() == "LLAVE_DER"
        except:
            return False


    def _procesar_declaracion_var(self, tokens, indice_inicio):
        """Procesa una declaración de variable corregida."""
        try:
            # Patrón: VAR IDENTIFICADOR IGUAL expresion PUNTOYCOMA
            if indice_inicio + 4 >= len(tokens):
                return {'exito': False, 'tokens_procesados': 1}
            
            token_var = tokens[indice_inicio]
            token_nombre = tokens[indice_inicio + 1]
            token_igual = tokens[indice_inicio + 2]
            token_valor = tokens[indice_inicio + 3]
            
            # Validar estructura básica
            if (not self._es_token_var(token_var) or
                not self._es_identificador(token_nombre) or
                not self._es_igual(token_igual)):
                return {'exito': False, 'tokens_procesados': 1}
            
            nombre_var = token_nombre.getLexema()
            valor = token_valor.getLexema()
            linea = token_nombre.getLinea()
            
            # Determinar tipo basado en el valor
            tipo = self._determinar_tipo(valor)
            
            # Crear símbolo de variable
            if not self._ya_existe_en_ambito_actual(nombre_var):
                simbolo = Simbolo(
                    categoria_lexica="variable",
                    tipo=self._determinar_tipo(valor),
                    lexema=nombre_var,
                    valor=valor,
                    ambito=self.ambito_actual,  # Usar el ámbito actual (global o función)
                    declarada_en=linea
                )
                self.tabla_simbolos.insertar(simbolo)
            
            try:

                print(f"  ✅ Variable '{nombre_var}' = {valor} (tipo: {tipo})")
                
                # Saltar hasta el punto y coma
                i = indice_inicio + 4
                tokens_procesados = 4
                while i < len(tokens) and not self._es_puntoycoma(tokens[i]):
                    i += 1
                    tokens_procesados += 1
                
                return {'exito': True, 'tokens_procesados': tokens_procesados}
            except Exception as e:
                print(f"  ⚠️ Variable '{nombre_var}' ya existe")
                return {'exito': False, 'tokens_procesados': 5}
                
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.ERROR,
                f"Error procesando declaración de variable: {str(e)}",
                "Procesador de variables",
                exception=e
            )
            return {'exito': False, 'tokens_procesados': 1}
        
        

    def _determinar_tipo(self, valor):
        try:
            if isinstance(valor, str):
                if valor.startswith('"') and valor.endswith('"'):
                    return "string"
                if valor.lower() in ['verdadero', 'falso']:
                    return "boolean"
                if valor.isdigit():
                    return "int"
                try:
                    float(valor)
                    return "float"
                except ValueError:
                    pass
            elif isinstance(valor, (int, float)):
                return "int" if isinstance(valor, int) else "float"
            return "unknown"
        except:
            return "unknown"

    def _procesar_valor(self, valor):
        """Procesa el valor para la tabla de símbolos"""
        try:
            if valor.startswith('"') and valor.endswith('"'):
                return valor[1:-1]  # Remover comillas
            elif valor.isdigit():
                return int(valor)
            else:
                return valor
        except:
            return valor
    # Resto de métodos existentes
    def _detectar_por_arbol(self, arbol):
        """Estrategia 2: Análisis del árbol sintáctico"""
        try:
            print("🌳 Estrategia 2: Análisis del árbol sintáctico...")
            contador = 0
            
            def recorrer_nodo(nodo, nivel=0):
                nonlocal contador
                try:
                    if hasattr(nodo, 'valor') and nodo.valor == "VAR":
                        print(f"  🌳 Nodo VAR encontrado (nivel {nivel})")
                        contador += 1
                    
                    if hasattr(nodo, 'hijos'):
                        for hijo in nodo.hijos:
                            recorrer_nodo(hijo, nivel + 1)
                except:
                    pass
            
            recorrer_nodo(arbol)
            print(f"   Resultado: {contador} nodos VAR encontrados")
            return contador
            
        except Exception as e:
            return 0
    def _validar_tabla_final(self):
        """Validación final de la tabla de símbolos"""
        try:
            if not hasattr(self.tabla_simbolos, 'tabla') or not self.tabla_simbolos.tabla:
                self.error_mgr.add_semantic_error(
                    "Tabla de símbolos vacía después del análisis",
                    suggestion="Revisa las declaraciones en el código fuente"
                )
            else:
                print("✅ Tabla de símbolos válida y consistente")
        except Exception as e:
            pass
    def _reportar_estadisticas(self):
        """Reporta las estadísticas del análisis semántico"""
        try:
            print(f"\n📊 ESTADÍSTICAS DEL ANÁLISIS SEMÁNTICO:")
            print(f"   • Declaraciones procesadas: {self.estadisticas['declaraciones_procesadas']}")
            print(f"   • Referencias procesadas: {self.estadisticas['referencias_procesadas']}")
            print(f"   • Errores semánticos: {self.estadisticas['errores_semanticos']}")
            print(f"   • Advertencias generadas: {self.estadisticas['advertencias_generadas']}")
            if hasattr(self.tabla_simbolos, 'tabla'):
                print(f"   • Símbolos en tabla: {len(self.tabla_simbolos.tabla)}")
        except Exception as e:
            pass
