from AnalizadorLexico import *
from AnalizadorSintactico import *
import sys
import tempfile
import os
import copy

sys.setrecursionlimit(2147483647)

class Symbol:
    def __init__(self, name, data_type, scope_name, line_declared, symbol_type="variable", params=None, value=None):
        self.name = name
        self.data_type = data_type 
        self.scope_name = scope_name
        self.line_declared = line_declared
        self.symbol_type = symbol_type  
        self.params = params if params is not None else []  
        self.is_active = True
        self.value = value  

    def __str__(self):
        return (f"Symbol(Nombre: {self.name}, TipoDato: {self.data_type}, Ambito: {self.scope_name}, "
                f"TipoSimbolo: {self.symbol_type}, Linea: {self.line_declared})")

class ScopeManager:
    def __init__(self):
        self.symbol_table = []
        self.scope_stack = ["global"] 
        self.current_scope_name = "global"
        self.error_list = []

    def log_error(self, message):
        self.error_list.append(message)

    def enter_scope(self):
        new_scope_name = f"scope_{len(self.scope_stack)}"
        self.scope_stack.append(new_scope_name)
        self.current_scope_name = new_scope_name

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope_name = self.scope_stack[-1]

    def add_symbol(self, symbol_name, data_type, line_declared, symbol_type="variable", params=None, value=None):
        for sym in self.symbol_table:
            if sym.name == symbol_name and sym.scope_name == self.current_scope_name and sym.is_active:
                self.log_error(f"Error Semántico (Línea {line_declared}): Símbolo '{symbol_name}' ya declarado en el ámbito '{self.current_scope_name}'.")
                return None
        
        new_symbol = Symbol(symbol_name, data_type, self.current_scope_name, line_declared, symbol_type, params, value)
        self.symbol_table.append(new_symbol)
        return new_symbol

    def lookup_symbol(self, name, line_used):
        for scope in reversed(self.scope_stack):
            for sym in self.symbol_table:
                if sym.name == name and sym.scope_name == scope and sym.is_active:
                    return sym
        self.log_error(f"Error Semántico (Línea {line_used}): Símbolo '{name}' no ha sido declarado.")
        return None

    def update_symbol_value(self, name, value, line_used):
        symbol = self.lookup_symbol(name, line_used)
        if symbol:
            symbol.value = value
            return True
        return False

    def print_errors(self):
        if not self.error_list:
            print("✅ Análisis semántico completado sin errores.")
        else:
            print(f"❌ Análisis semántico completado con {len(self.error_list)} error(es):")
            for error in self.error_list:
                print(f"  - {error}")

def analyze_semantics(node, scope_manager):
    if node is None:
        return

    node_type = node.valor

    if node_type == 'Program':
        for child in node.hijos:
            analyze_semantics(child, scope_manager)

    elif node_type == 'DefinitionList':
        for child in node.hijos:
            analyze_semantics(child, scope_manager)

    elif node_type == 'DeclaracionVariable':
        identifier_node = node.hijos[1]
        type_node = node.hijos[2]
        variable_name = get_node_value(identifier_node)
        data_type = extract_data_type_from_type_node(type_node)
        line_declared = get_node_line(identifier_node)

        scope_manager.add_symbol(variable_name, data_type, line_declared)

    elif node_type == 'IdBasedStmt':
        identifier_node = node.hijos[0]
        rest_node = node.hijos[1]
        variable_name = get_node_value(identifier_node)
        line_used = get_node_line(identifier_node)

        if rest_node.hijos[0].valor == 'OPERADOR_ASIGNACION':
            expression_node = rest_node.hijos[1]
            assigned_value = evaluate_expression(expression_node, scope_manager)
            scope_manager.update_symbol_value(variable_name, assigned_value, line_used)

    elif node_type == 'RetornoConValor':
        expression_node = node.hijos[1]
        return_value = evaluate_expression(expression_node, scope_manager)
        # Aquí se puede manejar el valor de retorno según sea necesario

    elif node_type == 'PrintStmt':
        argument_list_node = node.hijos[2]
        if argument_list_node.hijos and argument_list_node.hijos[0].valor != 'epsilon_node':
            for arg in argument_list_node.hijos:
                value = evaluate_expression(arg, scope_manager)
                print(value)

def evaluate_expression(expression_node, scope_manager):
    if expression_node.valor == 'Dato':
        return get_literal_value_from_dato_node(expression_node, scope_manager)
    elif expression_node.valor == 'Id':
        identifier_name = get_node_value(expression_node)
        return scope_manager.lookup_symbol(identifier_name, get_node_line(expression_node)).value
    return None

def get_literal_value_from_dato_node(dato_node, scope_manager):
    # Implementar la lógica para obtener el valor de un nodo de dato
    return None

def extract_data_type_from_type_node(type_node):
    if type_node and type_node.valor == 'Type':
        return type_node.hijos[0].valor  # Cambiar según la lógica real
    return "void"  # Cambiar según la lógica real

if __name__ == "__main__":
    # Suponiendo que 'syntax_tree' es el árbol sintáctico generado
    syntax_tree = construir_arbol_sintactico(codigo_fuente_str, ruta_tabla_csv)

    if syntax_tree:
        scope_manager = ScopeManager()
        analyze_semantics(syntax_tree, scope_manager)
        scope_manager.print_errors()
    else:
        print("❌ Falló el análisis sintáctico o léxico. No se generó el árbol.")
