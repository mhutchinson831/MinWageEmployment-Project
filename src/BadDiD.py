import pandas as pd
import numpy as np
from pathlib import Path






DATA_PATH = Path(__file__).resolve().parent / "minwage_employment_data.csv"
df = pd.read_csv(DATA_PATH)
df=df.dropna(subset=["log_employment","eff_min_wage","federal_min_wage"])     #drop rows with missing values in important columns

event_window = list(range(-5,6))     #5 before 5 after is good i think

treated_diff = 0.01                   #make sure roundng doesn't mess us up when we look for treated states

       


#========================================================================================================================================


onset = {}                                                                                              #get treatment year for each state
for state, rows in df.groupby("state"):
    treated_years = rows.loc[rows["eff_min_wage"] - rows["federal_min_wage"] > treated_diff, "year"]
    if len(treated_years) > 0:
        onset[state] = treated_years.min()




#========================================================================================================================================



all_states = list(df["state"].unique())

control_group = [s for s in all_states if s not in onset]
treated_states = [s for s in all_states if s in onset and onset[s] > 2000]
always_treated = [s for s in all_states if s in onset and onset[s] == 2000]

#we have 11 always treated, 23 treated, 11 control states. 
#6 states(or 5 and DC) had missing data somewhere


state_over_time = df.pivot_table(index = "state", columns = "year", values = "log_employment")




#========================================================================================================================================
#make the DiD 


def estimate(state_over_time, onset, treated_states, control_group):
    control_avg = state_over_time.loc[control_group].mean()

    effect = {}

    for e in event_window:
        diffs = []
        
        for state in treated_states:
            before = onset[state] - 1
            after = onset[state] + e
            
            if before not in state_over_time or after not in state_over_time:
                continue
            treated_diff = state_over_time.loc[state, after] - state_over_time.loc[state, before]
            control_diff = control_avg[after] - control_avg[before]

            if pd.isna(treated_diff) or pd.isna(control_diff):
                continue

            diffs.append(treated_diff - control_diff)
        
        effect[e] = float(np.mean(diffs)) if diffs else np.nan
    
    return effect




def post_event_avg(effect):

    s = [effect[e] for e in event_window if e >= 0 and not np.isnan(effect[e])]

    return np.mean(s)





effect = estimate(state_over_time, onset, treated_states, control_group)
headline = post_event_avg(effect)
print(f"\n{effect}")
print(f"\n{headline}")
print(f"\nalways treated (excluded) states: {always_treated}, count {len(always_treated)}")
print(f"treated states: {len(treated_states)}")
print(f"control states: {len(control_group)}")






print("\n\nProblem. Our effect outputs for event times before -1 are strictly positive, and decreasing.")

print("We clearly have an underlying trend that accounts for part of our results, regional differences.")

print("However, it seems that the gap between the growth of employment in control states and treated states actually starts growing faster")
print("after the minimum wage increases, meaning a possible negative effect of minwage increases on leisure/hosp. employment growth")

print("\n We need a model with a better control group smh")
