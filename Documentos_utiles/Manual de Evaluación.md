# Métricas de Evaluación y Rúbrica de Puntuación
### Escala Likert 1-5

Este manual establece los criterios estándar para la evaluación de respuestas generadas por el sistema.

---

## 1. Faithfulness (Veracidad Factual)
**Pregunta Guía:** ¿La respuesta se adhiere estricta y únicamente a la información presente en los datos de origen (`dato_recuperado`)?

* **5 (Perfecta):** La respuesta es un resumen perfecto de la información de la fuente. Todos los datos, cifras y afirmaciones se derivan directamente de la fuente.
* **4 (Menor Extrapolación):** La respuesta introduce alguna afirmación plausible o de sentido común que no está explícitamente en la fuente, pero no la contradice y enriquece la explicación.
* **3 (Extrapolación Significativa):** La respuesta añade información relevante que no está en la fuente. No es una contradicción directa, pero el sistema está "inventando" contexto.
* **2 (Contradicción Menor):** La respuesta contiene al menos una afirmación o dato que contradice sutilmente la información de la fuente.
* **1 (Contradicción Grave):** La respuesta inventa datos numéricos clave o hace afirmaciones que contradicen directamente y de forma grave la información de la fuente. Es una alucinación clara.

---

## 2. Relevance (Relevancia)
**Pregunta Guía:** ¿La respuesta aborda de forma directa y completa la pregunta del usuario?

* **5 (Totalmente Relevante):** La respuesta contesta directamente a todas las partes de la pregunta del usuario de forma concisa y completa.
* **4 (Mayormente Relevante):** La respuesta contesta la pregunta principal, pero puede omitir un matiz o un aspecto secundario de la misma.
* **3 (Parcialmente Relevante):** La respuesta aborda el tema general de la pregunta pero no contesta directamente a la cuestión específica planteada.
* **2 (Ligeramente Relevante):** La respuesta contiene información relacionada con el tema de la pregunta, pero falla completamente en contestarla.
* **1 (Irrelevante):** La respuesta no tiene ninguna relación con la pregunta formulada.

---

## 3. Fluency (Fluidez Lingüística)
**Pregunta Guía:** ¿La respuesta está escrita en un español gramaticalmente correcto y natural?

* **5 (Perfecta):** El texto no tiene errores gramaticales, de puntuación o de tipeo. Se lee de forma natural y fluida.
* **4 (Errores Menores):** Contiene uno o dos errores menores (ej. un acento faltante, un error de tipeo) que no afectan a la comprensión.
* **3 (Errores Notables):** Contiene varios errores gramaticales o frases extrañas que hacen la lectura un poco difícil, pero el significado general sigue siendo comprensible.
* **2 (Errores Graves):** Los errores gramaticales y de sintaxis son tan frecuentes que dificultan seriamente la comprensión del texto.
* **1 (Ininteligible):** El texto es un conjunto de palabras sin sentido gramatical.

---

## 4. Coherence (Coherencia)
**Pregunta Guía:** ¿Las ideas de la respuesta están organizadas de forma lógica y fluyen bien entre sí?

* **5 (Muy Coherente):** La respuesta está perfectamente estructurada. Las ideas se presentan en un orden lógico, y las transiciones entre frases y párrafos son suaves.
* **4 (Coherente):** La estructura general es lógica, aunque alguna transición podría ser más fluida.
* **3 (Parcialmente Coherente):** Se puede seguir el hilo argumental, pero hay saltos lógicos o ideas desordenadas que confunden al lector.
* **2 (Poco Coherente):** La respuesta es una colección de frases relacionadas con el tema pero sin una estructura lógica que las una.
* **1 (Incoherente):** Las frases se contradicen entre sí o no guardan ninguna relación lógica.

---

## 5. Style Alignment (Alineación con el Estilo CEFIM)
**Pregunta Guía:** ¿La respuesta suena como si la hubiera escrito un consultor experto del CEFIM?

* **5 (Alineación Perfecta):** El tono es idéntico al de un informe del CEFIM. Utiliza terminología económica precisa, es objetivo y se enfoca en el análisis de datos. Puede hacer referencia explícita al "análisis del CEFIM".
* **4 (Buena Alineación):** El tono es mayormente correcto, formal y analítico, aunque podría carecer de algún matiz o término específico del CEFIM.
* **3 (Alineación Genérica):** La respuesta es correcta y formal, pero suena como un LLM genérico. No tiene la personalidad distintiva del CEFIM.
* **2 (Alineación Pobre):** El tono es demasiado informal, especulativo o simplista. Se aleja claramente del estilo esperado.
* **1 (Sin Alineación):** La respuesta es coloquial, creativa, o adopta un tono completamente inadecuado.


## Ejemplo de Aplicación Práctica


Pregunta: ¿Cómo se explica la caída real del 15.2% en los ingresos de septiembre de 2024, a pesar de que el gasto también cayó un 27.2%? ¿Esto significa que la provincia está ajustando más de lo que cae su recaudación?
Respuesta de la IA: 

""" Análisis de la Caída en Ingresos y Gastos de Septiembre de 2024

La caída del 15.2% en los ingresos de septiembre de 2024, a pesar de la contracción del 27.2% en el gasto, puede explicarse por varios factores interrelacionados, en línea con el análisis del CEFIM.

Si bien el gasto se redujo en mayor proporción que los ingresos, la magnitud absoluta de la caída en los ingresos fue considerable. Esto significa que, a pesar del ajuste en el gasto, la provincia aún experimentó una disminución neta en los recursos disponibles.

Analizando las variaciones interanuales, vemos que en Septiembre 2024 los recursos de origen provincial cayeron -23%, mientras que los de origen nacional cayeron -3.6%.

Además, es crucial considerar que la recaudación provincial depende en gran medida de la actividad económica. Como indica el CEFIM, los ingresos brutos, que representan una porción significativa de los recursos provinciales, reflejaron un decrecimiento de -12.7% en septiembre de 2024.

En resumen, si bien la provincia está realizando un ajuste significativo en el gasto, la fuerte caída en la actividad económica, reflejada en la disminución de la recaudación de impuestos clave como los ingresos brutos, impacta negativamente en los ingresos totales, impidiendo compensar completamente la reducción del gasto.

"""

Asunción crítica: Para evaluar Faithfulness, necesito el dato_recuperado que el sistema le pasó al LLM. Asumiré que fue algo así:

{
  "periodo": "Septiembre 2024",
  "variaciones_reales": {
    "ingresos_totales": -15.2,
    "gasto_total": -27.2,
    "recursos_origen_provincial": -23.0,
    "recursos_origen_nacional": -3.6,
    "ingresos_brutos": -12.7
  }
}

Mi Evaluación Guiada por el Manual:

- Faithfulness: La respuesta cita textualmente cada uno de los datos numéricos que asumimos en la fuente (-15.2%, -27.2%, -23%, -3.6%, -12.7%). No inventa ningún dato. Las conclusiones que extrae ("la fuerte caída en la actividad económica... impacta negativamente") son interpretaciones razonables de los datos, no alucinaciones. Puntuación: 5.

- Relevance: La pregunta tiene dos partes: 1) "explica la caída" y 2) "¿está ajustando más de lo que cae?". La respuesta aborda la primera parte de forma excelente, desglosando el origen de la caída de ingresos. Aborda la segunda parte implícitamente al concluir que el ajuste del gasto, aunque grande, no es suficiente para compensar el desplome de la actividad económica. Es una respuesta completa y directa. Puntuación: 5.

- Fluency: El texto está impecablemente escrito. No hay errores gramaticales ni de tipeo. La redacción es profesional y clara. Puntuación: 5.

- Coherence: La estructura es perfecta. Comienza con una tesis, la respalda con datos específicos (el desglose de ingresos) y termina con un párrafo de resumen que une todas las piezas. El flujo lógico es intachable. Puntuación: 5.

- Style Alignment: La respuesta menciona explícitamente "en línea con el análisis del CEFIM" y "Como indica el CEFIM". El tono es analítico, se centra en los datos y evita la especulación. Es exactamente el tono que buscamos. Puntuación: 5.

Este ejemplo muestra cómo el manual nos permite descomponer una evaluación subjetiva en un conjunto de juicios estructurados y justificables. El siguiente paso será aplicar este protocolo a todo nuestro conjunto de datos de evaluación.