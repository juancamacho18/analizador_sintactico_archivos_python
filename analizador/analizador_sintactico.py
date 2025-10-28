from analizador_lexico_AFD import AnalizadorLexicoAFD

class AnalizadorSintactico:
    def __init__(self):
        self.tokens = []
        self.posicion = 0
        self.error_sintactico = None
        self.archivo_salida = None

        # Gramática de Python
        self.gramatica = {
            # Programa principal
            "programa": [["sentencias"]],
            "sentencias": [["sentencia", "sentencias"], ["ε"]],
            
            # Tipos de sentencias
            "sentencia": [
                ["def_funcion"],
                ["def_clase"],
                ["sentencia_if"],
                ["sentencia_for"],
                ["sentencia_while"],
                ["sentencia_with"],
                ["sentencia_try"],
                ["sentencia_import"],
                ["sentencia_from"],
                ["sentencia_return"],
                ["sentencia_break"],
                ["sentencia_continue"],
                ["asignacion"],
                ["expresion"],
                ["ε"]
            ],
            
            # Definiciones
            "def_funcion": [["def", "id", "tk_par_izq", "parametros", "tk_par_der", "tk_dos_puntos", "bloque"]],
            "def_clase": [["class", "id", "herencia", "tk_dos_puntos", "bloque"]],
            "herencia": [["tk_par_izq", "id", "tk_par_der"], ["ε"]],
            "parametros": [["id", "mas_parametros"], ["ε"]],
            "mas_parametros": [["tk_coma", "id", "mas_parametros"], ["ε"]],
            
            # Control de flujo
            "sentencia_if": [["if", "expresion", "tk_dos_puntos", "bloque", "elifs", "else_opt"]],
            "elifs": [["elif", "expresion", "tk_dos_puntos", "bloque", "elifs"], ["ε"]],
            "else_opt": [["else", "tk_dos_puntos", "bloque"], ["ε"]],
            
            "sentencia_for": [["for", "id", "in", "expresion", "tk_dos_puntos", "bloque"]],
            "sentencia_while": [["while", "expresion", "tk_dos_puntos", "bloque"]],
            "sentencia_with": [["with", "expresion_with", "tk_dos_puntos", "bloque"]],
            "expresion_with": [["open", "tk_par_izq", "expresion", "tk_par_der"], ["expresion"]],
            
            # Try/Except/Finally
            "sentencia_try": [["try", "tk_dos_puntos", "bloque", "excepts", "else_opt", "finally_opt"]],
            "excepts": [["except", "except_expr", "tk_dos_puntos", "bloque", "excepts"], ["ε"]],
            "except_expr": [["expresion"], ["ε"]],
            "finally_opt": [["finally", "tk_dos_puntos", "bloque"], ["ε"]],
            
            # Sentencias de importación
            "sentencia_import": [["import", "id"]],
            "sentencia_from": [["from", "id", "import", "id"]],
            
            # Otras sentencias
            "sentencia_return": [["return", "expresion_opt"]],
            "sentencia_break": [["break"]],
            "sentencia_continue": [["continue"]],
            
            "expresion_opt": [["expresion"], ["ε"]],
            "asignacion": [["id", "tk_asignar", "expresion"]],
            
            # Expresiones con operadores lógicos y de comparación
            "expresion": [["expr_or"]],
            "expr_or": [["expr_and", "expr_or_prime"]],
            "expr_or_prime": [["or", "expr_and", "expr_or_prime"], ["ε"]],
            "expr_and": [["expr_not", "expr_and_prime"]],
            "expr_and_prime": [["and", "expr_not", "expr_and_prime"], ["ε"]],
            "expr_not": [["not", "expr_comparacion"], ["expr_comparacion"]],
            "expr_comparacion": [["expr_aritmetica", "expr_comp_prime"]],
            "expr_comp_prime": [["op_comp", "expr_aritmetica", "expr_comp_prime"], ["ε"]],
            "op_comp": [["tk_menor"], ["tk_mayor"], ["tk_menor_igual"], ["tk_mayor_igual"], 
                       ["tk_igual"], ["tk_distinto"]],
            
            # Expresiones aritméticas
            "expr_aritmetica": [["termino", "expr_arit_prime"]],
            "expr_arit_prime": [["tk_suma", "termino", "expr_arit_prime"], 
                               ["tk_resta", "termino", "expr_arit_prime"], ["ε"]],
            "termino": [["factor", "termino_prime"]],
            "termino_prime": [["tk_multi", "factor", "termino_prime"], 
                             ["tk_div", "factor", "termino_prime"], ["ε"]],
            "factor": [
                ["id", "sufijos"],
                ["tk_entero"],
                ["tk_string"],
                ["tk_par_izq", "expresion", "tk_par_der"]
            ],
            
            "sufijos": [["sufijo", "sufijos"], ["ε"]],
            "sufijo": [
                ["tk_par_izq", "argumentos", "tk_par_der"],
                ["tk_cor_izq", "expresion", "tk_cor_der"]
            ],
            
            "argumentos": [["expresion", "mas_args"], ["ε"]],
            "mas_args": [["tk_coma", "expresion", "mas_args"], ["ε"]],
            
            "bloque": [["sentencia", "sentencias"]],
        }

        self.terminales = {t for reglas in self.gramatica.values() for prod in reglas for t in prod 
                          if t.islower() or t.startswith("tk_")}
        self.primero = self.calcular_primeros()
        self.siguiente = self.calcular_siguientes("programa")
        self.predicciones = self.calcular_predicciones()

    # ==================== CÁLCULOS DE GRAMÁTICA ====================
    def calcular_primeros(self):
        primero = {}
        for terminal in self.terminales.union({"ε"}):
            primero[terminal] = {terminal}

        def obtener_primero(simbolo):
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

    # ==================== UTILIDADES ====================
    def token_actual(self):
        if self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            return token.strip("<>").split(",")[0].strip()
        return "$"

    def obtener_info_token(self):
        """Obtiene información completa del token actual"""
        if self.posicion < len(self.tokens):
            token = self.tokens[self.posicion]
            partes = token.strip("<>").split(",")
            
            if len(partes) == 4:
                return {
                    'tipo': partes[0].strip(),
                    'lexema': partes[1].strip(),
                    'linea': partes[2].strip(),
                    'columna': partes[3].strip()
                }
            elif len(partes) == 3:
                return {
                    'tipo': partes[0].strip(),
                    'lexema': partes[0].strip(),
                    'linea': partes[1].strip(),
                    'columna': partes[2].strip()
                }
        return {'tipo': '$', 'lexema': '', 'linea': '?', 'columna': '?'}

    def match(self, esperado):
        actual = self.token_actual()
        if actual == esperado:
            self.posicion += 1
        else:
            self.reportar_error([esperado])

    def convertir_token_legible(self, token):
        """Convierte tokens internos a símbolos legibles"""
        mapeo = {
            'tk_par_izq': '(',
            'tk_par_der': ')',
            'tk_cor_izq': '[',
            'tk_cor_der': ']',
            'tk_llave_izq': '{',
            'tk_llave_der': '}',
            'tk_coma': ',',
            'tk_dos_puntos': ':',
            'tk_punto': '.',
            'tk_suma': '+',
            'tk_resta': '-',
            'tk_multi': '*',
            'tk_div': '/',
            'tk_asignar': '=',
            'tk_igual': '==',
            'tk_distinto': '!=',
            'tk_menor': '<',
            'tk_mayor': '>',
            'tk_menor_igual': '<=',
            'tk_mayor_igual': '>=',
        }
        return mapeo.get(token, token)

    def reportar_error(self, esperados):
        info = self.obtener_info_token()
        lexema = info['lexema'] if info['lexema'] else info['tipo']
        linea = info['linea']
        columna = info['columna']
        
        esperados_legibles = [self.convertir_token_legible(e) for e in esperados]
        esperados_formateados = ', '.join(f'"{e}"' for e in esperados_legibles)
        mensaje = f"<{linea},{columna}> Error sintactico: se encontro: \"{lexema}\"; se esperaba: {esperados_formateados}."
        
        with open(self.archivo_salida, "w", encoding="utf-8") as f:
            f.write(mensaje)
        print(mensaje)
        exit(1)

    def reportar_error_indentacion(self):
        info = self.obtener_info_token()
        linea = info['linea']
        columna = info['columna']
        mensaje = f"<{linea},{columna}>Error sintactico: falla de indentacion"
        
        with open(self.archivo_salida, "w", encoding="utf-8") as f:
            f.write(mensaje)
        print(mensaje)
        exit(1)

    # ==================== MÉTODOS DE PARSING ====================
    def programa(self):
        # programa -> sentencias
        self.sentencias()
        if self.token_actual() != '$':
            self.reportar_error(['fin de archivo'])

    def sentencias(self):
        # sentencias -> sentencia sentencias | ε
        tk = self.token_actual()
        tokens_inicio = {'def', 'class', 'if', 'for', 'while', 'with', 'try', 'import', 'from',
                        'return', 'break', 'continue', 'id', 'tk_entero', 'tk_string', 'tk_par_izq', 'not'}
        
        if tk in tokens_inicio:
            self.sentencia()
            self.sentencias()
        # else: ε

    def sentencia(self):
        # Detecta y procesa el tipo de sentencia
        tk = self.token_actual()
        
        if tk == 'def':
            self.def_funcion()
        elif tk == 'class':
            self.def_clase()
        elif tk == 'if':
            self.sentencia_if()
        elif tk == 'for':
            self.sentencia_for()
        elif tk == 'while':
            self.sentencia_while()
        elif tk == 'with':
            self.sentencia_with()
        elif tk == 'try':
            self.sentencia_try()
        elif tk == 'import':
            self.sentencia_import()
        elif tk == 'from':
            self.sentencia_from()
        elif tk == 'return':
            self.sentencia_return()
        elif tk == 'break':
            self.match('break')
        elif tk == 'continue':
            self.match('continue')
        elif tk == 'id':
            # Puede ser asignación o expresión
            pos_guardada = self.posicion
            self.match('id')
            if self.token_actual() == 'tk_asignar':
                # Es asignación
                self.match('tk_asignar')
                self.expresion()
            else:
                # Es expresión, retroceder y procesarla completa
                self.posicion = pos_guardada
                self.expresion()
        else:
            # Expresión
            self.expresion()

    # ==================== DEFINICIONES ====================
    def def_funcion(self):
        # def id(parametros): bloque
        self.match('def')
        self.match('id')
        self.match('tk_par_izq')
        self.parametros()
        self.match('tk_par_der')
        self.match('tk_dos_puntos')
        self.bloque()

    def def_clase(self):
        # class id[(id)]: bloque
        self.match('class')
        self.match('id')
        self.herencia()
        self.match('tk_dos_puntos')
        self.bloque()

    def herencia(self):
        # (id) | ε
        if self.token_actual() == 'tk_par_izq':
            self.match('tk_par_izq')
            self.match('id')
            self.match('tk_par_der')

    def parametros(self):
        # id, id, ... | ε
        if self.token_actual() == 'id':
            self.match('id')
            self.mas_parametros()

    def mas_parametros(self):
        # , id mas_parametros | ε
        if self.token_actual() == 'tk_coma':
            self.match('tk_coma')
            self.match('id')
            self.mas_parametros()

    # ==================== CONTROL DE FLUJO ====================
    def sentencia_if(self):
        # if expresion: bloque [elif expresion: bloque]* [else: bloque]
        self.match('if')
        self.expresion()
        self.match('tk_dos_puntos')
        self.bloque()
        self.elifs()
        self.else_opt()

    def elifs(self):
        # elif expresion: bloque elifs | ε
        if self.token_actual() == 'elif':
            self.match('elif')
            self.expresion()
            self.match('tk_dos_puntos')
            self.bloque()
            self.elifs()

    def else_opt(self):
        # else: bloque | ε
        if self.token_actual() == 'else':
            self.match('else')
            self.match('tk_dos_puntos')
            self.bloque()

    def sentencia_for(self):
        # for id in expresion: bloque
        self.match('for')
        self.match('id')
        self.match('in')
        self.expresion()
        self.match('tk_dos_puntos')
        self.bloque()

    def sentencia_while(self):
        # while expresion: bloque
        self.match('while')
        self.expresion()
        self.match('tk_dos_puntos')
        self.bloque()

    def sentencia_with(self):
        # with expresion: bloque
        self.match('with')
        # Puede ser 'open(...)' o una expresión normal
        if self.token_actual() == 'open':
            self.match('open')
            self.match('tk_par_izq')
            self.expresion()
            self.match('tk_par_der')
        else:
            self.expresion()
        self.match('tk_dos_puntos')
        self.bloque()

    # ==================== TRY/EXCEPT/FINALLY ====================
    def sentencia_try(self):
        # try: bloque except [expresion]: bloque [else: bloque] [finally: bloque]
        self.match('try')
        self.match('tk_dos_puntos')
        self.bloque()
        self.excepts()
        self.else_opt()
        self.finally_opt()

    def excepts(self):
        # except [expresion]: bloque excepts | ε
        if self.token_actual() == 'except':
            self.match('except')
            self.except_expr()
            self.match('tk_dos_puntos')
            self.bloque()
            self.excepts()

    def except_expr(self):
        # expresion | ε
        tk = self.token_actual()
        if tk in ['id', 'tk_entero', 'tk_string', 'tk_par_izq', 'not']:
            self.expresion()

    def finally_opt(self):
        # finally: bloque | ε
        if self.token_actual() == 'finally':
            self.match('finally')
            self.match('tk_dos_puntos')
            self.bloque()

    # ==================== IMPORTACIONES ====================
    def sentencia_import(self):
        # import id
        self.match('import')
        self.match('id')

    def sentencia_from(self):
        # from id import id
        self.match('from')
        self.match('id')
        self.match('import')
        self.match('id')

    # ==================== OTRAS SENTENCIAS ====================
    def sentencia_return(self):
        # return [expresion]
        self.match('return')
        self.expresion_opt()

    def expresion_opt(self):
        # expresion | ε
        tk = self.token_actual()
        if tk in ['id', 'tk_entero', 'tk_string', 'tk_par_izq', 'not']:
            self.expresion()

    # ==================== EXPRESIONES CON OPERADORES LÓGICOS ====================
    def expresion(self):
        # expresion -> expr_or
        self.expr_or()

    def expr_or(self):
        # expr_or -> expr_and expr_or_prime
        self.expr_and()
        self.expr_or_prime()

    def expr_or_prime(self):
        # expr_or_prime -> or expr_and expr_or_prime | ε
        if self.token_actual() == 'or':
            self.match('or')
            self.expr_and()
            self.expr_or_prime()

    def expr_and(self):
        # expr_and -> expr_not expr_and_prime
        self.expr_not()
        self.expr_and_prime()

    def expr_and_prime(self):
        # expr_and_prime -> and expr_not expr_and_prime | ε
        if self.token_actual() == 'and':
            self.match('and')
            self.expr_not()
            self.expr_and_prime()

    def expr_not(self):
        # expr_not -> not expr_comparacion | expr_comparacion
        if self.token_actual() == 'not':
            self.match('not')
            self.expr_comparacion()
        else:
            self.expr_comparacion()

    def expr_comparacion(self):
        # expr_comparacion -> expr_aritmetica expr_comp_prime
        self.expr_aritmetica()
        self.expr_comp_prime()

    def expr_comp_prime(self):
        # expr_comp_prime -> op_comp expr_aritmetica expr_comp_prime | ε
        tk = self.token_actual()
        if tk in ['tk_menor', 'tk_mayor', 'tk_menor_igual', 'tk_mayor_igual',
                  'tk_igual', 'tk_distinto']:
            self.match(tk)
            self.expr_aritmetica()
            self.expr_comp_prime()

    # ==================== EXPRESIONES ARITMÉTICAS ====================
    def expr_aritmetica(self):
        # expr_aritmetica -> termino expr_arit_prime
        self.termino()
        self.expr_arit_prime()

    def expr_arit_prime(self):
        # expr_arit_prime -> + termino expr_arit_prime | - termino expr_arit_prime | ε
        tk = self.token_actual()
        if tk == 'tk_suma':
            self.match('tk_suma')
            self.termino()
            self.expr_arit_prime()
        elif tk == 'tk_resta':
            self.match('tk_resta')
            self.termino()
            self.expr_arit_prime()

    def termino(self):
        # termino -> factor termino_prime
        self.factor()
        self.termino_prime()

    def termino_prime(self):
        # termino_prime -> * factor termino_prime | / factor termino_prime | ε
        tk = self.token_actual()
        if tk == 'tk_multi':
            self.match('tk_multi')
            self.factor()
            self.termino_prime()
        elif tk == 'tk_div':
            self.match('tk_div')
            self.factor()
            self.termino_prime()
        # else: ε

    def factor(self):
        # factor -> id sufijos | numero | string | (expresion)
        tk = self.token_actual()
        
        if tk == 'id':
            self.match('id')
            self.sufijos()
        elif tk == 'tk_entero':
            self.match('tk_entero')
        elif tk == 'tk_string':
            self.match('tk_string')
        elif tk == 'tk_par_izq':
            self.match('tk_par_izq')
            self.expresion()
            self.match('tk_par_der')
        else:
            self.reportar_error(['id', 'tk_entero', 'tk_string', '('])

    def sufijos(self):
        # sufijos -> sufijo sufijos | ε
        tk = self.token_actual()
        if tk in ['tk_par_izq', 'tk_cor_izq']:
            self.sufijo()
            self.sufijos()

    def sufijo(self):
        # sufijo -> (argumentos) | [expresion]
        tk = self.token_actual()
        if tk == 'tk_par_izq':
            # Llamada a función
            self.match('tk_par_izq')
            self.argumentos()
            self.match('tk_par_der')
        elif tk == 'tk_cor_izq':
            # Indexación
            self.match('tk_cor_izq')
            self.expresion()
            self.match('tk_cor_der')

    def argumentos(self):
        # argumentos -> expresion mas_args | ε
        tk = self.token_actual()
        if tk in ['id', 'tk_entero', 'tk_string', 'tk_par_izq', 'not']:
            self.expresion()
            self.mas_args()

    def mas_args(self):
        # mas_args -> , expresion mas_args | ε
        if self.token_actual() == 'tk_coma':
            self.match('tk_coma')
            self.expresion()
            self.mas_args()

    # ==================== BLOQUES ====================
    def bloque(self):
        # bloque -> sentencia sentencias (con verificación de indentación)
        if not self.verificar_bloque_indentado():
            self.reportar_error_indentacion()
        self.sentencia()
        self.sentencias()
    
    def verificar_bloque_indentado(self):
        # Verifica si el bloque tiene indentación correcta
        if self.posicion >= len(self.tokens):
            return False
        
        info_actual = self.obtener_info_token()
        
        if self.posicion == 0:
            return True
        
        # Obtener token anterior
        token_anterior = self.tokens[self.posicion - 1].strip("<>").split(",")
        
        # Si el token anterior era ':', verificar indentación
        if len(token_anterior) >= 3:
            tipo_anterior = token_anterior[0].strip()
            if tipo_anterior == 'tk_dos_puntos':
                # Obtener línea anterior
                if len(token_anterior) == 4:
                    linea_anterior = int(token_anterior[2].strip())
                elif len(token_anterior) == 3:
                    linea_anterior = int(token_anterior[1].strip())
                else:
                    return True
                
                linea_actual = int(info_actual['linea'])
                columna_actual = int(info_actual['columna'])
                
                # Si es la misma línea, está bien (sentencia en línea)
                if linea_actual == linea_anterior:
                    return True
                
                # Si es nueva línea, debe tener indentación
                columna_inicio_bloque = self.buscar_columna_inicio_bloque()
                
                if columna_actual <= columna_inicio_bloque:
                    return False
        
        return True
    
    def buscar_columna_inicio_bloque(self):
        # Busca la columna donde inicia el bloque actual
        pos = self.posicion - 1
        while pos >= 0:
            token = self.tokens[pos].strip("<>").split(",")
            tipo = token[0].strip()
            
            if tipo in ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'with', 'try', 'except', 'finally']:
                if len(token) == 4:
                    return int(token[3].strip())
                elif len(token) == 3:
                    return int(token[2].strip())
            pos -= 1
        
        return 1

    # ==================== ANÁLISIS PRINCIPAL ====================
    def analizar(self, archivo_py):
        # Primero ejecutar análisis léxico
        try:
            with open(archivo_py, 'r', encoding='utf-8') as f:
                codigo_leido = f.read()
            
            analizador_lexico = AnalizadorLexicoAFD(codigo_leido)
            tokens, errores = analizador_lexico.analizar()
            
            if errores:
                print("Errores léxicos encontrados:")
                for error in errores:
                    print(error)
                return
            
            # Guardar tokens en archivo .lex
            archivo_lex = archivo_py + '.lex'
            with open(archivo_lex, 'w', encoding='utf-8') as f:
                for token in tokens:
                    f.write(token + '\n')
        
        except FileNotFoundError:
            print(f"Error: no se pudo encontrar el archivo {archivo_py}")
            return
        except Exception as e:
            print(f"Error inesperado en análisis léxico: {str(e)}")
            return

        # Leer tokens del archivo .lex
        with open(archivo_lex, "r", encoding="utf-8") as f:
            self.tokens = [linea.strip() for linea in f if linea.strip()]

        self.archivo_salida = archivo_py + ".txt"

        try:
            self.programa()
            # Si llegamos aquí, el análisis fue exitoso
            with open(self.archivo_salida, "w", encoding="utf-8") as f:
                f.write("El analisis sintactico ha finalizado exitosamente.\n")
            print("✅ El analisis sintactico ha finalizado exitosamente.")
            print(f"📄 Resultado guardado en: {self.archivo_salida}")
        except SystemExit:
            # Ya se reportó el error
            pass

if __name__ == "__main__":
    archivo = input("Ingrese el archivo .py a analizar: ")
    analizador = AnalizadorSintactico()
    analizador.analizar(archivo)
