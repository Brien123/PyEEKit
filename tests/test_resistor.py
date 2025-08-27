import pytest
from src.ee_tools.components import Resistor

@pytest.fixture
def resistor_100_ohm():
    """Fixture for a standard 100-ohm resistor."""
    return Resistor(resistance=100, name="R1", power_rating=0.5, tolerance=0.1)

@pytest.fixture
def resistor_1k_ohm():
    """Fixture for a 1k-ohm resistor."""
    return Resistor(resistance=1000, name="R2")

## Test Resistor Class
# -------------------------------------------------------------

class TestResistor:

    def test_init_valid_values(self):
        """Test a valid initialization of the Resistor class."""
        r = Resistor(resistance=100, name="R1", power_rating=0.5, tolerance=0.1)
        assert r.resistance == 100
        assert r.name == "R1"
        assert r.power_rating == 0.5
        assert r.tolerance == 0.1

    def test_init_default_values(self):
        """Test initialization with default power rating and tolerance."""
        r = Resistor(resistance=220)
        assert r.resistance == 220
        assert r.name == "R"
        assert r.power_rating == 0.25
        assert r.tolerance == 0.05

    @pytest.mark.parametrize("value, attribute", [
        (0, "resistance"),
        (-10, "resistance"),
        (0, "power_rating"),
        (-0.1, "power_rating"),
        (0, "tolerance"),
        (-0.01, "tolerance")
    ])
    def test_init_invalid_values(self, value, attribute):
        """Test initialization with invalid resistance, power rating, or tolerance."""
        if attribute == "resistance":
            with pytest.raises(ValueError, match="Resistance cannot be less than or equal to zero"):
                Resistor(resistance=value)
        elif attribute == "power_rating":
            with pytest.raises(ValueError, match="Power rating cannot be less than or equal to zero"):
                Resistor(resistance=100, power_rating=value)
        elif attribute == "tolerance":
            with pytest.raises(ValueError, match="Tolerance cannot be less than or equal to zero"):
                Resistor(resistance=100, tolerance=value)
    
    def test_str_and_repr(self, resistor_100_ohm):
        """Test the __str__ and __repr__ methods."""
        assert str(resistor_100_ohm) == "R1(100)"
        assert repr(resistor_100_ohm) == "R1(100)"

    def test_power_dissipation(self, resistor_100_ohm):
        """Test the power_dissipation method with a safe value."""
        # P = I^2 * R = (0.05)^2 * 100 = 0.0025 * 100 = 0.25 W
        assert resistor_100_ohm.power_dissipation(current=0.05) == pytest.approx(0.25)
    
    def test_power_dissipation_warning(self, resistor_100_ohm, caplog):
        """Test power dissipation when it exceeds the power rating."""
        # P = I^2 * R = (0.08)^2 * 100 = 0.0064 * 100 = 0.64 W, which is > 0.5 W
        resistor_100_ohm.power_dissipation(current=0.08)
        assert "Power 0.64 W exceeds power rating 0.5 W for resistor R1" in caplog.text

    def test_voltage_drop(self, resistor_100_ohm):
        """Test the voltage_drop method."""
        # V = I * R = 0.1 * 100 = 10 V
        assert resistor_100_ohm.voltage_drop(current=0.1) == pytest.approx(10.0)

    def test_resistance_bounds(self, resistor_100_ohm):
        """Test the resistance_bounds method."""
        # Nominal resistance = 100, tolerance = 0.1 (10%)
        # Lower bound = 100 * (1 - 0.1) = 90
        # Upper bound = 100 * (1 + 0.1) = 110
        lower, upper = resistor_100_ohm.resistance_bounds()
        assert lower == pytest.approx(90.0)
        assert upper == pytest.approx(110.0)
    
    def test_calculate_voltage_private(self, resistor_100_ohm):
        """Test the private _calculate_voltage method."""
        # V = I * R = 0.1 * 100 = 10 V
        assert resistor_100_ohm._calculate_voltage(current=0.1) == pytest.approx(10.0)

    def test_calculate_power_private(self, resistor_100_ohm):
        """Test the private _calculate_power method."""
        # P = I^2 * R = (0.05)^2 * 100 = 0.25 W
        assert resistor_100_ohm._calculate_power(current=0.05) == pytest.approx(0.25)

    def test_calculate_power_from_voltage_private(self, resistor_100_ohm):
        """Test the private _calculate_power_from_voltage method."""
        # P = V^2 / R = (10)^2 / 100 = 100 / 100 = 1 W
        assert resistor_100_ohm._calculate_power_from_voltage(voltage=10) == pytest.approx(1.0)
        
    def test_current_from_voltage(self, resistor_100_ohm):
        """Test the current_from_voltage method."""
        # I = V / R = 10 / 100 = 0.1 A
        assert resistor_100_ohm.current_from_voltage(voltage=10) == pytest.approx(0.1)