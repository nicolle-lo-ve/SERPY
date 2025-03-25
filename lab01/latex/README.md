# Analizador Léxico con PLY

Este proyecto implementa un analizador léxico utilizando la biblioteca `ply` en Python. El objetivo es procesar código fuente de un lenguaje de programación ficticio basado en Python y extraer tokens para su posterior análisis.

## Instalación

Asegúrate de tener Python instalado en tu sistema. Luego, instala `ply` si aún no lo tienes:

```bash
pip install ply
```

## Descripción del Código

El código se divide en varias secciones principales:

### 1. Importación de PLY

```python
import ply.lex as lex
```

PLY (Python Lex-Yacc) es una herramienta que permite definir analizadores léxicos y sintácticos en Python.

### 2. Definición de Tokens

El conjunto de tokens está definido en la variable `tokens`, incluyendo identificadores, operadores, delimitadores y otros símbolos del lenguaje:

```python
tokens = ('IDENTIFICADOR', 'ENTERO', 'DECIMAL', 'CADENA', 'ASIGNACION', 'SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION', 'IGUALDAD', 'DESIGUALDAD', 'MAYORQUE', 'MENORQUE', 'YLOGICO', 'OLOGICO', 'NEGACION', 'COMA', 'PARENTESISAPERTURA', 'PARENTESISCIERRE', 'LLAVEAPERTURA', 'LLAVECIERRE', 'CORCHETEAPERTURA', 'CORCHETECERRADURA', 'COMENTARIOUNALINEA', 'COMENTARIOMULTILINEA')
```

Además, se definen palabras clave del lenguaje como `si`, `sino`, `mientras`, `para`, `funcion`, `retornar`, etc.

### 3. Expresiones Regulares

Se definen expresiones regulares para identificar cada token:

```python
t_ASIGNACION = r'='
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'
t_IGUALDAD = r'=='
t_DESIGUALDAD = r'!='
t_MAYORQUE = r'>'
t_MENORQUE = r'<'
t_YLOGICO = r'y'
t_OLOGICO = r'o'
t_NEGACION = r'no'
t_COMA = r','
t_PARENTESISAPERTURA = r'\('
t_PARENTESISCIERRE = r'\)'
t_LLAVEAPERTURA = r'\{'
t_LLAVECIERRE = r'\}'
t_CORCHETEAPERTURA = r'\['
t_CORCHETECERRADURA = r'\]'
```

Funciones adicionales manejan identificadores, números, cadenas y comentarios:

```python
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFICADOR')
    return t

def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_DECIMAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CADENA(t):
    r'"([^"\\]*(\\.[^"\\]*)*)"'
    t.value = t.value[1:-1]
    return t
```

### 4. Manejo de Comentarios y Errores

Los comentarios de una línea y multilínea se ignoran:

```python
def t_COMENTARIOUNALINEA(t):
    r'//.*'
    pass

def t_COMENTARIOMULTILINEA(t):
    r'/\*[\s\S]*?\*/'
    pass
```

Errores léxicos se manejan informando el carácter ilegal:

```python
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
    t.lexer.skip(1)
```

### 5. Construcción del Lexer

```python
lexer = lex.lex()
```

Se carga y analiza un archivo de código fuente:

```python
with open("codigo_fuente.txt", "r", encoding="utf-8") as f:
    data = f.read()
lexer.input(data)
```

### 6. Ejemplo de Código Fuente Analizado

El código fuente de prueba contiene funciones, estructuras de control y operaciones matemáticas:

```python
imprimir("Hola Mundo")

i = 0
mientras i < 3 {
    j = 0
    mientras j < 3 {
        imprimir("Posición: (" + i + ", " + j + ")")
        j = j + 1
    }
    i = i + 1
}

definir factorial(n) {
    si n == 0 {
        retornar 1
    } sino {
        retornar n * factorial(n - 1)
    }
}
imprimir(factorial(5))
```

### 7. Salida del Analizador Léxico

El lexer generará una lista de tokens con su tipo, valor y posición en el código fuente.

```python
for token in tokens_list:
    print(token)
```

Ejemplo de salida:

```json
{
    "type": "IDENTIFICADOR",
    "lexeme": "imprimir",
    "line": 1,
    "column": 1
}
```




