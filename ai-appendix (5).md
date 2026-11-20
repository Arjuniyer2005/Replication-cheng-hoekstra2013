# AI Appendix

## Statement

ChatGPT (GPT-6) was used to assist with Python code for the robustness analyses in Section 3 and the dataset-download script in Section 6. The code was reviewed, revised, and checked against the results generated in the notebook.

The P.R.I.M.E. prompts below were reconstructed from the coding discussions, while the code reflects the final implementations.

## One Entry per Use

### Section 3, Exercise 1 — Modern Difference-in-Differences

**The P.R.I.M.E. prompt, in full**

- **[Prep]** Act as an econometrics research assistant specializing in difference-in-differences estimation.
- **[Request]** I am replicating Cheng and Hoekstra (2013), which estimates the effect of Castle Doctrine laws on homicide rates. My dataset contains `sid`, `year`, `effyear`, `cdl`, `l_homicide`, and `popwt`. Help me implement group-time treatment effects using never-treated and not-yet-treated states as comparison groups.
- **[Iterate]** Use Python, pandas, and NumPy. Work with my existing `castle` DataFrame. Do not change my original TWFE regression, and avoid using already-treated states as controls.
- **[Mechanism Check]** Explain why traditional TWFE may produce misleading estimates when treatment is adopted at different times and effects vary across states or periods.
- **[Evaluate]** Calculate the overall treatment effect under both comparison groups. Compare the results with my replicated TWFE estimate and explain whether the positive homicide effect remains.

**The verification log**

**1. Prompt:** The complete P.R.I.M.E. prompt is provided above.

**2. Generated code:**

```python
def att_gt(outcome, weighted, control="never", first="effyear", data=None):
    d = (castle if data is None else data).copy()
    g_of = d.groupby("sid")["effyear"].first()

    if first == "full":
        g_of = g_of + 1

    d["g"] = d["sid"].map(g_of)
    w = d["popwt"] if weighted else pd.Series(1.0, index=d.index)
    d["w"] = w

    def wmean(rows):
        return np.average(rows[outcome], weights=rows["w"])

    cells = []

    for g in sorted(g_of.dropna().unique()):
        coh = d[d["g"] == g]
        base = g - 1

        for t in sorted(d["year"].unique()):
            if t == base:
                continue

            if control == "never":
                ctl = d[d["g"].isna()]
            else:
                ctl = d[
                    d["g"].isna() |
                    (d["g"] > max(t, base))
                ]

            if control != "never":
                ctl = ctl[ctl["g"] != g]

            a = (
                wmean(coh[coh.year == t])
                - wmean(coh[coh.year == base])
            )

            b = (
                wmean(ctl[ctl.year == t])
                - wmean(ctl[ctl.year == base])
            )

            cells.append({
                "g": int(g),
                "t": int(t),
                "e": int(t - g),
                "att": a - b,
                "size": (
                    coh[coh.year == t]["w"].sum()
                    if weighted
                    else coh["sid"].nunique()
                )
            })

    cells = pd.DataFrame(cells)
    post = cells[cells["e"] >= 0]

    overall = np.average(
        post["att"],
        weights=post["size"]
    )

    by_e = cells.groupby("e").apply(
        lambda x: np.average(
            x["att"],
            weights=x["size"]
        ),
        include_groups=False
    )

    return overall, by_e, cells
```

**3. What I changed and why:** I used the group-time estimator in the notebook to compare two control-group definitions separately. I also retained the original TWFE estimate as the benchmark rather than replacing the baseline regression.

**4. What I verified:** I compared the resulting estimates with the original TWFE coefficient and checked the implied percentage effects.

- Original TWFE: +8.34%.
- Never-treated controls: +11.42%.
- Not-yet-treated controls: +11.57%.

Both alternative estimates were positive. The implementation is a simplified group-time estimator rather than the full Callaway–Sant'Anna procedure.

---

### Section 3, Exercise 2 — Treatment-Timing Sensitivity

**The P.R.I.M.E. prompt, in full**

- **[Prep]** Act as an applied econometrics assistant helping me conduct a robustness test.
- **[Request]** My replication of Cheng and Hoekstra (2013) produces an approximately 8.34% increase in homicide rates. I want to test whether the result changes if treatment starts in the first full calendar year after Castle Doctrine adoption. The dataset includes `year`, `effyear`, `sid`, `l_homicide`, `cdl`, and `popwt`.
- **[Iterate]** Use statsmodels in Python. Keep the original population-weighted TWFE specification, state and year fixed effects, and state-clustered standard errors. Change only how treatment is defined.
- **[Mechanism Check]** Explain why including the adoption year could influence the estimate when a law is effective for only part of that year.
- **[Evaluate]** Report both coefficients, standard errors, p-values, and percentage effects. Determine whether the positive relationship survives the alternative definition.

**The verification log**

**1. Prompt:** The complete P.R.I.M.E. prompt is provided above.

**2. Generated code:**

```python
df = castle.dropna(
    subset=["l_homicide", "cdl", "sid", "year", "popwt"]
).copy()

df["cdl_full_year"] = (
    df["effyear"].notna() &
    (df["year"] > df["effyear"])
).astype(int)

results = []

for name, treatment in [
    ("Original treatment timing", "cdl"),
    ("First full year only", "cdl_full_year")
]:
    fit = smf.wls(
        f"l_homicide ~ {treatment} + C(sid) + C(year)",
        data=df,
        weights=df["popwt"]
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["sid"]}
    )

    results.append({
        "Specification": name,
        "Coefficient": fit.params[treatment],
        "Standard Error": fit.bse[treatment],
        "P-value": fit.pvalues[treatment],
        "Effect (%)": 100 * (
            np.exp(fit.params[treatment]) - 1
        )
    })

timing_results = pd.DataFrame(results)

print(timing_results.round(4).to_string(index=False))
```

**3. What I changed and why:** I constructed `cdl_full_year` using `year > effyear` so that states would only be considered treated beginning in the calendar year after adoption. This isolates sensitivity to the treatment-timing definition.

**4. What I verified:** I compared the new regression against the original specification, keeping the model structure unchanged.

- Original treatment timing: +8.34%.
- First-full-year treatment: +7.85%.

The revised estimate remained positive and statistically significant. The relatively small change suggests that the result is not particularly sensitive to this treatment-timing definition.

---

### Section 3, Exercise 3 — Pre-Treatment Placebo Test

**The P.R.I.M.E. prompt, in full**

- **[Prep]** Act as an econometrics assistant specializing in causal inference and placebo testing.
- **[Request]** I want to run a placebo test for my replication of Cheng and Hoekstra (2013). Create a fake Castle Doctrine treatment variable beginning two years before the actual adoption date. The dataset has `sid`, `year`, `effyear`, `l_homicide`, and `popwt`.
- **[Iterate]** Use my existing `castle` DataFrame and the original weighted TWFE regression structure. Include state and year fixed effects, cluster standard errors by state, and exclude observations after actual adoption for treated states.
- **[Mechanism Check]** Explain how this placebo can identify evidence of changes preceding the law and why a statistically insignificant placebo does not necessarily prove parallel trends.
- **[Evaluate]** Report the placebo coefficient, standard error, p-value, and exact percentage effect.

**The verification log**

**1. Prompt:** The complete P.R.I.M.E. prompt is provided above.

**2. Generated code:**

```python
d = castle[
    castle["effyear"].isna() |
    (castle["year"] < castle["effyear"])
].copy()

d["fake_cdl"] = (
    d["effyear"].notna() &
    (d["year"] >= d["effyear"] - 2)
).astype(int)

placebo_fit = smf.wls(
    "l_homicide ~ fake_cdl + C(sid) + C(year)",
    data=d,
    weights=d["popwt"]
).fit(
    cov_type="cluster",
    cov_kwds={"groups": d["sid"]}
)

print("Pre-treatment placebo")
print("Coefficient:", placebo_fit.params["fake_cdl"])
print("Standard error:", placebo_fit.bse["fake_cdl"])
print("P-value:", placebo_fit.pvalues["fake_cdl"])
```

**3. What I changed and why:** I restricted adopting states to their pre-adoption observations while retaining never-treated comparison states. This prevents actual post-treatment effects from affecting the placebo regression.

**4. What I verified:** I checked the coefficient, standard error, and p-value against the notebook output.

- Coefficient: approximately −0.02881.
- Standard error: approximately 0.02578.
- Percentage effect: −2.84%.
- P-value: 0.264.

The placebo estimate was not statistically significant. This provides some reassurance but does not establish that the parallel-trends assumption holds.

---

### Section 3, Exercise 4 — Leave-One-State-Out Analysis

**The P.R.I.M.E. prompt, in full**

- **[Prep]** Act as an econometrics and Python programming assistant.
- **[Request]** I am replicating the effect of Castle Doctrine laws on homicide rates. I want to determine whether the estimated effect is driven by one particular state. Write code to re-estimate my baseline TWFE regression after excluding one state at a time.
- **[Iterate]** Use the `castle` DataFrame and `sid` as the state identifier. Preserve `l_homicide`, `cdl`, population weights, state and year fixed effects, and state-clustered standard errors. Run the regression for every state automatically.
- **[Mechanism Check]** Explain how leave-one-state-out estimation identifies influential states and why stability across exclusions strengthens confidence in the result.
- **[Evaluate]** Report the range of estimated percentage effects, identify the smallest and largest estimates, and determine whether excluding any state reverses the coefficient.

**The verification log**

**1. Prompt:** The complete P.R.I.M.E. prompt is provided above.

**2. Generated code:**

```python
loo_results = []

for state in castle["sid"].unique():
    d = castle[castle["sid"] != state].copy()

    fit = smf.wls(
        "l_homicide ~ cdl + C(sid) + C(year)",
        data=d,
        weights=d["popwt"]
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": d["sid"]}
    )

    loo_results.append({
        "Excluded State": state,
        "Coefficient": fit.params["cdl"],
        "Standard Error": fit.bse["cdl"],
        "P-value": fit.pvalues["cdl"]
    })

loo_results = pd.DataFrame(loo_results)

loo_results["Effect (%)"] = 100 * (
    np.exp(loo_results["Coefficient"]) - 1
)

print(loo_results["Effect (%)"].describe().round(3))

print("\nSmallest estimates:")
print(
    loo_results.nsmallest(
        5, "Effect (%)"
    ).to_string(index=False)
)

print("\nLargest estimates:")
print(
    loo_results.nlargest(
        5, "Effect (%)"
    ).to_string(index=False)
)

loo_results.to_csv("leave_one_out.csv", index=False)
```

**3. What I changed and why:** I implemented the procedure systematically across all 50 states rather than removing only selected states. I also retained the full results in a DataFrame and exported them to `leave_one_out.csv`.

**4. What I verified:** I examined the distribution of all 50 estimates and compared the minimum and maximum against the baseline.

- Minimum estimated effect: +6.25%.
- Maximum estimated effect: +9.80%.
- All estimates remained positive.

The finding was not driven entirely by any single state.

---

### Section 3 — Population-Weighting Sensitivity

**The P.R.I.M.E. prompt, in full**

- **[Prep]** Act as an applied econometrics assistant working with Python and statsmodels.
- **[Request]** My Cheng and Hoekstra replication uses a population-weighted TWFE regression. I want to check whether removing the population weights changes the estimated homicide effect. The relevant variables are `l_homicide`, `cdl`, `sid`, `year`, and `popwt`.
- **[Iterate]** Keep the same dependent variable, treatment variable, state and year fixed effects, and standard errors clustered by state. Estimate the weighted model using WLS and the unweighted model using OLS.
- **[Mechanism Check]** Explain why weighting by population changes how much influence each state has on the estimate and why the standard errors might also change.
- **[Evaluate]** Compare coefficients, standard errors, p-values, and exact percentage effects.

**The verification log**

**1. Prompt:** The complete P.R.I.M.E. prompt is provided above.

**2. Generated code:**

```python
formula = "l_homicide ~ cdl + C(sid) + C(year)"

weighted_fit = smf.wls(
    formula,
    data=castle,
    weights=castle["popwt"]
).fit(
    cov_type="cluster",
    cov_kwds={"groups": castle["sid"]}
)

unweighted_fit = smf.ols(
    formula,
    data=castle
).fit(
    cov_type="cluster",
    cov_kwds={"groups": castle["sid"]}
)

comparison = pd.DataFrame({
    "Specification": [
        "Population-weighted",
        "Unweighted"
    ],
    "Coefficient": [
        weighted_fit.params["cdl"],
        unweighted_fit.params["cdl"]
    ],
    "Standard Error": [
        weighted_fit.bse["cdl"],
        unweighted_fit.bse["cdl"]
    ],
    "P-value": [
        weighted_fit.pvalues["cdl"],
        unweighted_fit.pvalues["cdl"]
    ]
})

comparison["Effect (%)"] = 100 * (
    np.exp(comparison["Coefficient"]) - 1
)

print(comparison.round(4).to_string(index=False))
```

**3. What I changed and why:** I added an unweighted OLS specification alongside the original weighted WLS regression while keeping the remaining model components identical.

**4. What I verified:** I compared the results from both regressions.

- Population-weighted estimate: +8.34%, p ≈ 0.026.
- Unweighted estimate: +9.17%, p ≈ 0.190.

The unweighted estimate was larger but no longer statistically significant at the 5% level. This indicates that statistical inference is sensitive to population weighting.

---

### Section 6 — Dataset Download Script

**The P.R.I.M.E. prompt, in full**

- **[Prep]** Act as a Python programming assistant helping make an economics replication project reproducible.
- **[Request]** Create a Python script called `download_data.py` to download the Castle Doctrine dataset used in my replication of Cheng and Hoekstra (2013). The dataset is publicly available at `https://raw.githubusercontent.com/scunning1975/mixtape/master/castle.dta`.
- **[Iterate]** Use only Python's standard library. Save the dataset in a folder called `data` and name it `castle.dta`. Create the folder automatically and avoid downloading the file again if it already exists.
- **[Mechanism Check]** Explain how the script handles the directory path, downloads the dataset, and avoids leaving an empty file after a failed download.
- **[Evaluate]** Produce a complete script that can be run from the repository root and prints confirmation when the download succeeds.

**The verification log**

**1. Original request:** "lets start with download_data"

**2. Generated code:**

```python
"""Download the Castle Doctrine dataset."""

from pathlib import Path
from urllib.request import urlopen

DATA_URL = "https://raw.githubusercontent.com/scunning1975/mixtape/master/castle.dta"
DATA_PATH = Path(__file__).resolve().parent / "data" / "castle.dta"


def main():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DATA_PATH.is_file() and DATA_PATH.stat().st_size > 0:
        print(f"Dataset already exists: {DATA_PATH}")
        return

    try:
        with urlopen(DATA_URL, timeout=30) as response:
            content = response.read()

        if not content:
            raise ValueError("Downloaded dataset is empty")

        DATA_PATH.write_bytes(content)
    except Exception:
        DATA_PATH.unlink(missing_ok=True)
        raise

    print(f"Downloaded dataset to {DATA_PATH} ({len(content):,} bytes)")


if __name__ == "__main__":
    main()
```

**3. What I changed and why:** The script was organized to place the downloaded dataset in a dedicated `data` directory rather than mixing the raw data with the notebook and repository documentation.

**4. What I verified:** I checked that the URL corresponds to the dataset used by the notebook, that the destination is constructed relative to the script location, and that the script creates the output directory when needed.

The code includes checks for an existing nonempty file and an empty download. A successful clean-checkout execution has not yet been independently verified.
