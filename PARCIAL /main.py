# main.py
from lexicoo import Lexico
from arbolito import AnalizadorSintacticoLL, imprimir_tabla
import os

def main():
    # Configuración de archivos
    archivo_fuente = "codigo_fuente.txt"
    archivo_tabla = "tabla_ll1.csv"
    
    # Paso 1: Análisis léxico
    print("\n=== ETAPA 1: ANÁLISIS LÉXICO ===")
    lexer = Lexico()
    codigo = lexer.cargar_desde_archivo(archivo_fuente)
    
    if not codigo:
        print(f"No se pudo leer el archivo fuente: {archivo_fuente}")
        return
    
    tokens = lexer.analizar(codigo)
    
    # Mostrar resultados del análisis léxico
    print("\nTokens encontrados:")
    print("Lexema\t\tToken\t\tLínea:Columna")
    print("-" * 50)
    for token in tokens:
        print(token.toString())
    
    # Verificar si hay errores léxicos
    if lexer.errores:
        print("\nErrores léxicos encontrados:")
        for error in lexer.errores:
            print(error)
        return
    
    # Paso 2: Preparar tokens para el análisis sintáctico
    lista_tokens = [token.getToken() for token in tokens]
    print("\nLista de tokens para análisis sintáctico:")
    print(" ".join(lista_tokens))
    
    # Paso 3: Análisis sintáctico
    print("\n=== ETAPA 2: ANÁLISIS SINTÁCTICO ===")
    analizador = AnalizadorSintacticoLL(archivo_tabla)
    resultado = analizador.analizar(lista_tokens)
    
    # Mostrar resultados
    print("\n" + "="*50)
    print("RESULTADO DEL ANÁLISIS SINTÁCTICO")
    print("="*50)
    print(f"\nEntrada analizada: {' '.join(lista_tokens)}")
    print(f"\nConclusión: {resultado['CONCLUSION']}")
    print(f"Mensaje: {resultado['mensaje']}")
    
    # Mostrar pasos del análisis si hay error
    if resultado['CONCLUSION'] != "ACEPTADO :)":
        print("\nPasos del análisis hasta el error:")
        titulos = ["Paso", "Pila", "Entrada", "Acción"]
        anchos = [5, 30, 30, 30]
        datos = [(p[0], p[1], p[2], p[3]) for p in resultado['pasos']]
        imprimir_tabla(datos, titulos, anchos)
    
    # Generar gráfico del árbol si fue exitoso
    if resultado['graphviz_code']:
        print("\n=== REPRESENTACIÓN GRÁFICA DEL ÁRBOL ===")
        print("\nCódigo Graphviz generado:")
        print(resultado['graphviz_code'])
        
        # Guardar el código DOT en un archivo
        with open("arbol_sintactico.dot", "w", encoding="utf-8") as f:
            f.write(resultado['graphviz_code'])
        
        print("\nEl archivo 'arbol_sintactico.dot' ha sido generado.")
        print("Puedes visualizarlo en: https://dreampuf.github.io/GraphvizOnline/")

if __name__ == "__main__":
    main()
