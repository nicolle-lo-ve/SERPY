import os
from AnalizadorLexico import analyze_file
from AnalizadorSintactico import parser_ll1, cargar_tabla_desde_csv, imprimir_arbol
from AnalizadorSemantico import AnalizadorSemantico

def main():
    # 1. Análisis Léxico
    ruta_archivo = os.path.join("input", "programa.serpy")
    tokens = analyze_file(ruta_archivo)
    
    # 2. Análisis Sintáctico
    tabla_ll1 = cargar_tabla_desde_csv("table_ll1.csv")
    ast = parser_ll1(tokens, tabla_ll1, start_symbol="PROGRAMA")
    
    if ast:
        print("✅ Análisis Sintáctico Exitoso")
        # 3. Análisis Semántico
        analizador_sem = AnalizadorSemantico()
        if analizador_sem.analizar(ast):
            print("✅ Análisis Semántico Exitoso")
            # Exportar el AST final (con tipos)
            from AnalizadorSintactico import exportar_arbol_a_graphviz
            exportar_arbol_a_graphviz(ast, "output/arbol_parseo_final.dot")
            print("Árbol de sintaxis exportado a 'output/arbol_parseo_final.dot'")
        else:
            print("❌ Error en el análisis semántico")
    else:
        print("❌ Error en el análisis sintáctico")

if __name__ == "__main__":
    main()
