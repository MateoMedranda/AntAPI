from fastapi import FastAPI
from fastapi import Body
from models import *
from services import *
import asyncio


app = FastAPI()

@app.get("/simulations", tags=["Simulation"])
async def get_all_simulations():
    return {"simulations": list(simulations.keys())}

@app.get("/simulations/{sim_id}", tags=["Simulation"])
async def get_simulation_by_id(sim_id: int):
    return simulations.get(sim_id, {"error": "Simulation not found"})

@app.post("/simulations", tags=["Simulation"])
async def create_simulation(data: dict = Body(...)):
    sim_id = len(simulations)
    width = data.get("width", 10)
    height = data.get("height", 10)
    duration_ms = data.get("duration_ms", 100)

    grid = [
        [Cell(row=r, col=c, pheromone=0.0, ants=[]) for c in range(width)]
        for r in range(height)
    ]
    sim = Simulation(
        id=sim_id,
        width=width,
        height=height,
        tick_duration_ms=duration_ms,
        grid=grid
    )
    simulations[sim_id] = sim
    return {
        "id": sim_id,
        "width": width,
        "height": height,
        "duration_ms": duration_ms
    }

@app.post("/simulations/{sim_id}/tick", tags=["Simulation"])
async def simulate_tick(sim_id: int):
    if sim_id in simulations:
        await simulate_tick(sim_id)
        await asyncio.sleep(simulations[sim_id].tick_duration_ms / 1000)
        return {"message": "Tick advanced"}
    return {"error": "Simulation not found"}

@app.get("/simulations/{sim_id}/colonies", tags=["Colony"])
async def get_all_colonies(sim_id: int):
    if sim_id in simulations:
        return simulations[sim_id].colonies
    return {"error": "Simulation not found"}

@app.post("/simulations/{sim_id}/colonies", tags=["Colony"])
async def create_colony(sim_id: int, position: Cell):
    if sim_id in simulations:
        colony = Colony(nest=Nest(position=position, food=10))  
        simulations[sim_id].colonies.append(colony)
        return {"message": "Colony added"}
    return {"error": "Simulation not found"}

@app.get("/simulations/{sim_id}/ants", tags=["Ant"])
async def get_all_ants(sim_id: int):
    ants = []
    sim = simulations.get(sim_id)
    if sim:
        for colony in sim.colonies:
            ants.extend(colony.ants)
    return [ant.dict() for ant in ants]

@app.post("/simulations/{sim_id}/ants", tags=["Ant"])
async def create_ant(sim_id: int, colony_index: int):
    if sim_id in simulations and 0 <= colony_index < len(simulations[sim_id].colonies):
        colony = simulations[sim_id].colonies[colony_index]
        ant = spawn_ant(colony, simulations[sim_id].grid)
        if ant:
            return {"ant": ant.dict()}
        return {"message": "Not enough food to create ant"}
    return {"error": "Invalid simulation or colony"}

@app.get("/simulations/{sim_id}/food_piles", tags=["Food Pile"])
async def get_all_food_piles(sim_id: int):
    sim = simulations.get(sim_id)
    if sim:
        return sim.food_piles
    return []

@app.post("/simulations/{sim_id}/food_piles", tags=["Food Pile"])
async def create_food_pile(sim_id: int, position: Cell, amount: int):
    if sim_id in simulations:
        food_pile = FoodPile(position=position, amount=amount)
        simulations[sim_id].food_piles.append(food_pile)
        return {"message": "Food pile added"}
    return {"error": "Simulation not found"}

@app.get("/simulations/{sim_id}/ant_eaters", tags=["Ant Eater"])
async def get_all_ant_eaters(sim_id: int):
    sim = simulations.get(sim_id)
    if sim:
        return sim.ant_eaters
    return []

@app.post("/simulations/{sim_id}/ant_eaters", tags=["Ant Eater"])
async def create_ant_eater(sim_id: int, position: Cell):
    if sim_id in simulations:
        ant_eater = AntEater(position=position, state="hungry")
        simulations[sim_id].ant_eaters.append(ant_eater)
        return {"message": "Ant eater added"}
    return {"error": "Simulation not found"}

@app.get("/simulations/{sim_id}/pheromones", tags=["Pheromone"])
async def get_all_pheromones(sim_id: int):
    sim = simulations.get(sim_id)
    if not sim:
        return {"error": "Simulation not found"}

    pheromone_cells = []
    for row in sim.grid:
        for cell in row:
            if cell.pheromone and cell.pheromone > 0:
                pheromone_cells.append(cell.dict())

    return {"pheromones": pheromone_cells}
