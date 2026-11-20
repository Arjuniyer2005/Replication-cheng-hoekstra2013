# Replication-cheng-hoekstra2013
# Castle Doctrine Laws and Homicide: Replication of Cheng & Hoekstra (2013)

## Research Question

Do expansions of Castle Doctrine and stand-your-ground self-defense laws deter crime, or are they associated with increased homicide rates?

This project replicates Cheng and Hoekstra's (2013) findings and evaluates whether their results remain consistent under alternative statistical methods and assumptions.

**Original Paper:** Cheng, Cheng, and Mark Hoekstra (2013). “Does Strengthening Self-Defense Law Deter Crime or Escalate Violence? Evidence from Expansions to Castle Doctrine.” *Journal of Human Resources*, 48(3), 821–854.

## Original Findings and Replication

Cheng and Hoekstra (2013) found that expanding Castle Doctrine laws was associated with an approximately 8% increase in homicide rates, with no significant reductions in burglary, robbery, or aggravated assault.

My replication reproduces the original homicide coefficient of approximately 0.0801, corresponding to an 8.34% increase.

| Metric | Original Paper | My Replication |
|---|---|---|
| Coefficient | 0.0801 | 0.080064 |
| Standard Error | 0.0342 | 0.0359 |
| Estimated Effect | Approximately +8% | +8.34% |

The point estimates match to four decimal places. The small difference in standard errors may reflect differences in statistical software or finite-sample corrections, although the exact cause remains unresolved.

## Methodology

The original study uses a difference-in-differences (DiD) approach with state and year fixed effects. The analysis compares changes in homicide rates between states that expanded Castle Doctrine laws and states that did not.

The dataset covers 50 US states from 2000 to 2010.

## Robustness Tests

I conducted four main robustness exercises to evaluate the original finding.

### 1. Modern Difference-in-Differences

I used a simplified group-time DiD approach with never-treated and not-yet-treated comparison groups to avoid using already-treated states as controls.

- Never-treated controls: +11.42%
- Not-yet-treated controls: +11.57%

Both estimates remain positive and are larger than the original 8.34% estimate.

### 2. Treatment-Timing Sensitivity

I redefined treatment to begin in the first full year following adoption instead of including partial treatment during the adoption year.

The estimated homicide increase was 7.85%, suggesting limited sensitivity to treatment timing.

### 3. Pre-Treatment Placebo

I assigned a hypothetical treatment date two years before actual adoption to test whether homicide rates were already changing.

The estimated placebo effect was −2.84% (p = 0.264), which was not statistically significant.

### 4. Leave-One-State-Out Analysis

I reran the original regression 50 times, excluding one state each time.

The estimated homicide increases ranged from 6.25% to 9.80%, indicating that no individual state reversed the positive result.

## Additional Analyses

I also examined event-study estimates and population-weighting sensitivity.

The event study showed positive post-adoption effects but also some positive pre-adoption estimates, raising concerns about the parallel-trends assumption.

Removing population weights increased the estimated homicide effect to 9.17%, although the result was no longer statistically significant.

## Conclusion

My findings generally support Cheng and Hoekstra's conclusion that expanding Castle Doctrine laws is associated with increased homicide rates. The positive relationship remains across the main robustness tests, although the estimated magnitude varies.

However, differences in statistical significance and pre-treatment trends suggest that the precise causal effect remains uncertain.

## Dataset

The publicly available dataset is from Scott Cunningham's *Mixtape* repository:

https://raw.githubusercontent.com/scunning1975/mixtape/master/castle.dta

The repository includes `download_data.py`, which downloads the dataset and saves it to `data/castle.dta`.

## Reproducing the Results

### 1. Install Dependencies

Using Python 3, run:

```bash
python -m pip install -r requirements.txt
```

### 2. Download the Dataset

```bash
python download_data.py
```

The notebook currently loads the same dataset directly from GitHub. An internet connection is therefore required when executing it.

### 3. Run the Analysis

From the repository's root directory, execute:

```bash
python -m jupyter nbconvert --to notebook --execute cheng_hoekstra_replication.ipynb --output cheng_hoekstra_executed.ipynb --ExecutePreprocessor.timeout=1200
```

This command executes the complete analysis and produces the replication and robustness results.

The notebook generates the following CSV files:

- `did_comparison.csv`
- `event_study_results.csv`
- `robustness_results.csv`
- `leave_one_out.csv`

**Reproducibility status:** The notebook has saved successful execution outputs. The complete command has not yet been independently verified from a clean repository checkout.

## Repository Files

- `cheng_hoekstra_replication.ipynb` — Main analysis notebook.
- `download_data.py` — Dataset download script.
- `requirements.txt` — Pinned Python dependencies.
- `ai-appendix.md` — Documentation of AI assistance and required transcripts.
- `README.md` — Project documentation.

## AI Disclosure

AI assistance was used in developing code output. Detailed documentation and the required transcripts are provided in `ai-appendix.md`.
