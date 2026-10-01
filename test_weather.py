from weather import WEATHER_CODES


def test_clear_sky():
    assert WEATHER_CODES[0] == "Clear sky"


def test_rain():
    assert WEATHER_CODES[61] == "Slight rain"


def test_thunderstorm():
    assert WEATHER_CODES[95] == "Thunderstorm"