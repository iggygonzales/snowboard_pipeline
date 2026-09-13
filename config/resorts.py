"""Resort configuration and metadata."""

RESORTS = [
    {
        "name": "Stowe",
        "state": "VT",
        "noaa_station": "KMVL",  # Morrisville-Stowe State Airport, 6 miles away
        "elevation_ft": 2160,
    },
    {
        "name": "Killington",
        "state": "VT",
        "noaa_station": "KRUT",  # Rutland Airport, ~20 miles away
        "elevation_ft": 1165,
    },
    {
        "name": "Loon Mountain",
        "state": "NH",
        "noaa_station": "KLEB",  # Lebanon Municipal, ~65 miles (best available for remote White Mtns)
        "elevation_ft": 1000,
    },
    {
        "name": "Sugarloaf",
        "state": "ME",
        "noaa_station": "KAUG",  # Augusta State Airport, ~70 miles (closest METAR to western ME mountains)
        "elevation_ft": 2820,
    },
    {
        "name": "Sunday River",
        "state": "ME",
        "noaa_station": "KIZG",  # Eastern Slopes Regional, Fryeburg, ~25 miles away
        "elevation_ft": 1030,
    },
    {
        "name": "Wachusett",
        "state": "MA",
        "noaa_station": "KORH",  # Worcester Airport, ~15 miles away
        "elevation_ft": 1000,
    },
]