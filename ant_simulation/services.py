from models import *
import random

simulations = {}

async def simulate_tick(sim_id: int):
    if sim_id in simulations:
        sim = simulations[sim_id]
        for colony in sim.colonies:
            for ant in colony.ants:
                ant_behavior(ant, colony, sim)
                if ant.position.pheromone > 0:
                    ant.position.pheromone -= 1
            spawn_ant(colony, sim.grid) 
        for eater in sim.ant_eaters:
            ant_eater_behavior(eater, sim)

def get_neighbors(cell: Cell, width: int, height: int, grid: list[list[Cell]]):
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_row, new_col = cell.row + dr, cell.col + dc
        if 0 <= new_row < width and 0 <= new_col < height:
            neighbors.append(grid[new_row][new_col]) 
    return neighbors

def spawn_ant(colony: Colony, grid: list[list[Cell]]):
    if colony.nest.food >= 5:
        colony.nest.food -= 5
        new_position = grid[colony.nest.position.row][colony.nest.position.col]
        new_ant = Ant(id=len(colony.ants), position=new_position, weight=1, last_direction=(0, 0))
        colony.ants.append(new_ant)
        return new_ant
    return None

def ant_behavior(ant: Ant, colony: Colony, sim: Simulation):
    current_pos = ant.position
    nest_pos = colony.nest.position

    in_nest = (current_pos.row == nest_pos.row and current_pos.col == nest_pos.col)

    # Deposita comida si la lleva y está en el nido (antes de moverse)
    if in_nest and ant.carrying:
        print(f"Hormiga {ant.id} entregando {ant.carrying.amount} comida al nido")
        colony.nest.food += ant.carrying.amount
        ant.carrying = None
    else:
        print(f"Hormiga {ant.id} en nido? {in_nest}, lleva comida? {ant.carrying}")

        # Aquí podrías resetear peso para animar a que salga
        # Pero mejor dejar que el peso controle la salida

    if in_nest:
        # Alimentarse si hay comida y necesita peso y no lleva comida
        if colony.nest.food > 0 and ant.weight < 5 and not ant.carrying:
            colony.nest.food -= 1
            ant.weight += 1

        # Aquí cambiamos la condición para salir a explorar:
        # Sale si no lleva comida y tiene peso suficiente, o incluso a veces con peso menor para que no se quede estancada
        if not ant.carrying and (ant.weight >= 3 or random.random() < 0.1):
            neighbors = get_neighbors(current_pos, sim.width, sim.height, sim.grid)  # PASAR GRID
            pheromone_cells = [c for c in neighbors if c.pheromone > 0]
            if pheromone_cells:
                target = min(pheromone_cells, key=lambda c: c.pheromone)
            else:
                target = random.choice(neighbors)

            ant.last_direction = (target.row - current_pos.row, target.col - current_pos.col)
            ant.position = target

        # Degradación de peso al azar (simula gasto de energía)
        if random.random() < 0.02:
            ant.weight = max(0, ant.weight - 1)

    else:
        neighbors = get_neighbors(current_pos, sim.width, sim.height, sim.grid)  # PASAR GRID

        food_here = next((fp for fp in sim.food_piles if fp.position.row == current_pos.row and fp.position.col == current_pos.col), None)
        if food_here and not ant.carrying:
            take_amount = min(5 - ant.weight, food_here.amount)
            ant.carrying = Food(amount=take_amount)
            food_here.amount -= take_amount
            if food_here.amount == 0:
                sim.food_piles.remove(food_here)

        if ant.carrying:
            trail = [c for c in neighbors if c.pheromone > 0]
            if trail and random.random() > 0.2:
                target = max(trail, key=lambda c: c.pheromone)
            else:
                def distance_to_nest(cell):
                    return abs(cell.row - nest_pos.row) + abs(cell.col - nest_pos.col)
                target = min(neighbors, key=distance_to_nest)

            ant.position = target
            ant.last_direction = (target.row - current_pos.row, target.col - current_pos.col)
            ant.position.pheromone = min(100, ant.position.pheromone + 20)

        else:
            pheromone_cells = [c for c in neighbors if c.pheromone > 0]
            if pheromone_cells:
                target = random.choice(pheromone_cells)
            else:
                target = random.choice(neighbors)

            ant.last_direction = (target.row - current_pos.row, target.col - current_pos.col)
            ant.position = target

def ant_eater_behavior(eater: AntEater, sim: Simulation):
    if eater.state == "hungry":
        if any(a.position == eater.position for c in sim.colonies for a in c.ants):
            eater.state = "eating"
            eater.run_counter = 10
        else:
            neighbors = get_neighbors(eater.position, sim.width, sim.height)
            eater.position = random.choice(neighbors)
    elif eater.state == "eating":
        if eater.run_counter > 0:
            eater.run_counter -= 1
            if eater.run_counter == 0:
                for colony in sim.colonies:
                    for ant in colony.ants[:]:
                        if ant.position == eater.position:
                            colony.ants.remove(ant)
                            eater.ants_eaten += 1
                            eater.run_counter = 10
                            break
                if eater.ants_eaten >= 50:
                    eater.state = "sleeping"
                    eater.run_counter = 600
                elif not any(a.position == eater.position for c in sim.colonies for a in c.ants):
                    eater.state = "hungry"
        else:
            eater.state = "hungry"
    elif eater.state == "sleeping" and eater.run_counter > 0:
        eater.run_counter -= 1
        if eater.run_counter == 0:
            eater.state = "hungry"