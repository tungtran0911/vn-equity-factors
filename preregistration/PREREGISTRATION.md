# Pre-registration: limit-up days and one-month continuation on HOSE

Frozen 2026-09-26 (Asia/Ho_Chi_Minh), before any of the data that will test it
existed. The git commit that adds this file, tagged `prereg-2026-09`, is the proof of
timing. Everything below is fixed at that commit and is not to be changed; a
correction, if ever needed, goes in a dated addendum at the end of this file, and the
original text stays.

## What was known when this was written

The in-sample study (README, sections 4-5) covers formation months 2017-04 to
2026-07 on data through 2026-09-25. In it, two characteristics were significant in a
joint Fama-MacBeth regression and kept their sign and size in both halves of the
sample: the number of limit-up days in the formation month (negative) and the
one-month return (positive). The limit-up count was defined after seeing that MAX
saturates at the 7% band, so its in-sample estimate is not an unbiased estimate of
its true effect.

## Frozen artefacts

| Artefact | Identity |
|---|---|
| Characteristic definitions and scoring code | git tag `prereg-2026-09` |
| `frozen.json` | sha256 `821561076e319e569fe71e9e26498379c20814c05837cc3746baa62209af0521` |
| `lgbm_15l_100t.txt` | sha256 `121e00133b0c69fb0297ecf528eb583352b044d59b63cf875a9448e16201e44d` |

`factors/score.py` refuses to run if the model file does not match its recorded
hash.

## Hypotheses

Each is tested with a monthly Fama-MacBeth regression of next-month return on the
percentile ranks of all six characteristics (momentum 12-1, momentum extremity,
one-month return, idiosyncratic volatility, Dimson beta, limit-up days), on the
eligible HOSE universe, exactly as defined in the tagged code.

- **H1.** The slope on limit-up days is negative. In-sample: -1.18% a month.
- **H2.** The slope on the one-month return is positive. In-sample: +1.17% a month.

## Strategies

- **Primary, `signs`.** Score = rank(one-month return) - rank(limit-up days). Hold the
  top quintile, equal-weighted, long only, rebalanced monthly one session after
  formation. Benchmark: the equal-weighted scored universe. Cost: 0.4% round trip on
  turnover.
- **Secondary, `lgbm`.** The frozen gradient-boosted model, fitted once on all 112
  historical formation months, same portfolio rules. It exists to test, on genuinely
  new data, whether a flexible model adds anything to two theory-backed signals.

## Out-of-sample data

Formation months from 2026-09 onward. The August 2026 portfolio is excluded because
it is held through September, part of which was already observed at the freeze. A
month is scored once its holding period has ended and is appended to
`results/oos_ledger.csv`, which is never rewritten.

## Decision rule

- **Primary look at 60 scored months** (the formation month of 2031-08). A hypothesis
  is supported if its mean monthly slope has the predicted sign with a one-sided
  Newey-West t-statistic of 1.645 or more; otherwise it is not supported. Having the
  wrong sign at the primary look is a rejection.
- **Interim looks at 12, 24 and 36 months are descriptive only.** Nothing is accepted
  or rejected at an interim look, so repeated looking cannot inflate the error rate.
- The strategies are reported at every look with the same statistics; no threshold
  is set for them, since their purpose is to show what the hypotheses are worth after
  costs, not to be tested separately.

## Power

Probability of meeting the primary criterion if the true effect equals the in-sample
estimate. Because that estimate was found on the same data it is measured on, these
figures are upper bounds.

| Months of new data | H1 expected t | H1 power | H2 expected t | H2 power |
|---|---|---|---|---|
| 12 | 0.84 | 21% | 0.77 | 19% |
| 24 | 1.19 | 33% | 1.08 | 29% |
| 36 | 1.46 | 43% | 1.33 | 38% |
| 60 | 1.89 | 60% | 1.71 | 53% |

A failure to confirm at 60 months is therefore weak evidence against either
hypothesis. A wrong-signed estimate is not.

## Known threats

- **Universe.** Each scoring run uses the listing at that date, so a stock delisted
  during a holding period may be missing. Scoring monthly and never rewriting the
  ledger limits this to delistings within the month itself.
- **Provider changes.** The KBS endpoints are unofficial and may change. If the data
  source must change, both sources are to be run in parallel for at least three
  months and the difference recorded in an addendum before the switch.
- **Adjusted prices** are restated by the provider after every stock dividend. Returns
  are unaffected; levels are not used.
- **Cost** is an assumption (0.4% round trip), kept fixed.

## Addenda

None.
