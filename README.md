# Integrantes: Juan Camilo Camacho Mejía y Juan Esteban Martínez Cantero

# analizador_sintactico_archivos_python

Este proyecto implementa un analizador sintáctico LL(1) para una versión simplificada del lenguaje Python.
El objetivo es procesar código fuente, generar una lista de tokens y posteriormente validar su estructura sintáctica con base en una gramática definida.

-  Estructura del proyecto

        ├── analizador_lexico_AFD.py
        ├── analizador_sintactico.py

# Analizador Léxico (analizador_lexico_AFD.py)

El analizador léxico se encarga de recorrer el código fuente carácter por carácter y generar una secuencia de tokens válidos, o reportar errores léxicos en caso de encontrar símbolos desconocidos.

Características principales:

- Basado en un Autómata Finito Determinista (AFD).

- Reconoce identificadores, números, cadenas, palabras reservadas y operadores de Python.

- Soporta comentarios (#) y saltos de línea.

- Detecta errores léxicos con información de línea y columna.

- Genera un archivo de salida con extensión .lex que contiene la lista de tokens.

# Analizador Sintáctico (analizador_sintactico.py)

El analizador sintáctico es el núcleo del proyecto.
Utiliza los tokens producidos por el analizador léxico para validar que la secuencia cumpla con una gramática libre de contexto LL(1).

Principales características

- Implementa una gramática explícita para construcciones comunes de Python:

  - Definiciones de funciones (def).
  
  - Sentencias condicionales (if, elif, else).
  
  - Bucles (for, while).
  
  - Sentencias simples (return, break, continue, asignaciones).
  
  - Expresiones lógicas, aritméticas y comparativas.

- Cálculo automático de los conjuntos:

  - PRIMERO
  
  - SIGUIENTE
  
  - Predicciones (tabla LL(1))

- Soporte básico para bloques indentados, simulando la estructura por tabulación de Python.

- Detección de errores sintácticos detallados, indicando:

  - Línea y columna del error.
  
  - Token encontrado.
  
  - Tokens esperados.

- Salida del análisis:

  - Si hay errores, se guarda el mensaje en <archivo>.txt.
  
  - Si no hay errores, el archivo .txt indica:
  "El análisis sintáctico ha finalizado exitosamente."

# Como Ejecutar

El usuario ejecuta el archivo principal:

    python analizador_sintactico.py

Se solicita el archivo fuente a analizar:

    Ingrese el archivo a analizar: prueba.py

El programa realiza:

  - Análisis léxico: genera prueba.py.lex
  
  - Análisis sintáctico: valida los tokens y genera prueba.py.txt

Resultado:

- Si no hay errores →
  prueba.py.txt contendrá:
  
      El análisis sintáctico ha finalizado exitosamente.


- Si hay errores →
  Se detallará el tipo de error y su ubicación:

      <5,12> Error sintactico: se encontro: ":"; se esperaba: "=".

- Estructura interna del analizador sintáctico:

      Componente                          Descripción
      gramatica	                         Diccionario con todas las producciones del lenguaje.
      calcular_primeros()	                Genera los conjuntos PRIMERO de la gramática.
      calcular_siguientes()	             Genera los conjuntos SIGUIENTE.
      calcular_predicciones()	            Calcula la tabla de predicción LL(1).
      aplicar_produccion()	             Aplica la regla correspondiente según el token actual.
      emparejar()	                        Verifica y consume tokens esperados.
      reportar_error()	                 Escribe los errores sintácticos en el archivo de salida.
      verificar_bloque_indentado()	     Comprueba la indentación de bloques (if, for, def, etc.).
