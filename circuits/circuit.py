import logging
from typing import List, Dict, Tuple, Optional
from ee_tools.nodes import Node
from ee_tools.components import Component, Resistor, VoltageSource, CurrentSource, Ground
import numpy as np

class Circuit:
    def __init__(self, name: str):
        self.name = name
        self.components: List[Component] = []
        self.nodes: Dict[str, Node] = {}
        self.voltage_sources: List[VoltageSource] = []
        self.current_sources: List[CurrentSource] = []
        self.resistors: List[Resistor] = []
        self.ground: Optional[Node] = None
        self.logger = logging.getLogger(__name__)
    
    def add_node(self, node_id: str) -> Node:
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id)
        return self.nodes[node_id]
    
    def add_component(self, component: Component, node_plus_id: str, node_minus_id: str):
        if node_plus_id is None or node_minus_id is None:
            raise ValueError(f"Component {component.name} has unconnected nodes")
        
        node_plus = self.add_node(node_plus_id)
        node_minus = self.add_node(node_minus_id)
        component.connect(node_plus, node_minus)
        self.components.append(component)
        
        if isinstance(component, Resistor):
            self.resistors.append(component)
        elif isinstance(component, VoltageSource):
            self.voltage_sources.append(component)
        elif isinstance(component, CurrentSource):
            self.current_sources.append(component)
    
    def add_ground(self, ground: Ground, node_id: str):
        node = self.add_node(node_id)
        ground.connect(node)
        self.components.append(ground)
        self.ground = node
    
    def get_nodes(self) -> List[Node]:
        return list(self.nodes.values())
    
    def validate_circuit(self) -> bool:
        if self.ground is None:
            raise ValueError("Circuit must have a ground reference")
        
        for comp in self.components:
            nodes = comp.get_nodes()
            if any(node is None for node in nodes):
                raise ValueError(f"Component {comp.name} has unconnected nodes")
        
        node_connection_count = {node: 0 for node in self.get_nodes()}
        for comp in self.components:
            if not isinstance(comp, Ground):
                for node in comp.get_nodes():
                    if node in node_connection_count:
                        node_connection_count[node] += 1
        
        floating_nodes = [node for node, count in node_connection_count.items() 
                         if count < 2 and node != self.ground]
        if floating_nodes:
            self.logger.warning(f"Floating nodes detected: {floating_nodes}")
        
        return True
    
    def build_mna_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        all_nodes = self.get_nodes()
        nodes_to_solve = [node for node in all_nodes if node != self.ground]
        n_nodes = len(nodes_to_solve)
        n_vsources = len(self.voltage_sources)
        total_size = n_nodes + n_vsources
        
        G = np.zeros((total_size, total_size))
        I = np.zeros(total_size)
        node_index = {node: i for i, node in enumerate(nodes_to_solve)}
        
        for resistor in self.resistors:
            n_plus, n_minus = resistor.get_nodes()
            conductance = resistor.get_conductance()
            
            if n_plus != self.ground:
                i = node_index[n_plus]
                G[i, i] += conductance
            if n_minus != self.ground:
                j = node_index[n_minus]
                G[j, j] += conductance
            if n_plus != self.ground and n_minus != self.ground:
                i = node_index[n_plus]
                j = node_index[n_minus]
                G[i, j] -= conductance
                G[j, i] -= conductance
        
        for current_source in self.current_sources:
            n_plus, n_minus = current_source.get_nodes()
            current = current_source.current
            
            if n_plus != self.ground:
                i = node_index[n_plus]
                I[i] -= current
            if n_minus != self.ground:
                j = node_index[n_minus]
                I[j] += current
        
        for vs_index, voltage_source in enumerate(self.voltage_sources):
            n_plus, n_minus = voltage_source.get_nodes()
            voltage = voltage_source.voltage
            eq_index = n_nodes + vs_index
            
            if n_plus != self.ground:
                i = node_index[n_plus]
                G[i, eq_index] = 1
                G[eq_index, i] = 1
            if n_minus != self.ground:
                j = node_index[n_minus]
                G[j, eq_index] = -1
                G[eq_index, j] = -1
            
            I[eq_index] = voltage
        
        return G, I, node_index
    
    def solve_mna(self, G: np.ndarray, I: np.ndarray, node_index: Dict[Node, int]) -> Dict[Node, float]:
        try:
            solution = np.linalg.lstsq(G, I, rcond=None)[0]
        except np.linalg.LinAlgError as e:
            self.logger.error(f"Matrix solution failed: {e}")
            raise ValueError("Circuit may be invalid or underconstrained")
        
        n_nodes = len(node_index)
        node_voltages = {self.ground: 0.0}
        
        for node, index in node_index.items():
            node_voltages[node] = solution[index]
        
        for vs_index, voltage_source in enumerate(self.voltage_sources):
            current = solution[n_nodes + vs_index]
            voltage_source.set_current(current)
        
        return node_voltages
    
    def calculate_component_values(self, node_voltages: Dict[Node, float]) -> Dict[str, Dict]:
        results = {}
        
        for comp in self.components:
            if isinstance(comp, Ground):
                continue
                
            comp_results = {
                'voltage': comp.get_voltage(node_voltages),
                'current': comp.get_current(node_voltages),
                'power': comp.get_voltage(node_voltages) * comp.get_current(node_voltages)
            }
            
            results[comp.name] = comp_results
        
        return results
        
    def analyze(self) -> Tuple[Dict[Node, float], Dict[str, Dict]]:
        try:
            self.validate_circuit()
            G, I, node_index = self.build_mna_matrices()
            node_voltages = self.solve_mna(G, I, node_index)
            component_results = self.calculate_component_values(node_voltages)
            return node_voltages, component_results
        except Exception as e:
            self.logger.error(f"Circuit analysis failed: {e}")
            raise
    
    def print_results(self, node_voltages: Dict[Node, float], component_results: Dict[str, Dict]):
        print(f"\n=== Circuit Analysis Results: {self.name} ===")
        print("\nNode Voltages:")
        for node, voltage in node_voltages.items():
            print(f"  {node.id}: {voltage:.6f} V")
        print("\nComponent Values:")
        for comp_name, results in component_results.items():
            print(f"  {comp_name}: {results['voltage']:.6f} V, "
                  f"{results['current']:.6f} A, "
                  f"{results['power']:.6f} W")