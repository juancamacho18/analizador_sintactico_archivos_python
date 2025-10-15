class AnalizadorLexicoAFD:
    def __init__(self, codigo_base):
        self.codigo_base=codigo_base
        self.tokens=[]
        self.linea_actual=1
        self.columna_actual=1
        self.posicion_actual=0
        self.lexema=""
        self.errores=[]
        #todas las palabras reservadas de python
        self.keywords=[
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield',
            'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple', 'object',
            'abs', 'all', 'any', 'ascii', 'bin', 'breakpoint', 'callable',
            'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dir',
            'divmod', 'enumerate', 'eval', 'exec', 'filter', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help',
            'hex', 'id', 'input', 'isinstance', 'issubclass', 'iter', 'len',
            'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object',
            'oct', 'open', 'ord', 'pow', 'print', 'property', 'range',
            'repr', 'reversed', 'round', 'setattr', 'slice', 'sorted',
            'staticmethod', 'sum', 'super', 'type', 'vars', 'zip', '__import__',
            'self'
        ]
        #mapeo de operaciones y simbolos con sus respectivos tokens
        self.operadores={
            '(': 'tk_par_izq',
            ')': 'tk_par_der',
            '[': 'tk_cor_izq',
            ']': 'tk_cor_der',
            '{': 'tk_llave_izq',
            '}': 'tk_llave_der',
            ',': 'tk_coma',
            ':': 'tk_dos_puntos',
            '.': 'tk_punto',
            ';': 'tk_punto_coma',
            '+': 'tk_suma',
            '-': 'tk_resta',
            '*': 'tk_multi',
            '/': 'tk_div',
            '%': 'tk_modulo',
            '=': 'tk_asignar',
            '==': 'tk_igual',
            '!=': 'tk_distinto',
            '<': 'tk_menor',
            '>': 'tk_mayor',
            '<=': 'tk_menor_igual',
            '>=': 'tk_mayor_igual',
            '->': 'tk_ejecuta',
            '**': 'tk_potencia',
            '//': 'tk_div_entera',
            '@': 'tk_arroba',
        }
        self.delta={
            # estado q0
            ("q0", "letra"): ("qID", "iniciar_lexema"),
            ("q0", "digito"): ("qNUM", "iniciar_numero"),
            ("q0", "comilla"): ("qCAD", "iniciar_string"),
            ("q0", "comentario"): ("qCOM", "skip_comentario"),
            ("q0", "espacio"): ("q0", "skip"),
            ("q0", "nueva_linea"): ("q0", "nueva_linea"),
            ("q0", "operador"): ("qOP", "check_operador"),
            ("q0", "otro"): ("qERR", "error"),
            ("q0", "EOF"): ("q0", "final"),
            # estado qID
            ("qID", "letra"): ("qID", "iniciar_lexema"),
            ("qID", "digito"): ("qNUM", "iniciar_numero"),
            ("qID", "comilla"): ("qCAD", "iniciar_string"),
            ("qID", "comentario"): ("qCOM", "skip_comentario"),
            ("qID", "espacio"): ("q0", "skip"),
            ("qID", "nueva_linea"): ("q0", "nueva_linea"),
            ("qID", "operador"): ("qOP", "check_operador"),
            ("qID", "otro"): ("qERR", "error"),
            ("qID", "EOF"): ("qID", "final"),
            # estado qNUM
            ("qNUM", "letra"): ("qID", "iniciar_lexema"),
            ("qNUM", "digito"): ("qNUM", "iniciar_numero"),
            ("qNUM", "comilla"): ("qCAD", "iniciar_string"),
            ("qNUM", "comentario"): ("qCOM", "skip_comentario"),
            ("qNUM", "espacio"): ("q0", "skip"),
            ("qNUM", "nueva_linea"): ("q0", "nueva_linea"),
            ("qNUM", "operador"): ("qOP", "check_operador"),
            ("qNUM", "otro"): ("qERR", "error"),
            ("qNUM", "EOF"): ("qNUM", "final"),
            # estado qCAD
            ("qCAD", "letra"): ("qID", "iniciar_lexema"),
            ("qCAD", "digito"): ("qNUM", "iniciar_numero"),
            ("qCAD", "comilla"): ("qCAD", "iniciar_string"),
            ("qCAD", "comentario"): ("qCOM", "skip_comentario"),
            ("qCAD", "espacio"): ("q0", "skip"),
            ("qCAD", "nueva_linea"): ("q0", "nueva_linea"),
            ("qCAD", "operador"): ("qOP", "check_operador"),
            ("qCAD", "otro"): ("qERR", "error"),
            ("qCAD", "EOF"): ("qCAD", "final"),
            # estado qCOM
            ("qCOM", "letra"): ("qID", "iniciar_lexema"),
            ("qCOM", "digito"): ("qNUM", "iniciar_numero"),
            ("qCOM", "comilla"): ("qCAD", "iniciar_string"),
            ("qCOM", "comentario"): ("qCOM", "skip_comentario"),
            ("qCOM", "espacio"): ("q0", "skip"),
            ("qCOM", "nueva_linea"): ("q0", "nueva_linea"),
            ("qCOM", "operador"): ("qOP", "check_operador"),
            ("qCOM", "otro"): ("qERR", "error"),
            ("qCOM", "EOF"): ("qCOM", "final"),
            # estado q OP
            ("qOP", "letra"): ("qID", "iniciar_lexema"),
            ("qOP", "digito"): ("qNUM", "iniciar_numero"),
            ("qOP", "comilla"): ("qCAD", "iniciar_string"),
            ("qOP", "comentario"): ("qCOM", "skip_comentario"),
            ("qOP", "espacio"): ("q0", "skip"),
            ("qOP", "nueva_linea"): ("q0", "nueva_linea"),
            ("qOP", "operador"): ("qOP", "check_operador"),
            ("qOP", "otro"): ("qERR", "error"),
            ("qOP", "EOF"): ("qOP", "final"),
        }

    def analizar(self):
        estado="q0"
        while True:
            caracter=self.mirar()
            tipo=self.tipo_caracter(caracter)
            nuevo_estado, accion=self.delta.get((estado, tipo), ("qERR", "error"))
            estado_resultado=self.ejecutar_accion(accion, caracter)
            if estado_resultado in ("qERR", "final"):
                break
            estado=nuevo_estado
        return self.tokens, self.errores
    
    def mirar(self, k=0):
        if self.posicion_actual+k<len(self.codigo_base):
            return self.codigo_base[self.posicion_actual+k]
        return None
    
    def tipo_caracter(self, caracter):
        if caracter is None:
            return 'EOF'
        if caracter.isalpha() or caracter=='_':
            return 'letra'
        if caracter.isdigit():
            return 'digito'
        if caracter in ("'", '"'):
            return 'comilla'
        if caracter in (' ', '\t'):
            return 'espacio'
        if caracter=='\n':
            return 'nueva_linea'
        if caracter=='#':
            return 'comentario'
        if caracter in self.operadores or caracter=='!':
            return 'operador'
        return 'otro'
    
    def avance(self, n=1):
        for _ in range(n):
            if self.posicion_actual>=len(self.codigo_base):
                return
            caracter = self.codigo_base[self.posicion_actual]
            self.posicion_actual+=1 
            if caracter=='\n':
                self.linea_actual+=1
                self.columna_actual=1
            else:
                self.columna_actual+=1
                
    def ejecutar_accion(self, accion, caracter):
        if accion=="iniciar_lexema":
            self.lexema=caracter
            self.avance()          
            while self.tipo_caracter(self.mirar()) in ('letra', 'digito'):
                self.lexema+=self.mirar()
                self.avance()            
            if self.lexema in self.keywords:
                self.tokens.append(f"<{self.lexema},{self.linea_actual},{self.columna_actual-len(self.lexema)}>")
            else:
                self.tokens.append(f"<id,{self.lexema},{self.linea_actual},{self.columna_actual-len(self.lexema)}>")
            self.lexema=""

        elif accion=="iniciar_numero":
            self.lexema=caracter
            self.avance()
            while self.tipo_caracter(self.mirar())=='digito':
                self.lexema+=self.mirar()
                self.avance()
            self.tokens.append(f"<tk_entero,{self.lexema},{self.linea_actual},{self.columna_actual-len(self.lexema)}>")
            self.lexema=""

        elif accion=="iniciar_string":
            comilla=caracter
            self.avance()
            #ignorar comentarios ''' ''' o """ """
            if self.mirar()==comilla and self.mirar(1)==comilla:
                self.avance(2)
                while True:
                    char=self.mirar()
                    if char is None:
                        self.errores.append(f">>>error lexico(linea:{self.linea_actual},posicion:{self.columna_actual})")
                        return "qERR"
                    if char==comilla and self.mirar(1)==comilla and self.mirar(2)==comilla:
                        self.avance(3)
                        break
                    self.avance()
                return
            else:
                posicion_inicial=self.posicion_actual
                while True:
                    char=self.mirar()
                    if char is None or char=='\n':
                        self.errores.append(f">>>error lexico(lines:{self.linea_actual},posicion:{self.columna_actual})")
                        return "qERR"
                    if char=='\\':
                        self.avance()
                        if self.mirar() is None:
                            self.errores.append(f">>>error lexico(linea:{self.linea_actual},posicion:{self.columna_actual})")
                            return "qERR"
                        self.avance()
                        continue
                    if char==comilla:
                        self.lexema=self.codigo_base[posicion_inicial:self.posicion_actual]
                        self.tokens.append(f"<tk_string,{self.lexema},{self.linea_actual},{self.columna_actual-len(self.lexema)-1}>")
                        self.lexema=""
                        self.avance()
                        break
                    self.avance()  

        elif accion=="skip":
            self.avance()

        elif accion=="nueva_linea":
            self.avance()

        elif accion=="skip_comentario":
            while self.mirar() not in (None, '\n'):
                self.avance()
            if self.mirar()=='\n':
                self.avance()

        elif accion=="check_operador":
            if caracter in '+-':
                if self.mirar(1) and self.mirar(1).isdigit():
                    self.lexema=caracter
                    self.avance()
                    while self.mirar() and self.mirar().isdigit():
                        self.lexema+=self.mirar()
                        self.avance()
                    self.tokens.append(f"<tk_entero,{self.lexema},{self.linea_actual},{self.columna_actual-len(self.lexema)}>")
                    self.lexema=""
                    return
            dos_operadores=(self.mirar() or '')+(self.mirar(1) or '')
            if dos_operadores in self.operadores:
                self.tokens.append(f"<{self.operadores[dos_operadores]},{self.linea_actual},{self.columna_actual}>")
                self.avance(2)
            elif self.mirar() in self.operadores:
                self.tokens.append(f"<{self.operadores[self.mirar()]},{self.linea_actual},{self.columna_actual}>")
                self.avance()
            else:
                self.errores.append(f">>>error lexico(linea:{self.linea_actual},posicion:{self.columna_actual})")
                return "qERR"
            
        elif accion=="error":
            self.errores.append(f">>>error lexico(linea:{self.linea_actual},posicion:{self.columna_actual})")
            return "qERR"
        
        elif accion=="final":
            return "final" 
    
    #leer archivo  
    def analizarlexico(archivo):
        try:    
            #la r del segundo argumento es el modo de apertura, y el tercero la especificacion de codficacion del texto
            with open(archivo, 'r',encoding='utf-8') as f:
                codigo_leido=f.read()
                    
            analizador=AnalizadorLexicoAFD(codigo_leido)
            tokens, errores=analizador.analizar()
                
            if errores:
                for token in tokens:
                    print(token+'\n')
                print(errores)
                return None
            else:
                #poner los tokens en el archivo a crear
                archivo_salida=archivo+'.lex'
                #'w'=modo escritura
                with open(archivo_salida, 'w', encoding='utf-8') as f:
                    for token in tokens:
                        f.write(token+'\n')
                            
                return archivo_salida
            
        except FileNotFoundError:
            print(f"Error: no se pudo encontrar el archivo {archivo}")
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
        return None