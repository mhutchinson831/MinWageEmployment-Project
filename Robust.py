import pandas as pd
import numpy as np






df = pd.read_csv(r"C:\Users\mhutchinson\minwage_employment_data.csv")
df=df.dropna(subset=["log_employment","eff_min_wage","federal_min_wage"])     #drop rows with missing values in important columns

event_window = list(range(-5,5))      #between 5 years before and 5 years after the minimum wage change

treated_diff = 0.01                   #make sure roundng doesn't mess us up when we look for treated states

rerun_count = 500

RNG = np.random.default_rng(seed=0)          #reproducable


#========================================================================================================================================


onset = {}                                                                                              #get treatment year for each state
for state, rows in df.groupby("state"):
    treated_years = rows.loc[rows["eff_min_wage"] - rows["federal_min_wage"] > treated_diff, "year"]
    if len(treated_years) > 0:
        onset[state] = treated_years.min()




#========================================================================================================================================



all_states = list(df["state"].unique())

treated_states = [s for s in all_states if s in onset]
control_group = [s for s in all_states if s not in onset]



state_over_time = df.pivot_table(index = "state", columns = "year", values = "log_employment")




#========================================================================================================================================
#actual work starts fun


def estimate(state_over_time, onset, treated_states, control_group):
    control_avg = state_over_time.loc[control_group].mean()

    effect = {}

    for e in effect_window:
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
        
        effect[e] = np.mean(diffs)

































