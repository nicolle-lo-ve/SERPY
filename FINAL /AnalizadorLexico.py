import ply.lex as lex
from prettytable import PrettyTable
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lista de tokens actualizada para SERPY
tokens = [
    # Palabras reservadas
    'VAR', 'RETORNAR', 'IMPRIMIR', 'SI', 'SINO', 'MIENTRAS', 'PARA', 'DEFINIR',
    'VERDADERO', 'FALSO',
    
    # Tipos de datos
    'NUMERO', 'CADENA', 'IDENTIFICADOR',
    
    # Operadores
    'IGUAL', 'IGUAL_IGUAL', 'DIFERENTE', 'MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL',
    'MAS', 'MENOS', 'MULT', 'DIV', 'POTENCIA', 'O_LOGICO', 'Y_LOGICO', 'NEGACION',
    
    # Delimitadores
    'PUNTOYCOMA', 'PAR_IZQ', 'PAR_DER', 'LLAVE_IZQ', 'LLAVE_DER', 'COMA'
]

# Palabras reservadas actualizadas
reserved_words = {
    'var': 'VAR',
    'retornar': 'RETORNAR',
    'imprimir': 'IMPRIMIR',
    'si': 'SI',
    'sino': 'SINO',
    'mientras': 'MIENTRAS',
    'para': 'PARA',
    'definir': 'DEFINIR',
    'verdadero': 'VERDADERO',
    'falso': 'FALSO'
}

# Expresiones regulares para tokens simples
t_IGUAL = r'='
t_IGUAL_IGUAL = r'=='
t_DIFERENTE = r'!='
t_MAYOR = r'>'
t_MENOR = r'<'
t_MAYOR_IGUAL = r'>='
t_MENOR_IGUAL = r'<='
t_MAS = r'\+'
t_MENOS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_POTENCIA = r'\^'
t_O_LOGICO = r'\|\|'
t_Y_LOGICO = r'&&'
t_NEGACION = r'!'
t_PUNTOYCOMA = r';'
t_PAR_IZQ = r'\('
t_PAR_DER = r'\)'
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_COMA = r','

# Ignorar espacios y tabulaciones
t_ignore = ' \t\r'

# Manejo de números (enteros y decimales)
def t_NUMERO(t):
    r'\d+\.\d+|\d+'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

# Manejo de cadenas entre comillas dobles o simples
def t_CADENA(t):
    r'\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\''
    t.value = t.value[1:-1]  # Eliminar las comillas
    return t

# Manejo de identificadores y palabras reservadas
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_words.get(t.value, 'IDENTIFICADOR')
    return t

# Comentarios de línea (comienzan con #)
def t_COMENTARIO_LINEA(t):
    r'\#.*'
    pass  # Ignorar comentarios

# Comentarios de bloque (/* ... */)
def t_COMENTARIO_BLOQUE(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')  # Actualizar contador de líneas
    pass  # Ignorar comentarios

# Manejo de saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}, posición {t.lexpos}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# Función para analizar un archivo (mantenida para compatibilidad con el main)
def analyze_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{filepath}'.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return None

    lexer.input(data)
    tokens_list = []
    table = PrettyTable(["Tipo", "Valor", "Línea", "Posición"])
    tokens_output_for_file = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)
        tokens_output_for_file.append(str(tok.type))
        table.add_row([tok.type, tok.value, tok.lineno, tok.lexpos])

    print("\nTokens encontrados:")
    print(table)

    # Guardar tokens en archivo para depuración
    tokens_output_path = os.path.join(BASE_DIR, "Outputs", "tokens_output.txt")
    os.makedirs(os.path.dirname(tokens_output_path), exist_ok=True)
    
    try:
        with open(tokens_output_path, 'w', encoding='utf-8') as output_file:
            for tok in tokens_list:
                output_file.write(f"{tok.type} {tok.value} {tok.lineno} {tok.lexpos}\n")
        print(f"\nTokens guardados en: {tokens_output_path}")
    except IOError as e:
        print(f"Error al escribir el archivo de tokens: {e}")

    return tokens_list

# Ejecución independiente para pruebas
if __name__ == '__main__':
    archivo_entrada_path = os.path.join(BASE_DIR, "Inputs", "programa.serpy")
    
    if not os.path.exists(archivo_entrada_path):
        print(f"Creando archivo de ejemplo en: {archivo_entrada_path}")
        os.makedirs(os.path.dirname(archivo_entrada_path), exist_ok=True)
        with open(archivo_entrada_path, 'w', encoding='utf-8') as f:
            f.write("""var x = 10;
imprimir(x);

definir suma(a, b) {
    retornar a + b;
}

var resultado = suma(5, 3);
imprimir(resultado);
""")
    
    print(f"Analizando archivo: {archivo_entrada_path}")
    tokens_found = analyze_file(archivo_entrada_path)
    
    if tokens_found:
        print(f"\nSe encontraron {len(tokens_found)} tokens")
    else:
        print("\nNo se encontraron tokens o hubo un error")
