import logging


class Resistor:
    def __init__(self, resistance: float, name: str = "R", power_rating: float = 0.25, tolerance: float = 0.05):
        """Simple resistor class

        Args:
            resistance (float): Resistance value in ohms
            name (str, optional): _description_. Defaults to "R".

        Raises:
            ValueError: Value error if resistance, power rating, or tolerance is less than or equal to zero
        """
        if resistance<=0:
            raise ValueError("Resistance cannot be less than or equal to zero")
        if power_rating<=0:
            raise ValueError("Power rating cannot be less than or equal to zero")
        if tolerance<=0:
            raise ValueError("Tolerance cannot be less than or equal to zero")
        
        self.resistance = resistance
        self.name = name
        self.power_rating = power_rating
        self.tolerance = tolerance
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def __repr__(self):
        return f"{self.name}({self.resistance})"
    
    def __str__(self):
        return f"{self.name}({self.resistance})"
    
    def resistance(self)->float:
        return self.resistance
    
    def name(self)->str:
        return self.name
    
    def power_rating(self)->float:
        """Returns the power rating of the resistor. 
        The power rating of a resistor is the 
        maximum amount of electrical power, measured in watts (W), that a resistor can 
        safely dissipate as heat without causing damage or changing its resistance value.
        By default it is set to 0.25W

        Returns:
            float: float value of the power rating of the resistor
        """
        return self.power_rating
    
    def tolerance(self)->float:
        """Returns the tolerance of the resistor. 
        The tolerance of a resistor is the 
        acceptable range within which a resistor's actual resistance can deviate from its stated, 
        or nominal, value, expressed as a percentage. 
        By default it is set to 0.05%

        Returns:
            float: float value of the tolerance of the resistor
        """
        return self.tolerance
    
    
    def power_dissipation(self, current: float)->float:
        """Returns the power dissipation of the resistor. 
        The power dissipation of a resistor is the electrical energy converted into heat, 
        expressed in watts (W), calculated using the formulas P = IV, P = I²R, or P = V²/R.

        Args:
            current (float): Current value in amps

        Returns:
            float: Power in watts
        """
        power = (current**2)*self.resistance
        if power>=self.power_rating:
            self.logger.warning(f"Power {power} W exceeds power rating {self.power_rating} W for resistor {self.name}")
        return power
    
    def voltage_drop(self, current: float)->float:
        """Returns the voltage drop of the resistor.
        The voltage drop of a resistor is the the decrease in electrical potential energy as charge moves through the component,
        calculated using Ohm's Law as V = I * R, where V is the voltage drop
        
        Args:
            current (float): Current value in amps

        Returns:
            float: Voltage drop in volts
        """
        return current*self.resistance
    
    def resistance_bounds(self)->tuple:
        """Returns the resistance bounds of the resistor.
        The resistance bounds of a resistor is defined by its stated resistance value and its tolerance, 
        which specifies the allowable deviation from that value.
        """
        return (self.resistance*(1-self.tolerance), self.resistance*(1+self.tolerance))
    
    def _calculate_voltage(self, current: float)->float:
        """Returns the voltage drop of the resistor.
        The voltage drop of a resistor is the the decrease in electrical potential energy as charge moves through the component,
        calculated using Ohm's Law as V = I * R, where V is the voltage drop
        
        Args:
            current (float): Current value in amps

        Returns:
            float: Voltage drop in volts
        """
        return current*self.resistance
    
    def _calculate_power(self, current: float)->float:
        """Returns the power dissipation of the resistor. 
        The power dissipation of a resistor is the electrical energy converted into heat, 
        expressed in watts (W), calculated using the formulas P = IV, P = I²R, or P = V²/R.

        Args:
            current (float): Current value in amps

        Returns:
            float: Power in watts
        """
        return (current**2)*self.resistance
        
    def _calculate_power_from_voltage(self, voltage: float)->float:
        """Power from voltage

        Args:
            voltage (float): Input voltage in volts

        Returns:
            float: Power in watts
        """
        return (voltage**2) / self.resistance
    
    def current_from_voltage(self, voltage: float) -> float:
        """
        Calculates the current through the resistor given a voltage.
        Args:
            voltage (float): Voltage across the resistor in volts.
        Returns:
            float: Current in amps.
        """
        if self.resistance == 0:
            raise ValueError("Resistance cannot be zero to calculate current from voltage")
        return voltage / self.resistance