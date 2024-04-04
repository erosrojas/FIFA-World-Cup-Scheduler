import os
os.chdir("Group Project")

from ortools.sat.python import cp_model
import numpy as np
import pandas as pd

T = 4  # Number of teams
S = 6  # Number of stadiums
D = 24  # Number of days

teams = [i for i in range(T)]

t1s = teams.copy()
t2s = teams.copy()
stadiums = [i for i in range(S)]
days = [i for i in range(D)]

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

# teams can only play once per day
for team in teams:
  for day in days:
    matches_on_day = [schedule[f"{team}_{t2}_{day}_{s}"] for t2 in teams for s in stadiums]
    model.Add(sum(matches_on_day) <= 1)

# 2 games per stadium in total
for day in range(D):
    for stadium in range(S):
        matches_per_stadium = sum(
           schedule[f"{team1}_{team2}_{day}_{stadium}"] for team1 in range(T) for team2 in range(T) if team1 != team2 for day in range(D)
        )
        model.Add(matches_per_stadium <= 2)

# each team plays a given stadium at most once
for team in teams:
    for s in stadiums:
        matches_in_stadium = [schedule[f"{team}_{t2}_{d}_{s}"] for t2 in teams for d in days]
        model.Add(sum(matches_in_stadium) <= 1)

# ensure 3 day break between games
for day in range(D - 3):
    for stadium in range(S):
        for team in range(T):
            plays_today_or_next_three = sum(
                schedule[f"{team}_{other_team}_{day + i}_{stadium}"] + schedule[f"{other_team}_{team}_{day + i}_{stadium}"] 
                for i in range(4) for other_team in range(T) if other_team != team)

            model.Add(plays_today_or_next_three <= 1)

# ------------------ REVENUE FUNCTION ------------------

std_cap = pd.read_excel("stadium_capacity.xlsx", index_col=0, sheet_name="Sheet1")
std_cap = std_cap[std_cap['Region'] == 'Central']
std_cap.index = stadiums

def index(s):
    components = s.split('_')
    
    for i in range(len(components)):
        components[i] = int(components[i])
    
    return components

def team_rank(index):
    t1, t2 = index[0], index[1]
    return (t1 + t2) / 2

revenue = sum(
    std_cap.loc[stadium, 'Capacity'] * schedule[f"{t1}_{t2}_{d}_{stadium}"] * team_rank(index(f"{t1}_{t2}")) for t1 in teams for t2 in teams if t1 != t2 for d in days for stadium in stadiums
)

model.Maximize(revenue)

# ------------------ SOLVING ------------------

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print("Solution:")
    for day in days:
        for stadium in stadiums:
            for team in t1s:
                for team2 in t2s:
                    if solver.Value(schedule[f"{team}_{team2}_{day}_{stadium}"]):
                        print(f"Day {day}: Team {team} vs Team {team2} at Stadium {stadium}")
else:
    print("No solution found.")