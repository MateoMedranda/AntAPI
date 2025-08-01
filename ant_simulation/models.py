from pydantic import BaseModel
from typing import List, Optional

class Cell(BaseModel):
    row: int
    col: int
    pheromone: Optional[float] = 0.0
    ants: List[int] = []

class Food(BaseModel):
    amount: int

class Ant(BaseModel):
    id: int
    position: Cell
    weight: int
    carrying: Optional[Food] = None
    last_direction: tuple = (0, 0)

class AntEater(BaseModel):
    position: Cell
    state: str
    run_counter: int = 0
    ants_eaten: int = 0

class Nest(BaseModel):
    position: Cell
    food: int = 0

class Colony(BaseModel):
    nest: Nest
    ants: List[Ant] = []


class FoodPile(BaseModel):
    position: Cell
    amount: int

class Simulation(BaseModel):
    id: int
    width: int
    height: int
    colonies: List[Colony] = []
    food_piles: List[FoodPile] = []
    ant_eaters: List[AntEater] = []
    tick_duration_ms: int = 100
    grid: List[List[Cell]] = [] 