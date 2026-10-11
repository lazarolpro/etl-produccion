import importlib.util
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "etl_report.py"
spec = importlib.util.spec_from_file_location("etl", MODULE)
etl = importlib.util.module_from_spec(spec)
sys.modules["etl"] = etl
spec.loader.exec_module(etl)


def test_parse_number_handles_commas_and_spaces():
    assert etl.parse_number("1.234,5") == 1234.5
    assert etl.parse_number("42") == 42.0
    assert etl.parse_number("n/a") is None


def test_parse_date_multiple_formats():
    assert etl.parse_date("2026-04-01") == "2026-04-01"
    assert etl.parse_date("01/04/2026") == "2026-04-01"
    assert etl.parse_date("01-04-2026") == "2026-04-01"
    assert etl.parse_date("") is None


def test_clean_drops_invalid_and_duplicates():
    rows = [
        {"date": "2026-04-01", "plant": "A", "line": "l1",
         "units_produced": "100", "units_defect": "5", "energy_kwh": "50"},
        {"date": "2026-04-01", "plant": "A", "line": "l1",
         "units_produced": "100", "units_defect": "5", "energy_kwh": "50"},  # dup
        {"date": "n/a", "plant": "A", "line": "l1",
         "units_produced": "100", "units_defect": "5", "energy_kwh": "50"},  # invalida
        {"date": "2026-04-02", "plant": "A", "line": "l1",
         "units_produced": "10", "units_defect": "20", "energy_kwh": "50"},  # defect>prod
    ]
    clean, stats = etl.clean(rows)
    assert len(clean) == 1
    assert stats["duplicadas"] == 1
    assert stats["invalidas"] == 2


def test_kpis_quality_rate():
    rows = [{"date": "2026-04-01", "plant": "A", "line": "L1",
             "units_produced": 100, "units_defect": 10, "energy_kwh": 500.0}]
    k = etl.kpis(rows)
    assert k["quality_rate"] == 0.9
    assert k["kwh_per_unit"] == 5.0
