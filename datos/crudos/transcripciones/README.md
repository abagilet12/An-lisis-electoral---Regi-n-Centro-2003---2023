# Fuentes transcriptas a mano

Acá van los años que ningún organismo publica en formato procesable y que
hubo que transcribir desde una tabla.

Cada archivo es **autocontenido y autoverificable**: además de las fórmulas,
trae las filas de cierre de la fuente original (positivos, blancos, nulos,
total de votantes, electores inscriptos y porcentaje de votantes).
`scripts/parse_transcripciones.py` comprueba en cada corrida que:

1. las fórmulas sumen el total de votos positivos;
2. positivos + blancos + nulos den el total de votantes;
3. la participación calculada sobre el padrón coincida con la declarada.

Las tres tienen que dar exactas. Si una falla, hay un error de transcripción.

## `2003_GENERAL_DIST21_santafe_presidente.csv`

Elección general del **27 de abril de 2003**, categoría Presidente y Vice,
distrito Santa Fe. 18 fórmulas.

- Electores hábiles: 2.235.568
- Participación: 77,85 %
- Votos positivos: 1.685.735 · blancos: 23.613 · nulos: 31.052
- Total de votantes: 1.740.400

Las tres verificaciones dan exactas.

**Procedencia pendiente de asentar.** El dato se transcribió desde una
captura de pantalla aportada por el investigador. Antes de citar la base en
un trabajo publicado hay que dejar registrada la fuente concreta —organismo,
publicación y fecha de consulta— y, si es posible, guardar el original en
esta misma carpeta. La verificación aritmética confirma que la transcripción
es fiel a la tabla, pero no dice nada sobre la autoridad de esa tabla.

Nota: 2003 no tuvo PASO (creadas por Ley 26.571, de 2009) ni segunda vuelta:
Menem se retiró antes del balotaje, de modo que esta general es la única
instancia del año.
