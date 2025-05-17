class Valor:
    def __init__(self, lexema, token, linea, columna):
        self.lexema = lexema
        self.token = token
        self.linea = linea
        self.columna = columna

    def toString(self):
        # Alineación básica para que se vea ordenado
        return f"{str(self.lexema):<10}\t{str(self.token):<10}\t{self.linea}:{self.columna}"
    
    def getLexema(self):
        return self.lexema
    
    def getToken(self):
        return self.token
    
    def getLinea(self):
        return self.linea
    
    def getColumna(self):
        return self.columna
    
    def setLexema(self, c):
        self.lexema = c

    def setToken(self, s):
        self.token = s
