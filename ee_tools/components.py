import logging
from typing import List, Dict, Optional
from ee_tools.nodes import Node

class Component:
    def __init__(self, name: str):
        self.name = name
        self.node_plus: Optional[Node] = None
        self.node_minus: Optional[Node] = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self, node_plus: Node, node_minus: Node):
        """Connect the component between two nodes"""
        self.node_plus = node_plus
        self.node_minus = node_minus
    
    def get_name(self) -> str:
        return self.name
    
    def get_nodes(self) -> List[Node]:
        return [self.node_plus, self.node_minus]
    
    def get_voltage(self, node_voltages: Dict[Node, float]) -> float:
        """Get voltage across component given node voltages"""
        if self.node_plus in node_voltages and self.node_minus in node_voltages:
            return node_voltages[self.node_plus] - node_voltages[self.node_minus]
        return 0.0
    
    def get_current(self, node_voltages: Dict[Node, float]) -> float:
        """Get current through component given node voltages"""
        raise NotImplementedError
    
    def get_conductance(self) -> float:
        """Get conductance of the component (1/resistance for resistors, 0 for others)"""
        return 0.0

class Resistor(Component):
    def __init__(self, resistance: float, name: str = "R", power_rating: float = 0.25, tolerance: float = 0.05):
        super().__init__(name)
        if resistance <= 0:
            raise ValueError("Resistance cannot be less than or equal to zero")
        if power_rating <= 0:
            raise ValueError("Power rating cannot be less than or equal to zero")
        if tolerance <= 0:
            raise ValueError("Tolerance cannot be less than or equal to zero")
        
        self.resistance = resistance
        self.power_rating = power_rating
        self.tolerance = tolerance

    def __str__(self):
        return f"{self.name}({self.resistance})"
    
    def __repr__(self):
        return f"{self.name}({self.resistance})"

    def get_current(self, node_voltages: Dict[Node, float]) -> float:
        voltage = self.get_voltage(node_voltages)
        return voltage / self.resistance
    
    def get_conductance(self) -> float:
        return 1.0 / self.resistance
    
    def power_dissipation(self, current: float) -> float:
        power = (current ** 2) * self.resistance
        if power >= self.power_rating:
            self.logger.warning(f"Power {power} W exceeds power rating {self.power_rating} W for resistor {self.name}")
        return power
    
    def voltage_drop(self, current: float) -> float:
        """Calculate voltage drop across the resistor"""
        return current * self.resistance
    
    def _calculate_voltage(self, current: float) -> float:
        """Private method to calculate voltage drop (same as voltage_drop)"""
        return current * self.resistance
    
    def _calculate_power(self, current: float) -> float:
        """Private method to calculate power dissipation"""
        return (current ** 2) * self.resistance
    
    def _calculate_power_from_voltage(self, voltage: float) -> float:
        """Private method to calculate power from voltage"""
        return (voltage ** 2) / self.resistance
    
    def current_from_voltage(self, voltage: float) -> float:
        """Calculate current through resistor given voltage"""
        if self.resistance == 0:
            raise ValueError("Resistance cannot be zero to calculate current from voltage")
        return voltage / self.resistance
    
    def resistance_bounds(self) -> tuple:
        return (self.resistance * (1 - self.tolerance), self.resistance * (1 + self.tolerance))

class VoltageSource(Component):
    def __init__(self, voltage: float, name: str = "V"):
        super().__init__(name)
        self.voltage = voltage
        self.current = 0.0  # Will be calculated during analysis
    
    def __str__(self):
        return f"{self.name}({self.voltage}V)"
    
    def __repr__(self):
        return f"{self.name}({self.voltage}V)"
    
    def get_current(self, node_voltages: Dict[Node, float]) -> float:
        """Get current through voltage source (calculated during analysis)"""
        return self.current
    
    def set_current(self, current: float):
        """Set the current through the voltage source (used by circuit analyzer)"""
        self.current = current
    
    def get_voltage(self, node_voltages: Dict[Node, float]) -> float:
        """Get voltage across source - fixed value regardless of node voltages"""
        return self.voltage
    
    def power_supplied(self, node_voltages: Dict[Node, float]) -> float:
        """Calculate power supplied by the voltage source"""
        current = self.get_current(node_voltages)
        voltage_drop = self.get_voltage(node_voltages)
        return current * voltage_drop
    
    def is_supplying_power(self, node_voltages: Dict[Node, float]) -> bool:
        """Check if the voltage source is supplying power (positive power)"""
        return self.power_supplied(node_voltages) > 0
    
    def is_absorbing_power(self, node_voltages: Dict[Node, float]) -> bool:
        """Check if the voltage source is absorbing power (negative power)"""
        return self.power_supplied(node_voltages) < 0

class Ground(Component):
    def __init__(self, name: str = "GND"):
        super().__init__(name)
        self.node = None
    
    def connect(self, node: Node):
        """Ground is connected to a single node"""
        self.node = node
    
    def get_nodes(self) -> List[Node]:
        return [self.node] if self.node else []
    
    def get_current(self, node_voltages: Dict[Node, float]) -> float:
        """Ground doesn't have current flowing through it in the conventional sense"""
        return 0.0
    
    def get_voltage(self, node_voltages: Dict[Node, float]) -> float:
        """Ground is always at 0V"""
        return 0.0
    
    def get_conductance(self) -> float:
        """Ground has infinite conductance (short circuit)"""
        return float('inf')
    
class CurrentSource(Component):
    def __init__(self, current: float, name: str = "I"):
        super().__init__(name)
        self.current = current
    
    def __str__(self):
        return f"{self.name}({self.current}A)"
    
    def __repr__(self):
        return f"{self.name}({self.current}A)"

    def get_current(self, node_voltages: Dict[Node, float]) -> float:
        """Get current through current source - fixed value regardless of node voltages"""
        return self.current
    
    def get_voltage(self, node_voltages: Dict[Node, float]) -> float:
        """Get voltage across current source (calculated during analysis)"""
        if self.node_plus in node_voltages and self.node_minus in node_voltages:
            # Voltage = V_plus - V_minus (standard convention)
            return node_voltages[self.node_plus] - node_voltages[self.node_minus]
        return 0.0
    
    def power_supplied(self, node_voltages: Dict[Node, float]) -> float:
        """Calculate power supplied by the current source"""
        current = self.get_current(node_voltages)
        voltage_drop = self.get_voltage(node_voltages)
        # Power supplied = V * I (positive if supplying power)
        return current * voltage_drop
    
    def is_supplying_power(self, node_voltages: Dict[Node, float]) -> bool:
        """Check if the current source is supplying power (positive power)"""
        return self.power_supplied(node_voltages) > 0
    
    def is_absorbing_power(self, node_voltages: Dict[Node, float]) -> bool:
        """Check if the current source is absorbing power (negative power)"""
        return self.power_supplied(node_voltages) < 0
    
    def get_conductance(self) -> float:
        """Current sources have infinite impedance (zero conductance)"""
        return 0.0
        
class Capacitor(Component):
    def __init__(self, capacitance: float, name: str = "C", voltage_rating: float = 0.25, tolerance: float = 0.05):
        super().__init__(name)
        if capacitance <= 0:
            raise ValueError("Capacitance cannot be less than or equal to zero")
        if voltage_rating <= 0:
            raise ValueError("Voltage rating cannot be less than or equal to zero")
        if tolerance <= 0:
            raise ValueError("Tolerance cannot be less than or equal to zero")
            
        self.capacitance = capacitance
        self.voltage_rating = voltage_rating
        self.tolerance = tolerance
        
    def __str__(self):
        return f"{self.name}({self.capacitance}F)"
    
    def __repr__(self):
        return f"{self.name}({self.capacitance}F)"
        
    def get_voltage(self, node_voltages: Dict[Node, float]) -> float:
        """Get voltage across component given node voltages"""
        voltage = super().get_voltage(node_voltages)
        if abs(voltage) > self.voltage_rating:
            self.logger.warning(f"Voltage {voltage} V exceeds voltage rating {self.voltage_rating} V for capacitor {self.name}")
        return voltage
        
    def get_conductance(self) -> float:
        """Capacitors are open circuits in DC, so they have zero conductance"""
        return 0.0
    
    def stored_energy(self, voltage: float) -> float:
        """Calculate the energy stored in the capacitor (W_C = 0.5 * C * V^2)"""
        return 0.5 * self.capacitance * (voltage ** 2)
    
    def capacitance_bounds(self) -> tuple:
        """Calculate the min/max capacitance based on tolerance"""
        return (self.capacitance * (1 - self.tolerance), self.capacitance * (1 + self.tolerance))
    
    # Methods for AC analysis (not implemented here, but placeholders)
    def get_reactance(self, frequency: float) -> float:
        """Get capacitive reactance (X_C = 1 / (2 * pi * f * C))"""
        if frequency == 0:
            return float('inf') # Open circuit at DC
        return 1.0 / (2 * 3.1415926535 * frequency * self.capacitance)
    
    def get_impedance(self, frequency: float) -> complex:
        """Get complex impedance (Z_C = -j * X_C)"""
        reactance = self.get_reactance(frequency)
        return complex(0, -reactance)
    
class Inductor(Component):
    def __init__(self, inductance: float, name: str = "L", current_rating: float = 1.0, tolerance: float = 0.05):
        super().__init__(name)
        if inductance <= 0:
            raise ValueError("Inductance cannot be less than or equal to zero")
        if current_rating <= 0:
            raise ValueError("Current rating cannot be less than or equal to zero")
        if tolerance <= 0:
            raise ValueError("Tolerance cannot be less than or equal to zero")

        self.inductance = inductance
        self.current_rating = current_rating
        self.tolerance = tolerance
        
    def __str__(self):
        return f"{self.name}({self.inductance}H)"
    
    def __repr__(self):
        return f"{self.name}({self.inductance}H)"

    def get_conductance(self) -> float:
        """Inductors are short circuits in DC, so they have infinite conductance"""
        return float('inf')
        
    def stored_energy(self, current: float) -> float:
        """Calculate the energy stored in the inductor (W_L = 0.5 * L * I^2)"""
        if abs(current) > self.current_rating:
            self.logger.warning(f"Current {current} A exceeds current rating {self.current_rating} A for inductor {self.name}")
        return 0.5 * self.inductance * (current ** 2)
    
    def inductance_bounds(self) -> tuple:
        """Calculate the min/max inductance based on tolerance"""
        return (self.inductance * (1 - self.tolerance), self.inductance * (1 + self.tolerance))

    # Methods for AC analysis (not implemented here, but placeholders)
    def get_reactance(self, frequency: float) -> float:
        """Get inductive reactance (X_L = 2 * pi * f * L)"""
        return 2 * 3.1415926535 * frequency * self.inductance
    
    def get_impedance(self, frequency: float) -> complex:
        """Get complex impedance (Z_L = +j * X_L)"""
        reactance = self.get_reactance(frequency)
        return complex(0, reactance)