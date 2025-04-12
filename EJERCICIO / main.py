import csv
import time
import sys
import io

# Configuración universal de codificación
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class AnalizadorSintacticoLL:
    def __init__(self, archivo_tabla):
        self.tabla = self.cargar_tabla_csv(archivo_tabla)
    
    def cargar_tabla_csv(self, archivo):
        tabla = {}
        with open(archivo, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';'))
            terminales = reader[0][1:]  # Saltar la primera columna vacía
            for fila in reader[1:]:
                no_terminal = fila[0]
                for i, celda in enumerate(fila[1:]):
                    produccion = celda.strip()
                    if produccion:  # Solo agregamos si hay producción
                        lado_derecho = produccion.split() if produccion != 'ε' else ['ε']
                        tabla[(no_terminal, terminales[i])] = lado_derecho
        return tabla

    def mostrar_pila(self, pila):
        """Función para mostrar la pila de manera gráfica (versión compatible)"""
        print("\nEstado actual de la pila:")
        print("+-------+")
        for elemento in reversed(pila):
            print(f"| {elemento.center(5)} |")
            print("+-------+")

    def analizar(self, tokens):
        """
        Analiza una lista de tokens utilizando el algoritmo LL.
        """
        # Agregar el símbolo de fin de entrada
        tokens.append('$')
        
        # Inicializar pila y puntero de entrada
        pila = ['$', 'E']  # Comenzamos con el símbolo inicial E y el marcador de fondo $
        indice = 0
        token_actual = tokens[indice]
        
        print("\n INICIANDO ANALISIS")
        print(" Nuestra pila siempre empezará ['$', 'E']):")
        self.mostrar_pila(pila)
        print(f"• Primer token a procesar: '{token_actual}'")
        time.sleep(1)
        
        pasos = []
        paso_num = 1
        
        while pila[-1] != '$':
            X = pila[-1]
            
            print(f"\n >>> PASO {paso_num} <<<")
            print(f"Tope de Pila: '{X}'")
            print(f"Token actual de Entrada: '{token_actual}'")
            
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            accion = ""
            
            if X == token_actual:
                accion = f"Emparejar {X}"
                print(f"\n ¡COINCIDENCIA! El tope '{X}' coincide con el token actual")
                print(f"• Solucion: Sacar '{X}' de la pila y avanzar al siguiente token")
                pila.pop()
                indice += 1
                if indice < len(tokens):
                    token_actual = tokens[indice]
                
                self.mostrar_pila(pila)
                print(f"• Nuevo token: '{token_actual}'")
                time.sleep(1)
                
            elif (X, token_actual) in self.tabla:
                produccion = self.tabla[(X, token_actual)]
                produccion_str = ' -> '.join(produccion) if produccion != ['ε'] else 'ε'
                accion = f"{X} -> {produccion_str}"
                print(f"\n EXPANSIÓN Aplicando regla gramatical: {accion}")
                print(f"• Sacamos '{X}' de la pila y agregamos la producción")
                
                pila.pop()
                
                for simbolo in reversed(produccion):
                    if simbolo != 'ε':
                        pila.append(simbolo)
                        print(f"  - Agregando '{simbolo}' a la pila")
                
                self.mostrar_pila(pila)
                print(f"• Token actual se mantiene: '{token_actual}' (no avanzamos)")
                time.sleep(1)
                
            else:
                print(f"\n ¡ERROR! ¡No existe regla en la tabla para ({X}, {token_actual})!")
                print("Posibles causas:")
                print(f"- Falta una producción para '{X}' con el token '{token_actual}'")
                print(f"- Token inesperado en la posición {indice}")
                print(f"- Error en la gramática (revisar tabla sintáctica)")
                pasos.append((paso_num, pila_actual, entrada_restante, "ERROR: No hay regla definida"))
                return {
                    "CONCLUSION": "ERROR SINTACTICO :(",
                    "mensaje": f"Error sintáctico en el token '{token_actual}' (posición {indice}). No hay regla definida para el no terminal '{X}'.",
                    "pasos": pasos
                }
            
            pasos.append((paso_num, pila_actual, entrada_restante, accion))
            paso_num += 1
        
        if token_actual == '$':
            print("\n <<< PILA VACIA >>> ")
            print("¡Proceso completado exitosamente!")
            print("La pila solo contiene '$' (se vació correctamente)")
            print("Todos los tokens fueron procesados")
            print("CONCLUSIÓN: La cadena es válida según la gramática")
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            pasos.append((paso_num, pila_actual, entrada_restante, "ACEPTAR"))
            
            return {
                "CONCLUSION": "ACEPTADO :)",
                "mensaje": "¡Esta cadena si pertenece a tu gramatica!",
                "pasos": pasos
            }
        else:
            print("\n <<< FALLO >>>")
            print("¡Proceso terminado con errores!")
            print(f" Token pendiente sin procesar: '{token_actual}'")
            print(" La pila se vació pero quedaron tokens sin consumir")
            entrada_restante = ' '.join(tokens[indice:])
            pila_actual = ' '.join(pila)
            pasos.append((paso_num, pila_actual, entrada_restante, "ERROR: Entrada no consumida"))
            
            return {
                "CONCLUSION": "ERROR SINTACTICO :(",
                "mensaje": f"Entrada no consumida completamente. Token actual: '{token_actual}'",
                "pasos": pasos
            }
def imprimir_tabla(datos, titulos, anchos):
    def formatear_celda(texto, ancho):
        texto = str(texto)
        if len(texto) > ancho:
            return texto[:ancho-3] + "..."
        return texto.ljust(ancho)
    
    separador = "+" + "+".join(["-" * (ancho + 2) for ancho in anchos]) + "+"
    
    print(separador)
    header = "|"
    for titulo, ancho in zip(titulos, anchos):
        header += " " + formatear_celda(titulo, ancho) + " |"
    print(header)
    print(separador)
    
    for fila in datos:
        linea = "|"
        for valor, ancho in zip(fila, anchos):
            # Reemplazar caracteres Unicode problemáticos
            valor_str = str(valor).replace('→', '->').replace('ε', 'epsilon')
            linea += " " + formatear_celda(valor_str, ancho) + " |"
        print(linea)
    
    print(separador)

def analizar_cadena(cadena):
    """
    Analiza una cadena de tokens separados por espacios.
    """
    tokens = cadena.strip().split()
    analizador = AnalizadorSintacticoLL("tabla_sintactica.csv")
    resultado = analizador.analizar(tokens)
    
    print("\n <<< RESUMEN DEL ANÁLISIS >>>")
    print(f"ENTRADA: {cadena}")
    print(f"CONCLUSION: {resultado['CONCLUSION']}")
    print(f"SALIDA: {resultado['mensaje']}")
    return resultado

if __name__ == "__main__":
    print("\n EJEMPLO N° 1 ")
    analizar_cadena("int mas int")
