# main.py
from lexico import Lexico
from sintactico import Sintactico

def main():
    # 1. Análisis léxico
    lexico = Lexico()
    codigo = lexico.cargar_desde_archivo("codigo_fuente.txt")
    lexico.analizar(codigo)
    
    # 2. Análisis sintáctico
    try:
        sintactico = Sintactico(
            tokens=lexico.lista_tokens,
            archivo_tabla_csv="tabla_sintactica.csv"
        )
        
        mensaje, arbol = sintactico.analizar()
        
        if mensaje.startswith("Error"):
            print(f"\nERROR {mensaje}")
        else:
            print(f"\nCORRECTO {mensaje}")
            if arbol:
                print("\nÁrbol sintáctico:")
                arbol.recorrer()
                
    except Exception as e:
        print(f"\n Error en análisis sintáctico: {e}")

if __name__ == "__main__":
    main()
