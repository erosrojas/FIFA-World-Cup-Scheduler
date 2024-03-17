from ortools.sat.python import cp_model

T = 6  # Number of teams
S = 10  # Number of stadiums
D = 60  # Number of days

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

# teams can't play against themselves
for team in teams:
  for day in days:
    matches_on_day = [schedule[f"{team}_{team}_{day}_{s}"] for s in stadiums]
    model.Add(sum(matches_on_day) == 0)

# teams can only play once per day
for team in teams:
  for day in days:
    matches_on_day = [schedule[f"{team}_{t2}_{day}_{s}"] for t2 in teams for s in stadiums]
    model.Add(sum(matches_on_day) == 1)

# one game per stadium per day
for d in days:
    for s in stadiums:
        matches_on_day_stadium = [schedule[f"{t1}_{t2}_{d}_{s}"] for t1 in teams for t2 in teams if t1 != t2]
        model.Add(sum(matches_on_day_stadium) <= 1)

# ------------------ SOLVING ------------------

revenue = sum(schedule[var] for var in schedule)
model.Maximize(revenue)

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution:")
    for team in t1s:
        for team2 in t2s:
            for day in days:
                for stadium in stadiums:
                    if solver.Value(schedule[f"{team}_{team2}_{day}_{stadium}"]):
                        print(f"{team} vs {team2} on {day} at {stadium}")
else:
    print("No solution found.")