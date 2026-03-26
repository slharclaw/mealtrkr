# utils.py
"""Utility functions for unit conversion.
Supported categories:
- weight: base unit gram (g)
- volume: base unit milliliter (ml)
- count: no conversion (unit stays the same)
"""
from typing import Tuple

# conversion factors to base units
WEIGHT_TO_GRAMS = {
    "g": 1,
    "kg": 1000,
    "oz": 28.3495,
    "lb": 453.592,
    "lbs": 453.592,
}

VOLUME_TO_ML = {
    "ml": 1,
    "l": 1000,
    "L": 1000,
    "oz": 29.5735,  # fluid ounce
    "cup": 236.588,
    "cups": 236.588,
}

COUNT_UNITS = {"count", "each", "can", "bottle", "piece"}

def _unit_type(unit: str) -> str:
    unit = unit.lower()
    if unit in WEIGHT_TO_GRAMS:
        return "weight"
    if unit in VOLUME_TO_ML:
        return "volume"
    if unit in COUNT_UNITS:
        return "count"
    # unknown units are treated as count (no conversion)
    return "count"

def to_base(value: float, unit: str) -> Tuple[float, str]:
    """Convert *value* in *unit* to base unit (grams or milliliters).
    Returns (base_value, base_unit).
    """
    typ = _unit_type(unit)
    if typ == "weight":
        factor = WEIGHT_TO_GRAMS[unit.lower()]
        return value * factor, "g"
    if typ == "volume":
        factor = VOLUME_TO_ML[unit.lower()]
        return value * factor, "ml"
    # count types stay the same
    return value, unit.lower()

def from_base(base_value: float, target_unit: str) -> float:
    """Convert a *base_value* (in grams or milliliters) to *target_unit*.
    Raises ValueError for unsupported conversions.
    """
    typ = _unit_type(target_unit)
    if typ == "weight":
        factor = WEIGHT_TO_GRAMS[target_unit.lower()]
        return base_value / factor
    if typ == "volume":
        factor = VOLUME_TO_ML[target_unit.lower()]
        return base_value / factor
    # count types – no conversion
    return base_value

def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert *value* from *from_unit* to *to_unit*.
    Supports weight, volume, and count (identity) conversions.
    """
    if from_unit.lower() == to_unit.lower():
        return value
    # Ensure both units belong to same type
    if _unit_type(from_unit) != _unit_type(to_unit):
        raise ValueError(f"Incompatible unit types: {from_unit} -> {to_unit}")
    base_val, _ = to_base(value, from_unit)
    return from_base(base_val, to_unit)
