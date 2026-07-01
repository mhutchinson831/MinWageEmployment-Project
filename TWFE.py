import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "minwage_employment_data.csv"
df = pd.read_csv(DATA_PATH)


#get rid of rows with missing important values


need = ["log_employment","log_min_wage","state","year"]

df = df.dropna(subset=need).copy()
df = df.reset_index(drop=True)




#do the regression




regression = smf.ols("log_employment ~ log_min_wage +C(state) + C(year)", data= df)

result = regression.fit(cov_type="cluster", cov_kwds={"groups": df["state"]})              #cluster error by state of course


#gimme the values
b=result.params["log_min_wage"]
se=result.bse["log_min_wage"]
p=result.pvalues["log_min_wage"]

ci_low, ci_high = result.conf_int().loc["log_min_wage"]




#see results 





print("Two-way fixed-effects estimate (state + year), clustered by state:")

print(f"Minimum-wage elasticity of employment : {b: .3f}")
print(f"Clustered standard error              : {se: .3f}")
print(f"p-value                               : {p: .3f}")
print(f"95% confidence interval               : [{ci_low: .3f}, {ci_high: .3f}]")
print()
print(f"Plain reading: a 10% higher minimum wage is associated with roughly a"
      f" {b * 10: .2f}% change in Leisure & Hospitality employment.")

