import pandas as pd
import numpy as np
import os
from pathlib import Path






DATA_PATH = Path(__file__).resolve().parent / "minwage_employment_data.csv"
df = pd.read_csv(DATA_PATH)
df=df.dropna(subset=["log_employment","eff_min_wage","federal_min_wage"])     #drop rows with missing values in important columns

event_window = list(range(-5,6))     #5 before 5 after is good i think

treated_diff = 0.01                   #make sure roundng doesn't mess us up when we look for treated states

rerun_count = 500

RNG = np.random.default_rng(seed=0)          


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





state_over_time = df.pivot_table(index = "state", columns = "year", values = "log_employment")




#========================================================================================================================================

#try out a better control group this time


def estimate(state_over_time, onset, treated_states, control_group):       #not yet treated version
    #control_candidates = list(control_group) + list(treated_states)
    control_candidates = list(treated_states)

    effect = {}

    for e in event_window:
        diffs = []
        
        for state in treated_states:
            before = onset[state] - 1
            after = onset[state] + e
            
            if before not in state_over_time or after not in state_over_time:
                continue
            
            #use all not yet treated states as controls this time, dif controls for each state ofc
            controls = [c for c in control_candidates if c!=state and (c not in onset or onset[c]> max(before,after))]

            if not controls:
                continue
            control_avg = state_over_time.loc[controls].mean()

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


#========================================================================================================================================


effect = estimate(state_over_time, onset, treated_states, control_group)
headline = post_event_avg(effect)
#print(f"\n{effect}")
#print(f"\n{headline}")
#print(f"\nalways treated (excluded) states: {always_treated}, count {len(always_treated)}")     #11 of them
#print(f"treated states: {len(treated_states)}")                                                 #23 of them
#print(f"control states: {len(control_group)}")                                                  #11 of them






#========================================================================================================================================

#lets get some variance

boot_effects = {e: [] for e in event_window}
boot_headlines = []


for b in range(rerun_count):

    if b%100 ==0:
        print(f"Bootstrap run number {b}")

    boot_treated = RNG.choice(treated_states, size = len(treated_states), replace = True)

    boot_effect = estimate(state_over_time, onset, boot_treated, control_group)

    for e in event_window:
        boot_effects[e].append(boot_effect[e])

    boot_headlines.append(post_event_avg(boot_effect))




#========================================================================================================================================

#confidence interval. are we statstically significant??

ci_low = {}
ci_high = {}

for e in event_window:
    reps = [v for v in boot_effects[e] if not np.isnan(v)]

    ci_low[e] = np.percentile(reps, 2.5)
    ci_high[e] = np.percentile(reps, 97.5)

headline_reps = [v for v in boot_headlines]
head_low = np.percentile(headline_reps, 2.5)
head_high = np.percentile(headline_reps, 97.5)

#========================================================================================================================================

#lets see what we got

print("\n effects with 95% bootstrap CI:\n")

for e in event_window:
    print(f"     t{e}: {effect[e]: .4f} [{ci_low[e]: .4f}, {ci_high[e]: .4f}]")

print(f"\n     headline stats: {headline: .4f}  CI: [{head_low: .4f}, {head_high: .4f}]")




#========================================================================================================================================

#lets go to tableau

visual = pd.DataFrame({"event time": event_window,
                         "effect": [effect[e] for e in event_window], 
                         "ci_low": [ci_low[e] for e in event_window],
                         "ci_high":[ci_high[e] for e in event_window],
                         "period": ["pre" if e<0 else "post" for e in event_window]})

visual.to_csv("event_study_results.csv")

file_path = os.path.abspath("event_study_results.csv")

print(f"path: {file_path}")

