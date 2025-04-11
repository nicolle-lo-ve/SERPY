from lexico import Lexico
 
 def main():
     # Crear instancia del analizador léxico
     lexico = Lexico()
     
     # Cargar código fuente desde archivo
     archivo_fuente = "codigo_fuente.txt"  # Puedes cambiarlo por sys.argv[1] para recibirlo como parámetro
     codigo = lexico.cargar_desde_archivo(archivo_fuente)
     
     if codigo is None:
         print(f"No se pudo cargar el archivo {archivo_fuente}")
         exit(1)
     
     # Analizar el código
     lexico.analizar(codigo)
     
     # Obtener y mostrar resultados
     print("Resultados del análisis léxico:")
     print("=" * 50)
     print(lexico.obtener_resultados())
     
     # Opcional: mostrar tokens en formato de lista
     print("\nLista de tokens detectados:")
     print("=" * 50)
     for i, valor in enumerate(lexico.lista_tokens, 1):
         print(f"{i}. {valor.getToken():<15} {valor.getLexema()} (Línea: {valor.getLinea()}, Columna: {valor.getColumna()})")
 
 if __name__ == "__main__":
     main()
