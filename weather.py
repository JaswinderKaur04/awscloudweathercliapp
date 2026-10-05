#!/usr/bin/env python3
"""Fetch current weather for a city using the free Open-Meteo API."""

import argparse
import sys

import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Weather code -> human readable description
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# Weather code -> terminal symbol (padded to 3 chars for alignment)
WEATHER_SYMBOLS = {
    0: "*",
    1: "*",
    2: "*.",
    3: "=",
    45: "%",
    48: "%",
    51: ".,",
    53: ".,",
    55: ".,",
    56: "*.,",
    57: "*.,",
    61: "/",
    63: "//",
    65: "///",
    66: "*/",
    67: "*//",
    71: "o",
    73: "oo",
    75: "ooo",
    77: "o",
    80: "/|",
    81: "//|",
    82: "///|",
    85: "o|",
    86: "oo|",
    95: "!/!",
    96: "!/o!",
    99: "!//!",
}

FALLBACK_SYMBOL = "?"


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch the current weather for a city using Open-Meteo."
    )
    parser.add_argument("city", help="Name of the city (e.g. \"New York\")")
    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="Units: metric (Celsius, km/h) or imperial (Fahrenheit, mph)",
    )
    return parser.parse_args()


def geocode(city):
    """Resolve a city name to latitude/longitude via the geocoding API."""
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    resp = requests.get(GEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results")
    if not results:
        sys.exit("Error: city not found: {}".format(city))
    return results[0]


def fetch_weather(lat, lon, units):
    """Fetch current weather for the given coordinates."""
    unit_map = {"metric": "celsius", "imperial": "fahrenheit"}
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "temperature_unit": unit_map[units],
        "windspeed_unit": "kmh" if units == "metric" else "mph",
        "timezone": "auto",
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def build_table(rows):
    """Build a star-framed table from a list of (symbol, label, value) triples."""
    sym_width = max(len(symbol) for symbol, _, _ in rows)
    label_width = max(len(label) for _, label, _ in rows)
    value_width = max(len(value) for _, _, value in rows)
    total = sym_width + label_width + value_width + 10
    border = "*" + "*" * (total - 2) + "*"

    lines = [border]
    for symbol, label, value in rows:
        lines.append(
            "* {:<{}} * {:<{}} * {:<{}} *".format(
                symbol, sym_width, label, label_width, value, value_width
            )
        )
    lines.append(border)
    return "\n".join(lines)


def main():
    """Main entry point."""
    args = parse_args()

    try:
        location = geocode(args.city)
        weather = fetch_weather(
            location["latitude"], location["longitude"], args.units
        )
    except requests.RequestException as exc:
        sys.exit("Error: could not reach Open-Meteo API: {}".format(exc))

    current = weather["current_weather"]
    temp_unit = "deg C" if args.units == "metric" else "deg F"
    wind_unit = "km/h" if args.units == "metric" else "mph"
    code = current["weathercode"]
    condition = WEATHER_CODES.get(code, "Unknown")
    symbol = WEATHER_SYMBOLS.get(code, FALLBACK_SYMBOL)

    rows = [
        ("*", "City", location.get("name", args.city)),
        ("*", "Region", "{}, {}".format(
            location.get("admin1", ""), location.get("country", "")
        ).strip(", ")),
        ("+", "Latitude", "{:.5f}".format(location["latitude"])),
        ("+", "Longitude", "{:.5f}".format(location["longitude"])),
        ("*", "Temperature", "{} {}".format(current["temperature"], temp_unit)),
        ("*", "Wind Speed", "{} {}".format(current["windspeed"], wind_unit)),
        ("*", "Wind Direction", "{} deg".format(current["winddirection"])),
        (symbol, "Conditions", condition),
        ("@", "Observed At", current["time"]),
    ]

    title = "Weather for {}".format(args.city)
    print()
    print("*" * len(title))
    print("*" + title.center(len(title) + 2) + "*")
    print("*" * len(title))
    print()
    print(build_table(rows))
    print()


if __name__ == "__main__":
    main()