from valor import Valor
import ply.lex as lex

class Lexico:
    # Lista de nombres de tokens (como lo deseas)
    tokens = (
        'IDENTIFICADOR', 'NUMERO', 'CADENA', 'MAS', 'MENOS', 'MULT', 'DIV', 'POTENCIA',
        'IGUAL', 'DIFERENTE', 'IGUAL_IGUAL', 'MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL',
        'Y_LOGICO', 'O_LOGICO', 'NEGACION', 'COMA', 'PUNTOYCOMA', 'PAR_IZQ', 'PAR_DER',
        'LLAVE_IZQ', 'LLAVE_DER'
    )

    # Palabras reservadas (como lo deseas)
    reserved = {
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
    tokens = tokens + tuple(reserved.values())

    # Expresiones regulares para tokens simples
    t_MAS = r'\+'
    t_MENOS = r'-'
    t_MULT = r'\*'
    t_DIV = r'/'
    t_POTENCIA = r'\^'
    t_IGUAL = r'='
    t_IGUAL_IGUAL = r'=='
    t_DIFERENTE = r'!='
    t_MAYOR = r'>'
    t_MENOR = r'<'
    t_MAYOR_IGUAL = r'>='
    t_MENOR_IGUAL = r'<='
    t_Y_LOGICO = r'&&'
    t_O_LOGICO = r'\|\|'
    t_NEGACION = r'!'
    t_PUNTOYCOMA = r';'
    t_COMA = r','
    t_PAR_IZQ = r'\('
    t_PAR_DER = r'\)'
    t_LLAVE_IZQ = r'\{'
    t_LLAVE_DER = r'\}'

    # Ignorar espacios y tabs
    t_ignore = ' \t'

    def __init__(self):
        self.lexer = None
        self.lista_tokens = []
        self.errores = []

    def cargar_desde_archivo(self, archivo):
        """Carga el código fuente desde un archivo"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = f.read()
            return data
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return None

    def construir(self):
        """Construye el lexer de PLY"""
        self.lexer = lex.lex(module=self)

    def analizar(self, data):
        """Analiza el código fuente"""
        if not self.lexer:
            self.construir()
        
        self.lexer.input(data)
        self.lista_tokens = []
        
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            
            # Crear objeto Valor para cada token
            valor_token = Valor(
                lexema=tok.value,
                token=tok.type,
                linea=tok.lineno,
                columna=self.find_column(data, tok)
            )
            
            self.lista_tokens.append(valor_token)
        
        return self.lista_tokens



    def find_column(self, input_text, token):
        """Calcula la columna exacta del token"""
        last_newline = input_text.rfind('\n', 0, token.lexpos)
        if last_newline < 0:
            return token.lexpos + 1
        return token.lexpos - last_newline

    # Definición de tokens complejos
    def t_IDENTIFICADOR(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value.lower(), 'IDENTIFICADOR')
        return t

    def t_NUMERO(self, t):
        r'\d+(\.\d+)?'
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    def t_CADENA(self, t):
        r'"([^"\\]*(\\.[^"\\]*)*)"' 
        t.value = t.value[1:-1]  # Eliminar comillas externas
        return t

    def t_COMENTARIO_UNALINEA(self, t):
        r'//.*'
        pass  # Ignorar comentarios

    def t_COMENTARIO_MULTILINEA(self, t):
        r'/\*[\s\S]*?\*/'
        pass  # Ignorar comentarios

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        self.errores.append(f"Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
        t.lexer.skip(1)

    def obtener_resultados(self):
        """Devuelve los resultados formateados"""
        auxcad = "Lexema\tToken\tLinea:Columna\n"
        auxcad += "-----------------------------------------\n"
        for token in self.lista_tokens:
            auxcad += token.toString() + "\n"
        return auxcad
