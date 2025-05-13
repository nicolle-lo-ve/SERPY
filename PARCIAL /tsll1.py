#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analizador LL(1) - Generador de tabla sintáctica LL(1)
"""

import re
import csv

class AnalizadorLL1:
    def __init__(self, ruta_gramatica):
        # Símbolo para épsilon (vacío)
        self.EPSILON = "ε"
        # Símbolos especiales
        self.EOF = "$"
        
        # Estructuras para la gramática
        self.no_terminales = set()
        self.terminales = set()
        self.producciones = {}
        self.simbolo_inicial = None
        
        # Conjuntos para la construcción de la tabla
        self.first = {}
        self.follow = {}
        self.tabla_ll1 = {}
        
        # Cargar gramática desde archivo
        self.cargar_gramatica(ruta_gramatica)
    
    def cargar_gramatica(self, ruta):
        """Carga una gramática desde un archivo de texto"""
        print("Cargando gramática desde:", ruta)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            # Procesar cada línea de la gramática
            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    continue
                
                # Dividir la producción en lado izquierdo y derecho
                partes = re.split(r'\s*->\s*', linea)
                if len(partes) != 2:
                    print(f"Error en línea: {linea}")
                    continue
                
                no_terminal = partes[0].strip()
                producciones_nt = partes[1].strip().split('|')
                
                # Guardar el primer símbolo no terminal como símbolo inicial
                if self.simbolo_inicial is None:
                    self.simbolo_inicial = no_terminal
                
                # Añadir no terminal a la lista
                self.no_terminales.add(no_terminal)
                
                # Procesar producciones para este no terminal
                if no_terminal not in self.producciones:
                    self.producciones[no_terminal] = []
                
                for prod in producciones_nt:
                    prod = prod.strip()
                    # Reemplazar '' por épsilon
                    if prod == "''":
                        prod = self.EPSILON
                    # Añadir producción
                    self.producciones[no_terminal].append(prod)
                    
                    # Identificar terminales en la producción
                    if prod != self.EPSILON:
                        simbolos = prod.split()
                        for simbolo in simbolos:
                            if simbolo not in self.no_terminales and simbolo != self.EPSILON:
                                self.terminales.add(simbolo)
            
            # Añadir el símbolo de fin de entrada a los terminales
            self.terminales.add(self.EOF)
            
            print(f"Gramática cargada con éxito. Símbolo inicial: {self.simbolo_inicial}")
            print(f"No terminales: {self.no_terminales}")
            print(f"Terminales: {self.terminales}")
            print("Producciones:")
            for nt, prods in self.producciones.items():
                print(f"  {nt} -> {' | '.join(prods)}")
            
        except Exception as e:
            print(f"Error al cargar la gramática: {e}")
            raise
    
    def calcular_first(self):
        """Calcula el conjunto FIRST para cada símbolo de la gramática"""
        print("\nCalculando conjuntos FIRST...")
        
        # Inicializar conjuntos FIRST
        for nt in self.no_terminales:
            self.first[nt] = set()
        
        for t in self.terminales:
            self.first[t] = {t}
        
        self.first[self.EPSILON] = {self.EPSILON}
        
        # Calcular FIRST para no terminales
        cambio = True
        while cambio:
            cambio = False
            
            for no_terminal in self.no_terminales:
                for produccion in self.producciones[no_terminal]:
                    if produccion == self.EPSILON:
                        if self.EPSILON not in self.first[no_terminal]:
                            self.first[no_terminal].add(self.EPSILON)
                            cambio = True
                    else:
                        simbolos = produccion.split()
                        
                        # Para cada símbolo en la producción
                        all_can_be_epsilon = True
                        for i, simbolo in enumerate(simbolos):
                            if simbolo not in self.first:
                                self.first[simbolo] = {simbolo}  # Terminal
                            
                            # Añadir FIRST del símbolo (sin épsilon) al FIRST del no terminal
                            simbolo_first = self.first[simbolo].copy()
                            if self.EPSILON in simbolo_first:
                                simbolo_first.remove(self.EPSILON)
                            
                            first_size_antes = len(self.first[no_terminal])
                            self.first[no_terminal].update(simbolo_first)
                            if len(self.first[no_terminal]) > first_size_antes:
                                cambio = True
                            
                            # Si este símbolo no puede derivar épsilon, no seguimos
                            if self.EPSILON not in self.first[simbolo]:
                                all_can_be_epsilon = False
                                break
                        
                        # Si todos los símbolos pueden derivar épsilon, añadir épsilon al FIRST
                        if all_can_be_epsilon and self.EPSILON not in self.first[no_terminal]:
                            self.first[no_terminal].add(self.EPSILON)
                            cambio = True
        
        # Mostrar conjuntos FIRST
        print("Conjuntos FIRST calculados:")
        for simbolo, conjunto in self.first.items():
            print(f"  FIRST({simbolo}) = {conjunto}")
    
    def calcular_first_de_cadena(self, cadena):
        """Calcula el conjunto FIRST para una cadena de símbolos"""
        if not cadena or cadena == self.EPSILON:
            return {self.EPSILON}
        
        simbolos = cadena.split()
        resultado = set()
        
        all_can_be_epsilon = True
        for simbolo in simbolos:
            if simbolo not in self.first:
                # Si es un terminal que no conocemos
                resultado.add(simbolo)
                all_can_be_epsilon = False
                break
            
            # Añadir FIRST del símbolo (sin épsilon) al resultado
            simbolo_first = self.first[simbolo].copy()
            if self.EPSILON in simbolo_first:
                simbolo_first.remove(self.EPSILON)
            
            resultado.update(simbolo_first)
            
            # Si este símbolo no puede derivar épsilon, no seguimos
            if self.EPSILON not in self.first[simbolo]:
                all_can_be_epsilon = False
                break
        
        # Si todos los símbolos pueden derivar épsilon, añadir épsilon al resultado
        if all_can_be_epsilon:
            resultado.add(self.EPSILON)
        
        return resultado
    
    def calcular_follow(self):
        """Calcula el conjunto FOLLOW para cada no terminal"""
        print("\nCalculando conjuntos FOLLOW...")
        
        # Inicializar conjuntos FOLLOW
        for nt in self.no_terminales:
            self.follow[nt] = set()
        
        # Regla 1: Añadir $ al FOLLOW del símbolo inicial
        self.follow[self.simbolo_inicial].add(self.EOF)
        
        # Calcular FOLLOW
        cambio = True
        while cambio:
            cambio = False
            
            for no_terminal in self.no_terminales:
                for produccion_izq in self.no_terminales:
                    for produccion in self.producciones[produccion_izq]:
                        if produccion == self.EPSILON:
                            continue
                        
                        simbolos = produccion.split()
                        
                        # Buscar ocurrencias del no terminal en la producción
                        for i, simbolo in enumerate(simbolos):
                            if simbolo != no_terminal:
                                continue
                            
                            # Caso: A -> αBβ, añadir FIRST(β) - {ε} a FOLLOW(B)
                            if i < len(simbolos) - 1:
                                resto = " ".join(simbolos[i+1:])
                                first_resto = self.calcular_first_de_cadena(resto)
                                
                                # Añadir FIRST(resto) - {ε} a FOLLOW(no_terminal)
                                follow_size_antes = len(self.follow[no_terminal])
                                for terminal in first_resto:
                                    if terminal != self.EPSILON:
                                        self.follow[no_terminal].add(terminal)
                                if len(self.follow[no_terminal]) > follow_size_antes:
                                    cambio = True
                                
                                # Caso: A -> αBβ y ε está en FIRST(β), añadir FOLLOW(A) a FOLLOW(B)
                                if self.EPSILON in first_resto:
                                    follow_size_antes = len(self.follow[no_terminal])
                                    self.follow[no_terminal].update(self.follow[produccion_izq])
                                    if len(self.follow[no_terminal]) > follow_size_antes:
                                        cambio = True
                            
                            # Caso: A -> αB, añadir FOLLOW(A) a FOLLOW(B)
                            elif i == len(simbolos) - 1:
                                follow_size_antes = len(self.follow[no_terminal])
                                self.follow[no_terminal].update(self.follow[produccion_izq])
                                if len(self.follow[no_terminal]) > follow_size_antes:
                                    cambio = True
        
        # Mostrar conjuntos FOLLOW
        print("Conjuntos FOLLOW calculados:")
        for nt, conjunto in self.follow.items():
            print(f"  FOLLOW({nt}) = {conjunto}")
    
    def construir_tabla_ll1(self):
        """Construye la tabla de análisis sintáctico LL(1)"""
        print("\nConstruyendo tabla de análisis sintáctico LL(1)...")
        
        # Inicializar tabla con valores vacíos
        for nt in self.no_terminales:
            self.tabla_ll1[nt] = {}
            for t in self.terminales:
                self.tabla_ll1[nt][t] = None
        
        # Llenar tabla según las reglas
        for no_terminal in self.no_terminales:
            for produccion in self.producciones[no_terminal]:
                if produccion == self.EPSILON:
                    # Para A -> ε, añadir A -> ε a M[A, b] para todo b en FOLLOW(A)
                    for terminal in self.follow[no_terminal]:
                        if self.tabla_ll1[no_terminal][terminal] is not None:
                            print(f"¡Conflicto! La gramática no es LL(1). Celda: [{no_terminal}, {terminal}]")
                            print(f"  Conflicto entre: {self.tabla_ll1[no_terminal][terminal]} y {produccion}")
                        else:
                            self.tabla_ll1[no_terminal][terminal] = produccion
                else:
                    # Para A -> α, añadir A -> α a M[A, b] para todo b en FIRST(α)
                    first_produccion = self.calcular_first_de_cadena(produccion)
                    for terminal in first_produccion:
                        if terminal != self.EPSILON:
                            if self.tabla_ll1[no_terminal][terminal] is not None:
                                print(f"¡Conflicto! La gramática no es LL(1). Celda: [{no_terminal}, {terminal}]")
                                print(f"  Conflicto entre: {self.tabla_ll1[no_terminal][terminal]} y {produccion}")
                            else:
                                self.tabla_ll1[no_terminal][terminal] = produccion
                    
                    # Si ε está en FIRST(α), añadir A -> α a M[A, b] para todo b en FOLLOW(A)
                    if self.EPSILON in first_produccion:
                        for terminal in self.follow[no_terminal]:
                            if self.tabla_ll1[no_terminal][terminal] is not None:
                                print(f"¡Conflicto! La gramática no es LL(1). Celda: [{no_terminal}, {terminal}]")
                                print(f"  Conflicto entre: {self.tabla_ll1[no_terminal][terminal]} y {produccion}")
                            else:
                                self.tabla_ll1[no_terminal][terminal] = produccion
        
        print("Tabla LL(1) construida con éxito")
    
    def guardar_tabla_csv(self, ruta_salida):
        """Guarda la tabla de análisis sintáctico LL(1) en un archivo CSV"""
        print(f"\nGuardando tabla LL(1) en: {ruta_salida}")
        
        try:
            with open(ruta_salida, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Encabezados: una celda vacía seguida de los terminales
                encabezados = [''] + sorted(list(self.terminales))
                writer.writerow(encabezados)
                
                # Filas: no terminales y sus producciones para cada terminal
                for nt in sorted(list(self.no_terminales)):
                    fila = [nt]
                    for t in sorted(list(self.terminales)):
                        produccion = self.tabla_ll1[nt][t]
                        fila.append(produccion if produccion is not None else '')
                    writer.writerow(fila)
            
            print(f"Tabla guardada con éxito en: {ruta_salida}")
        except Exception as e:
            print(f"Error al guardar la tabla: {e}")
    
    def mostrar_tabla(self):
        """Muestra la tabla de análisis sintáctico LL(1) en la consola"""
        print("\nTabla de análisis sintáctico LL(1):")
        
        # Encabezados
        print(f"{'':15}", end='')
        for t in sorted(list(self.terminales)):
            print(f"{t:15}", end='')
        print()
        
        # Filas
        for nt in sorted(list(self.no_terminales)):
            print(f"{nt:15}", end='')
            for t in sorted(list(self.terminales)):
                produccion = self.tabla_ll1[nt][t]
                print(f"{produccion if produccion is not None else '':15}", end='')
            print()
    
    def analizar(self):
        """Realiza el análisis completo y genera la tabla LL(1)"""
        self.calcular_first()
        self.calcular_follow()
        self.construir_tabla_ll1()
        self.mostrar_tabla()

def main():
    """Función principal"""
    try:
        # Obtener rutas de archivos
        ruta_gramatica = input("Introduzca la ruta del archivo de gramática (por defecto: gramatica.txt): ").strip()
        if not ruta_gramatica:
            ruta_gramatica = "gramatica.txt"
        
        ruta_salida = input("Introduzca la ruta del archivo de salida CSV (por defecto: tabla_ll1.csv): ").strip()
        if not ruta_salida:
            ruta_salida = "tabla_ll1.csv"
        
        # Crear analizador y procesar gramática
        analizador = AnalizadorLL1(ruta_gramatica)
        analizador.analizar()
        analizador.guardar_tabla_csv(ruta_salida)
        
        print("\n¡Proceso completado con éxito!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
