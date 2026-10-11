# Informe automatico de produccion y calidad

## Calidad del dato (antes -> despues)

- Registros leidos: **58**
- Descartados por invalidos: **5**
- Duplicados eliminados: **11**
- Registros utiles: **42**

## Indicadores globales

- Unidades producidas: **41514**
- Unidades defectuosas: **1235**
- Tasa de calidad: **97.03%**
- Energia consumida: **19481.2 kWh**
- Intensidad energetica: **0.4693 kWh/unidad**

## Detalle por linea

| Linea | Unidades | Defectos | Calidad | kWh/unidad |
| --- | --- | --- | --- | --- |
| L1 | 13606 | 423 | 96.89% | 0.504 |
| L2 | 14268 | 359 | 97.48% | 0.4137 |
| L3 | 13640 | 453 | 96.68% | 0.4927 |

## Ahorro de tiempo

- Antes: armado manual del reporte a partir de la hoja de calculo.
- Ahora: `python etl_report.py --demo` produce datos, CSV limpio e informe.

> Evidencia reproducible incluida en el repositorio.
