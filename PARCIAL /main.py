# main.py - VERSIÓN SIN REPORTES DUPLICADOS
# Corrige el problema de reportes que se imprimen dos veces
from lexicoo import Lexico
from arbolito import AnalizadorSintacticoLL, imprimir_tabla
from semantico import Semantico
from error_manager import get_error_manager, reset_error_manager, ErrorType, ErrorSeverity
import os
import sys
# VARIABLE GLOBAL para evitar ejecución múltiple
_main_ejecutado = False
def main():
    """
    Función principal del compilador con manejo completo de errores.
    CORREGIDO: Solo ejecuta y reporta una vez.
    """
    global _main_ejecutado
    
    # Evitar ejecución múltiple
    if _main_ejecutado:
        return True
    
    _main_ejecutado = True
    
    # Reiniciar el gestor de errores para una nueva compilación
    error_mgr = reset_error_manager()
    error_mgr.set_debug_mode(False)  # Cambiar a True para debug detallado
    
    print("🚀 COMPILADOR CON MANEJO DE ERRORES ROBUSTO")
    print("=" * 60)
    
    compilacion_exitosa = False
    
    try:
        # Configuración de archivos
        archivo_fuente = "codigo_fuente.txt"
        archivo_tabla = "tabla_ll1.csv"
        
        error_mgr.set_execution_phase("INICIALIZACIÓN")
        
        # Verificar archivos necesarios
        if not verificar_archivos_necesarios(error_mgr, archivo_fuente, archivo_tabla):
            return generar_reporte_final_unico(error_mgr, False, "INICIALIZACIÓN")
        
        # ETAPA 1: Análisis léxico
        error_mgr.set_execution_phase("ANÁLISIS LÉXICO")
        print("\n=== ETAPA 1: ANÁLISIS LÉXICO ===")
        
        tokens = ejecutar_analisis_lexico(error_mgr, archivo_fuente)
        if tokens is None:
            return generar_reporte_final_unico(error_mgr, False, "ANÁLISIS LÉXICO")
        
        # ETAPA 2: Análisis sintáctico
        error_mgr.set_execution_phase("ANÁLISIS SINTÁCTICO")
        print("\n=== ETAPA 2: ANÁLISIS SINTÁCTICO ===")
        
        resultado_sintactico = ejecutar_analisis_sintactico(error_mgr, tokens, archivo_tabla)
        if resultado_sintactico is None:
            return generar_reporte_final_unico(error_mgr, False, "ANÁLISIS SINTÁCTICO")
        
        # ETAPA 3: Análisis semántico
        error_mgr.set_execution_phase("ANÁLISIS SEMÁNTICO")
        print("\n=== ETAPA 3: ANÁLISIS SEMÁNTICO ===")
        
        tabla_simbolos = ejecutar_analisis_semantico(error_mgr, tokens, resultado_sintactico['arbol'])
        if tabla_simbolos is None:
            return generar_reporte_final_unico(error_mgr, False, "ANÁLISIS SEMÁNTICO")
        
        # ETAPA 4: Generación de archivos de salida
        error_mgr.set_execution_phase("GENERACIÓN DE SALIDA")
        print("\n=== ETAPA 4: GENERACIÓN DE ARCHIVOS ===")
        
        generar_archivos_salida(error_mgr, resultado_sintactico, tabla_simbolos)
        
        compilacion_exitosa = True
        
    except KeyboardInterrupt:
        error_mgr.add_error(
            ErrorType.SISTEMA,
            ErrorSeverity.ERROR,
            "Compilación interrumpida por el usuario (Ctrl+C)",
            "Sistema",
            suggestion="Espera a que termine o usa 'exit()' si estás en modo interactivo"
        )
        print("\n⚠️ Compilación interrumpida por el usuario")
        
    except MemoryError:
        error_mgr.add_error(
            ErrorType.SISTEMA,
            ErrorSeverity.CRITICO,
            "Sin memoria suficiente para completar la compilación",
            "Sistema",
            suggestion="Cierra otros programas o usa un archivo de código más pequeño"
        )
        
    except Exception as e:
        error_mgr.add_error(
            ErrorType.SISTEMA,
            ErrorSeverity.CRITICO,
            f"Error inesperado del sistema: {str(e)}",
            "Sistema",
            exception=e,
            suggestion="Reporta este error al desarrollador con el código que causó el problema"
        )
        
    finally:
        # Generar reporte final SOLO UNA VEZ
        fase_final = error_mgr.execution_phase if hasattr(error_mgr, 'execution_phase') else "DESCONOCIDA"
        return generar_reporte_final_unico(error_mgr, compilacion_exitosa, fase_final)
def verificar_archivos_necesarios(error_mgr, archivo_fuente, archivo_tabla):
    """Verifica que todos los archivos necesarios existan."""
    archivos_ok = True
    
    # Verificar archivo de código fuente
    if not os.path.exists(archivo_fuente):
        error_mgr.add_file_error(
            f"No se encontró el archivo de código fuente: {archivo_fuente}",
            archivo_fuente,
            f"Crea el archivo {archivo_fuente} con tu código fuente"
        )
        archivos_ok = False
    elif os.path.getsize(archivo_fuente) == 0:
        error_mgr.add_file_error(
            f"El archivo de código fuente está vacío: {archivo_fuente}",
            archivo_fuente,
            f"Agrega código fuente al archivo {archivo_fuente}"
        )
        archivos_ok = False
    
    # Verificar tabla LL1 (opcional pero recomendada)
    if not os.path.exists(archivo_tabla):
        error_mgr.add_warning(
            f"No se encontró la tabla LL1: {archivo_tabla}",
            "Sistema de archivos",
            suggestion=f"Crea el archivo {archivo_tabla} para análisis sintáctico completo"
        )
        # No es crítico, continuamos
    
    return archivos_ok
def ejecutar_analisis_lexico(error_mgr, archivo_fuente):
    """Ejecuta el análisis léxico con manejo de errores."""
    try:
        lexer = Lexico()
        
        # Cargar código fuente
        codigo = lexer.cargar_desde_archivo(archivo_fuente)
        if not codigo:
            error_mgr.add_file_error(
                f"No se pudo leer el contenido del archivo: {archivo_fuente}",
                archivo_fuente,
                "Verifica que el archivo exista y tenga permisos de lectura"
            )
            return None
        
        print(f"📄 Código fuente leído: {len(codigo)} caracteres")
        print(f"   Primeras líneas: {repr(codigo[:100])}...")
        
        # Analizar tokens
        tokens = lexer.analizar(codigo)
        
        if hasattr(lexer, 'errores') and lexer.errores:
            print(f"\n❌ Se encontraron {len(lexer.errores)} errores léxicos:")
            for i, error in enumerate(lexer.errores, 1):
                print(f"   {i}. {error}")
                error_mgr.add_lexical_error(
                    str(error),
                    suggestion="Revisa la sintaxis del código fuente"
                )
            return None
        
        print(f"✅ Análisis léxico exitoso: {len(tokens)} tokens generados")
        
        # Mostrar resumen de tokens
        if tokens:
            tipos_token = {}
            for token in tokens:
                tipo = token.getToken()
                tipos_token[tipo] = tipos_token.get(tipo, 0) + 1
            
            print(f"📊 Tipos de tokens: {len(tipos_token)} diferentes")
            print("   Los más frecuentes:", end="")
            for tipo, count in sorted(tipos_token.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f" {tipo}({count})", end="")
            print()
        
        return tokens
        
    except ImportError as e:
        error_mgr.add_error(
            ErrorType.SISTEMA,
            ErrorSeverity.CRITICO,
            f"Error importando el analizador léxico: {str(e)}",
            "Analizador Léxico",
            exception=e,
            suggestion="Verifica que el archivo lexicoo.py esté en el directorio actual"
        )
        return None
        
    except Exception as e:
        error_mgr.add_error(
            ErrorType.LEXICO,
            ErrorSeverity.CRITICO,
            f"Error inesperado en análisis léxico: {str(e)}",
            "Analizador Léxico",
            exception=e,
            suggestion="Revisa la sintaxis del código fuente"
        )
        return None
def ejecutar_analisis_sintactico(error_mgr, tokens, archivo_tabla):
    """Ejecuta el análisis sintáctico con manejo de errores."""
    try:
        # Preparar lista de tokens
        lista_tokens = [token.getToken() for token in tokens]
        print(f"🔗 Tokens a analizar: {' '.join(lista_tokens[:10])}{'...' if len(lista_tokens) > 10 else ''}")
        
        # Crear analizador sintáctico
        analizador = AnalizadorSintacticoLL(archivo_tabla)
        
        # Ejecutar análisis
        resultado = analizador.analizar(lista_tokens)
        
        # Verificar resultado
        if not resultado:
            error_mgr.add_syntax_error(
                "El analizador sintáctico no devolvió resultado",
                suggestion="Verifica la tabla LL1 y la gramática"
            )
            return None
        
        if resultado.get('CONCLUSION') != "ACEPTADO :)":
            mensaje_error = resultado.get('mensaje', 'Error sintáctico desconocido')
            error_mgr.add_syntax_error(
                mensaje_error,
                suggestion="Revisa que la estructura del código coincida con la gramática"
            )
            
            # Mostrar detalles del error si están disponibles
            if 'pasos' in resultado and resultado['pasos']:
                print("\n🔍 Pasos del análisis hasta el error:")
                pasos = resultado['pasos'][-5:]  # Últimos 5 pasos
                for paso in pasos:
                    print(f"   {paso}")
            
            return None
        
        print("✅ Análisis sintáctico exitoso")
        
        # Mostrar estadísticas si están disponibles
        if 'estadisticas' in resultado:
            stats = resultado['estadisticas']
            print(f"📊 Estadísticas: {stats.get('nodos_creados', 0)} nodos, {stats.get('producciones_aplicadas', 0)} producciones")
        
        # Generar archivo DOT si es posible
        if resultado.get('graphviz_code'):
            try:
                with open("arbol_sintactico.dot", "w", encoding="utf-8") as f:
                    f.write(resultado['graphviz_code'])
                print("📊 Archivo 'arbol_sintactico.dot' generado")
            except Exception as e:
                error_mgr.add_warning(
                    f"No se pudo generar archivo DOT: {str(e)}",
                    "Generador de gráficos",
                    suggestion="Esto no afecta la compilación, es solo para visualización"
                )
        
        return resultado
        
    except FileNotFoundError:
        error_mgr.add_file_error(
            f"No se encontró la tabla LL1: {archivo_tabla}",
            archivo_tabla,
            "Usa un árbol sintáctico simulado o crea la tabla LL1"
        )
        
        # Intentar usar árbol simulado
        try:
            from arbolito import Node
            print("⚠️ Usando árbol sintáctico simulado para continuar")
            return {
                'CONCLUSION': "ACEPTADO :)",
                'arbol': Node('PROGRAMA'),
                'mensaje': 'Análisis simulado exitoso',
                'graphviz_code': None
            }
        except Exception:
            error_mgr.add_syntax_error(
                "No se pudo crear árbol sintáctico simulado",
                suggestion="Verifica que el archivo arbolito.py esté disponible"
            )
            return None
            
    except Exception as e:
        error_mgr.add_error(
            ErrorType.SINTACTICO,
            ErrorSeverity.CRITICO,
            f"Error inesperado en análisis sintáctico: {str(e)}",
            "Analizador Sintáctico",
            exception=e,
            suggestion="Verifica la gramática y la tabla LL1"
        )
        return None
def ejecutar_analisis_semantico(error_mgr, tokens, arbol):
    """Ejecuta el análisis semántico con manejo de errores."""
    try:
        semantico = Semantico()
        
        # Construir tabla de símbolos
        tabla_simbolos = semantico.construir_tabla_simbolos(tokens, arbol)
        
        if not tabla_simbolos:
            error_mgr.add_semantic_error(
                "No se pudo crear la tabla de símbolos",
                suggestion="Verifica que el código tenga declaraciones válidas"
            )
            return None
        
        if not hasattr(tabla_simbolos, 'tabla') or not tabla_simbolos.tabla:
            error_mgr.add_semantic_error(
                "La tabla de símbolos está vacía",
                suggestion="Verifica que el código tenga declaraciones de variables o funciones"
            )
            return None
        
        print(f"✅ Análisis semántico exitoso: {len(tabla_simbolos.tabla)} símbolos")
        
        # Mostrar tabla de símbolos
        if hasattr(tabla_simbolos, 'imprimir_tabla_mejorada'):
            tabla_simbolos.imprimir_tabla_mejorada()
        else:
            tabla_simbolos.imprimir_tabla()
        
        # Validar tabla de símbolos
        if hasattr(tabla_simbolos, 'validar_tabla'):
            if tabla_simbolos.validar_tabla():
                print("🔍 Validación: ✅ Tabla de símbolos válida")
            else:
                error_mgr.add_warning(
                    "La tabla de símbolos tiene inconsistencias menores",
                    "Validador semántico",
                    suggestion="Revisa las declaraciones duplicadas o tipos inconsistentes"
                )
        
        return tabla_simbolos
        
    except ImportError as e:
        error_mgr.add_error(
            ErrorType.SISTEMA,
            ErrorSeverity.CRITICO,
            f"Error importando el analizador semántico: {str(e)}",
            "Analizador Semántico",
            exception=e,
            suggestion="Verifica que los archivos semantico.py y tabla_simbolos.py estén disponibles"
        )
        return None
        
    except Exception as e:
        error_mgr.add_error(
            ErrorType.SEMANTICO,
            ErrorSeverity.CRITICO,
            f"Error inesperado en análisis semántico: {str(e)}",
            "Analizador Semántico",
            exception=e,
            suggestion="Revisa las declaraciones de variables y funciones"
        )
        return None
def generar_archivos_salida(error_mgr, resultado_sintactico, tabla_simbolos):
    """Genera archivos de salida con manejo de errores."""
    archivos_generados = 0
    
    # Generar tabla de símbolos
    try:
        with open("tabla_simbolos.txt", "w", encoding="utf-8") as f:
            original_stdout = sys.stdout
            sys.stdout = f
            if hasattr(tabla_simbolos, 'imprimir_tabla'):
                tabla_simbolos.imprimir_tabla()
            sys.stdout = original_stdout
        
        print("💾 Tabla de símbolos guardada en 'tabla_simbolos.txt'")
        archivos_generados += 1
        
    except Exception as e:
        error_mgr.add_warning(
            f"No se pudo guardar tabla de símbolos: {str(e)}",
            "Generador de archivos",
            suggestion="Verifica permisos de escritura en el directorio"
        )
    
    # Generar estadísticas
    try:
        if hasattr(tabla_simbolos, 'obtener_estadisticas'):
            stats = tabla_simbolos.obtener_estadisticas()
            print(f"\n📈 ESTADÍSTICAS FINALES:")
            print(f"   • Símbolos totales: {stats.get('total_simbolos', 0)}")
            print(f"   • Variables: {stats.get('variables', 0)}")
            print(f"   • Funciones: {stats.get('funciones', 0)}")
            
    except Exception as e:
        error_mgr.add_warning(
            f"No se pudieron generar estadísticas: {str(e)}",
            "Generador de estadísticas"
        )
    
    if archivos_generados > 0:
        print(f"📁 {archivos_generados} archivo(s) de salida generado(s)")
def generar_reporte_final_unico(error_mgr, compilacion_exitosa, fase_fallo):
    """
    Genera el reporte final de errores y resultados.
    CORREGIDO: Solo se ejecuta una vez, no duplica reportes.
    """
    # Marcar que ya se generó el reporte para evitar duplicación
    if hasattr(error_mgr, '_reporte_generado') and error_mgr._reporte_generado:
        return compilacion_exitosa and not error_mgr.has_errors()
    
    error_mgr._reporte_generado = True
    
    print("\n" + "=" * 60)
    print("📋 REPORTE FINAL DE COMPILACIÓN")
    print("=" * 60)
    
    if compilacion_exitosa and not error_mgr.has_errors():
        print("🎉 ¡COMPILACIÓN COMPLETAMENTE EXITOSA!")
        print("✅ No se encontraron errores")
        if error_mgr.errors:  # Solo advertencias
            print(f"⚠️ Se encontraron {len(error_mgr.errors)} advertencia(s)")
    elif compilacion_exitosa and error_mgr.has_errors():
        print("⚠️ COMPILACIÓN COMPLETADA CON ADVERTENCIAS")
        print("✅ Compilación técnicamente exitosa")
        print("⚠️ Hay advertencias que deberías revisar")
    else:
        print("❌ COMPILACIÓN FALLIDA")
        print(f"🛑 Falló en fase: {fase_fallo}")
        if error_mgr.has_critical_errors():
            print("🔴 Se encontraron errores críticos")
    
    # Mostrar reporte de errores detallado SOLO SI HAY ERRORES
    if error_mgr.errors:
        reporte = error_mgr.generate_error_report()
        print(f"\n{reporte}")
        
        # Guardar log de errores
        try:
            if error_mgr.save_error_log():
                print(f"\n💾 Log detallado guardado en 'compilador_errores.log'")
        except Exception:
            pass  # No es crítico si no se puede guardar
    
    print("\n" + "=" * 60)
    
    return compilacion_exitosa and not error_mgr.has_errors()
# IMPORTANTE: Evitar que se ejecute múltiples veces
if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n💥 ERROR FATAL DEL SISTEMA: {e}")
        sys.exit(2)
