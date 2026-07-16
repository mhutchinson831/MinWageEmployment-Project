import pandas as pd
import differences
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent / "minwage_employment_data.csv"
df = pd.read_csv(DATA_PATH)
df.dropna(subset=["log_employment", "eff_min_wage","federal_min_wage"])

treated_diff = 0.01

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

d = df[df["state"].isin(treated_states)].copy()

d["cohort"] = d["state"].map(onset).astype(int)

d = d.set_index(["state", "year"]).sort_index()


#========================================================================================================================================

att = differences.ATTgt(data = d, cohort_column = "cohort", base_period="universal")
att.fit(formula = "log_employment", control_group = "not_yet_treated")

att.aggregate("event").to_csv("differences_event_study.csv")