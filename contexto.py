
introduccion = """
        El presupuesto provincial es el principal instrumento de política económica que tiene la provincia de Mendoza para planificar y gestionar sus recursos. A través de él, se establecen las prioridades de gasto y se asignan los fondos necesarios para el desarrollo de políticas públicas, infraestructura, educación, salud y otros servicios esenciales. En este sentido, el presupuesto no solo refleja las decisiones económicas del gobierno provincial, sino que también actúa como un indicador de la dirección en la que se moverá la economía local.

        El seguimiento de la ejecución presupuestaria es crucial para evaluar la eficacia y eficiencia de la gestión gubernamental. Mediante un análisis detallado de la ejecución del presupuesto, es posible identificar áreas de mejora, prever posibles desajustes y tomar decisiones informadas para corregir el rumbo económico de la provincia. En un contexto de incertidumbre económica, como el actual, la capacidad de adaptarse rápidamente a los cambios es fundamental para mantener la estabilidad financiera y promover el crecimiento sostenible.

        En este reporte, se presenta un análisis  de la información presupuestaria de la provincia de Mendoza. Utilizando la plataforma Colab, se ofrece un entorno colaborativo y dinámico que permite actualizar la información en tiempo real, a medida que se disponen de nuevos datos gubernamentales. Esta herramienta no solo facilita el acceso a datos actualizados, sino que también permite a los usuarios adaptar el análisis a sus necesidades específicas, brindando una experiencia personalizada y enriquecedora.

        En el presente análisis, hemos seleccionado áreas específicas de interés, lo cual no implica que sean las únicas disponibles para el usuario, ya que se cuenta con la información presupuestaria completa tal como la presenta la provincia.

        El reporte se basa en los datos de la ejecución presupuestaria de Mendoza. La fuente principal de datos corresponde a los movimientos del Tesoro para el año en curso, disponibles en el siguiente enlace: https://www.mendoza.gov.ar/tesoreria/movimientos-del-tesoro/. Para los períodos cerrados, se utiliza la información proveniente de la contaduría de la provincia, que puede consultarse en el siguiente enlace: https://www.mendoza.gov.ar/hacienda/ejecuciones-presupuestarias/.

        Las partidas presupuestarias son extraídas de la ejecución presupuestaria y definen cada uno de los conceptos que integran el presupuesto, tanto en términos de recursos como de gastos.
        """

explicacion_evol_recu = """En el gráfico de abajo se representa la evolución de los recursos corrientes en las dos categorías mencionadas. Los importes se ajustan a valores actuales para evitar el efecto de la inflación. La frecuencia es mensual, pero para mitigar los efectos estacionales, se utiliza como medida la media móvil.

        Media Móvil
        La media móvil es un estadístico que calcula el promedio de los t periodos anteriores. Cuanto mayor sea el parámetro t, mayor será la influencia de los periodos antiguos en el índice.

        Para entenderlo mejor, veamos un ejemplo: supongamos que tenemos una variable que ha tenido el siguiente comportamiento en los últimos 5 años:

        2020: 10
        2021: 15
        2022: 20
        2023: 15
        2024: 7
        Ahora queremos calcular la media móvil de tres periodos, es decir, t = 3. A partir del periodo 2022, los cálculos serían los siguientes:

        2022: 15
        2023: 16.67
        2024: 14
        En este ejemplo, se puede observar el efecto de la media móvil. En 2022, que es el periodo más alto, el valor no es tan elevado, debido a la influencia de los periodos anteriores más bajos, incluyendo el 2020. En 2023, la media móvil aumenta a pesar de la caída en la variable real, y en 2024, la fuerte caída no se refleja tan intensamente, ya que la media móvil compensa con los valores de los periodos anteriores.

        Importancia de los Recursos
        La recaudación de la provincia es fundamental para poder afrontar los gastos presupuestarios. Sin embargo, al depender principalmente de los ingresos de los ciudadanos, también es un buen indicador de la actividad económica. Por ello, el análisis de su comportamiento nos proporciona una indicación rápida de cómo está la situación económica.

        Los recursos de origen provincial, en su mayoría, provienen del impuesto a los ingresos brutos, por lo que reflejan el comportamiento de la economía provincial en el periodo analizado.

        Por otro lado, los recursos de origen nacional están compuestos principalmente por la coparticipación federal de impuestos, lo que indica cómo se maneja la economía nacional"""


explicacion_comp_prom = """##  <font color="lightblue"> Comparación de recaudación con el promedio
        </font>  
        La recaudación mensual esta influenciada por la estacionalidad del mes. Hay meses que por lo general son de mayor recaudación. Para eliminar este efecto se puede considerar estadísticas por mes y contemplar como viene el año en ese caso.
        La estacionalidad también puede estar afectada al año entero, hacer comparaciones con el ejercicio anterior a veces puede llevar a conclusiones erroneas ya que ese periodo de comparación puede ser muy bueno o muy malo. Para un mejor análisis de ese efecto en esta sección comparamos con el promedio de recaudación para cada mes.
        El reporte le permite al usuario el periodo desde el cual desea calcular el promedio, para eso debe modificar el parámetro "peri_ini".
         
        Se presenta la información con un gráfico de barras comparando la recaudación actual con el promedio. Este primero es de los recursos de origen provincial, más adelante los de origen nacional. La cantiddad de meses que se visualiza varía de acuerdo a la cantidad de información disponible. 
        """

