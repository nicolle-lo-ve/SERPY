import os
from collections import defaultdict

# Importar clases y funciones del analizador sintáctico si es necesario
# from AnalizadorSintactico import Nodo, parser_ll1, cargar_tabla_desde_csv, exportar_arbol_a_graphviz
# from AnalizadorLexico import analyze_file

# Definición de tipos de datos básicos para SERPY
class Tipo:
    def __init__(self, nombre):
        self.nombre = nombre

    def __eq__(self, other):
        return isinstance(other, Tipo) and self.nombre == other.nombre

    def __hash__(self):
        return hash(self.nombre)

    def __repr__(self):
        return self.nombre

TIPO_NUMERO = Tipo("NUMERO")
TIPO_CADENA = Tipo("CADENA")
TIPO_BOOLEANO = Tipo("BOOLEANO")
TIPO_VOID = Tipo("VOID") # Para funciones que no retornan valor
TIPO_DESCONOCIDO = Tipo("DESCONOCIDO") # Para errores o tipos no inferidos

class EntradaTablaSimbolos:
    def __init__(self, nombre, tipo, categoria, valor=None, num_params=None):
        self.nombre = nombre
        self.tipo = tipo # Objeto Tipo
        self.categoria = categoria # 'variable', 'funcion'
        self.valor = valor # Valor inicial si es una variable, o None
        self.num_params = num_params # Solo para funciones

    def __repr__(self):
        if self.categoria == 'funcion':
            return f"Entrada(Nombre: {self.nombre}, Tipo: {self.tipo}, Categoria: {self.categoria}, Params: {self.num_params})"
        return f"Entrada(Nombre: {self.nombre}, Tipo: {self.tipo}, Categoria: {self.categoria}, Valor: {self.valor})"

class TablaSimbolos:
    def __init__(self):
        self.scopes = [{}] # Lista de diccionarios, cada uno representa un ámbito
        self.current_scope_index = 0

    def push_scope(self):
        self.scopes.append({})
        self.current_scope_index += 1

    def pop_scope(self):
        if self.current_scope_index > 0:
            self.scopes.pop()
            self.current_scope_index -= 1
        else:
            print("Error: Intentando salir del ámbito global.")

    def add_symbol(self, nombre, tipo, categoria, valor=None, num_params=None):
        if nombre in self.scopes[self.current_scope_index]:
            return False # Símbolo ya declarado en este ámbito
        self.scopes[self.current_scope_index][nombre] = EntradaTablaSimbolos(nombre, tipo, categoria, valor, num_params)
        return True

    def lookup_symbol(self, nombre):
        # Buscar desde el ámbito actual hacia arriba (global)
        for i in reversed(range(self.current_scope_index + 1)):
            if nombre in self.scopes[i]:
                return self.scopes[i][nombre]
        return None # Símbolo no encontrado

    def display_scopes(self):
        print("\n--- Tabla de Símbolos ---")
        for i, scope in enumerate(self.scopes):
            print(f"Ámbito {i}:")
            if not scope:
                print("  (Vacío)")
            for name, entry in scope.items():
                print(f"  {name}: {entry}")
        print("-------------------------\n")

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
        self.errores_semanticos = []
        self.ast = None # El AST que recibiremos del analizador sintáctico

    def reportar_error(self, mensaje, nodo=None):
        linea = nodo.token_original.lineno if nodo and nodo.token_original else "Desconocida"
        self.errores_semanticos.append(f"Error Semántico (Línea {linea}): {mensaje}")

    def analizar(self, ast):
        self.ast = ast
        if not self.ast:
            self.reportar_error("AST vacío, no se puede realizar el análisis semántico.")
            return False

        print("\n--- Iniciando Análisis Semántico ---")
        self.recorrer_ast(self.ast)

        if self.errores_semanticos:
            print("\n--- Errores Semánticos Encontrados ---")
            for error in self.errores_semanticos:
                print(error)
            print("-------------------------------------\n")
            return False
        else:
            print("\n✅ Análisis Semántico Completado sin errores.")
            self.tabla_simbolos.display_scopes()
            return True

    def recorrer_ast(self, nodo):
        if not nodo:
            return

        # Reglas semánticas basadas en la gramática
        # PROGRAMA -> lista_sentencias
        if nodo.valor == 'PROGRAMA':
            self.tabla_simbolos.push_scope() # Ámbito global
            for hijo in nodo.hijos:
                self.recorrer_ast(hijo)
            self.tabla_simbolos.pop_scope()

        # lista_sentencias -> sentencia lista_sentencias | ε
        elif nodo.valor == 'lista_sentencias':
            for hijo in nodo.hijos:
                self.recorrer_ast(hijo)

        # sentencia -> VAR IDENTIFICADOR IGUAL expresion PUNTOYCOMA
        elif nodo.valor == 'sentencia' and len(nodo.hijos) > 0 and nodo.hijos[0].valor == 'VAR':
            # Declaración de variable
            identificador_nodo = nodo.hijos[1] # IDENTIFICADOR
            expresion_nodo = nodo.hijos[3] # expresion

            self.recorrer_ast(expresion_nodo) # Evaluar el tipo de la expresión
            tipo_expresion = getattr(expresion_nodo, 'tipo', TIPO_DESCONOCIDO)

            nombre_var = identificador_nodo.token_original.value
            if not self.tabla_simbolos.add_symbol(nombre_var, tipo_expresion, 'variable'):
                self.reportar_error(f"Variable '{nombre_var}' ya declarada en este ámbito.", identificador_nodo)
            else:
                print(f"Declarada variable '{nombre_var}' de tipo {tipo_expresion}")

        # sentencia -> IDENTIFICADOR asignacion_o_llamada PUNTOYCOMA
        elif nodo.valor == 'sentencia' and len(nodo.hijos) > 0 and nodo.hijos[0].valor == 'IDENTIFICADOR':
            identificador_nodo = nodo.hijos[0]
            nombre_id = identificador_nodo.token_original.value
            entrada_simbolo = self.tabla_simbolos.lookup_symbol(nombre_id)

            if not entrada_simbolo:
                self.reportar_error(f"Uso de identificador no declarado '{nombre_id}'.", identificador_nodo)
                # Asignar un tipo desconocido para evitar cascada de errores
                setattr(identificador_nodo, 'tipo', TIPO_DESCONOCIDO)
            else:
                setattr(identificador_nodo, 'tipo', entrada_simbolo.tipo)
                setattr(identificador_nodo, 'categoria', entrada_simbolo.categoria)

            asignacion_o_llamada_nodo = nodo.hijos[1]
            self.recorrer_ast(asignacion_o_llamada_nodo) # Esto manejará la asignación o la llamada

            # Después de recorrer asignacion_o_llamada, verificar si es una asignación
            if asignacion_o_llamada_nodo.hijos and asignacion_o_llamada_nodo.hijos[0].valor == 'IGUAL':
                # Es una asignación
                if entrada_simbolo and entrada_simbolo.categoria != 'variable':
                    self.reportar_error(f"No se puede asignar a '{nombre_id}' porque no es una variable.", identificador_nodo)
                else:
                    tipo_expresion_asignada = getattr(asignacion_o_llamada_nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                    if entrada_simbolo and entrada_simbolo.tipo != tipo_expresion_asignada and tipo_expresion_asignada != TIPO_DESCONOCIDO:
                        self.reportar_error(f"Incompatibilidad de tipos en la asignación de '{nombre_id}': se esperaba {entrada_simbolo.tipo}, se obtuvo {tipo_expresion_asignada}.", identificador_nodo)
                    print(f"Asignación a '{nombre_id}' (tipo {entrada_simbolo.tipo if entrada_simbolo else 'Desconocido'})")
            elif asignacion_o_llamada_nodo.hijos and asignacion_o_llamada_nodo.hijos[0].valor == 'PAR_IZQ':
                # Es una llamada a función
                if entrada_simbolo and entrada_simbolo.categoria != 'funcion':
                    self.reportar_error(f"'{nombre_id}' no es una función y no puede ser llamada.", identificador_nodo)
                else:
                    # La verificación de argumentos se hace en lista_argumentos
                    pass


        # sentencia -> RETORNAR expresion PUNTOYCOMA
        elif nodo.valor == 'sentencia' and len(nodo.hijos) > 0 and nodo.hijos[0].valor == 'RETORNAR':
            expresion_nodo = nodo.hijos[1]
            self.recorrer_ast(expresion_nodo)
            tipo_retorno = getattr(expresion_nodo, 'tipo', TIPO_DESCONOCIDO)
            # Aquí se debería verificar que el tipo de retorno coincida con el tipo declarado de la función actual
            # Esto requiere un seguimiento del tipo de retorno de la función actual, que no está implementado en este esqueleto.
            print(f"Sentencia 'retornar' con tipo {tipo_retorno}")


        # sentencia -> IMPRIMIR PAR_IZQ lista_argumentos PAR_DER PUNTOYCOMA
        elif nodo.valor == 'sentencia' and len(nodo.hijos) > 0 and nodo.hijos[0].valor == 'IMPRIMIR':
            lista_argumentos_nodo = nodo.hijos[2]
            self.recorrer_ast(lista_argumentos_nodo)
            # No hay verificación de tipo estricta para imprimir, puede tomar cualquier tipo.
            print("Sentencia 'imprimir'")

        # si_sentencia -> SI PAR_IZQ expresion PAR_DER bloque sino_parte
        elif nodo.valor == 'si_sentencia':
            condicion_nodo = nodo.hijos[2]
            self.recorrer_ast(condicion_nodo)
            tipo_condicion = getattr(condicion_nodo, 'tipo', TIPO_DESCONOCIDO)
            if tipo_condicion != TIPO_BOOLEANO and tipo_condicion != TIPO_DESCONOCIDO:
                self.reportar_error(f"La condición de la sentencia 'si' debe ser de tipo BOOLEANO, se obtuvo {tipo_condicion}.", condicion_nodo)

            self.recorrer_ast(nodo.hijos[4]) # bloque
            self.recorrer_ast(nodo.hijos[5]) # sino_parte
            print("Sentencia 'si'")

        # mientras_sentencia -> MIENTRAS PAR_IZQ expresion PAR_DER bloque
        elif nodo.valor == 'mientras_sentencia':
            condicion_nodo = nodo.hijos[2]
            self.recorrer_ast(condicion_nodo)
            tipo_condicion = getattr(condicion_nodo, 'tipo', TIPO_DESCONOCIDO)
            if tipo_condicion != TIPO_BOOLEANO and tipo_condicion != TIPO_DESCONOCIDO:
                self.reportar_error(f"La condición de la sentencia 'mientras' debe ser de tipo BOOLEANO, se obtuvo {tipo_condicion}.", condicion_nodo)

            self.recorrer_ast(nodo.hijos[4]) # bloque
            print("Sentencia 'mientras'")

        # para_sentencia -> PARA PAR_IZQ para_inicio PUNTOYCOMA expresion PUNTOYCOMA IDENTIFICADOR IGUAL expresion PAR_DER bloque
        elif nodo.valor == 'para_sentencia':
            self.tabla_simbolos.push_scope() # Nuevo ámbito para el bucle for
            self.recorrer_ast(nodo.hijos[2]) # para_inicio
            
            condicion_nodo = nodo.hijos[4] # expresion (condición)
            self.recorrer_ast(condicion_nodo)
            tipo_condicion = getattr(condicion_nodo, 'tipo', TIPO_DESCONOCIDO)
            if tipo_condicion != TIPO_BOOLEANO and tipo_condicion != TIPO_DESCONOCIDO:
                self.reportar_error(f"La condición del bucle 'para' debe ser de tipo BOOLEANO, se obtuvo {tipo_condicion}.", condicion_nodo)

            # Actualización (IDENTIFICADOR IGUAL expresion)
            identificador_actualizacion_nodo = nodo.hijos[6]
            expresion_actualizacion_nodo = nodo.hijos[8]
            
            nombre_id_actualizacion = identificador_actualizacion_nodo.token_original.value
            entrada_simbolo_actualizacion = self.tabla_simbolos.lookup_symbol(nombre_id_actualizacion)
            if not entrada_simbolo_actualizacion:
                self.reportar_error(f"Variable de actualización '{nombre_id_actualizacion}' no declarada en el bucle 'para'.", identificador_actualizacion_nodo)
            elif entrada_simbolo_actualizacion.categoria != 'variable':
                self.reportar_error(f"'{nombre_id_actualizacion}' no es una variable y no puede ser actualizada en el bucle 'para'.", identificador_actualizacion_nodo)
            
            self.recorrer_ast(expresion_actualizacion_nodo)
            tipo_expresion_actualizacion = getattr(expresion_actualizacion_nodo, 'tipo', TIPO_DESCONOCIDO)
            if entrada_simbolo_actualizacion and entrada_simbolo_actualizacion.tipo != tipo_expresion_actualizacion and tipo_expresion_actualizacion != TIPO_DESCONOCIDO:
                self.reportar_error(f"Incompatibilidad de tipos en la actualización del bucle 'para' para '{nombre_id_actualizacion}': se esperaba {entrada_simbolo_actualizacion.tipo}, se obtuvo {tipo_expresion_actualizacion}.", identificador_actualizacion_nodo)

            self.recorrer_ast(nodo.hijos[10]) # bloque
            self.tabla_simbolos.pop_scope()
            print("Sentencia 'para'")

        # para_inicio -> VAR IDENTIFICADOR IGUAL expresion
        elif nodo.valor == 'para_inicio' and nodo.hijos[0].valor == 'VAR':
            identificador_nodo = nodo.hijos[1]
            expresion_nodo = nodo.hijos[3]
            self.recorrer_ast(expresion_nodo)
            tipo_expresion = getattr(expresion_nodo, 'tipo', TIPO_DESCONOCIDO)
            nombre_var = identificador_nodo.token_original.value
            if not self.tabla_simbolos.add_symbol(nombre_var, tipo_expresion, 'variable'):
                self.reportar_error(f"Variable '{nombre_var}' ya declarada en este ámbito del bucle 'para'.", identificador_nodo)
            print(f"Declarada variable de inicio de 'para' '{nombre_var}' de tipo {tipo_expresion}")

        # para_inicio -> IDENTIFICADOR IGUAL expresion
        elif nodo.valor == 'para_inicio' and nodo.hijos[0].valor == 'IDENTIFICADOR':
            identificador_nodo = nodo.hijos[0]
            expresion_nodo = nodo.hijos[2]
            nombre_id = identificador_nodo.token_original.value
            entrada_simbolo = self.tabla_simbolos.lookup_symbol(nombre_id)
            if not entrada_simbolo:
                self.reportar_error(f"Variable '{nombre_id}' no declarada para la inicialización del bucle 'para'.", identificador_nodo)
            elif entrada_simbolo.categoria != 'variable':
                self.reportar_error(f"'{nombre_id}' no es una variable y no puede ser inicializada en el bucle 'para'.", identificador_nodo)
            
            self.recorrer_ast(expresion_nodo)
            tipo_expresion = getattr(expresion_nodo, 'tipo', TIPO_DESCONOCIDO)
            if entrada_simbolo and entrada_simbolo.tipo != tipo_expresion and tipo_expresion != TIPO_DESCONOCIDO:
                self.reportar_error(f"Incompatibilidad de tipos en la inicialización del bucle 'para' para '{nombre_id}': se esperaba {entrada_simbolo.tipo}, se obtuvo {tipo_expresion}.", identificador_nodo)
            print(f"Inicialización de variable de 'para' '{nombre_id}' (tipo {entrada_simbolo.tipo if entrada_simbolo else 'Desconocido'})")


        # funcion_def -> DEFINIR IDENTIFICADOR PAR_IZQ parametros PAR_DER bloque
        elif nodo.valor == 'funcion_def':
            identificador_nodo = nodo.hijos[1]
            nombre_funcion = identificador_nodo.token_original.value
            parametros_nodo = nodo.hijos[3]
            bloque_nodo = nodo.hijos[5]

            # Contar parámetros para la tabla de símbolos
            num_params = 0
            if parametros_nodo.hijos and parametros_nodo.hijos[0].valor != 'epsilon_node':
                num_params = 1 # Al menos un parámetro
                current_param_cont = parametros_nodo.hijos[1]
                while current_param_cont.hijos and current_param_cont.hijos[0].valor == 'COMA':
                    num_params += 1
                    current_param_cont = current_param_cont.hijos[2]

            if not self.tabla_simbolos.add_symbol(nombre_funcion, TIPO_VOID, 'funcion', num_params=num_params): # Tipo de retorno por defecto VOID
                self.reportar_error(f"Función '{nombre_funcion}' ya declarada en este ámbito.", identificador_nodo)
            print(f"Declarada función '{nombre_funcion}' con {num_params} parámetros.")

            self.tabla_simbolos.push_scope() # Nuevo ámbito para la función
            self.recorrer_ast(parametros_nodo) # Declarar parámetros en el nuevo ámbito
            self.recorrer_ast(bloque_nodo) # Recorrer el cuerpo de la función
            self.tabla_simbolos.pop_scope()


        # parametros -> IDENTIFICADOR parametros_cont | ε
        elif nodo.valor == 'parametros':
            if nodo.hijos and nodo.hijos[0].valor != 'epsilon_node':
                identificador_param_nodo = nodo.hijos[0]
                nombre_param = identificador_param_nodo.token_original.value
                # Por simplicidad, asumimos tipo NUMERO para los parámetros por ahora.
                # En un sistema real, se necesitaría una forma de declarar tipos de parámetros.
                if not self.tabla_simbolos.add_symbol(nombre_param, TIPO_NUMERO, 'variable'):
                    self.reportar_error(f"Parámetro '{nombre_param}' ya declarado en esta función.", identificador_param_nodo)
                print(f"Declarado parámetro '{nombre_param}' de tipo {TIPO_NUMERO}")
                self.recorrer_ast(nodo.hijos[1]) # parametros_cont

        # parametros_cont -> COMA IDENTIFICADOR parametros_cont | ε
        elif nodo.valor == 'parametros_cont':
            if nodo.hijos and nodo.hijos[0].valor == 'COMA':
                identificador_param_nodo = nodo.hijos[1]
                nombre_param = identificador_param_nodo.token_original.value
                if not self.tabla_simbolos.add_symbol(nombre_param, TIPO_NUMERO, 'variable'):
                    self.reportar_error(f"Parámetro '{nombre_param}' ya declarado en esta función.", identificador_param_nodo)
                print(f"Declarado parámetro '{nombre_param}' de tipo {TIPO_NUMERO}")
                self.recorrer_ast(nodo.hijos[2]) # parametros_cont

        # bloque -> LLAVE_IZQ lista_sentencias LLAVE_DER
        elif nodo.valor == 'bloque':
            self.tabla_simbolos.push_scope() # Nuevo ámbito para el bloque
            self.recorrer_ast(nodo.hijos[1]) # lista_sentencias
            self.tabla_simbolos.pop_scope()

        # asignacion_o_llamada -> IGUAL expresion
        elif nodo.valor == 'asignacion_o_llamada' and nodo.hijos[0].valor == 'IGUAL':
            self.recorrer_ast(nodo.hijos[1]) # expresion
            # El tipo de la expresión se adjuntará al nodo de la expresión
            setattr(nodo, 'tipo', getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO))

        # asignacion_o_llamada -> PAR_IZQ lista_argumentos PAR_DER
        elif nodo.valor == 'asignacion_o_llamada' and nodo.hijos[0].valor == 'PAR_IZQ':
            self.recorrer_ast(nodo.hijos[1]) # lista_argumentos
            # Aquí se debería verificar el número y tipo de argumentos con la definición de la función
            # Esto requiere que el nodo padre (IDENTIFICADOR) tenga la información de la función.
            # Por ahora, solo se asegura que los argumentos se evalúen.
            
            # Obtener el número de argumentos pasados
            num_args_pasados = getattr(nodo.hijos[1], 'num_args', 0)
            
            # Buscar el nodo IDENTIFICADOR padre para obtener la información de la función
            # Esto es un poco complicado sin un puntero al padre en el AST.
            # Una solución sería pasar el contexto (función actual) al recorrer.
            # Por ahora, asumimos que el IDENTIFICADOR ya fue procesado y tiene su categoría.
            
            # Si el nodo padre es una sentencia de llamada (IDENTIFICADOR asignacion_o_llamada)
            # y el IDENTIFICADOR es una función, podemos verificar.
            # Esto es una simplificación, en un AST bien formado, el nodo de llamada tendría la referencia a la función.
            
            # Para este ejemplo, asumimos que el nodo 'asignacion_o_llamada' es hijo de un 'sentencia'
            # y que el 'IDENTIFICADOR' de esa sentencia es la función que se está llamando.
            # Esto es una aproximación y puede no ser robusta para todos los casos.
            
            # Si el nodo 'asignacion_o_llamada' tiene un padre que es 'sentencia'
            # y el primer hijo de 'sentencia' es un 'IDENTIFICADOR'
            # y ese IDENTIFICADOR es una función...
            
            # Esto es un hack, idealmente el AST debería tener punteros a padres o un mejor diseño.
            # Para una implementación más robusta, se pasaría el símbolo de la función al llamar a esta regla.
            
            # Simulación de verificación de argumentos:
            # Si el nodo 'asignacion_o_llamada' es parte de una llamada a función,
            # el nodo 'IDENTIFICADOR' (nombre de la función) debería ser su "hermano" anterior.
            # No podemos acceder directamente al hermano aquí.
            # Una forma sería que el nodo 'sentencia' (padre) pase la información de la función.
            
            # Por ahora, solo se evalúan los argumentos.
            print(f"Llamada a función con {num_args_pasados} argumentos.")


        # lista_argumentos -> expresion lista_argumentos_cont | ε
        elif nodo.valor == 'lista_argumentos':
            num_args = 0
            if nodo.hijos and nodo.hijos[0].valor != 'epsilon_node':
                self.recorrer_ast(nodo.hijos[0]) # expresion
                num_args += 1
                
                # Recorrer lista_argumentos_cont para contar más argumentos
                current_arg_cont = nodo.hijos[1]
                while current_arg_cont.hijos and current_arg_cont.hijos[0].valor == 'COMA':
                    self.recorrer_ast(current_arg_cont.hijos[1]) # expresion
                    num_args += 1
                    current_arg_cont = current_arg_cont.hijos[2]
            setattr(nodo, 'num_args', num_args) # Adjuntar el número de argumentos al nodo
            print(f"Evaluando lista de argumentos: {num_args} argumentos.")

        # lista_argumentos_cont -> COMA expresion lista_argumentos_cont | ε
        elif nodo.valor == 'lista_argumentos_cont':
            # Los argumentos ya se procesan en lista_argumentos para el conteo
            pass

        # sino_parte -> SINO bloque | ε
        elif nodo.valor == 'sino_parte':
            if nodo.hijos and nodo.hijos[0].valor == 'SINO':
                self.recorrer_ast(nodo.hijos[1]) # bloque

        # Expresiones (orden de precedencia de menor a mayor)
        # expresion -> exp_logico_and exp_logico_or_resto
        elif nodo.valor == 'expresion':
            self.recorrer_ast(nodo.hijos[0]) # exp_logico_and
            self.recorrer_ast(nodo.hijos[1]) # exp_logico_or_resto
            
            tipo_izq = getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO)
            tipo_resto = getattr(nodo.hijos[1], 'tipo', TIPO_VOID) # ε tiene tipo VOID o similar
            
            if tipo_resto == TIPO_VOID: # Si no hay O_LOGICO
                setattr(nodo, 'tipo', tipo_izq)
            elif tipo_izq == TIPO_BOOLEANO and tipo_resto == TIPO_BOOLEANO:
                setattr(nodo, 'tipo', TIPO_BOOLEANO)
            else:
                self.reportar_error(f"Operación lógica '||' requiere operandos BOOLEANO, se obtuvo {tipo_izq} y {tipo_resto}.", nodo)
                setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

        # exp_logico_or_resto -> O_LOGICO exp_logico_and exp_logico_or_resto | ε
        elif nodo.valor == 'exp_logico_or_resto':
            if nodo.hijos and nodo.hijos[0].valor == 'O_LOGICO':
                self.recorrer_ast(nodo.hijos[1]) # exp_logico_and
                self.recorrer_ast(nodo.hijos[2]) # exp_logico_or_resto
                
                tipo_op1 = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                tipo_op2 = getattr(nodo.hijos[2], 'tipo', TIPO_VOID)
                
                if tipo_op1 == TIPO_BOOLEANO and (tipo_op2 == TIPO_BOOLEANO or tipo_op2 == TIPO_VOID):
                    setattr(nodo, 'tipo', TIPO_BOOLEANO)
                else:
                    self.reportar_error(f"Operación lógica '||' requiere operandos BOOLEANO, se obtuvo {tipo_op1} y {tipo_op2}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # ε
                setattr(nodo, 'tipo', TIPO_VOID) # Representa que no hay operación

        # exp_logico_and -> exp_igualdad exp_logico_and_resto
        elif nodo.valor == 'exp_logico_and':
            self.recorrer_ast(nodo.hijos[0]) # exp_igualdad
            self.recorrer_ast(nodo.hijos[1]) # exp_logico_and_resto
            
            tipo_izq = getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO)
            tipo_resto = getattr(nodo.hijos[1], 'tipo', TIPO_VOID)
            
            if tipo_resto == TIPO_VOID:
                setattr(nodo, 'tipo', tipo_izq)
            elif tipo_izq == TIPO_BOOLEANO and tipo_resto == TIPO_BOOLEANO:
                setattr(nodo, 'tipo', TIPO_BOOLEANO)
            else:
                self.reportar_error(f"Operación lógica '&&' requiere operandos BOOLEANO, se obtuvo {tipo_izq} y {tipo_resto}.", nodo)
                setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

        # exp_logico_and_resto -> Y_LOGICO exp_igualdad exp_logico_and_resto | ε
        elif nodo.valor == 'exp_logico_and_resto':
            if nodo.hijos and nodo.hijos[0].valor == 'Y_LOGICO':
                self.recorrer_ast(nodo.hijos[1]) # exp_igualdad
                self.recorrer_ast(nodo.hijos[2]) # exp_logico_and_resto
                
                tipo_op1 = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                tipo_op2 = getattr(nodo.hijos[2], 'tipo', TIPO_VOID)
                
                if tipo_op1 == TIPO_BOOLEANO and (tipo_op2 == TIPO_BOOLEANO or tipo_op2 == TIPO_VOID):
                    setattr(nodo, 'tipo', TIPO_BOOLEANO)
                else:
                    self.reportar_error(f"Operación lógica '&&' requiere operandos BOOLEANO, se obtuvo {tipo_op1} y {tipo_op2}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # ε
                setattr(nodo, 'tipo', TIPO_VOID)

        # exp_igualdad -> exp_comparacion exp_igualdad_resto
        elif nodo.valor == 'exp_igualdad':
            self.recorrer_ast(nodo.hijos[0]) # exp_comparacion
            self.recorrer_ast(nodo.hijos[1]) # exp_igualdad_resto
            
            tipo_izq = getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO)
            tipo_resto = getattr(nodo.hijos[1], 'tipo', TIPO_VOID)
            
            if tipo_resto == TIPO_VOID:
                setattr(nodo, 'tipo', tipo_izq)
            elif tipo_izq == tipo_resto and tipo_izq != TIPO_DESCONOCIDO: # Tipos deben ser iguales
                setattr(nodo, 'tipo', TIPO_BOOLEANO) # Resultado de comparación es booleano
            else:
                self.reportar_error(f"Operación de igualdad/diferencia requiere operandos del mismo tipo, se obtuvo {tipo_izq} y {tipo_resto}.", nodo)
                setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

        # exp_igualdad_resto -> op_igualdad exp_comparacion exp_igualdad_resto | ε
        elif nodo.valor == 'exp_igualdad_resto':
            if nodo.hijos and nodo.hijos[0].valor in ['IGUAL_IGUAL', 'DIFERENTE']:
                self.recorrer_ast(nodo.hijos[1]) # exp_comparacion
                self.recorrer_ast(nodo.hijos[2]) # exp_igualdad_resto
                
                tipo_op1 = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                tipo_op2 = getattr(nodo.hijos[2], 'tipo', TIPO_VOID)
                
                if tipo_op1 == tipo_op2 and tipo_op1 != TIPO_DESCONOCIDO:
                    setattr(nodo, 'tipo', TIPO_BOOLEANO)
                else:
                    self.reportar_error(f"Operación de igualdad/diferencia requiere operandos del mismo tipo, se obtuvo {tipo_op1} y {tipo_op2}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # ε
                setattr(nodo, 'tipo', TIPO_VOID)

        # exp_comparacion -> exp_suma exp_comparacion_resto
        elif nodo.valor == 'exp_comparacion':
            self.recorrer_ast(nodo.hijos[0]) # exp_suma
            self.recorrer_ast(nodo.hijos[1]) # exp_comparacion_resto
            
            tipo_izq = getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO)
            tipo_resto = getattr(nodo.hijos[1], 'tipo', TIPO_VOID)
            
            if tipo_resto == TIPO_VOID:
                setattr(nodo, 'tipo', tipo_izq)
            elif tipo_izq == TIPO_NUMERO and tipo_resto == TIPO_NUMERO:
                setattr(nodo, 'tipo', TIPO_BOOLEANO) # Resultado de comparación es booleano
            else:
                self.reportar_error(f"Operación de comparación requiere operandos NUMERO, se obtuvo {tipo_izq} y {tipo_resto}.", nodo)
                setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

        # exp_comparacion_resto -> op_comp exp_suma exp_comparacion_resto | ε
        elif nodo.valor == 'exp_comparacion_resto':
            if nodo.hijos and nodo.hijos[0].valor in ['MAYOR', 'MENOR', 'MAYOR_IGUAL', 'MENOR_IGUAL']:
                self.recorrer_ast(nodo.hijos[1]) # exp_suma
                self.recorrer_ast(nodo.hijos[2]) # exp_comparacion_resto
                
                tipo_op1 = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                tipo_op2 = getattr(nodo.hijos[2], 'tipo', TIPO_VOID)
                
                if tipo_op1 == TIPO_NUMERO and (tipo_op2 == TIPO_NUMERO or tipo_op2 == TIPO_VOID):
                    setattr(nodo, 'tipo', TIPO_BOOLEANO)
                else:
                    self.reportar_error(f"Operación de comparación requiere operandos NUMERO, se obtuvo {tipo_op1} y {tipo_op2}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # ε
                setattr(nodo, 'tipo', TIPO_VOID)

        # exp_suma -> exp_mult exp_suma_resto
        elif nodo.valor == 'exp_suma':
            self.recorrer_ast(nodo.hijos[0]) # exp_mult
            self.recorrer_ast(nodo.hijos[1]) # exp_suma_resto
            
            tipo_izq = getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO)
            tipo_resto = getattr(nodo.hijos[1], 'tipo', TIPO_VOID)
            
            if tipo_resto == TIPO_VOID:
                setattr(nodo, 'tipo', tipo_izq)
            elif tipo_izq == TIPO_NUMERO and tipo_resto == TIPO_NUMERO:
                setattr(nodo, 'tipo', TIPO_NUMERO)
            elif tipo_izq == TIPO_CADENA and tipo_resto == TIPO_CADENA and getattr(nodo.hijos[1].hijos[0], 'valor', '') == 'MAS':
                # Concatenación de cadenas
                setattr(nodo, 'tipo', TIPO_CADENA)
            else:
                self.reportar_error(f"Operación de suma/resta requiere operandos NUMERO, o concatenación de CADENA, se obtuvo {tipo_izq} y {tipo_resto}.", nodo)
                setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

        # exp_suma_resto -> op_suma exp_mult exp_suma_resto | ε
        elif nodo.valor == 'exp_suma_resto':
            if nodo.hijos and nodo.hijos[0].valor in ['MAS', 'MENOS']:
                self.recorrer_ast(nodo.hijos[1]) # exp_mult
                self.recorrer_ast(nodo.hijos[2]) # exp_suma_resto
                
                tipo_op1 = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                tipo_op2 = getattr(nodo.hijos[2], 'tipo', TIPO_VOID)
                
                if tipo_op1 == TIPO_NUMERO and (tipo_op2 == TIPO_NUMERO or tipo_op2 == TIPO_VOID):
                    setattr(nodo, 'tipo', TIPO_NUMERO)
                elif tipo_op1 == TIPO_CADENA and (tipo_op2 == TIPO_CADENA or tipo_op2 == TIPO_VOID) and nodo.hijos[0].valor == 'MAS':
                    setattr(nodo, 'tipo', TIPO_CADENA)
                else:
                    self.reportar_error(f"Operación de suma/resta requiere operandos NUMERO, o concatenación de CADENA, se obtuvo {tipo_op1} y {tipo_op2}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # ε
                setattr(nodo, 'tipo', TIPO_VOID)

        # exp_mult -> exp_potencia exp_mult_resto
        elif nodo.valor == 'exp_mult':
            self.recorrer_ast(nodo.hijos[0]) # exp_potencia
            self.recorrer_ast(nodo.hijos[1]) # exp_mult_resto
            
            tipo_izq = getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO)
            tipo_resto = getattr(nodo.hijos[1], 'tipo', TIPO_VOID)
            
            if tipo_resto == TIPO_VOID:
                setattr(nodo, 'tipo', tipo_izq)
            elif tipo_izq == TIPO_NUMERO and tipo_resto == TIPO_NUMERO:
                setattr(nodo, 'tipo', TIPO_NUMERO)
            else:
                self.reportar_error(f"Operación de multiplicación/división requiere operandos NUMERO, se obtuvo {tipo_izq} y {tipo_resto}.", nodo)
                setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

        # exp_mult_resto -> op_mult exp_potencia exp_mult_resto | ε
        elif nodo.valor == 'exp_mult_resto':
            if nodo.hijos and nodo.hijos[0].valor in ['MULT', 'DIV']:
                self.recorrer_ast(nodo.hijos[1]) # exp_potencia
                self.recorrer_ast(nodo.hijos[2]) # exp_mult_resto
                
                tipo_op1 = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                tipo_op2 = getattr(nodo.hijos[2], 'tipo', TIPO_VOID)
                
                if tipo_op1 == TIPO_NUMERO and (tipo_op2 == TIPO_NUMERO or tipo_op2 == TIPO_VOID):
                    setattr(nodo, 'tipo', TIPO_NUMERO)
                else:
                    self.reportar_error(f"Operación de multiplicación/división requiere operandos NUMERO, se obtuvo {tipo_op1} y {tipo_op2}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # ε
                setattr(nodo, 'tipo', TIPO_VOID)

        # exp_potencia -> exp_unario exp_potencia_resto
        elif nodo.valor == 'exp_potencia':
            self.recorrer_ast(nodo.hijos[0]) # exp_unario
            self.recorrer_ast(nodo.hijos[1]) # exp_potencia_resto
            
            tipo_izq = getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO)
            tipo_resto = getattr(nodo.hijos[1], 'tipo', TIPO_VOID)
            
            if tipo_resto == TIPO_VOID:
                setattr(nodo, 'tipo', tipo_izq)
            elif tipo_izq == TIPO_NUMERO and tipo_resto == TIPO_NUMERO:
                setattr(nodo, 'tipo', TIPO_NUMERO)
            else:
                self.reportar_error(f"Operación de potencia requiere operandos NUMERO, se obtuvo {tipo_izq} y {tipo_resto}.", nodo)
                setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

        # exp_potencia_resto -> POTENCIA exp_unario exp_potencia_resto | ε
        elif nodo.valor == 'exp_potencia_resto':
            if nodo.hijos and nodo.hijos[0].valor == 'POTENCIA':
                self.recorrer_ast(nodo.hijos[1]) # exp_unario
                self.recorrer_ast(nodo.hijos[2]) # exp_potencia_resto
                
                tipo_op1 = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                tipo_op2 = getattr(nodo.hijos[2], 'tipo', TIPO_VOID)
                
                if tipo_op1 == TIPO_NUMERO and (tipo_op2 == TIPO_NUMERO or tipo_op2 == TIPO_VOID):
                    setattr(nodo, 'tipo', TIPO_NUMERO)
                else:
                    self.reportar_error(f"Operación de potencia requiere operandos NUMERO, se obtuvo {tipo_op1} y {tipo_op2}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # ε
                setattr(nodo, 'tipo', TIPO_VOID)

        # exp_unario -> NEGACION exp_unario | MENOS exp_unario | primario
        elif nodo.valor == 'exp_unario':
            operador = nodo.hijos[0].valor
            if operador == 'NEGACION':
                self.recorrer_ast(nodo.hijos[1]) # exp_unario
                tipo_op = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                if tipo_op == TIPO_BOOLEANO:
                    setattr(nodo, 'tipo', TIPO_BOOLEANO)
                else:
                    self.reportar_error(f"Operador de negación '!' requiere operando BOOLEANO, se obtuvo {tipo_op}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            elif operador == 'MENOS':
                self.recorrer_ast(nodo.hijos[1]) # exp_unario
                tipo_op = getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO)
                if tipo_op == TIPO_NUMERO:
                    setattr(nodo, 'tipo', TIPO_NUMERO)
                else:
                    self.reportar_error(f"Operador unario '-' requiere operando NUMERO, se obtuvo {tipo_op}.", nodo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
            else: # primario
                self.recorrer_ast(nodo.hijos[0])
                setattr(nodo, 'tipo', getattr(nodo.hijos[0], 'tipo', TIPO_DESCONOCIDO))

        # primario -> NUMERO | CADENA | VERDADERO | FALSO | IDENTIFICADOR primario_llamada_opcional | PAR_IZQ expresion PAR_DER
        elif nodo.valor == 'primario':
            primer_hijo = nodo.hijos[0]
            if primer_hijo.valor == 'NUMERO':
                setattr(nodo, 'tipo', TIPO_NUMERO)
            elif primer_hijo.valor == 'CADENA':
                setattr(nodo, 'tipo', TIPO_CADENA)
            elif primer_hijo.valor == 'VERDADERO' or primer_hijo.valor == 'FALSO':
                setattr(nodo, 'tipo', TIPO_BOOLEANO)
            elif primer_hijo.valor == 'IDENTIFICADOR':
                nombre_id = primer_hijo.token_original.value
                entrada_simbolo = self.tabla_simbolos.lookup_symbol(nombre_id)
                if not entrada_simbolo:
                    self.reportar_error(f"Uso de identificador no declarado '{nombre_id}'.", primer_hijo)
                    setattr(nodo, 'tipo', TIPO_DESCONOCIDO)
                else:
                    setattr(nodo, 'tipo', entrada_simbolo.tipo)
                    setattr(nodo, 'categoria', entrada_simbolo.categoria) # Para verificar si es función o variable
                
                # Procesar primario_llamada_opcional
                self.recorrer_ast(nodo.hijos[1])
                
                # Si es una llamada a función, el tipo del primario es el tipo de retorno de la función
                if getattr(nodo.hijos[1], 'es_llamada', False):
                    if entrada_simbolo and entrada_simbolo.categoria == 'funcion':
                        setattr(nodo, 'tipo', entrada_simbolo.tipo) # Asumimos que el tipo de la función es su tipo de retorno
                        # Verificar número de argumentos
                        num_args_pasados = getattr(nodo.hijos[1], 'num_args', 0)
                        if entrada_simbolo.num_params != num_args_pasados:
                            self.reportar_error(f"Llamada a función '{nombre_id}' con {num_args_pasados} argumentos, se esperaban {entrada_simbolo.num_params}.", primer_hijo)
                    else:
                        self.reportar_error(f"'{nombre_id}' no es una función y no puede ser llamada.", primer_hijo)
                        setattr(nodo, 'tipo', TIPO_DESCONOCIDO)

            elif primer_hijo.valor == 'PAR_IZQ':
                self.recorrer_ast(nodo.hijos[1]) # expresion dentro de paréntesis
                setattr(nodo, 'tipo', getattr(nodo.hijos[1], 'tipo', TIPO_DESCONOCIDO))
            
            # Adjuntar el token original al nodo primario si es un literal o identificador
            if primer_hijo.token_original:
                setattr(nodo, 'token_original', primer_hijo.token_original)


        # primario_llamada_opcional -> PAR_IZQ lista_argumentos PAR_DER | ε
        elif nodo.valor == 'primario_llamada_opcional':
            if nodo.hijos and nodo.hijos[0].valor == 'PAR_IZQ':
                setattr(nodo, 'es_llamada', True) # Marcar que es una llamada
                self.recorrer_ast(nodo.hijos[1]) # lista_argumentos
                setattr(nodo, 'num_args', getattr(nodo.hijos[1], 'num_args', 0))
            else: # ε
                setattr(nodo, 'es_llamada', False)

        # Para nodos terminales que no son manejados explícitamente pero pueden tener un token_original
        elif hasattr(nodo, 'token_original') and nodo.token_original:
            # No hay acción semántica directa, pero se asegura que el token_original esté presente
            pass
        
        # Recorrer hijos para reglas no específicas o para asegurar el paso
        else:
            for hijo in nodo.hijos:
                self.recorrer_ast(hijo)

# Integración con el main del analizador sintáctico
if __name__ == '__main__':
    # Asegúrate de que los imports de AnalizadorSintactico y AnalizadorLexico estén correctos
    # y que las funciones como analyze_file, cargar_tabla_desde_csv, parser_ll1, etc., estén disponibles.
    
    # Simulación de imports para que este archivo pueda ejecutarse directamente para pruebas
    try:
        from AnalizadorSintactico import Nodo, parser_ll1, cargar_tabla_desde_csv, exportar_arbol_a_graphviz, imprimir_arbol
        from AnalizadorLexico import analyze_file
    except ImportError:
        print("Asegúrate de que 'AnalizadorSintactico.py' y 'AnalizadorLexico.py' estén en el mismo directorio.")
        print("Este script está diseñado para ser ejecutado después de que el análisis sintáctico genere un AST.")
        exit()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    tabla_csv_path = os.path.join(BASE_DIR, "table_ll1.csv")
    archivo_entrada_path = os.path.join(BASE_DIR, "Inputs", "programa.serpy")
    archivo_salida_graphviz = "arbol_parseo_semantico.dot"

    if not os.path.exists(tabla_csv_path):
        print(f"Error: No se encontró la tabla de parsing en {tabla_csv_path}")
        print("Ejecute primero creadorTabla.py para generar la tabla")
        exit(1)
    
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

var y = "hola";
var z = y + " mundo"; # Concatenación de cadenas
imprimir(z);

var es_cierto = verdadero;
si (es_cierto && (10 > 5)) {
    imprimir("Condición verdadera");
} sino {
    imprimir("Condición falsa");
}

var contador = 0;
mientras (contador < 3) {
    imprimir(contador);
    contador = contador + 1;
}

para (var i = 0; i < 5; i = i + 1) {
    imprimir(i);
}

# Ejemplo con error semántico: re-declaración de variable
# var x = 20;

# Ejemplo con error semántico: uso de variable no declarada
# imprimir(no_existe);

# Ejemplo con error semántico: asignación de tipo incorrecto
# var num = 10;
# num = "texto";

# Ejemplo con error semántico: operación de tipos incompatibles
# var res_error = 5 + "texto";

# Ejemplo con error semántico: llamada a función con argumentos incorrectos
# suma(1);
""")
    
    print(f"--- Cargando tabla de parsing desde: {tabla_csv_path} ---")
    tabla_parsing = cargar_tabla_desde_csv(tabla_csv_path)
    
    if tabla_parsing is None:
        print("No se pudo continuar debido a un error al cargar la tabla de parsing.")
        exit(1)
    
    print(f"--- Analizando léxicamente el archivo: {archivo_entrada_path} ---")
    lista_de_tokens = analyze_file(archivo_entrada_path) 

    if not lista_de_tokens:
        print("\n❌ Error durante el análisis léxico o el archivo no contiene tokens.")
        exit(1)
    
    print(f"--- Iniciando análisis sintáctico ---")
    arbol_sintactico = parser_ll1(lista_de_tokens, tabla_parsing, start_symbol='PROGRAMA')

    if arbol_sintactico:
        print("\n✅ Entrada aceptada por el analizador sintáctico.")
        
        print("\nEstructura del árbol sintáctico (antes de semántico):")
        imprimir_arbol(arbol_sintactico)
        
        print(f"\n--- Iniciando Análisis Semántico para {archivo_entrada_path} ---")
        analizador_semantico = AnalizadorSemantico()
        semantico_ok = analizador_semantico.analizar(arbol_sintactico)

        if semantico_ok:
            print("\nAnálisis Semántico Exitoso. Generando Graphviz del AST con información semántica.")
            exportar_arbol_a_graphviz(arbol_sintactico, archivo_salida_graphviz)
        else:
            print("\nAnálisis Semántico Fallido. No se generará el archivo Graphviz.")
            for error in analizador_semantico.errores_semanticos:
                print(error)
        
    else:
        print("\n❌ Entrada rechazada por el analizador sintáctico. No se realizará el análisis semántico.")
        exit(1)

