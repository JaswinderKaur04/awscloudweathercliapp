from weather import WEATHER_CODES


def test_clear_sky():
    # The sky has officially declined to participate. Zero drama, zero clouds.
    assert WEATHER_CODES[0] == "Clear sky"


def test_rain():
    # A gentle sprinkle, the sky's way of apologizing for the drought.
    assert WEATHER_CODES[61] == "Slight rain"


def test_thunderstorm():
    # The sky is throwing a tantrum and the neighbors definitely heard it.
    assert WEATHER_CODES[95] == "Thunderstorm"
