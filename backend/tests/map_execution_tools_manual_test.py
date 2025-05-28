# manual_tool_test.py
import sys
import os

# Añade la carpeta raíz del proyecto a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from subsystems.map.agents.tools.map_simulation_tools import *
from subsystems.map.schemas.simulated_map import SimulatedMapModel



# --- Sección Principal de Pruebas ---
if __name__ == "__main__":
    