class Nodo:
    def __init__(self, regla, noTer=None, Ter=None):
        self.regla = regla
        self.noTerminales = noTer if noTer is not None else []
        self.terminales = Ter if Ter is not None else []

    def terIsEmpty(self):
        return len(self.terminales) == 0
    
    def noTerIsEmpty(self):
        return len(self.noTerminales) == 0

    def revTerminales(self):
        self.terminales.reverse()
    
    def revNoTerminales(self):
        self.noTerminales.reverse()
    
    def recorrer(self):
        print("")
        print("")
        print("Inicio R"+str(self.regla))
        print("↓")
        print("Terminales:")
        for i in self.terminales:
            print(str(i.getLexema())+"\t",end="")    
        print("")
        print("No Terminales:")
        self.noTerminales.reverse()
        for i in self.noTerminales:
            print("R"+str(i.getRegla())+"\t",end="")

        for i in self.noTerminales:
            i.recorrer()

    def addNoTerminal(self, x):
        self.noTerminales.append(x)
    
    def getNoTerminales(self):
        return self.noTerminales
    
    def addTerminal(self, t):
        self.terminales.append(t)
    
    def getTerminales(self):
        return self.terminales
    
    def getRegla(self):
        return self.regla
    
    def setRegla(self, r):
        self.regla = r
