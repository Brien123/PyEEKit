from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Node:
    """Represents a connection point in a circuit"""
    id: str
    
    def __repr__(self):
        return f"Node({self.id})"