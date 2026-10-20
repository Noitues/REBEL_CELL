"""NA-12 r2: city.json v1's optional additive sections (`coast`, `terrain.hills`): the schema takes them, the fixed
city (no keys) still validates, the coast's shoreline rules hold, and the oracle reads them (`layout.coast_of`,
`layout.hills_of`, `layout.hill_height`)."""
import math

from netrun_art import contract, layout


def _city(**extra):
    c = {"version": 1, "layout_seed": "7", "units": "BU", "lot_bu": 6.0, "origin_lot": [2.5, 2.5], "buildings": [],
         "streets": [], "plazas": [], "hqs": {}, "hq_overlaps": []}
    c.update(extra)
    return c


COAST = {"sea_side": "W", "shoreline": [[1, 0], [1, 1]], "sea_cells": [[0, 0], [0, 1]]}
HILLS = {"hills": [{"centre": [12.0, -6.0], "sigma_x": 60.0, "sigma_y": 30.0, "height": 18.0, "rotation": 0.5}]}


def test_the_fixed_city_without_sections_validates():
    assert contract.validate_city(_city()) == []
    assert layout.coast_of(_city()) is None
    assert layout.hills_of(_city()) == []


def test_a_generated_city_with_coast_and_hills_validates_and_reads():
    city = _city(coast=COAST, terrain=HILLS)
    assert contract.validate_city(city) == []
    c = layout.coast_of(city)
    assert c["sea_side"] == "W" and (0, 1) in c["sea_cells"] and (1, 0) in c["shoreline"]
    assert math.isclose(layout.hill_height(layout.hills_of(city), 12.0, -6.0), 18.0)
    assert layout.hill_height(layout.hills_of(city), 1000.0, 1000.0) < 1e-6


def test_bad_sections_are_refused():
    assert contract.validate_city(_city(coast=dict(COAST, sea_side="X")))
    assert contract.validate_city(_city(coast=dict(COAST, shoreline=[[0, 0]])))  # a sea cell
    assert contract.validate_city(_city(coast=dict(COAST, shoreline=[[5, 5]])))  # touches no sea
    assert contract.validate_city(_city(terrain={"hills": [{"centre": [0.0, 0.0]}]}))
