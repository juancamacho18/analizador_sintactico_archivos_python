from analizador_lexico_AFD import AnalizadorLexicoAFD

class AnalizadorSintactico:
    def __init__(self):
        self.tokens=[]
        self.posicion=0
        self.error_sintactico=None

        # ✅ Gramática simplificada LL(1)
        self.gramatica = {
    "programa": [["sentencia", "programa"], ["ε"]],

    "sentencia": [["asignacion"],["importacion"],["operacion"],["ciclo"],["condicional"],["funcion"],["clase"]],

    "asignacion": [["id", "tk_asignar", "expresion"]],
    "importacion": [["import", "id"]],
    "operacion": [["expresion", "operador", "expresion"]],
    "ciclo": [["for", "id", "in", "expresion", "tk_dos_puntos"]],
    "condicional": [["if", "expresion", "tk_dos_puntos"]],
    "funcion": [["def", "id", "tk_par_izq", "tk_par_der", "tk_dos_puntos"]],
    "clase": [["class", "id", "tk_par_izq", "expresion", "tk_par_der", "tk_dos_puntos"]],

    "expresion": [
        ["id"],
        ["tk_entero"],
        ["tk_string"],
        ["tk_par_izq", "expresion", "tk_par_der"]
    ],

    "operador": [
        ["tk_suma"], ["tk_resta"], ["tk_multi"], ["tk_div"],
        ["tk_modulo"], ["tk_potencia"], ["tk_div_entera"],
        ["tk_igual"], ["tk_distinto"], ["tk_mayor"],
        ["tk_menor"], ["tk_mayor_igual"], ["tk_menor_igual"]
    ]
}


        self.terminales = {t for reglas in self.gramatica.values() for prod in reglas for t in prod if t.islower() or t.startswith("tk_")}
        self.primero = self.calcular_primeros()
        self.siguiente = self.calcular_siguientes("programa")
        self.predicciones = self.calcular_predicciones()

    # ------------------------------------------
    def calcular_primeros(self):
        primero = {}
        for terminal in self.terminales.union({"ε"}):
            primero[terminal] = {terminal}

        def obtener_primero(simbolo):
            # ✅ corregido: aseguramos que no devuelva un conjunto vacío sin calcular
            if simbolo in primero and primero[simbolo]:
                return primero[simbolo]
            primero[simbolo] = set()
            for produccion in self.gramatica.get(simbolo, []):
                for s in produccion:
                    primeros_s = obtener_primero(s)
                    primero[simbolo].update(primeros_s - {"ε"})
                    if "ε" not in primeros_s:
                        break
                else:
                    primero[simbolo].add("ε")
            return primero[simbolo]

        for simbolo in self.gramatica:
            obtener_primero(simbolo)
        return primero


    # ------------------------------------------
    def calcular_siguientes(self, simbolo_inicial):
        siguiente = {nt: set() for nt in self.gramatica}
        siguiente[simbolo_inicial].add("$")
        cambiado = True
        while cambiado:
            cambiado = False
            for nt in self.gramatica:
                for produccion in self.gramatica[nt]:
                    for i, simbolo in enumerate(produccion):
                        if simbolo in self.gramatica:
                            resto = produccion[i + 1:]
                            antes = len(siguiente[simbolo])
                            if resto:
                                primero_resto = set()
                                for s in resto:
                                    primeros_s = self.primero[s]
                                    primero_resto.update(primeros_s - {"ε"})
                                    if "ε" not in primeros_s:
                                        break
                                else:
                                    primero_resto.add("ε")
                                siguiente[simbolo].update(primero_resto - {"ε"})
                                if "ε" in primero_resto:
                                    siguiente[simbolo].update(siguiente[nt])
                            else:
                                siguiente[simbolo].update(siguiente[nt])
                            if len(siguiente[simbolo]) > antes:
                                cambiado = True
        return siguiente

    # ------------------------------------------
    def calcular_predicciones(self):
        pred = {}
        for nt in self.gramatica:
            for prod in self.gramatica[nt]:
                regla = f"{nt} -> {' '.join(prod)}"
                conjunto = set()
                for s in prod:
                    primeros_s = self.primero[s]
                    conjunto.update(primeros_s - {"ε"})
                    if "ε" not in primeros_s:
                        break
                else:
                    conjunto.add("ε")
                pred[regla] = conjunto - {"ε"}
                if "ε" in conjunto:
                    pred[regla].update(self.siguiente[nt])
        return pred

    # ------------------------------------------
    def programa(self):
        # ✅ Forzar los tokens válidos que pueden iniciar una sentencia
        tokens_inicio_sentencia = {"id", "import", "for", "if", "def", "class", "tk_numero"}
        
        if self.token_actual() in tokens_inicio_sentencia:
            self.sentencia()
            self.programa()
        elif self.token_actual() == "$":
            return
        else:
            self.reportar_error(["sentencia", "$"])


    def sentencia(self):
        tk = self.token_actual()
        if tk == "id":
            self.asignacion()
        elif tk == "import":
            self.importacion()
        elif tk == "for":
            self.ciclo()
        elif tk == "if":
            self.condicional()
        elif tk == "def":
            self.funcion()
        elif tk == "class":
            self.clase()
        elif tk == "tk_entero":  # si es número
            self.operacion()
        else:
            self.reportar_error(list(self.primero["sentencia"]))

    def asignacion(self):
        self.match("id")
        self.match("tk_asignar")
        self.expresion()

    def importacion(self):
        self.match("import")
        self.match("id")

    def ciclo(self):
        self.match("for")
        self.match("id")
        self.match("in")
        self.expresion()
        self.match("tk_dos_puntos")

    def condicional(self):
        self.match("if")
        self.expresion()
        self.match("tk_dos_puntos")

    def funcion(self):
        self.match("def")
        self.match("id")
        self.match("tk_par_izq")
        self.match("tk_par_der")
        self.match("tk_dos_puntos")

    def clase(self):
        self.match("class")
        self.match("id")
        self.match("tk_par_izq")
        self.match("id")
        self.match("tk_par_der")
        self.match("tk_dos_puntos")

    def expresion(self):
        tk = self.token_actual()
        if tk == "id":
            self.match("id")
        elif tk == "tk_entero":
            self.match("tk_entero")
        else:
            self.reportar_error(["id", "tk_entero"])

    # ------------------------------------------
    def token_actual(self):
        if self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            return token.strip("<>").split(",")[0].strip()
        return "$"

    def match(self, esperado):
        actual = self.token_actual()
        if actual == esperado:
            self.posicion += 1
        else:
            self.reportar_error([esperado])

    def reportar_error(self, esperados):
        if self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            partes = token.strip("<>").split(",")

            tipo = partes[0].strip()
            if len(partes) == 4:
                lexema = partes[1].strip()
                linea = partes[2].strip()
                columna = partes[3].strip()
            elif len(partes) == 3:
                lexema = partes[0].strip()
                linea = partes[1].strip()
                columna = partes[2].strip()
            else:
                lexema = tipo
                linea = "?"
                columna = "?"

            mensaje = f"<{linea},{columna}> Error sintactico: se encontro: \"{lexema}\"; se esperaba: {', '.join(f'\"{e}\"' for e in esperados)}."
        else:
            mensaje = "Error sintactico: fin inesperado del archivo."

        with open(self.archivo_salida, "w", encoding="utf-8") as f:
            f.write(mensaje)
        print(mensaje)
        exit(1)

    # ------------------------------------------
    def analizar(self, archivo_py):
        archivo_lex = AnalizadorLexicoAFD.analizarlexico(archivo_py)
        if not archivo_lex:
            return

        with open(archivo_lex, "r", encoding="utf-8") as f:
            self.tokens = [linea.strip() for linea in f if linea.strip()]


        self.archivo_salida = archivo_py + ".txt"

        try:
            self.programa()
        except SystemExit:
            pass

        with open(self.archivo_salida, "w", encoding="utf-8") as out:
            if self.error_sintactico:
                out.write(self.error_sintactico + "\n")
            else:
                out.write("El analisis sintactico ha finalizado exitosamente.\n")

        print(f"📄 Resultado del análisis sintáctico guardado en: {self.archivo_salida}")

if __name__ == "__main__":
    archivo = input("Ingrese el archivo .py a analizar:\n")
    analizador = AnalizadorSintactico()
    analizador.analizar(archivo)
