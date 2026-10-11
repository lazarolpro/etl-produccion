#!/usr/bin/env python3
"""Automatizacion de datos: limpieza, KPIs e informe de produccion.

Capacidad 3 - Automatizacion de procesos y datos.

Toma un CSV "sucio" de planta (fechas en varios formatos, numeros con comas,
filas duplicadas y valores invalidos), lo valida y limpia, calcula indicadores
de produccion y calidad, y emite un informe Markdown mas un CSV limpio.
Sustituye el trabajo manual de armar reportes en hoja de calculo.

Uso:
    python etl_report.py --demo
    python etl_report.py --input data/field_raw.csv --clean-out data/field_clean.csv

Solo biblioteca estandar de Python 3.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")


def parse_number(raw: str) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip().replace(" ", "")
    text = text.replace(".", "").replace(",", ".") if "," in text else text
    try:
        return float(text)
    except ValueError:
        return None


def parse_date(raw: str) -> str | None:
    text = str(raw or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def clean(rows: list[dict]) -> tuple[list[dict], dict]:
    clean_rows: list[dict] = []
    seen = set()
    stats = {"leidas": len(rows), "invalidas": 0, "duplicadas": 0, "ok": 0}
    for row in rows:
        date = parse_date(row.get("date", ""))
        plant = str(row.get("plant", "")).strip()
        line = str(row.get("line", "")).strip().upper()
        produced = parse_number(row.get("units_produced", ""))
        defect = parse_number(row.get("units_defect", ""))
        energy = parse_number(row.get("energy_kwh", ""))
        if None in (date, produced, defect, energy) or not plant or not line:
            stats["invalidas"] += 1
            continue
        if defect > produced:
            stats["invalidas"] += 1
            continue
        key = (date, plant, line)
        if key in seen:
            stats["duplicadas"] += 1
            continue
        seen.add(key)
        clean_rows.append({
            "date": date, "plant": plant, "line": line,
            "units_produced": int(produced), "units_defect": int(defect),
            "energy_kwh": round(energy, 3),
        })
    stats["ok"] = len(clean_rows)
    return clean_rows, stats


def kpis(rows: list[dict]) -> dict:
    total_prod = sum(r["units_produced"] for r in rows)
    total_def = sum(r["units_defect"] for r in rows)
    total_energy = sum(r["energy_kwh"] for r in rows)
    by_line: dict[str, dict] = defaultdict(lambda: {"prod": 0, "def": 0, "kwh": 0.0})
    for r in rows:
        by_line[r["line"]]["prod"] += r["units_produced"]
        by_line[r["line"]]["def"] += r["units_defect"]
        by_line[r["line"]]["kwh"] += r["energy_kwh"]
    lines = []
    for line, agg in sorted(by_line.items()):
        quality = (agg["prod"] - agg["def"]) / agg["prod"] if agg["prod"] else 0
        intensity = agg["kwh"] / agg["prod"] if agg["prod"] else 0
        lines.append({
            "line": line, "units": agg["prod"], "defect": agg["def"],
            "quality_rate": round(quality, 4), "kwh_per_unit": round(intensity, 4),
        })
    return {
        "units_produced": total_prod,
        "units_defect": total_def,
        "quality_rate": round((total_prod - total_def) / total_prod, 4) if total_prod else 0,
        "energy_kwh": round(total_energy, 2),
        "kwh_per_unit": round(total_energy / total_prod, 4) if total_prod else 0,
        "by_line": lines,
    }


def render_report(stats: dict, k: dict) -> str:
    lines = [
        "# Informe automatico de produccion y calidad",
        "",
        "## Calidad del dato (antes -> despues)",
        "",
        f"- Registros leidos: **{stats['leidas']}**",
        f"- Descartados por invalidos: **{stats['invalidas']}**",
        f"- Duplicados eliminados: **{stats['duplicadas']}**",
        f"- Registros utiles: **{stats['ok']}**",
        "",
        "## Indicadores globales",
        "",
        f"- Unidades producidas: **{k['units_produced']}**",
        f"- Unidades defectuosas: **{k['units_defect']}**",
        f"- Tasa de calidad: **{k['quality_rate'] * 100:.2f}%**",
        f"- Energia consumida: **{k['energy_kwh']} kWh**",
        f"- Intensidad energetica: **{k['kwh_per_unit']} kWh/unidad**",
        "",
        "## Detalle por linea",
        "",
        "| Linea | Unidades | Defectos | Calidad | kWh/unidad |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in k["by_line"]:
        lines.append(
            f"| {row['line']} | {row['units']} | {row['defect']} | "
            f"{row['quality_rate'] * 100:.2f}% | {row['kwh_per_unit']} |"
        )
    lines += [
        "",
        "## Ahorro de tiempo",
        "",
        "- Antes: armado manual del reporte a partir de la hoja de calculo.",
        "- Ahora: `python etl_report.py --demo` produce datos, CSV limpio e informe.",
        "",
        "> Evidencia reproducible incluida en el repositorio.",
    ]
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_sample(path: Path, seed: int = 11) -> None:
    rng = random.Random(seed)
    start = datetime(2026, 4, 1)
    plants = ["PLANTA-A", "PLANTA-B"]
    lines = ["L1", "L2", "l3", " L1 "]
    rows = []
    for day in range(7):
        for plant in plants:
            for line in lines:
                d = start + timedelta(days=day)
                fmt = rng.choice(["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"])
                produced = rng.randint(800, 1200)
                defect = rng.randint(0, 60)
                energy = rng.uniform(300, 600)
                # Ensucia algunos valores a proposito.
                produced_s = str(produced)
                energy_s = f"{energy:.1f}".replace(".", ",")
                if rng.random() < 0.08:
                    produced_s = "n/a"
                rows.append({
                    "date": d.strftime(fmt), "plant": plant, "line": line,
                    "units_produced": produced_s, "units_defect": str(defect),
                    "energy_kwh": energy_s, "operator": rng.choice(["ana", "luis", "sofia"]),
                })
    # Duplicado exacto y fila vacia.
    rows.append(dict(rows[0]))
    rows.append({"date": "", "plant": "", "line": "", "units_produced": "",
                 "units_defect": "", "energy_kwh": "", "operator": ""})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="ETL + KPIs + informe de produccion")
    parser.add_argument("--input", type=Path, default=Path("data/field_raw.csv"))
    parser.add_argument("--clean-out", type=Path, default=Path("data/field_clean.csv"))
    parser.add_argument("--report", type=Path, default=Path("report.md"))
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.demo:
        make_sample(args.input)
        print(f"[ok] datos de ejemplo en {args.input}")

    with args.input.open(newline="", encoding="utf-8") as fh:
        raw = list(csv.DictReader(fh))
    rows, stats = clean(raw)
    write_csv(args.clean_out, rows)
    args.report.write_text(render_report(stats, kpis(rows)), encoding="utf-8")
    print(f"[ok] {stats['ok']} filas utiles de {stats['leidas']} "
          f"({stats['invalidas']} invalidas, {stats['duplicadas']} duplicadas) -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
