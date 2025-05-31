# tabla_simbolos.py - VERSIÓN CON MANEJO COMPLETO DE ERRORES
# Sistema robusto de tabla de símbolos con validación y manejo de errores detallado
from error_manager import get_error_manager, ErrorType, ErrorSeverity
import traceback
class Simbolo:
    def __init__(self, categoria_lexica, tipo, lexema, dimension=None, valor=None, ambito=None, declarada_en=None, referencias=None):
        """
        Inicializa un símbolo con validación de parámetros.
        
        Args:
            categoria_lexica (str): Tipo de símbolo (variable, funcion, etc.)
            tipo (str): Tipo de dato (int, string, etc.)
            lexema (str): Nombre del símbolo
            dimension (str, optional): Dimensión si es array
            valor (any, optional): Valor inicial
            ambito (str, optional): Ámbito del símbolo
            declarada_en (int, optional): Línea donde se declaró
            referencias (list, optional): Lista de referencias
        """
        self.error_mgr = get_error_manager()
        
        # Validar parámetros obligatorios
        if not categoria_lexica:
            self.error_mgr.add_semantic_error(
                "Símbolo creado sin categoría léxica",
                suggestion="Especifica la categoría léxica del símbolo"
            )
            categoria_lexica = "desconocida"
        
        if not tipo:
            self.error_mgr.add_semantic_error(
                "Símbolo creado sin tipo",
                suggestion="Especifica el tipo del símbolo"
            )
            tipo = "unknown"
        
        if not lexema:
            self.error_mgr.add_semantic_error(
                "Símbolo creado sin lexema (nombre)",
                suggestion="Especifica el nombre del símbolo"
            )
            lexema = "simbolo_sin_nombre"
        
        # Asignar valores con validación
        self.categoria_lexica = self._validar_categoria_lexica(categoria_lexica)
        self.tipo = self._validar_tipo(tipo)
        self.lexema = self._validar_lexema(lexema)
        self.dimension = dimension
        self.valor = valor
        self.ambito = ambito if ambito else "global"
        self.declarada_en = declarada_en
        self.referencias = referencias if referencias else []
        
        # Propiedades adicionales para funcionalidad mejorada
        self.inicializada = valor is not None
        self.usada = False
        self.tipo_inferido = False  # Si el tipo fue inferido automáticamente
    def _validar_categoria_lexica(self, categoria):
        """Valida la categoría léxica del símbolo."""
        categorias_validas = ['variable', 'funcion', 'parametro', 'constante', 'tipo']
        
        if categoria not in categorias_validas:
            self.error_mgr.add_warning(
                f"Categoría léxica no estándar: '{categoria}'",
                "Validador de símbolos",
                suggestion=f"Usa una de: {', '.join(categorias_validas)}"
            )
        
        return categoria
    def _validar_tipo(self, tipo):
        """Valida el tipo del símbolo."""
        tipos_validos = ['int', 'float', 'string', 'boolean', 'void', 'unknown']
        
        if tipo == "entero":
            tipo = "int"
        elif tipo == "desconocido":
            tipo = "unknown"

        if tipo not in tipos_validos:
            self.error_mgr.add_warning(
                f"Tipo no estándar: '{tipo}'",
                "Validador de símbolos",
                suggestion=f"Usa uno de: {', '.join(tipos_validos)}"
            )
        
        return tipo
    def _validar_lexema(self, lexema):
        """Valida el nombre del símbolo."""
        try:
            # Verificar longitud
            if len(lexema) > 50:
                self.error_mgr.add_warning(
                    f"Nombre de símbolo muy largo: '{lexema}' ({len(lexema)} caracteres)",
                    "Validador de símbolos",
                    suggestion="Usa nombres más cortos para mejor legibilidad"
                )
            
            # Verificar caracteres válidos
            if not lexema.replace('_', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '').isalpha():
                self.error_mgr.add_warning(
                    f"Nombre contiene caracteres especiales: '{lexema}'",
                    "Validador de símbolos",
                    suggestion="Usa solo letras, números y guiones bajos"
                )
            
            return lexema
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error validando nombre de símbolo: {str(e)}",
                "Validador de símbolos"
            )
            return lexema
    def marcar_como_usado(self, linea=None, columna=None):
        """Marca el símbolo como usado y registra la referencia."""
        try:
            self.usada = True
            if linea and columna:
                referencia = f"{linea}:{columna}"
                if referencia not in self.referencias:
                    self.referencias.append(referencia)
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error marcando símbolo como usado: {str(e)}",
                "Administrador de símbolos"
            )
    def obtener_info_detallada(self):
        """Obtiene información detallada del símbolo."""
        try:
            return {
                'lexema': self.lexema,
                'categoria_lexica': self.categoria_lexica,
                'tipo': self.tipo,
                'valor': self.valor,
                'ambito': self.ambito,
                'declarada_en': self.declarada_en,
                'inicializada': self.inicializada,
                'usada': self.usada,
                'num_referencias': len(self.referencias),
                'referencias': self.referencias.copy()
            }
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error obteniendo información del símbolo: {str(e)}",
                "Administrador de símbolos"
            )
            return {'error': str(e)}
    def __repr__(self):
        try:
            return (f"Simbolo(lexema={self.lexema}, categoria_lexica={self.categoria_lexica}, "
                    f"tipo={self.tipo}, dimension={self.dimension}, valor={self.valor}, "
                    f"ambito={self.ambito}, declarada_en={self.declarada_en}, referencias={len(self.referencias)})")
        except Exception as e:
            return f"Simbolo(ERROR: {str(e)})"
class TablaSimbolos:
    def __init__(self):
        """Inicializa la tabla de símbolos con manejo de errores."""
        self.error_mgr = get_error_manager()
        self.tabla = {}
        self.ambitos = {'global': {}}  # Soporte para múltiples ámbitos
        self.ambito_actual = 'global'
        
        # Estadísticas para debugging y monitoreo
        self.estadisticas = {
            'inserciones': 0,
            'inserciones_exitosas': 0,
            'busquedas': 0,
            'busquedas_exitosas': 0,
            'actualizaciones': 0,
            'actualizaciones_exitosas': 0,
            'errores': 0,
            'validaciones': 0
        }
    def insertar(self, simbolo):
        """
        Inserta un símbolo en la tabla con validación completa.
        
        Args:
            simbolo (Simbolo): Símbolo a insertar
            
        Raises:
            ValueError: Si el símbolo ya existe o es inválido
        """
        try:
            self.estadisticas['inserciones'] += 1
            
            # Validar símbolo
            if not self._validar_simbolo_para_insercion(simbolo):
                self.estadisticas['errores'] += 1
                raise ValueError(f"Símbolo inválido: {simbolo.lexema}")
            
            # Verificar duplicados
            if simbolo.lexema in self.tabla:
                simbolo_existente = self.tabla[simbolo.lexema]
                
                # Verificar si es el mismo ámbito
                if simbolo_existente.ambito == simbolo.ambito:
                    self.estadisticas['errores'] += 1
                    error_msg = f"El símbolo '{simbolo.lexema}' ya está declarado en el ámbito '{simbolo.ambito}'"
                    
                    if simbolo_existente.declarada_en:
                        error_msg += f" (declarado en línea {simbolo_existente.declarada_en})"
                    
                    self.error_mgr.add_semantic_error(
                        error_msg,
                        simbolo.declarada_en,
                        suggestion=f"Usa un nombre diferente para '{simbolo.lexema}' o elimina la declaración duplicada"
                    )
                    raise ValueError(error_msg)
                else:
                    # Diferente ámbito, permitir pero advertir
                    self.error_mgr.add_warning(
                        f"Símbolo '{simbolo.lexema}' redeclarado en ámbito diferente (original: {simbolo_existente.ambito}, nuevo: {simbolo.ambito})",
                        "Administrador de símbolos",
                        simbolo.declarada_en,
                        "Verifica si esta redeclaración es intencional"
                    )
            
            # Insertar símbolo
            self.tabla[simbolo.lexema] = simbolo
            
            # Mantener ámbitos organizados
            if simbolo.ambito not in self.ambitos:
                self.ambitos[simbolo.ambito] = {}
            self.ambitos[simbolo.ambito][simbolo.lexema] = simbolo
            
            self.estadisticas['inserciones_exitosas'] += 1
            
            # Log de inserción exitosa
            self._log_operacion_exitosa('inserción', simbolo.lexema, simbolo.ambito)
            
        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            self.estadisticas['errores'] += 1
            error_msg = f"Error inesperado insertando símbolo '{simbolo.lexema if hasattr(simbolo, 'lexema') else 'desconocido'}': {str(e)}"
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.ERROR,
                error_msg,
                "Tabla de símbolos",
                exception=e,
                suggestion="Verifica la estructura del símbolo"
            )
            raise ValueError(error_msg)
    def _validar_simbolo_para_insercion(self, simbolo):
        """Valida que un símbolo sea válido para inserción."""
        try:
            if not isinstance(simbolo, Simbolo):
                self.error_mgr.add_semantic_error(
                    "Intento de insertar objeto que no es un Símbolo",
                    suggestion="Asegúrate de crear objetos Simbolo válidos"
                )
                return False
            
            if not hasattr(simbolo, 'lexema') or not simbolo.lexema:
                self.error_mgr.add_semantic_error(
                    "Símbolo sin lexema (nombre)",
                    suggestion="Asigna un nombre válido al símbolo"
                )
                return False
            
            if not hasattr(simbolo, 'categoria_lexica') or not simbolo.categoria_lexica:
                self.error_mgr.add_semantic_error(
                    f"Símbolo '{simbolo.lexema}' sin categoría léxica",
                    suggestion="Asigna una categoría léxica válida"
                )
                return False
            
            if not hasattr(simbolo, 'tipo') or not simbolo.tipo:
                self.error_mgr.add_semantic_error(
                    f"Símbolo '{simbolo.lexema}' sin tipo",
                    suggestion="Asigna un tipo válido al símbolo"
                )
                return False
            
            return True
            
        except Exception as e:
            self.error_mgr.add_semantic_error(
                f"Error validando símbolo: {str(e)}",
                suggestion="Verifica la estructura del símbolo"
            )
            return False
    def buscar(self, lexema):
        """
        Busca un símbolo en la tabla con registro de estadísticas.
        
        Args:
            lexema (str): Nombre del símbolo a buscar
            
        Returns:
            Simbolo or None: Símbolo encontrado o None
        """
        try:
            self.estadisticas['busquedas'] += 1
            
            if not lexema:
                self.error_mgr.add_warning(
                    "Búsqueda con lexema vacío",
                    "Buscador de símbolos",
                    suggestion="Proporciona un nombre válido para buscar"
                )
                return None
            
            simbolo = self.tabla.get(lexema, None)
            
            if simbolo:
                self.estadisticas['busquedas_exitosas'] += 1
                # Marcar como usado
                if hasattr(simbolo, 'marcar_como_usado'):
                    simbolo.marcar_como_usado()
                else:
                    simbolo.usada = True
                
                self._log_operacion_exitosa('búsqueda', lexema, simbolo.ambito)
            else:
                # No encontrado, pero no es necesariamente un error
                pass
            
            return simbolo
            
        except Exception as e:
            self.estadisticas['errores'] += 1
            self.error_mgr.add_warning(
                f"Error buscando símbolo '{lexema}': {str(e)}",
                "Buscador de símbolos",
                suggestion="Verifica que el nombre del símbolo sea válido"
            )
            return None
    def actualizar(self, lexema, **kwargs):
        """
        Actualiza un símbolo existente con validación.
        
        Args:
            lexema (str): Nombre del símbolo a actualizar
            **kwargs: Propiedades a actualizar
            
        Raises:
            ValueError: Si el símbolo no existe o la actualización es inválida
        """
        try:
            self.estadisticas['actualizaciones'] += 1
            
            if not lexema:
                self.estadisticas['errores'] += 1
                error_msg = "Intento de actualizar símbolo sin lexema"
                self.error_mgr.add_semantic_error(
                    error_msg,
                    suggestion="Proporciona el nombre del símbolo a actualizar"
                )
                raise ValueError(error_msg)
            
            if lexema not in self.tabla:
                self.estadisticas['errores'] += 1
                error_msg = f"El símbolo '{lexema}' no está declarado"
                self.error_mgr.add_semantic_error(
                    error_msg,
                    suggestion=f"Declara '{lexema}' antes de intentar actualizarlo"
                )
                raise ValueError(error_msg)
            
            simbolo = self.tabla[lexema]
            propiedades_actualizadas = []
            
            # Actualizar propiedades con validación
            for key, value in kwargs.items():
                if hasattr(simbolo, key):
                    old_value = getattr(simbolo, key)
                    setattr(simbolo, key, value)
                    propiedades_actualizadas.append(f"{key}: {old_value} → {value}")
                else:
                    self.error_mgr.add_warning(
                        f"Propiedad desconocida '{key}' en símbolo '{lexema}'",
                        "Actualizador de símbolos",
                        suggestion="Verifica que la propiedad exista"
                    )
            
            if propiedades_actualizadas:
                self.estadisticas['actualizaciones_exitosas'] += 1
                self._log_operacion_exitosa('actualización', lexema, simbolo.ambito, propiedades_actualizadas)
            else:
                self.error_mgr.add_warning(
                    f"No se actualizaron propiedades del símbolo '{lexema}'",
                    "Actualizador de símbolos",
                    suggestion="Verifica que las propiedades a actualizar sean válidas"
                )
                
        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            self.estadisticas['errores'] += 1
            error_msg = f"Error inesperado actualizando símbolo '{lexema}': {str(e)}"
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.ERROR,
                error_msg,
                "Tabla de símbolos",
                exception=e,
                suggestion="Verifica los parámetros de actualización"
            )
            raise ValueError(error_msg)
    def eliminar(self, lexema):
        """
        Elimina un símbolo de la tabla con validación.
        
        Args:
            lexema (str): Nombre del símbolo a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        try:
            if not lexema:
                self.error_mgr.add_warning(
                    "Intento de eliminar símbolo sin lexema",
                    "Eliminador de símbolos"
                )
                return False
            
            if lexema in self.tabla:
                simbolo = self.tabla[lexema]
                del self.tabla[lexema]
                
                # Eliminar de ámbitos también
                if simbolo.ambito in self.ambitos and lexema in self.ambitos[simbolo.ambito]:
                    del self.ambitos[simbolo.ambito][lexema]
                
                self._log_operacion_exitosa('eliminación', lexema, simbolo.ambito)
                return True
            else:
                self.error_mgr.add_warning(
                    f"Intento de eliminar símbolo inexistente: '{lexema}'",
                    "Eliminador de símbolos",
                    suggestion="Verifica que el símbolo exista antes de eliminarlo"
                )
                return False
                
        except Exception as e:
            self.estadisticas['errores'] += 1
            self.error_mgr.add_warning(
                f"Error eliminando símbolo '{lexema}': {str(e)}",
                "Eliminador de símbolos"
            )
            return False
    def imprimir_tabla(self):
        """Imprime la tabla de símbolos de forma compatible con código existente."""
        try:
            print("Tabla de Símbolos:")
            print(f"{'Lexema':<15} {'Categoría Lexica':<20} {'Tipo':<10} {'Dimensión':<10} {'Valor':<10} {'Ámbito':<10} {'Declarada En':<15} {'Referencias':<20}")
            print("-" * 120)
            
            for simbolo in self.tabla.values():
                try:
                    referencias_str = ', '.join(simbolo.referencias) if simbolo.referencias else 'ninguna'
                    print(f"{simbolo.lexema:<15} {simbolo.categoria_lexica:<20} {simbolo.tipo:<10} {simbolo.dimension or 'N/A':<10} {simbolo.valor or 'N/A':<10} {simbolo.ambito:<10} {simbolo.declarada_en or 'N/A':<15} {referencias_str}")
                except Exception as e:
                    print(f"ERROR mostrando símbolo: {str(e)}")
                    
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error imprimiendo tabla de símbolos: {str(e)}",
                "Impresor de tabla"
            )
            print(f"Error imprimiendo tabla: {str(e)}")
    def imprimir_tabla_mejorada(self):
        """Versión mejorada de imprimir_tabla con más información y manejo de errores."""
        try:
            print("\n📊 TABLA DE SÍMBOLOS MEJORADA")
            print(f"📈 ESTADÍSTICAS: {len(self.tabla)} símbolos totales")
            
            # Estadísticas por categoría
            categorias = {}
            for simbolo in self.tabla.values():
                cat = simbolo.categoria_lexica
                categorias[cat] = categorias.get(cat, 0) + 1
            
            for categoria, cantidad in categorias.items():
                print(f"   • {categoria.capitalize()}s: {cantidad}")
            
            # Estadísticas de operaciones
            stats = self.estadisticas
            print(f"   • Inserciones exitosas: {stats['inserciones_exitosas']}/{stats['inserciones']}")
            print(f"   • Búsquedas exitosas: {stats['busquedas_exitosas']}/{stats['busquedas']}")
            print(f"   • Actualizaciones exitosas: {stats['actualizaciones_exitosas']}/{stats['actualizaciones']}")
            print(f"   • Errores totales: {stats['errores']}")
            
            if self.tabla:
                print("\n🏗️ ESTRUCTURA POR ÁMBITOS:")
                
                for ambito, simbolos_ambito in self.ambitos.items():
                    if simbolos_ambito:  # Solo mostrar ámbitos con símbolos
                        print(f"📁 {ambito} - {len(simbolos_ambito)} símbolos")
                        
                        for lexema, simbolo in simbolos_ambito.items():
                            try:
                                estado = []
                                if simbolo.inicializada:
                                    estado.append("inicializada")
                                if simbolo.usada:
                                    estado.append("usada")
                                if not estado:
                                    estado.append("sin usar")
                                estado_str = ", ".join(estado)
                                
                                referencias = f", referencias: {len(simbolo.referencias)}" if simbolo.referencias else ""
                                valor_str = f", valor={simbolo.valor}" if simbolo.valor is not None else ""
                                
                                print(f"  • {simbolo.lexema}: {simbolo.tipo} ({simbolo.categoria_lexica}) [{estado_str}{valor_str}{referencias}]")
                                
                            except Exception as e:
                                print(f"  • ERROR mostrando {lexema}: {str(e)}")
            else:
                print("📋 Tabla vacía")
                
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error en imprimir_tabla_mejorada: {str(e)}",
                "Impresor mejorado"
            )
            print(f"Error imprimiendo tabla mejorada: {str(e)}")
            # Fallback a versión básica
            self.imprimir_tabla()
    def validar_tabla(self):
        """Valida la consistencia de la tabla de símbolos con reporte detallado."""
        try:
            self.estadisticas['validaciones'] += 1
            valida = True
            errores = []
            advertencias = []
            
            # Validación básica de estructura
            for lexema, simbolo in self.tabla.items():
                try:
                    # Verificar consistencia de lexema
                    if simbolo.lexema != lexema:
                        valida = False
                        errores.append(f"Inconsistencia en lexema: clave='{lexema}' vs símbolo.lexema='{simbolo.lexema}'")
                    
                    # Verificar propiedades obligatorias
                    if not simbolo.categoria_lexica:
                        valida = False
                        errores.append(f"Símbolo '{lexema}' sin categoría léxica")
                    
                    if not simbolo.tipo:
                        advertencias.append(f"Símbolo '{lexema}' sin tipo definido")
                    
                    # Verificar consistencia de ámbitos
                    if simbolo.ambito not in self.ambitos:
                        advertencias.append(f"Símbolo '{lexema}' referencia ámbito inexistente: '{simbolo.ambito}'")
                    elif lexema not in self.ambitos[simbolo.ambito]:
                        advertencias.append(f"Símbolo '{lexema}' no está registrado en su ámbito '{simbolo.ambito}'")
                    
                    # Verificar referencias válidas
                    if simbolo.referencias:
                        for ref in simbolo.referencias:
                            if ':' not in str(ref):
                                advertencias.append(f"Símbolo '{lexema}' tiene referencia con formato inválido: '{ref}'")
                    
                except Exception as e:
                    valida = False
                    errores.append(f"Error validando símbolo '{lexema}': {str(e)}")
            
            # Reportar resultados
            if errores:
                print("❌ Errores de validación encontrados:")
                for error in errores:
                    print(f"  • {error}")
                    self.error_mgr.add_semantic_error(
                        error,
                        suggestion="Revisa la construcción de la tabla de símbolos"
                    )
            
            if advertencias:
                print("⚠️ Advertencias de validación:")
                for advertencia in advertencias:
                    print(f"  • {advertencia}")
                    self.error_mgr.add_warning(
                        advertencia,
                        "Validador de tabla"
                    )
            
            if not errores and not advertencias:
                print("✅ Tabla de símbolos válida y consistente")
            
            return valida
            
        except Exception as e:
            self.estadisticas['errores'] += 1
            self.error_mgr.add_error(
                ErrorType.SEMANTICO,
                ErrorSeverity.WARNING,
                f"Error durante validación de tabla: {str(e)}",
                "Validador de tabla",
                exception=e
            )
            return False
    def obtener_estadisticas(self):
        """Retorna estadísticas completas de la tabla."""
        try:
            stats_basicas = {
                'total_simbolos': len(self.tabla),
                'total_ambitos': len([a for a in self.ambitos.values() if a]),
                'ambito_actual': self.ambito_actual
            }
            
            # Estadísticas por categoría
            por_categoria = {}
            por_tipo = {}
            por_ambito = {}
            
            for simbolo in self.tabla.values():
                # Por categoría
                cat = simbolo.categoria_lexica
                por_categoria[cat] = por_categoria.get(cat, 0) + 1
                
                # Por tipo
                tipo = simbolo.tipo
                por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
                
                # Por ámbito
                ambito = simbolo.ambito
                por_ambito[ambito] = por_ambito.get(ambito, 0) + 1
            
            return {
                **stats_basicas,
                'por_categoria': por_categoria,
                'por_tipo': por_tipo,
                'por_ambito': por_ambito,
                'estadisticas_operaciones': self.estadisticas.copy()
            }
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error obteniendo estadísticas: {str(e)}",
                "Generador de estadísticas"
            )
            return {'error': str(e)}
    def _log_operacion_exitosa(self, operacion, lexema, ambito, detalles=None):
        """Registra operaciones exitosas para debugging."""
        try:
            if hasattr(self.error_mgr, 'debug_mode') and self.error_mgr.debug_mode:
                mensaje = f"{operacion.capitalize()} exitosa: '{lexema}' en ámbito '{ambito}'"
                if detalles:
                    mensaje += f" ({', '.join(detalles) if isinstance(detalles, list) else detalles})"
                print(f"🔧 {mensaje}")
        except:
            pass  # No es crítico si el logging falla
    def limpiar_tabla(self):
        """Limpia completamente la tabla de símbolos."""
        try:
            simbolos_eliminados = len(self.tabla)
            self.tabla.clear()
            self.ambitos = {'global': {}}
            self.ambito_actual = 'global'
            
            # Resetear estadísticas
            for key in self.estadisticas:
                if key != 'validaciones':  # Mantener contador de validaciones
                    self.estadisticas[key] = 0
            
            print(f"🧹 Tabla de símbolos limpiada ({simbolos_eliminados} símbolos eliminados)")
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error limpiando tabla de símbolos: {str(e)}",
                "Limpiador de tabla"
            )
    def cambiar_ambito(self, nuevo_ambito):
        """Cambia el ámbito actual."""
        try:
            if not nuevo_ambito:
                self.error_mgr.add_warning(
                    "Intento de cambiar a ámbito vacío",
                    "Administrador de ámbitos"
                )
                return False
            
            ambito_anterior = self.ambito_actual
            self.ambito_actual = nuevo_ambito
            
            if nuevo_ambito not in self.ambitos:
                self.ambitos[nuevo_ambito] = {}
            
            if hasattr(self.error_mgr, 'debug_mode') and self.error_mgr.debug_mode:
                print(f"🔄 Ámbito cambiado: '{ambito_anterior}' → '{nuevo_ambito}'")
            
            return True
            
        except Exception as e:
            self.error_mgr.add_warning(
                f"Error cambiando ámbito: {str(e)}",
                "Administrador de ámbitos"
            )
            return False
