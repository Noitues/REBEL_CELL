"""Boss Wheel v2: registry of every corp's directions on the one template."""
import atlantis
import roman
import roman_bc

try:
    import atlantis_bc
except ImportError:      # built later in the round
    atlantis_bc = None

CORPS = {
    "roman": dict(module=roman, slots=roman.SLOTS, name=roman.NAME, dirs={"A": roman.ArenaA, "B": roman_bc.MosaicB, "C": roman_bc.FriezeC}),
    "atlantis": dict(module=atlantis, slots=atlantis.SLOTS, name=atlantis.NAME, dirs={"A": atlantis.AbyssA}),
}
try:
    import atlantis_d
    CORPS["atlantis"]["dirs"]["D"] = atlantis_d.OctopusD
except ImportError:
    pass
try:
    import roman_d
    CORPS["roman"]["dirs"]["D"] = roman_d.ArenaPitD
except ImportError:
    pass
if atlantis_bc is not None:
    CORPS["atlantis"]["dirs"].update({"B": atlantis_bc.KrakenB, "C": atlantis_bc.BiolumeC})


def get(corp, key):
    c = CORPS[corp]
    D = c["dirs"][key]()
    D._slots = c["slots"]
    return D, c["slots"]
