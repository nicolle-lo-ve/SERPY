# lexicoo.py - VERSIÓN CON MANEJO COMPLETO DE ERRORES
# Analizador léxico robusto que captura y reporta todos los errores de tokenización
from valor import Valor
import ply.lex as lex
from error_manager import get_error_manager, ErrorType, ErrorSeverity
import os
import traceback
class Lexico:
    def __init__(self):
        """Inicializa el analizador léxico con manejo de errores."""
        self.error_mgr = get_error_manager()
        self.errores = []  # Lista de errores para compatibilidad con código existente
        self.tokens_generados = []
        self.caracteres_procesados = 0
        self.lineas_procesadas = 0
        
        # Lista de nombres de tokens
        self.tokens = (
            'IDENTIFICADOR', 'NUMERO', 'CADENA', 'MAS', 'MENOS', 'MULT', 'DIV', 'POTENCIA',
            'IGUAL', 'DIFERENTE', 'IGUAL_IGUAL', 'MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL',
            'Y_LOGICO', 'O_LOGICO', 'NEGACION', 'COMA', 'PUNTOYCOMA', 'PAR_IZQ', 'PAR_DER',
            'LLAVE_IZQ', 'LLAVE_DER'
        )
        # Palabras reservadas
        self.reserved = {
            'si': 'SI',
            'sino': 'SINO',
            'mientras': 'MIENTRAS',
            'para': 'PARA',
            'definir': 'DEFINIR',
            'retornar': 'RETORNAR',
            'verdadero': 'VERDADERO',
            'falso': 'FALSO',
            'imprimir': 'IMPRIMIR',
            'var': 'VAR'
        }
        # Combinar tokens y palabras reservadas
        self.tokens = self.tokens + tuple(self.reserved.values())
        # Expresiones regulares para tokens simples
        self.t_MAS = r'\+'
        self.t_MENOS = r'-'
        self.t_MULT = r'\*'
        self.t_DIV = r'/'
        self.t_POTENCIA = r'\^'
        self.t_IGUAL = r'='
        self.t_DIFERENTE = r'!='
        self.t_IGUAL_IGUAL = r'=='
        self.t_MAYOR_IGUAL = r'>='
        self.t_MENOR_IGUAL = r'<='
        self.t_MAYOR = r'>'
        self.t_MENOR = r'<'
        self.t_Y_LOGICO = r'&&'
        self.t_O_LOGICO = r'\|\|'
        self.t_NEGACION = r'!'
        self.t_COMA = r','
        self.t_PUNTOYCOMA = r';'
        self.t_PAR_IZQ = r'\('
        self.t_PAR_DER = r'\)'
        self.t_LLAVE_IZQ = r'\{'
        self.t_LLAVE_DER = r'\}'
        # Caracteres ignorados (espacios y tabs)
        self.t_ignore = ' \t'
        self.lexer = None
        self._build_lexer()
    def _build_lexer(self):
        """Construye el lexer con manejo de errores."""
        try:
            self.lexer = lex.lex(module=self)
            return True
        except Exception as e:
            self.error_mgr.add_error(
                ErrorType.SISTEMA,
                ErrorSeverity.CRITICO,
                f"Error construyendo el analizador léxico: {str(e)}",
                "Constructor Léxico",
                exception=e,
                suggestion="Verifica la configuración de PLY (Python Lex-Yacc)"
            )
            return False
    def cargar_desde_archivo(self, archivo):
        """
        Carga código fuente desde un archivo con manejo robusto de errores.
        
        Args:
            archivo (str): Ruta del archivo a cargar
            
        Returns:
            str: Contenido del archivo o None si hay error
        """
        try:
            # Verificar que el archivo existe
            if not os.path.exists(archivo):
                error_msg = f"El archivo '{archivo}' no existe"
                self.errores.append(error_msg)
                self.error_mgr.add_file_error(
                    error_msg,
                    archivo,
                    f"Crea el archivo '{archivo}' o verifica la ruta"
                )
                return None
            
            # Verificar que es un archivo (no un directorio)
            if not os.path.isfile(archivo):
                error_msg = f"'{archivo}' no es un archivo válido"
                self.errores.append(error_msg)
                self.error_mgr.add_file_error(
                    error_msg,
                    archivo,
                    f"Verifica que '{archivo}' sea un archivo, no un directorio"
                )
                return None
            
            # Verificar permisos de lectura
            if not os.access(archivo, os.R_OK):
                error_msg = f"Sin permisos de lectura para '{archivo}'"
                self.errores.append(error_msg)
                self.error_mgr.add_file_error(
                    error_msg,
                    archivo,
                    f"Verifica los permisos del archivo '{archivo}'"
                )
                return None
            
            # Intentar leer con diferentes codificaciones
            codificaciones = ['utf-8', 'latin-1', 'cp1252']
            contenido = None
            
            for codif in codificaciones:
                try:
                    with open(archivo, 'r', encoding=codif) as f:
                        contenido = f.read()
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    if codif == codificaciones[-1]:  # Último intento
                        error_msg = f"Error leyendo '{archivo}': {str(e)}"
                        self.errores.append(error_msg)
                        self.error_mgr.add_file_error(
                            error_msg,
                            archivo,
                            f"Verifica que el archivo no esté corrupto o en uso"
                        )
                        return None
            
            if contenido is None:
                error_msg = f"No se pudo decodificar el archivo '{archivo}' con ninguna codificación"
                self.errores.append(error_msg)
                self.error_mgr.add_file_error(
                    error_msg,
                    archivo,
                    "Guarda el archivo con codificación UTF-8"
                )
                return None
            
            # Verificar que el archivo no esté vacío
            if not contenido.strip():
                error_msg = f"El archivo '{archivo}' está vacío"
                self.errores.append(error_msg)
                self.error_mgr.add_file_error(
                    error_msg,
                    archivo,
                    f"Agrega código fuente al archivo '{archivo}'"
                )
                return None
            
            return contenido
            
        except Exception as e:
            error_msg = f"Error inesperado cargando '{archivo}': {str(e)}"
            self.errores.append(error_msg)
            self.error_mgr.add_error(
                ErrorType.ARCHIVO,
                ErrorSeverity.CRITICO,
                error_msg,
                "Cargador de archivos",
                exception=e,
                suggestion="Verifica que el archivo sea accesible"
            )
            return None
    def analizar(self, input_text):
        """
        Analiza el texto de entrada y genera tokens con manejo completo de errores.
        
        Args:
            input_text (str): Texto a analizar
            
        Returns:
            list: Lista de tokens Valor o None si hay errores críticos
        """
        if not input_text:
            error_msg = "No hay texto para analizar"
            self.errores.append(error_msg)
            self.error_mgr.add_lexical_error(
                error_msg,
                suggestion="Proporciona código fuente válido para analizar"
            )
            return []
        
        if not self.lexer:
            error_msg = "El analizador léxico no está inicializado"
            self.errores.append(error_msg)
            self.error_mgr.add_error(
                ErrorType.SISTEMA,
                ErrorSeverity.CRITICO,
                error_msg,
                "Analizador Léxico",
                suggestion="Reinicializa el analizador léxico"
            )
            return None
        
        try:
            self.caracteres_procesados = len(input_text)
            self.lineas_procesadas = input_text.count('\n') + 1
            self.tokens_generados = []
            
            # Configurar el lexer
            self.lexer.input(input_text)
            
            # Procesar tokens
            while True:
                try:
                    tok = self.lexer.token()
                    if not tok:
                        break  # Fin de entrada
                    
                    # Calcular línea y columna
                    linea = self.find_line(input_text, tok)
                    columna = self.find_column(input_text, tok)
                    
                    # Crear objeto Valor
                    valor_token = Valor(tok.value, tok.type, linea, columna)
                    self.tokens_generados.append(valor_token)
                    
                except Exception as e:
                    error_msg = f"Error procesando token en posición {self.lexer.lexpos}: {str(e)}"
                    self.errores.append(error_msg)
                    self.error_mgr.add_lexical_error(
                        error_msg,
                        self.find_line(input_text, self.lexer.lexpos),
                        self.find_column(input_text, self.lexer.lexpos),
                        "Revisa el carácter en esa posición"
                    )
                    
                    # Intentar continuar
                    try:
                        self.lexer.skip(1)
                    except:
                        break
            
            # Verificar si se generaron tokens
            if not self.tokens_generados and not self.errores:
                warning_msg = "No se generaron tokens del código fuente"
                self.error_mgr.add_warning(
                    warning_msg,
                    "Analizador Léxico",
                    suggestion="Verifica que el código fuente tenga sintaxis válida"
                )
            
            # Reportar estadísticas
            if self.tokens_generados:
                # Detectar tokens potencialmente problemáticos
                self._validar_tokens_generados()
            
            return self.tokens_generados
            
        except Exception as e:
            error_msg = f"Error crítico en análisis léxico: {str(e)}"
            self.errores.append(error_msg)
            self.error_mgr.add_error(
                ErrorType.LEXICO,
                ErrorSeverity.CRITICO,
                error_msg,
                "Analizador Léxico",
                exception=e,
                suggestion="Revisa la sintaxis del código fuente"
            )
            return None
    def _validar_tokens_generados(self):
        """Valida los tokens generados y reporta posibles problemas."""
        try:
            # Verificar balance de paréntesis y llaves
            parentesis = 0
            llaves = 0
            
            for token in self.tokens_generados:
                if token.getToken() == 'PAR_IZQ':
                    parentesis += 1
                elif token.getToken() == 'PAR_DER':
                    parentesis -= 1
                elif token.getToken() == 'LLAVE_IZQ':
                    llaves += 1
                elif token.getToken() == 'LLAVE_DER':
                    llaves -= 1
                
                # Verificar balance intermedio
                if parentesis < 0:
                    self.error_mgr.add_warning(
                        f"Paréntesis de cierre sin apertura en línea {token.getLinea()}",
                        "Validador Léxico",
                        token.getLinea(),
                        "Verifica el balance de paréntesis"
                    )
                if llaves < 0:
                    self.error_mgr.add_warning(
                        f"Llave de cierre sin apertura en línea {token.getLinea()}",
                        "Validador Léxico", 
                        token.getLinea(),
                        "Verifica el balance de llaves"
                    )
            
            # Balance final
            if parentesis != 0:
                self.error_mgr.add_warning(
                    f"Paréntesis desbalanceados: {abs(parentesis)} {'abiertos' if parentesis > 0 else 'cerrados'} de más",
                    "Validador Léxico",
                    suggestion="Verifica que todos los paréntesis estén balanceados"
                )
            
            if llaves != 0:
                self.error_mgr.add_warning(
                    f"Llaves desbalanceadas: {abs(llaves)} {'abiertas' if llaves > 0 else 'cerradas'} de más",
                    "Validador Léxico",
                    suggestion="Verifica que todas las llaves estén balanceadas"
                )
            
            # Verificar cadenas potencialmente problemáticas
            for token in self.tokens_generados:
                if token.getToken() == 'CADENA':
                    if len(token.getLexema()) > 1000:
                        self.error_mgr.add_warning(
                            f"Cadena muy larga ({len(token.getLexema())} caracteres) en línea {token.getLinea()}",
                            "Validador Léxico",
                            token.getLinea(),
                            "Considera dividir cadenas muy largas"
                        )
                
                elif token.getToken() == 'IDENTIFICADOR':
                    if len(token.getLexema()) > 50:
                        self.error_mgr.add_warning(
                            f"Identificador muy largo ({len(token.getLexema())} caracteres) en línea {token.getLinea()}",
                            "Validador Léxico",
                            token.getLinea(),
                            "Usa nombres más cortos para variables y funciones"
                        )
        
        except Exception as e:
            # No es crítico si la validación falla
            self.error_mgr.add_warning(
                f"Error en validación de tokens: {str(e)}",
                "Validador Léxico",
                suggestion="La tokenización fue exitosa, solo falló la validación"
            )
    def find_line(self, input_text, token_or_pos):
        """Encuentra la línea de un token o posición."""
        try:
            if hasattr(token_or_pos, 'lineno'):
                return token_or_pos.lineno
            else:
                # Es una posición
                pos = token_or_pos if isinstance(token_or_pos, int) else token_or_pos.lexpos
                return input_text[:pos].count('\n') + 1
        except:
            return 1  # Valor por defecto
    def find_column(self, input_text, token_or_pos):
        """Encuentra la columna de un token o posición."""
        try:
            if hasattr(token_or_pos, 'lexpos'):
                pos = token_or_pos.lexpos
            else:
                pos = token_or_pos
            
            last_newline = input_text.rfind('\n', 0, pos)
            if last_newline < 0:
                return pos + 1
            return pos - last_newline
        except:
            return 1  # Valor por defecto
    # Definición de tokens complejos con manejo de errores
    def t_IDENTIFICADOR(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        try:
            t.type = self.reserved.get(t.value.lower(), 'IDENTIFICADOR')
            return t
        except Exception as e:
            self.error_mgr.add_lexical_error(
                f"Error procesando identificador '{t.value}': {str(e)}",
                self.find_line(t.lexer.lexdata, t),
                self.find_column(t.lexer.lexdata, t)
            )
            return None
    def t_NUMERO(self, t):
        r'\d+(\.\d+)?'
        try:
            if '.' in t.value:
                t.value = float(t.value)
            else:
                t.value = int(t.value)
                
            # Verificar rangos razonables
            if isinstance(t.value, int) and abs(t.value) > 2**31:
                self.error_mgr.add_warning(
                    f"Número muy grande: {t.value}",
                    "Analizador Léxico",
                    self.find_line(t.lexer.lexdata, t),
                    "Considera usar números más pequeños"
                )
            
            return t
        except ValueError as e:
            self.error_mgr.add_lexical_error(
                f"Número inválido '{t.value}': {str(e)}",
                self.find_line(t.lexer.lexdata, t),
                self.find_column(t.lexer.lexdata, t),
                "Verifica el formato del número"
            )
            return None
        except Exception as e:
            self.error_mgr.add_lexical_error(
                f"Error procesando número '{t.value}': {str(e)}",
                self.find_line(t.lexer.lexdata, t),
                self.find_column(t.lexer.lexdata, t)
            )
            return None
    def t_CADENA(self, t):
        r'"([^"\\]*(\\.[^"\\]*)*)"'
        try:
            t.value = t.value[1:-1]  # Eliminar comillas externas
            
            # Procesar secuencias de escape básicas
            t.value = t.value.replace('\\n', '\n')
            t.value = t.value.replace('\\t', '\t')
            t.value = t.value.replace('\\"', '"')
            t.value = t.value.replace('\\\\', '\\')
            
            return t
        except Exception as e:
            self.error_mgr.add_lexical_error(
                f"Error procesando cadena: {str(e)}",
                self.find_line(t.lexer.lexdata, t),
                self.find_column(t.lexer.lexdata, t),
                "Verifica las comillas y secuencias de escape"
            )
            return None
    def t_COMENTARIO_UNALINEA(self, t):
        r'//.*'
        # Los comentarios se ignoran, no generan tokens
        pass
    def t_COMENTARIO_MULTILINEA(self, t):
        r'/\*(.|\n)*?\*/'
        # Contar líneas para mantener numeración correcta
        t.lexer.lineno += t.value.count('\n')
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    def t_error(self, t):
        """Manejo robusto de errores léxicos."""
        try:
            char = t.value[0]
            linea = self.find_line(t.lexer.lexdata, t)
            columna = self.find_column(t.lexer.lexdata, t)
            
            # Determinar tipo de error
            if ord(char) < 32:  # Carácter de control
                error_msg = f"Carácter de control inválido (código {ord(char)})"
                suggestion = "Elimina caracteres de control del código"
            elif ord(char) > 127:  # Carácter no ASCII
                error_msg = f"Carácter no ASCII: '{char}'"
                suggestion = "Usa solo caracteres ASCII en el código"
            else:
                error_msg = f"Carácter inesperado: '{char}'"
                suggestion = f"Verifica que '{char}' sea válido en esta posición"
            
            self.errores.append(f"Línea {linea}, Columna {columna}: {error_msg}")
            self.error_mgr.add_lexical_error(
                error_msg,
                linea,
                columna,
                suggestion
            )
            
            # Saltar el carácter problemático
            t.lexer.skip(1)
            
        except Exception as e:
            # Error en el manejo de errores
            fallback_msg = f"Error léxico crítico: {str(e)}"
            self.errores.append(fallback_msg)
            self.error_mgr.add_error(
                ErrorType.LEXICO,
                ErrorSeverity.CRITICO,
                fallback_msg,
                "Manejador de errores léxicos",
                exception=e
            )
            t.lexer.skip(1)
    def obtener_estadisticas(self):
        """Obtiene estadísticas del análisis léxico."""
        return {
            'caracteres_procesados': self.caracteres_procesados,
            'lineas_procesadas': self.lineas_procesadas,
            'tokens_generados': len(self.tokens_generados),
            'errores_encontrados': len(self.errores),
            'tipos_token': len(set(token.getToken() for token in self.tokens_generados)) if self.tokens_generados else 0
        }
