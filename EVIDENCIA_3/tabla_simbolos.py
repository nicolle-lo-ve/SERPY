# tabla_simbolos_adaptada.py
# Versión adaptada y simplificada para el compilador existente
# Compatible con la arquitectura actual sin dependencias externas

class Simbolo:
    """Clase para representar un símbolo en la tabla de símbolos"""
    
    def __init__(self, categoria_lexica, tipo, lexema, dimension=None, valor=None, 
                 ambito="global", declarada_en=None, referencias=None):
        """
        Inicializa un símbolo.
        
        Args:
            categoria_lexica (str): Tipo de símbolo (variable, funcion, parametro)
            tipo (str): Tipo de dato (int, float, string, boolean, void)
            lexema (str): Nombre del símbolo
            dimension (str, optional): Dimensión si es array
            valor (any, optional): Valor inicial
            ambito (str): Ámbito del símbolo
            declarada_en (int, optional): Línea donde se declaró
            referencias (list, optional): Lista de referencias
        """
        self.categoria_lexica = categoria_lexica
        self.tipo = tipo
        self.lexema = lexema
        self.dimension = dimension
        self.valor = valor
        self.ambito = ambito
        self.declarada_en = declarada_en
        self.referencias = referencias if referencias else []
        
        # Propiedades adicionales
        self.inicializada = valor is not None
        self.usada = False
        self.parametros = []  # Para funciones
    
    def agregar_referencia(self, linea, columna=None):
        """Agrega una referencia al símbolo"""
        self.referencias.append({
            'linea': linea,
            'columna': columna,
            'usado': True
        })
        self.usada = True
    
    def __str__(self):
        return f"{self.lexema} ({self.categoria_lexica}:{self.tipo})"
    
    def __repr__(self):
        return self.__str__()


class TablaSimbolos:
    """Tabla de símbolos para el compilador"""
    
    def __init__(self):
        """Inicializa la tabla de símbolos"""
        self.tabla = {}  # {lexema: Simbolo}
        self.ambitos = ["global"]  # Stack de ámbitos
        self.ambito_actual = "global"
        self.estadisticas = {
            'total_simbolos': 0,
            'variables': 0,
            'funciones': 0,
            'parametros': 0,
            'errores': 0,
            'advertencias': 0
        }
        self.errores = []
        self.advertencias = []
    
    def cambiar_ambito(self, nuevo_ambito):
        """Cambia el ámbito actual"""
        self.ambitos.append(nuevo_ambito)
        self.ambito_actual = nuevo_ambito
    
    def salir_ambito(self):
        """Sale del ámbito actual"""
        if len(self.ambitos) > 1:
            self.ambitos.pop()
            self.ambito_actual = self.ambitos[-1]
    
    def existe_simbolo(self, lexema, ambito=None):
        """Verifica si existe un símbolo"""
        clave = self._generar_clave(lexema, ambito or self.ambito_actual)
        return clave in self.tabla
    
    def obtener_simbolo(self, lexema, ambito=None):
        """Obtiene un símbolo de la tabla"""
        # Buscar en el ámbito especificado
        if ambito:
            clave = self._generar_clave(lexema, ambito)
            if clave in self.tabla:
                return self.tabla[clave]
        
        # Buscar en ámbitos desde el actual hacia global
        for ambito_busqueda in reversed(self.ambitos):
            clave = self._generar_clave(lexema, ambito_busqueda)
            if clave in self.tabla:
                return self.tabla[clave]
        
        return None
    
    def agregar_simbolo(self, simbolo):
        """Agrega un símbolo a la tabla"""
        clave = self._generar_clave(simbolo.lexema, simbolo.ambito)
        
        # Verificar si ya existe en el mismo ámbito
        if clave in self.tabla:
            self.errores.append(f"Error: El símbolo '{simbolo.lexema}' ya está declarado en el ámbito '{simbolo.ambito}'")
            self.estadisticas['errores'] += 1
            return False
        
        # Agregar el símbolo
        self.tabla[clave] = simbolo
        self.estadisticas['total_simbolos'] += 1
        
        # Actualizar estadísticas
        if simbolo.categoria_lexica == 'variable':
            self.estadisticas['variables'] += 1
        elif simbolo.categoria_lexica == 'funcion':
            self.estadisticas['funciones'] += 1
        elif simbolo.categoria_lexica == 'parametro':
            self.estadisticas['parametros'] += 1
        
        return True
    
    def _generar_clave(self, lexema, ambito):
        """Genera una clave única para el símbolo"""
        return f"{ambito}::{lexema}"
    
    def imprimir_tabla(self):
        """Imprime la tabla de símbolos en el formato solicitado"""
        print("\n" + "="*120)
        print("Tabla de Símbolos:")
        print("="*120)
        
        if not self.tabla:
            print("⚠️  La tabla de símbolos está vacía")
            return
        
        # Encabezados con el formato exacto solicitado
        print(f"{'Lexema':<15} {'Categoría Lexica':<17} {'Tipo':<10} {'Dimensión':<12} {'Valor':<15} {'Ámbito':<15} {'Declarada En':<13} {'Referencias':<12}")
        print("-" * 120)
        
        # Ordenar símbolos por ámbito y luego por lexema para mejor organización
        simbolos_ordenados = sorted(self.tabla.values(), key=lambda s: (s.ambito, s.lexema))
        
        # Datos con formato mejorado
        for simbolo in simbolos_ordenados:
            # Formatear valores
            valor_str = str(simbolo.valor) if simbolo.valor is not None else "-"
            if len(valor_str) > 14:
                valor_str = valor_str[:11] + "..."
            
            linea_str = str(simbolo.declarada_en) if simbolo.declarada_en else "-"
            
            dimension_str = str(simbolo.dimension) if simbolo.dimension else "-"
            
            # Formatear referencias
            if simbolo.referencias:
                referencias_str = f"L:{','.join(str(ref.get('linea', '?')) for ref in simbolo.referencias[:3])}"
                if len(simbolo.referencias) > 3:
                    referencias_str += f"+{len(simbolo.referencias)-3}"
            else:
                referencias_str = "-"
            
            print(f"{simbolo.lexema:<15} {simbolo.categoria_lexica:<17} {simbolo.tipo:<10} {dimension_str:<12} "
                  f"{valor_str:<15} {simbolo.ambito:<15} {linea_str:<13} {referencias_str:<12}")
        
        # Agregar resumen por ámbitos
        self._imprimir_resumen_ambitos()
    
    def imprimir_tabla_mejorada(self):
        """Imprime la tabla de símbolos con formato mejorado"""
        print("\n" + "="*100)
        print("TABLA DE SÍMBOLOS DETALLADA")
        print("="*100)
        
        if not self.tabla:
            print("⚠️  La tabla de símbolos está vacía")
            return
        
        # Agrupar por ámbitos
        simbolos_por_ambito = {}
        for simbolo in self.tabla.values():
            if simbolo.ambito not in simbolos_por_ambito:
                simbolos_por_ambito[simbolo.ambito] = []
            simbolos_por_ambito[simbolo.ambito].append(simbolo)
        
        # Imprimir por ámbitos
        for ambito, simbolos in simbolos_por_ambito.items():
            print(f"\n🔍 ÁMBITO: {ambito.upper()}")
            print("-" * 50)
            
            if not simbolos:
                print("   (vacío)")
                continue
            
            for simbolo in simbolos:
                print(f"   📝 {simbolo.lexema}")
                print(f"      Categoría: {simbolo.categoria_lexica}")
                print(f"      Tipo: {simbolo.tipo}")
                if simbolo.valor is not None:
                    print(f"      Valor: {simbolo.valor}")
                if simbolo.declarada_en:
                    print(f"      Declarada en línea: {simbolo.declarada_en}")
                if simbolo.referencias:
                    print(f"      Referencias: {len(simbolo.referencias)} usos")
                print()
    
    def validar_tabla(self):
        """Valida la consistencia de la tabla de símbolos"""
        errores_validacion = []
        
        # Verificar que todas las funciones llamadas estén declaradas
        # Verificar que todas las variables usadas estén declaradas
        # etc.
        
        if errores_validacion:
            self.errores.extend(errores_validacion)
            return False
        
        return True
    
    def obtener_estadisticas(self):
        """Devuelve estadísticas de la tabla"""
        return {
            'total_simbolos': len(self.tabla),
            'variables': self.estadisticas['variables'],
            'funciones': self.estadisticas['funciones'],
            'parametros': self.estadisticas['parametros'],
            'ambitos': len(set(s.ambito for s in self.tabla.values())),
            'errores': len(self.errores),
            'advertencias': len(self.advertencias),
            'estadisticas_operaciones': f"Símbolos procesados: {len(self.tabla)}"
        }
    
    def buscar_por_categoria(self, categoria):
        """Busca símbolos por categoría"""
        return [s for s in self.tabla.values() if s.categoria_lexica == categoria]
    
    def buscar_por_tipo(self, tipo):
        """Busca símbolos por tipo"""
        return [s for s in self.tabla.values() if s.tipo == tipo]
    
    def obtener_funciones(self):
        """Obtiene todas las funciones declaradas"""
        return self.buscar_por_categoria('funcion')
    
    def obtener_variables(self):
        """Obtiene todas las variables declaradas"""
        return self.buscar_por_categoria('variable')
    
    def _imprimir_resumen_ambitos(self):
        """Imprime un resumen de símbolos por ámbito"""
        print("\n" + "="*60)
        print("RESUMEN POR ÁMBITOS:")
        print("="*60)
        
        # Agrupar símbolos por ámbito
        simbolos_por_ambito = {}
        for simbolo in self.tabla.values():
            if simbolo.ambito not in simbolos_por_ambito:
                simbolos_por_ambito[simbolo.ambito] = {
                    'variables': 0,
                    'funciones': 0,
                    'parametros': 0,
                    'total': 0
                }
            
            simbolos_por_ambito[simbolo.ambito]['total'] += 1
            if simbolo.categoria_lexica == 'variable':
                simbolos_por_ambito[simbolo.ambito]['variables'] += 1
            elif simbolo.categoria_lexica == 'funcion':
                simbolos_por_ambito[simbolo.ambito]['funciones'] += 1
            elif simbolo.categoria_lexica == 'parametro':
                simbolos_por_ambito[simbolo.ambito]['parametros'] += 1
        
        # Mostrar resumen
        for ambito, stats in simbolos_por_ambito.items():
            print(f"📍 {ambito.upper()}: {stats['total']} símbolos "
                  f"(Variables: {stats['variables']}, Funciones: {stats['funciones']}, Parámetros: {stats['parametros']})")
    
    def obtener_simbolos_ambito(self, ambito):
        """Obtiene todos los símbolos de un ámbito específico"""
        return [s for s in self.tabla.values() if s.ambito == ambito]
    
    def listar_ambitos(self):
        """Lista todos los ámbitos disponibles"""
        return list(set(s.ambito for s in self.tabla.values()))
