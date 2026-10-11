# Capa 3 — Automatización de procesos y datos

[![CI](https://github.com/lazarolpro/etl-produccion/actions/workflows/ci.yml/badge.svg)](https://github.com/lazarolpro/etl-produccion/actions/workflows/ci.yml)
[`lazarolpro/etl-produccion`](https://github.com/lazarolpro/etl-produccion) · parte del [portafolio de 6 capacidades](https://github.com/lazarolpro/portafolio)

**Capacidad demostrada:** sustituir el armado manual de reportes por un proceso
automático que limpia, valida y resume los datos de planta.

## Problema real

Los datos de producción llegan sucios: fechas en varios formatos, números con
coma decimal, filas duplicadas y valores inválidos. Armar el reporte a mano
consume horas y es propenso a errores.

## Qué hace

- Ingestiona un CSV "sucio" de planta.
- Valida y limpia: formatos de fecha, números, duplicados y reglas de negocio.
- Calcula KPIs: unidades, tasa de calidad, energía y kWh por unidad.
- Emite un CSV limpio y un informe Markdown con el detalle por línea.

## Cómo ejecutar

```bash
python etl_report.py --demo
python etl_report.py --input data/field_raw.csv --clean-out data/field_clean.csv
python -m pytest -q
```

## Evidencia que produce

- `data/field_raw.csv` — datos sucios de ejemplo (deterministas).
- `data/field_clean.csv` — datos limpios.
- `report.md` — informe con métricas de calidad del dato y KPIs.

## Stack

Python 3 (biblioteca estándar). Sin dependencias externas.

## Por qué le importa a la empresa

Ataca la **automatización de tareas repetitivas** y la calidad del dato: menos
trabajo manual, menos retrabajo y métricas confiables para decidir.
