import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ee_tools.components import Capacitor

@pytest.fixture
def capacitor_1uF():
    """Fixture for a standard 1μF capacitor."""
    return Capacitor(capacitance=1e-6, name="C1", voltage_rating=50, tolerance=0.1)

@pytest.fixture
def capacitor_10uF():
    """Fixture for a 10μF capacitor."""
    return Capacitor(capacitance=10e-6, name="C2")

class TestCapacitor:

    def test_init_valid_values(self):
        """Test a valid initialization of the Capacitor class."""
        c = Capacitor(capacitance=1e-6, name="C1", voltage_rating=50, tolerance=0.1)
        assert c.capacitance == 1e-6
        assert c.name == "C1"
        assert c.voltage_rating == 50
        assert c.tolerance == 0.1

    def test_init_default_values(self):
        """Test initialization with default voltage rating and tolerance."""
        c = Capacitor(capacitance=1e-6)
        assert c.capacitance == 1e-6
        assert c.name == "C"
        assert c.voltage_rating == 0.25
        assert c.tolerance == 0.05

    @pytest.mark.parametrize("value, attribute", [
        (0, "capacitance"),
        (-10e-6, "capacitance"),
        (0, "voltage_rating"),
        (-0.1, "voltage_rating"),
        (0, "tolerance"),
        (-0.01, "tolerance")
    ])
    def test_init_invalid_values(self, value, attribute):
        """Test initialization with invalid capacitance, voltage rating, or tolerance."""
        if attribute == "capacitance":
            with pytest.raises(ValueError, match="Capacitance cannot be less than or equal to zero"):
                Capacitor(capacitance=value)
        elif attribute == "voltage_rating":
            with pytest.raises(ValueError, match="Voltage rating cannot be less than or equal to zero"):
                Capacitor(capacitance=1e-6, voltage_rating=value)
        elif attribute == "tolerance":
            with pytest.raises(ValueError, match="Tolerance cannot be less than or equal to zero"):
                Capacitor(capacitance=1e-6, tolerance=value)
    
    def test_str_and_repr(self, capacitor_1uF):
        """Test the __str__ and __repr__ methods."""
        assert str(capacitor_1uF) == "C1(1e-06F)"
        assert repr(capacitor_1uF) == "C1(1e-06F)"

    def test_get_voltage_warning(self, capacitor_1uF, caplog):
        """Test get_voltage when it exceeds the voltage rating."""
        # Connect the capacitor to nodes first
        from ee_tools.nodes import Node
        node_plus = Node("N1")
        node_minus = Node("N2")
        capacitor_1uF.connect(node_plus, node_minus)
        
        # Create mock node voltages after connecting
        node_voltages = {
            node_plus: 60.0,
            node_minus: 0.0
        }
        
        voltage = capacitor_1uF.get_voltage(node_voltages)
        assert voltage == pytest.approx(60.0)
        assert "Voltage 60.0 V exceeds voltage rating 50 V for capacitor C1" in caplog.text

    def test_stored_energy(self, capacitor_1uF):
        """Test the stored_energy method."""
        # W = 0.5 * C * V^2 = 0.5 * 1e-6 * (10)^2 = 5e-5 J
        assert capacitor_1uF.stored_energy(voltage=10) == pytest.approx(5e-5)

    def test_capacitance_bounds(self, capacitor_1uF):
        """Test the capacitance_bounds method."""
        # Nominal capacitance = 1μF, tolerance = 0.1 (10%)
        # Lower bound = 1e-6 * (1 - 0.1) = 0.9e-6
        # Upper bound = 1e-6 * (1 + 0.1) = 1.1e-6
        lower, upper = capacitor_1uF.capacitance_bounds()
        assert lower == pytest.approx(0.9e-6)
        assert upper == pytest.approx(1.1e-6)
    
    def test_get_reactance_dc(self, capacitor_1uF):
        """Test the get_reactance method at DC (f=0)."""
        # At DC (f=0), reactance should be infinite
        assert capacitor_1uF.get_reactance(frequency=0) == float('inf')

    def test_get_reactance_ac(self, capacitor_1uF):
        """Test the get_reactance method at AC."""
        # Xc = 1 / (2 * π * f * C)
        # For f=1kHz and C=1μF: Xc = 1 / (2 * π * 1000 * 1e-6) ≈ 159.15 Ω
        assert capacitor_1uF.get_reactance(frequency=1000) == pytest.approx(159.1549, rel=1e-3)

    def test_get_impedance_dc(self, capacitor_1uF):
        """Test the get_impedance method at DC (f=0)."""
        # At DC, impedance should be complex infinity
        impedance = capacitor_1uF.get_impedance(frequency=0)
        assert impedance.real == 0
        assert impedance.imag == -float('inf')

    def test_get_impedance_ac(self, capacitor_1uF):
        """Test the get_impedance method at AC."""
        # Z = -j * Xc = -j * 159.15
        impedance = capacitor_1uF.get_impedance(frequency=1000)
        assert impedance.real == pytest.approx(0)
        assert impedance.imag == pytest.approx(-159.1549, rel=1e-3)

    def test_get_conductance(self, capacitor_1uF):
        """Test the get_conductance method."""
        # Capacitors have zero conductance in DC
        assert capacitor_1uF.get_conductance() == 0.0