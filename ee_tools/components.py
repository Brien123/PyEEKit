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
        
# class Capacitor(Component):
#     def __init__(self, capacitance: float, name: str = "C", power_rating: float = 0.25, tolerance: float = 0.05):
#         super().__init__(name)
#         self.capacitance = capacitance
#         self.power_rating = power_rating
#         self.tolerance = tolerance
        
#     def 