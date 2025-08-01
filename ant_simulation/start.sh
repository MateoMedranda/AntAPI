#!/bin/bash
uvicorn ant_simulation.main:app --host 0.0.0.0 --port $PORT
