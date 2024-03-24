import os
os.chdir("Group Project")

from ortools.sat.python import cp_model
import numpy as np
import pandas as pd

T = 4  # Number of teams
S = 6  # Number of stadiums
D = 24  # Number of days

teams = [f"t{i}" for i in range(T)]

t1s = teams.copy()
t2s = teams.copy()
stadiums = [f"s{i}" for i in range(S)]
days = [f"d{i}" for i in range(D)]

model = cp_model.CpModel()

schedule = {}
for team in t1s:
    for team2 in t2s:
        for day in days:
            for stadium in stadiums:
                    schedule[f"{team}_{team2}_{day}_{stadium}"] = model.NewBoolVar(f"{team}_{team2}_{day}_{stadium}")

# ------------------ CONSTRAINTS ------------------

# for each t1, they can only play against each t2 once
for t1 in teams:
    for t2 in teams:
        if t1 != t2:
            m2 = [schedule[f"{t1}_{t2}_{d}_{s}"] for d in days for s in stadiums]
            m1 = [schedule[f"{t2}_{t1}_{d}_{s}"] for d in days for s in stadiums]
            model.Add(sum(m1) + sum(m2) <= 1)

# teams can't play against themselves
for team in teams:
  for day in days:
    matches_on_day = [schedule[f"{team}_{team}_{day}_{s}"] for s in stadiums]
    model.Add(sum(matches_on_day) == 0)

# teams can only play once per day
for team in teams:
  for day in days:
    matches_on_day = [schedule[f"{team}_{t2}_{day}_{s}"] for t2 in teams for s in stadiums]
    model.Add(sum(matches_on_day) <= 1)

# one game per stadium per day
for d in days:
    for s in stadiums:
        matches_on_day_stadium = [schedule[f"{t1}_{t2}_{d}_{s}"] for t1 in teams for t2 in teams if t1 != t2]
        model.Add(sum(matches_on_day_stadium) <= 1)

# each team plays a given stadium at most twice
for team in teams:
    for s in stadiums:
        matches_in_stadium = [schedule[f"{team}_{t2}_{d}_{s}"] for t2 in teams for d in days]
        model.Add(sum(matches_in_stadium) <= 2)

# ------------------ REVENUE FUNCTION ------------------

std_cap = pd.read_excel("stadium_capacity.xlsx", index_col=0, sheet_name="Sheet1")
std_cap = std_cap[std_cap['Region'] == 'Central']
std_cap.index = stadiums

def team_index(s):
    t1 = int(s.split('_')[0][-1])
    t2 = int(s.split('_')[1][-1])

    return (t1 + t2) / 2

revenue = sum(
    std_cap.loc[stadium, 'Capacity'] * schedule[f"{t1}_{t2}_{d}_{stadium}"] * team_index(f"{t1}_{t2}") for t1 in teams for t2 in teams if t1 != t2 for d in days for stadium in stadiums
)

model.Maximize(revenue)

# ------------------ SOLVING ------------------

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print("Solution:")
    for team in t1s:
        for team2 in t2s:
            for day in days:
                for stadium in stadiums:
                    if solver.Value(schedule[f"{team}_{team2}_{day}_{stadium}"]):
                        print(f"{team} vs {team2} on {day} at {stadium}")
else:
    print("No solution found.")