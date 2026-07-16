# Minimum Wage and Employment: A Difference-in-Differences Study

**Does raising the minimum wage cost jobs?** I use U.S. state data (2000–2023) to
estimate the effect of a state raising its minimum wage above the federal floor
on employment in Leisure & Hospitality — the sector most exposed to the minimum
wage. The focus of the project is doing the causal inference *carefully*: starting
with a standard model, showing where it breaks, and fixing the design.

## The short version

- A standard **fixed-effects regression** gives one pooled number but can't tell
  you whether the comparison is fair to begin with.
- My **first difference-in-differences** attempt compared treated states to
  states that never raised their wage. The problem: those groups were already on
  different paths *before* any policy change, so the result wasn't causal.
- My **improved difference-in-differences** compares each treated state to states
  that hadn't raised their wage *yet*. This produces flat pre-trends (a fairer
  comparison) and a clear result, with confidence intervals from a bootstrap.
- A **modern estimator (Callaway & Sant'Anna)** is used as a second opinion and
  points the same way.

## Main result

![Event-study estimates: employment is flat before a minimum-wage increase and falls afterward, with 95% bootstrap confidence intervals.](results/event_study.png)

After a state raises its minimum wage above the federal floor, Leisure &
Hospitality employment growth falls by roughly **2–3%**, averaging about
**−2.4%** over the following five years. The effect grows for a few years after
the change, and the pre-change period is flat — which is what you want to see
before trusting a difference-in-differences result.

| Years after wage increase | Estimated effect | Significant? |
| --- | --- | --- |
| Before the increase | ~0% (flat) | No — good sign |
| Year 1 | −1.6% | Yes |
| Year 2 | −3.0% | Yes |
| Year 3 | −3.4% | Yes |
| Year 5 | −2.3% | Yes |

## Limitations

- **The Great Recession overlaps many treatment windows.** 16 of the 23 treated
  states used in the improved model raised their minimum wage during 2006–2008,
  so their post-increase employment is measured right through the 2008–09
  recession. Some of the estimated decline could reflect the downturn rather than
  the minimum wage itself. (Widen the lens to any state whose 5-years-before to
  5-years-after window merely *touches* the recession and it's 19 of 23 — either
  way, the recession is a real confounder here.)
- This is observational data, so the causal reading depends on the assumption
  that treated and control states would otherwise have moved together. The flat
  pre-trends support that, but can't prove it.
- Treatment is "did the state raise its wage above the federal floor," not the
  size of the raise — so this is the average effect of *being such a state*, not
  a per-dollar figure.
- Employment covers Leisure & Hospitality only; other sectors and effects on
  hours (vs. headcount) are out of scope.

## Data

All data is pulled from [FRED](https://fred.stlouisfed.org/) by
[`src/DataExtraction.py`](src/DataExtraction.py): state minimum wages, Leisure &
Hospitality employment by state, and the federal minimum wage, 2000–2023 (all 50
states + DC). It builds one panel in
[`data/minwage_employment_data.csv`](data/minwage_employment_data.csv).

## Repository

```
src/
  DataExtraction.py      # Builds the dataset from FRED
  TWFE.py                # Fixed-effects regression
  BadDiD.py              # First DiD attempt (fails the pre-trend check)
  betterDid.py           # Improved DiD (not-yet-treated controls + bootstrap)
  DifferencesLibrary.py  # Callaway & Sant'Anna robustness check
  plot_event_study.py    # Builds the event-study chart above
data/                    # The panel dataset
results/                 # Event-study output tables
```

## Run it

```bash
pip install -r requirements.txt
python src/TWFE.py
python src/BadDiD.py
python src/betterDid.py
python src/DifferencesLibrary.py
python src/plot_event_study.py   # regenerates the chart above
```

**Tools:** Python · pandas · NumPy · statsmodels · matplotlib · the
`differences` package · bootstrap inference.
