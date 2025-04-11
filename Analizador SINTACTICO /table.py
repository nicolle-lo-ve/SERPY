import sys
import io
from collections import defaultdict, deque

# Configurar la salida para UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class SLRTableGenerator:
    def __init__(self, grammar):
        self.grammar = grammar
        self.terminals = set()
        self.non_terminals = set()
        self.productions = []
        self.first_sets = defaultdict(set)
        self.follow_sets = defaultdict(set)
        self.states = []
        self.action_table = defaultdict(dict)
        self.goto_table = defaultdict(dict)
        self.prod_index = {}
        
        self._process_grammar()
        self._compute_first_sets()
        self._compute_follow_sets()
        self._build_lr0_items()
        self._build_slr_table()

    def _process_grammar(self):
        """Procesa la gramática y extrae terminales, no terminales y producciones"""
        for i, (head, body) in enumerate(self.grammar):
            self.non_terminals.add(head)
            for symbol in body:
                if symbol and symbol not in self.non_terminals:
                    self.terminals.add(symbol)
            
            # Convertir el cuerpo a tupla para que sea hashable
            body_tuple = tuple(body)
            self.productions.append((head, body_tuple))
            self.prod_index[(head, body_tuple)] = i
        
        self.terminals.add('$')

    def _compute_first_sets(self):
        """Calcula los conjuntos FIRST para todos los símbolos"""
        # Inicializar FIRST para terminales
        for t in self.terminals:
            self.first_sets[t].add(t)
        
        changed = True
        while changed:
            changed = False
            for head, body in self.productions:
                old_len = len(self.first_sets[head])
                
                if not body:
                    self.first_sets[head].add('')
                    continue
                
                all_have_epsilon = True
                for symbol in body:
                    self.first_sets[head].update(self.first_sets[symbol] - {''})
                    if '' not in self.first_sets[symbol]:
                        all_have_epsilon = False
                        break
                
                if all_have_epsilon:
                    self.first_sets[head].add('')
                
                if len(self.first_sets[head]) > old_len:
                    changed = True

    def _compute_follow_sets(self):
        """Calcula los conjuntos FOLLOW para los no terminales"""
        self.follow_sets[self.grammar[0][0]].add('$')
        
        changed = True
        while changed:
            changed = False
            for head, body in self.productions:
                for i, symbol in enumerate(body):
                    if symbol in self.non_terminals:
                        old_len = len(self.follow_sets[symbol])
                        
                        beta = body[i+1:]
                        if beta:
                            first_beta = self._compute_first_of_sequence(beta)
                            self.follow_sets[symbol].update(first_beta - {''})
                            
                            if '' in first_beta:
                                self.follow_sets[symbol].update(self.follow_sets[head])
                        else:
                            self.follow_sets[symbol].update(self.follow_sets[head])
                        
                        if len(self.follow_sets[symbol]) > old_len:
                            changed = True

    def _compute_first_of_sequence(self, sequence):
        first = set()
        all_have_epsilon = True
        
        for symbol in sequence:
            first.update(self.first_sets[symbol] - {''})
            if '' not in self.first_sets[symbol]:
                all_have_epsilon = False
                break
        
        if all_have_epsilon:
            first.add('')
        
        return first

    def _closure(self, items):
        """Calcula la clausura de un conjunto de items LR(0)"""
        closure = set(items)
        queue = deque(items)
        
        while queue:
            head, body, pos = queue.popleft()
            if pos < len(body) and body[pos] in self.non_terminals:
                for prod_head, prod_body in self.productions:
                    if prod_head == body[pos]:
                        new_item = (prod_head, prod_body, 0)
                        if new_item not in closure:
                            closure.add(new_item)
                            queue.append(new_item)
        return closure

    def _goto(self, items, symbol):
        """Calcula la función GOTO para un conjunto de items"""
        goto_items = set()
        for head, body, pos in items:
            if pos < len(body) and body[pos] == symbol:
                goto_items.add((head, body, pos + 1))
        return self._closure(goto_items) if goto_items else set()

    def _build_lr0_items(self):
        """Construye los estados LR(0)"""
        initial_item = (self.productions[0][0], self.productions[0][1], 0)
        initial_state = frozenset(self._closure({initial_item}))
        self.states.append(initial_state)
        
        queue = deque([0])
        state_indices = {initial_state: 0}
        
        while queue:
            current_idx = queue.popleft()
            current_state = self.states[current_idx]
            
            symbols = self.terminals.union(self.non_terminals)
            for symbol in symbols:
                new_state = frozenset(self._goto(current_state, symbol))
                if new_state:
                    if new_state not in state_indices:
                        state_indices[new_state] = len(self.states)
                        self.states.append(new_state)
                        queue.append(len(self.states) - 1)
                    next_state_idx = state_indices[new_state]
                    
                    if symbol in self.terminals:
                        self.action_table[current_idx][symbol] = ('shift', next_state_idx)
                    else:
                        self.goto_table[current_idx][symbol] = next_state_idx

    def _build_slr_table(self):
        """Completa la tabla SLR con las reducciones"""
        for i, state in enumerate(self.states):
            for item in state:
                head, body, pos = item
                if pos == len(body):
                    if head == self.productions[0][0]:
                        self.action_table[i]['$'] = 'accept'  # Cambiado a solo el valor
                    else:
                        prod_num = self.prod_index[(head, body)]
                        for terminal in self.follow_sets[head]:
                            if terminal in self.action_table[i]:
                                existing = self.action_table[i][terminal]
                                if isinstance(existing, tuple) and existing[0] == 'shift':
                                    continue
                            self.action_table[i][terminal] = ('reduce', prod_num)

    def print_table(self):
        """Imprime la tabla SLR en formato legible"""
        try:
            all_terminals = sorted(self.terminals)
            all_non_terminals = sorted(self.non_terminals - {self.grammar[0][0]})
            
            print("SLR(1) Parsing Table")
            print("="*80)
            print("{:<8}".format("State"), end="")
            
            for t in all_terminals:
                print("{:<12}".format(t), end="")
            
            for nt in all_non_terminals:
                print("{:<12}".format(nt), end="")
            print()
            
            for i in range(len(self.states)):
                print("{:<8}".format(i), end="")
                
                for t in all_terminals:
                    if t in self.action_table[i]:
                        action_val = self.action_table[i][t]
                        if action_val == 'accept':
                            print("{:<12}".format("acc"), end="")
                        elif isinstance(action_val, tuple) and len(action_val) == 2:
                            action, val = action_val
                            if action == 'shift':
                                print("{:<12}".format(f"s{val}"), end="")
                            elif action == 'reduce':
                                print("{:<12}".format(f"r{val}"), end="")
                        else:
                            print("{:<12}".format(str(action_val)), end="")
                    else:
                        print("{:<12}".format(""), end="")
                
                for nt in all_non_terminals:
                    if nt in self.goto_table[i]:
                        print("{:<12}".format(self.goto_table[i][nt]), end="")
                    else:
                        print("{:<12}".format(""), end="")
                print()
            
            print("\nProductions:")
            for i, (head, body) in enumerate(self.productions):
                # Usar 'ε' o 'epsilon' según lo que funcione en tu consola
                print(f"{i}: {head} -> {' '.join(body) if body else 'epsilon'}")
                
        except UnicodeEncodeError:
            # Fallback si UTF-8 no está soportado
            print("\nProductions:")
            for i, (head, body) in enumerate(self.productions):
                print(f"{i}: {head} -> {' '.join(body) if body else '(epsilon)'}")


    def export_to_csv(self, filename):
        """Exporta la tabla SLR a un archivo CSV"""
        import csv
        
        # Obtener todos los símbolos terminales y no terminales ordenados
        all_terminals = sorted(self.terminals)
        all_non_terminals = sorted(self.non_terminals - {self.grammar[0][0]})
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir encabezados
            headers = ['State'] + all_terminals + all_non_terminals
            writer.writerow(headers)
            
            # Escribir cada estado
            for i in range(len(self.states)):
                row = [i]
                
                # Acciones para terminales
                for t in all_terminals:
                    if t in self.action_table[i]:
                        action_val = self.action_table[i][t]
                        if action_val == 'accept':
                            row.append('acc')
                        elif isinstance(action_val, tuple):
                            action, val = action_val
                            row.append(f'{action[0]}{val}')
                        else:
                            row.append(str(action_val))
                    else:
                        row.append('')
                
                # Transiciones GOTO para no terminales
                for nt in all_non_terminals:
                    if nt in self.goto_table[i]:
                        row.append(str(self.goto_table[i][nt]))
                    else:
                        row.append('')
                
                writer.writerow(row)
            
            # Escribir las producciones al final
            writer.writerow([])
            writer.writerow(['Productions:'])
            for i, (head, body) in enumerate(self.productions):
                writer.writerow([f"{i}", f"{head} → {' '.join(body) if body else 'ε'}"])

# Tu gramática completa
grammar = [
    ('PROGRAMA', ['lista_sentencias']),
    ('lista_sentencias', ['sentencia', 'lista_sentencias']),
    ('lista_sentencias', []),
    ('sentencia', ['VAR', 'IDENTIFICADOR', 'IGUAL', 'expresion', 'PUNTOYCOMA']),
    ('sentencia', ['IDENTIFICADOR', 'asignacion_o_llamada', 'PUNTOYCOMA']),
    ('sentencia', ['RETORNAR', 'expresion', 'PUNTOYCOMA']),
    ('sentencia', ['IMPRIMIR', 'PAR_IZQ', 'lista_argumentos', 'PAR_DER', 'PUNTOYCOMA']),
    ('sentencia', ['si_sentencia']),
    ('sentencia', ['mientras_sentencia']),
    ('sentencia', ['para_sentencia']),
    ('sentencia', ['funcion_def']),
    ('asignacion_o_llamada', ['IGUAL', 'expresion']),
    ('asignacion_o_llamada', ['PAR_IZQ', 'lista_argumentos', 'PAR_DER']),
    ('lista_argumentos', ['expresion', 'lista_argumentos_cont']),
    ('lista_argumentos', []),
    ('lista_argumentos_cont', ['COMA', 'expresion', 'lista_argumentos_cont']),
    ('lista_argumentos_cont', []),
    ('si_sentencia', ['SI', 'PAR_IZQ', 'expresion', 'PAR_DER', 'bloque', 'sino_parte']),
    ('sino_parte', ['SINO', 'bloque']),
    ('sino_parte', []),
    ('mientras_sentencia', ['MIENTRAS', 'PAR_IZQ', 'expresion', 'PAR_DER', 'bloque']),
    ('para_sentencia', ['PARA', 'PAR_IZQ', 'para_inicio', 'PUNTOYCOMA', 'expresion', 'PUNTOYCOMA', 'IDENTIFICADOR', 'IGUAL', 'expresion', 'PAR_DER', 'bloque']),
    ('para_inicio', ['VAR', 'IDENTIFICADOR', 'IGUAL', 'expresion']),
    ('para_inicio', ['IDENTIFICADOR', 'IGUAL', 'expresion']),
    ('funcion_def', ['DEFINIR', 'IDENTIFICADOR', 'PAR_IZQ', 'parametros', 'PAR_DER', 'bloque']),
    ('parametros', ['IDENTIFICADOR', 'parametros_cont']),
    ('parametros', []),
    ('parametros_cont', ['COMA', 'IDENTIFICADOR', 'parametros_cont']),
    ('parametros_cont', []),
    ('bloque', ['LLAVE_IZQ', 'lista_sentencias', 'LLAVE_DER']),
    ('expresion', ['exp_logico_and', 'exp_logico_or_resto']),
    ('exp_logico_or_resto', ['O_LOGICO', 'exp_logico_and', 'exp_logico_or_resto']),
    ('exp_logico_or_resto', []),
    ('exp_logico_and', ['exp_igualdad', 'exp_logico_and_resto']),
    ('exp_logico_and_resto', ['Y_LOGICO', 'exp_igualdad', 'exp_logico_and_resto']),
    ('exp_logico_and_resto', []),
    ('exp_igualdad', ['exp_comparacion', 'exp_igualdad_resto']),
    ('exp_igualdad_resto', ['op_igualdad', 'exp_comparacion', 'exp_igualdad_resto']),
    ('exp_igualdad_resto', []),
    ('op_igualdad', ['IGUAL_IGUAL']),
    ('op_igualdad', ['DIFERENTE']),
    ('exp_comparacion', ['exp_suma', 'exp_comparacion_resto']),
    ('exp_comparacion_resto', ['op_comp', 'exp_suma', 'exp_comparacion_resto']),
    ('exp_comparacion_resto', []),
    ('op_comp', ['MAYOR']),
    ('op_comp', ['MENOR']),
    ('op_comp', ['MAYOR_IGUAL']),
    ('op_comp', ['MENOR_IGUAL']),
    ('exp_suma', ['exp_mult', 'exp_suma_resto']),
    ('exp_suma_resto', ['op_suma', 'exp_mult', 'exp_suma_resto']),
    ('exp_suma_resto', []),
    ('op_suma', ['MAS']),
    ('op_suma', ['MENOS']),
    ('exp_mult', ['exp_potencia', 'exp_mult_resto']),
    ('exp_mult_resto', ['op_mult', 'exp_potencia', 'exp_mult_resto']),
    ('exp_mult_resto', []),
    ('op_mult', ['MULT']),
    ('op_mult', ['DIV']),
    ('exp_potencia', ['exp_unario', 'exp_potencia_resto']),
    ('exp_potencia_resto', ['POTENCIA', 'exp_unario', 'exp_potencia_resto']),
    ('exp_potencia_resto', []),
    ('exp_unario', ['NEGACION', 'exp_unario']),
    ('exp_unario', ['MENOS', 'exp_unario']),
    ('exp_unario', ['primario']),
    ('primario', ['NUMERO']),
    ('primario', ['CADENA']),
    ('primario', ['VERDADERO']),
    ('primario', ['FALSO']),
    ('primario', ['IDENTIFICADOR', 'primario_llamada_opcional']),
    ('primario', ['PAR_IZQ', 'expresion', 'PAR_DER']),
    ('primario_llamada_opcional', ['PAR_IZQ', 'lista_argumentos', 'PAR_DER']),
    ('primario_llamada_opcional', []),
]

# Generar la tabla
try:
    generator = SLRTableGenerator(grammar)
    
    # Mostrar tabla en consola (opcional)
    generator.print_table()
    
    # Exportar a CSV
    generator.export_to_csv('slr_table.csv')
    print("\nTabla SLR guardada correctamente en 'slr_table.csv'")
    
except Exception as e:
    print(f"Error al generar la tabla: {e}")
    print(f"Tipo de error: {type(e).__name__}")
    import traceback
    traceback.print_exc()
