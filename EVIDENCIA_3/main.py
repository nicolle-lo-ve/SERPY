from lexicoo import Lexico
from arbolito import AnalizadorSintacticoLL, imprimir_tabla
from semantico import Semantico  # USA EL SEMÁNTICO CORREGIDO
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
        print(f"❌ Error: No se pudo leer el archivo fuente: {archivo_fuente}")
        return False
    
    tokens = lexer.analizar(codigo)
    # Mostrar resultados del análisis léxico
    print(f"\n📝 Tokens encontrados: {len(tokens)}")
    print("Lexema\t\tToken\t\tLínea:Columna")
    print("-" * 50)
    for token in tokens:
        print(token.toString())
    
    # Verificar si hay errores léxicos
    if lexer.errores:
        print("\n❌ Errores léxicos encontrados:")
        for error in lexer.errores:
            print(f"  • {error}")
        return False
    
    # Paso 2: Preparar tokens para el análisis sintáctico
    lista_tokens = [token.getToken() for token in tokens]
    print(f"\n🔗 Lista de tokens para análisis sintáctico: {' '.join(lista_tokens)}")
    
    # Paso 3: Análisis sintáctico
    print("\n=== ETAPA 2: ANÁLISIS SINTÁCTICO ===")
    try:
        analizador = AnalizadorSintacticoLL(archivo_tabla)
        resultado = analizador.analizar(lista_tokens)
        
        # Mostrar resultados
        print("\n" + "="*50)
        print("RESULTADO DEL ANÁLISIS SINTÁCTICO")
        print("="*50)
        print(f"Entrada analizada: {' '.join(lista_tokens)}")
        print(f"Conclusión: {resultado['CONCLUSION']}")
        print(f"Mensaje: {resultado['mensaje']}")
        
        # Mostrar pasos del análisis si hay error
        if resultado['CONCLUSION'] != "ACEPTADO :)":
            print("\n❌ Pasos del análisis hasta el error:")
            if 'pasos' in resultado and resultado['pasos']:
                titulos = ["Paso", "Pila", "Entrada", "Acción"]
                anchos = [5, 30, 30, 30]
                datos = [(p[0], p[1], p[2], p[3]) for p in resultado['pasos']]
                imprimir_tabla(datos, titulos, anchos)
            return False
        
    except Exception as e:
        print(f"❌ Error en análisis sintáctico: {e}")
        return False
    
    # Generar gráfico del árbol si fue exitoso
    if resultado['graphviz_code']:
        print("\n=== REPRESENTACIÓN GRÁFICA DEL ÁRBOL ===")
        print("Código Graphviz generado y guardado en 'arbol_sintactico.dot'")
        
        # Guardar el código DOT en un archivo
        try:
            with open("arbol_sintactico.dot", "w", encoding="utf-8") as f:
                f.write(resultado['graphviz_code'])
            print("📊 Visualízalo en: https://dreampuf.github.io/GraphvizOnline/")
        except Exception as e:
            print(f"⚠️ No se pudo guardar el archivo DOT: {e}")
    
    # Paso 4: Análisis Semántico - Tabla de Símbolos (MEJORADO)
    if resultado['CONCLUSION'] == "ACEPTADO :)" and resultado['arbol']:
        print("\n=== ETAPA 3: CONSTRUCCIÓN DE TABLA DE SÍMBOLOS (MEJORADA) ===")
        
        try:
            # USAR EL SEMÁNTICO CORREGIDO
            semantico = Semantico()
            tabla_simbolos = semantico.construir_tabla_simbolos(tokens, resultado['arbol'])
            
            if tabla_simbolos and tabla_simbolos.tabla:
                print("\n✅ ÉXITO: Tabla de símbolos construida correctamente")
                
                # Mostrar tabla con versión mejorada
                tabla_simbolos.imprimir_tabla_mejorada()
                
                # Validar tabla
                print(f"\n🔍 Validación: {'✅ Válida' if tabla_simbolos.validar_tabla() else '❌ Con errores'}")
                
                # Guardar tabla de símbolos en un archivo
                try:
                    with open("tabla_simbolos.txt", "w", encoding="utf-8") as f:
                        import sys
                        original_stdout = sys.stdout
                        sys.stdout = f
                        tabla_simbolos.imprimir_tabla()
                        sys.stdout = original_stdout
                    
                    print("\n💾 Tabla de símbolos guardada en 'tabla_simbolos.txt'")
                    
                except Exception as e:
                    print(f"⚠️ No se pudo guardar tabla de símbolos: {e}")
                
                # Mostrar estadísticas finales
                stats = tabla_simbolos.obtener_estadisticas()
                print(f"\n📊 ESTADÍSTICAS FINALES:")
                print(f"   • Total símbolos: {stats['total_simbolos']}")
                print(f"   • Variables: {stats['variables']}")
                print(f"   • Funciones: {stats['funciones']}")
                print(f"   • Operaciones realizadas: {stats['estadisticas_operaciones']}")
                
                return True
                
            else:
                print("❌ Error: No se pudo construir la tabla de símbolos.")
                print("   La tabla está vacía o es None.")
                return False
                
        except Exception as e:
            print(f"❌ Error en análisis semántico: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    else:
        print("⚠️ No se puede construir tabla de símbolos porque el análisis sintáctico falló.")
        return False
def main_original_compatible():
    """Versión exactamente compatible con el main.py original para testing."""
    from lexicoo import Lexico
    from arbolito import AnalizadorSintacticoLL, imprimir_tabla
    from semantico import Semantico
    import os
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
    
    # Paso 4: Análisis Semántico - Tabla de Símbolos
    if resultado['CONCLUSION'] == "ACEPTADO :)" and resultado['arbol']:
        print("\n=== ETAPA 3: CONSTRUCCIÓN DE TABLA DE SÍMBOLOS ===")
        semantico = Semantico()
        tabla_simbolos = semantico.construir_tabla_simbolos(tokens, resultado['arbol'])
        
        if tabla_simbolos:
            tabla_simbolos.imprimir_tabla()
            
            # Guardar tabla de símbolos en un archivo
            with open("tabla_simbolos.txt", "w", encoding="utf-8") as f:
                import sys
                original_stdout = sys.stdout
                sys.stdout = f
                tabla_simbolos.imprimir_tabla()
                sys.stdout = original_stdout
            
            print("\nTabla de símbolos guardada en 'tabla_simbolos.txt'")
        else:
            print("\nError: No se pudo construir la tabla de símbolos.")
if __name__ == "__main__":
    # Usar la versión mejorada por defecto
    exito = main()
    
    if exito:
        print("\n🎉 ¡COMPILACIÓN EXITOSA!")
    else:
        print("\n⚠️ Hubo errores en la compilación. Revisa los mensajes anteriores.")