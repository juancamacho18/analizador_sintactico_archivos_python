from analizador_lexico_AFD import AnalizadorLexicoAFD

class AnalizadorSintactico:
    def __init__(self):
        self.tokens=[]
        self.posicion=0
        self.error_sintactico=None
        self.archivo_salida=None 
        self.gramatica={
            #programa principal
            "programa": [["sentencias"]],
            "sentencias": [["sentencia", "sentencias"], ["ε"]],
            
            #sentencias
            "sentencia": [
                ["def_funcion"],
                ["sentencia_if"],
                ["sentencia_for"],
                ["sentencia_while"],
                ["sentencia_return"],
                ["sentencia_break"],
                ["sentencia_continue"],
                ["expresion"],
                ["asignacion"],
            ],
            
            #definiciones
            "def_funcion": [["def", "id", "tk_par_izq", "parametros", "tk_par_der", "tk_dos_puntos", "bloque"]],
            "parametros": [["id", "mas_parametros"], ["ε"]],
            "mas_parametros": [["tk_coma", "id", "mas_parametros"], ["ε"]],
            
            #condicionales
            "sentencia_if": [["if", "expresion", "tk_dos_puntos", "bloque", "elifs", "else_opt"]],
            "elifs": [["elif", "expresion", "tk_dos_puntos", "bloque", "elifs"], ["ε"]],
            "else_opt": [["else", "tk_dos_puntos", "bloque"], ["ε"]],
            
            "sentencia_for": [["for", "id", "in", "expresion", "tk_dos_puntos", "bloque"]],
            "sentencia_while": [["while", "expresion", "tk_dos_puntos", "bloque"]],

            #sentencias simples
            "sentencia_return": [["return", "expresion_opt"]],
            "sentencia_break": [["break"]],
            "sentencia_continue": [["continue"]],          
            "expresion_opt": [["expresion"], ["ε"]],
            "asignacion": [["id", "tk_asignar", "expresion"]],
            
            #expresiones logicas y comparativas
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
            
            #expresiones aritmeticas
            "expr_aritmetica": [["termino", "expr_arit_prime"]],
            "expr_arit_prime": [["tk_suma", "termino", "expr_arit_prime"], 
                               ["tk_resta", "termino", "expr_arit_prime"], ["ε"]],
            "termino": [["potencia", "termino_prime"]],
            "potencia": [["factor", "potencia_prime"]],
            "potencia_prime": [["tk_potencia", "factor", "potencia_prime"], ["ε"]],

            "termino_prime": [["tk_multi", "factor", "termino_prime"], 
                             ["tk_div", "factor", "termino_prime"], 
                             ["tk_modulo", "factor", "termino_prime"], ["ε"]],
            "factor": [
                ["id", "sufijos"],
                ["tk_entero"],
                ["tk_string"],
                ["True"],
                ["False"],
                ["tk_par_izq", "expresion", "tk_par_der"],
                ["conversion_tipo"],
                ["llamada_io"]
            ],
            
            "conversion_tipo": [
                ["int", "tk_par_izq", "arg_conversion", "tk_par_der"],
                ["float", "tk_par_izq", "arg_conversion", "tk_par_der"],
                ["str", "tk_par_izq", "arg_conversion", "tk_par_der"],
                ["bool", "tk_par_izq", "arg_conversion", "tk_par_der"]
            ],
            
            "arg_conversion": [
                ["id"],
                ["expresion"]
            ],
            
            "llamada_io": [
                ["input", "tk_par_izq", "argumentos_io", "tk_par_der"],
                ["print", "tk_par_izq", "argumentos_io", "tk_par_der"]
            ],
            "argumentos_io": [
                ["expresion", "mas_args_io"],
                ["tk_string", "mas_args_io"],
                ["ε"]
            ],
            "mas_args_io": [["tk_coma", "argumentos_io"], ["ε"]],

            "sufijos": [["sufijo", "sufijos"], ["ε"]],
            "sufijo": [
                ["tk_par_izq", "argumentos", "tk_par_der"],
                ["tk_cor_izq", "expresion", "tk_cor_der"],
                ["tk_string"]
            ],
            
            "argumentos": [["expresion", "mas_args"], ["ε"]],
            "mas_args": [["tk_coma", "expresion", "mas_args"], ["ε"]],
            
            #manejo bloque
            "bloque": [["sentencia", "sentencias"], ["ε"]],
        }

        todos_simbolos={t for reglas in self.gramatica.values() for prod in reglas for t in prod}
        no_terminales=set(self.gramatica.keys())
        self.terminales=todos_simbolos - no_terminales

        self.primero=self.calcular_primeros()
        self.siguiente=self.calcular_siguientes("programa")
        self.predicciones=self.calcular_predicciones()


    #CALCULO DE CONJUNTOS DE LA GRAMATICA
    def calcular_primeros(self):
        primero={}
        for terminal in self.terminales.union({"ε"}):
            primero[terminal]={terminal}

        def obtener_primero(simbolo):
            if simbolo in primero and primero[simbolo]:
                return primero[simbolo]
            primero[simbolo]=set()
            for produccion in self.gramatica.get(simbolo, []):
                for s in produccion:
                    primeros_s=obtener_primero(s)
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
        siguiente={nt: set() for nt in self.gramatica}
        siguiente[simbolo_inicial].add("$")
        cambiado=True
        while cambiado:
            cambiado=False
            for nt in self.gramatica:
                for produccion in self.gramatica[nt]:
                    for i, simbolo in enumerate(produccion):
                        if simbolo in self.gramatica:
                            resto=produccion[i + 1:]
                            antes=len(siguiente[simbolo])
                            if resto:
                                primero_resto=set()
                                for s in resto:
                                    primeros_s=self.primero[s]
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
                                cambiado=True
        return siguiente

    def calcular_predicciones(self):
        pred={}
        for nt in self.gramatica:
            for prod in self.gramatica[nt]:
                regla=f"{nt} -> {' '.join(prod)}"
                conjunto=set()
                for s in prod:
                    primeros_s=self.primero[s]
                    conjunto.update(primeros_s - {"ε"})
                    if "ε" not in primeros_s:
                        break
                else:
                    conjunto.add("ε")
                pred[regla]=conjunto - {"ε"}
                if "ε" in conjunto:
                    pred[regla].update(self.siguiente[nt])
        return pred

    #USOS
    def token_actual(self):
        if self.posicion<len(self.tokens):
            token=self.tokens[self.posicion]
            return token.strip("<>").split(",")[0].strip()
        return "$"

    def ver_siguiente_token(self):
        if self.posicion+1 < len(self.tokens):
            token=self.tokens[self.posicion + 1]
            return token.strip("<>").split(",")[0].strip()
        return "$"
    
    def ver_anterior_token(self):
        if self.posicion - 1 >= 0 and self.posicion - 1 < len(self.tokens):
            token = self.tokens[self.posicion - 1]
            partes = token.strip("<>").split(",")

            if len(partes) == 4:
                tipo, lexema, linea, columna = partes
            elif len(partes) == 3:
                tipo, linea, columna = partes
                lexema = ""
            else:
                # Token vacío o corrupto
                return None

            try:
                linea = int(linea)
                columna = int(columna)
            except:
                linea, columna = 0, 0

            return {
                "tipo": tipo.strip(),
                "lexema": lexema.strip(),
                "linea": linea,
                "columna": columna
            }
        return None
    
    def obtener_info_token(self):
        if self.posicion < len(self.tokens):
            token=self.tokens[self.posicion]
            partes=token.strip("<>").split(",")
            
            if len(partes)==4:
                return {
                    'tipo': partes[0].strip(),
                    'lexema': partes[1].strip(),
                    'linea': int(partes[2].strip()),
                    'columna': int(partes[3].strip())
                }
            elif len(partes)==3:
                return {
                    'tipo': partes[0].strip(),
                    'lexema': partes[0].strip(),
                    'linea': int(partes[1].strip()),
                    'columna': int(partes[2].strip())
                }
        return {'tipo': '$', 'lexema': '', 'linea': '?', 'columna': '?'}

    def emparejar(self, esperado):
        actual=self.token_actual()
        if actual==esperado:
            self.posicion+=1
        else:
            self.reportar_error([esperado])

    def convertir_token_legible(self, token):
        mapeo={
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
            'tk_modulo': '%',
            'tk_potencia': '**',
            'tk_string_incompleto': 'cadena sin cerrar',
            'tk_entero': 'numero entero',
            'tk_float': 'numero decimal',
            'tk_string': 'cadena',
        }
        return mapeo.get(token, token)

    #REPORTE DE ERRORES
    def reportar_error(self, esperados):
        info = self.obtener_info_token()
        lexema = info['lexema'] if info['lexema'] else info['tipo']

        anterior = self.ver_anterior_token()

        linea = info['linea']
        columna = info['columna']

        
        if anterior and info['linea'] > anterior['linea']:
            linea = anterior['linea']
            columna = anterior['columna'] + len(anterior['lexema'])
        
        if self.token_actual() == 'tk_string_incompleto' or info.get('tipo') == 'tk_string_incompleto':
            esperados = ['tk_string']
            
        encontrado=self.convertir_token_legible(lexema)
        esperados_legibles=[self.convertir_token_legible(e) for e in esperados]
        esperados_formateados= ', '.join(f'"{e}"' for e in esperados_legibles)
        mensaje = f"<{linea},{columna}> Error sintactico: se encontro: \"{encontrado}\"; se esperaba: {esperados_formateados}."
        with open(self.archivo_salida, "w", encoding="utf-8") as f:
            f.write(mensaje)
        print(mensaje)
        exit(1)

    def reportar_error_indentacion(self):
        info=self.obtener_info_token()
        linea=info['linea']
        columna=info['columna']
        mensaje= f"<{linea},{columna}> Error sintactico: falla de indentacion"
        
        with open(self.archivo_salida, "w", encoding="utf-8") as f:
            f.write(mensaje)
        print(mensaje)
        exit(1)

    def predicciones_clave(self, nombre_no_terminal):
        esperados=set()
        for produccion, pred in self.predicciones.items():
            if produccion.startswith(nombre_no_terminal + " ->"):
                esperados |= pred
        
        if not esperados and nombre_no_terminal in self.siguiente:
            esperados=set(self.siguiente[nombre_no_terminal])
        return esperados


    def aplicar_produccion(self, nombre_no_terminal):
        tk=self.token_actual()
        for produccion, pred in self.predicciones.items():
            if produccion.startswith(nombre_no_terminal + " ->") and tk in pred:
                derecha=produccion.split("->")[1].strip().split()
                if derecha==['ε']:
                    return

                for simbolo in derecha:
                    if simbolo in self.gramatica:  
                        getattr(self, simbolo)()
                    elif simbolo!='ε':
                        self.emparejar(simbolo) 
                return

        if nombre_no_terminal in self.siguiente and tk in self.siguiente[nombre_no_terminal]:
            puede_ser_vacio=any(prod==["ε"] for prod in self.gramatica[nombre_no_terminal])
            if puede_ser_vacio:
                return
        else:
            esperados=list(self.predicciones_clave(nombre_no_terminal))
            self.reportar_error(esperados)


    #METODOS
    def programa(self):
        self.aplicar_produccion('programa')
        if self.token_actual()!='$':
            self.reportar_error(['fin de archivo'])

    def sentencias(self):
        self.aplicar_produccion('sentencias')

    def sentencia(self):
        tk=self.token_actual()
        siguiente=self.ver_siguiente_token()

        if tk=='id' and siguiente=='tk_asignar':
            self.asignacion()
        else:
            self.aplicar_produccion('sentencia')

    def def_funcion(self):
        self.aplicar_produccion('def_funcion')

    def parametros(self):
        self.aplicar_produccion('parametros')

    def mas_parametros(self):
        self.aplicar_produccion('mas_parametros')

    def sentencia_if(self):
        self.aplicar_produccion('sentencia_if')

    def elifs(self):
        self.aplicar_produccion('elifs')

    def else_opt(self):
        self.aplicar_produccion('else_opt')

    def sentencia_for(self):
        self.aplicar_produccion('sentencia_for')

    def sentencia_while(self):
        self.aplicar_produccion('sentencia_while')

    def sentencia_return(self):
        self.aplicar_produccion('sentencia_return')

    def sentencia_break(self):
        self.aplicar_produccion('sentencia_break')

    def sentencia_continue(self):
        self.aplicar_produccion('sentencia_continue')

    def expresion_opt(self):
        self.aplicar_produccion('expresion_opt')
    
    def asignacion(self):
        self.aplicar_produccion('asignacion')

    def expresion(self):
        self.aplicar_produccion('expresion')

    def expr_or(self):
        self.aplicar_produccion('expr_or')

    def expr_or_prime(self):
        self.aplicar_produccion('expr_or_prime')

    def expr_and(self):
        self.aplicar_produccion('expr_and')

    def expr_and_prime(self):
        self.aplicar_produccion('expr_and_prime')

    def expr_not(self):
        self.aplicar_produccion('expr_not')

    def expr_comparacion(self):
        self.aplicar_produccion('expr_comparacion')

    def expr_comp_prime(self):
        tk = self.token_actual()
        comparadores = {
            'tk_menor', 'tk_mayor', 'tk_menor_igual',
            'tk_mayor_igual', 'tk_igual', 'tk_distinto'
        }

        if tk in comparadores:
            self.op_comp()
            # verificar que viene algo válido para una expresión
            siguiente = self.token_actual()
            primeros_expr = {
                'id', 'tk_entero', 'tk_string',
                'True', 'False', 'tk_par_izq',
                'int', 'float', 'input', 'print',
                'str', 'bool'
            }

            if siguiente not in primeros_expr:
                # aquí se detecta el caso de '>' sin valor a la derecha
                self.reportar_error(list(primeros_expr))
            self.expr_aritmetica()
            self.expr_comp_prime()
        else:
            return
    
    def op_comp(self):
        self.aplicar_produccion('op_comp')

    def expr_aritmetica(self):
        tk = self.token_actual()
        primeros_validos = {
            'id', 'tk_entero', 'tk_string',
            'True', 'False', 'tk_par_izq',
            'int', 'float', 'input', 'print',
            'str', 'bool'
        }
        if tk not in primeros_validos:
            self.reportar_error(list(primeros_validos))
        self.aplicar_produccion('expr_aritmetica')

    def expr_arit_prime(self):
        self.aplicar_produccion('expr_arit_prime')

    def termino(self):
        self.aplicar_produccion('termino')
    
    def potencia(self):
        self.aplicar_produccion('potencia')
        
    def potencia_prime(self):
        self.aplicar_produccion('potencia_prime')       
    

    def termino_prime(self):
        self.aplicar_produccion('termino_prime')

    def factor(self):
        tk = self.token_actual()
        if tk == "tk_string_incompleto":
            self.reportar_error(['tk_string'])
        else:
            self.aplicar_produccion('factor')

    def conversion_tipo(self):
        self.aplicar_produccion('conversion_tipo')

    def arg_conversion(self):
        self.aplicar_produccion('arg_conversion')
    
    def llamada_io(self):
        self.aplicar_produccion('llamada_io')

    def argumentos_io(self):
        self.aplicar_produccion('argumentos_io')
        
    def mas_args_io(self):
        self.aplicar_produccion('mas_args_io')
    
    def sufijos(self):
        self.aplicar_produccion('sufijos')

    def sufijo(self):
        self.aplicar_produccion('sufijo')

    def argumentos(self):
        self.aplicar_produccion('argumentos')

    def mas_args(self):
        self.aplicar_produccion('mas_args')
    

    #BLOQUES
    def bloque(self):
        if not self.verificar_bloque_indentado():
            self.reportar_error_indentacion()
        self.sentencia()
        self.sentencias()
    
    def verificar_bloque_indentado(self):
        if self.posicion>=len(self.tokens):
            return False
        
        info_actual=self.obtener_info_token()
        
        if self.posicion==0:
            return True
        
        token_anterior=self.tokens[self.posicion - 1].strip("<>").split(",")
        
        if len(token_anterior)>=3:
            tipo_anterior=token_anterior[0].strip()
            if tipo_anterior=='tk_dos_puntos':
                
                if len(token_anterior)==4:
                    linea_anterior=int(token_anterior[2].strip())

                elif len(token_anterior)==3:
                    linea_anterior=int(token_anterior[1].strip())

                else:
                    return True
                
                linea_actual=int(info_actual['linea'])
                columna_actual=int(info_actual['columna'])
                
                if linea_actual==linea_anterior:
                    return True

                columna_inicio_bloque=self.buscar_columna_inicio_bloque()
                
                if columna_actual<=columna_inicio_bloque:
                    return False
        
        return True
    
    def buscar_columna_inicio_bloque(self):
        pos=self.posicion - 1
        while pos>=0:
            token=self.tokens[pos].strip("<>").split(",")
            tipo=token[0].strip()
            
            if tipo in ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'with', 'try', 'except', 'finally']:
                if len(token)==4:
                    return int(token[3].strip())
                elif len(token)==3:
                    return int(token[2].strip())
            pos-=1
        
        return 1


    #MAIN
if __name__=="__main__":
    archivo=input("Ingrese el archivo a analizar: ")
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            codigo_leido=f.read()
            
        analizador_lexico=AnalizadorLexicoAFD(codigo_leido)
        tokens, errores=analizador_lexico.analizar()
            
        if errores:
            print("errores lexicos encontrados:")
            for error in errores:
                print(error)
            exit()

        archivo_lex=archivo+ '.lex'
        with open(archivo_lex, 'w', encoding='utf-8') as f:
            for token in tokens:
                f.write(token + '\n')
       
    except FileNotFoundError:
            print(f"error: no se pudo encontrar el archivo {archivo}")
            exit()

    except Exception as e:
            print(f"error inesperado en analisis lexico: {str(e)}")
            exit()

    with open(archivo_lex, "r", encoding="utf-8") as f:
        tokens=[linea.strip() for linea in f if linea.strip()]

    analizador=AnalizadorSintactico()
    analizador.tokens=tokens
    analizador.archivo_salida=archivo+".txt"

    try:
        analizador.programa()
        with open(analizador.archivo_salida, "w", encoding="utf-8") as f:
            f.write("el analisis sintactico ha finalizado exitosamente.\n")
        print(f"resultado guardado en: '{analizador.archivo_salida}'")
    except SystemExit:
        pass
