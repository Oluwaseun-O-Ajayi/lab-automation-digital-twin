# Case studies

Four worked examples. The first checks the simulation engine against results
known from queueing theory; the other three use an illustrative plate-screening
workcell defined in `examples/_common.py`. The workcell's capacities and times
are round numbers chosen for demonstration and do not describe any specific
laboratory or vendor system. Times are in minutes.

```bash
python examples/case_study_1_validation.py
python examples/case_study_2_bottleneck.py
python examples/case_study_3_what_if.py
python examples/case_study_4_traceability.py
```

Results are written to `examples/case_study_results/`. The numbers below were
produced with version 2.0.0; random runs use fixed seeds and are reproducible.

| Case | Application |
|---|---|
| 1 | Validating the engine against exact and queueing-theory results |
| 2 | Finding the device that limits throughput |
| 3 | Comparing equipment changes before buying anything |
| 4 | Reconstructing and checking every plate's chain of custody |

**The illustrative workcell.** Each plate goes Storage, Liquid handler, Incubator,
Plate reader, Storage, with 1.5 min transport between steps.

| Device | Slots | Time per plate |
|---|---|---|
| Storage | 10 | 0.5 |
| Liquid handler | 1 | 6 |
| Incubator | 8 | 60 |
| Plate reader | 1 | 4 |

## Case 1: Validation against theory

**Question.** Does the engine reproduce results that are known exactly?

**Result (a), flow line.** With all samples present at time 0, one slot per
device and fixed times, the makespan of n samples is the sum of the times plus
(n - 1) times the longest one. The simulation matches this exactly in all four
configurations tested, for example 608.0 min for 100 samples through five
devices of 3, 1, 6, 2 and 2 min.

**Result (b), single queue with random arrivals and service (M/M/1).** Theory
gives utilization rho and mean wait rho / (mu - lambda). With 100,000 samples:

| rho | Utilization (theory / simulated) | Mean wait (theory / simulated) |
|---|---|---|
| 0.5 | 0.500 / 0.502 | 1.000 / 1.017 |
| 0.7 | 0.700 / 0.703 | 2.333 / 2.419 |
| 0.9 | 0.900 / 0.903 | 9.000 / 9.213 |

**What it shows.** Deterministic results are reproduced exactly, and random
results agree with theory to within 4%, the remaining difference being sampling
error, which is largest near saturation. The test suite repeats both checks on
every push.

## Case 2: Finding the bottleneck

**Question.** Which device limits throughput, and does the simulation agree with
a capacity calculation?

**Result.** A device with c slots and time p per plate, visited k times per
plate, can handle at most c / (k p) plates per unit time. That gives 600
plates/hour for storage, 10 for the liquid handler, 8 for the incubator and 15
for the plate reader, so the incubator is the predicted bottleneck. With 96
plates queued at time 0, the simulation also identifies the incubator (92.4%
utilization) and achieves 7.39 plates/hour, 92.4% of the 8.00 ceiling; the rest
is the time to fill and empty the line.

**What it shows.** The liquid handler has the longest queue (up to 95 plates
waiting), but the incubator sets the pace. The queue forms in front of the
liquid handler simply because it is first in line. Queue length alone can point
to the wrong device; utilization against capacity does not.

## Case 3: What-if analysis

**Question.** For 48 plates arriving every 5 minutes, which change shortens the
run most?

**Result.**

| Scenario | Makespan | Mean turnaround | 95th percentile | Mean wait | Bottleneck |
|---|---|---|---|---|---|
| Baseline | 419 | 130.5 | 181.7 | 53.5 | Incubator |
| 12 incubator slots | 359 | 100.5 | 121.7 | 23.5 | Liquid handler |
| 2 liquid handlers | 412 | 127.0 | 177.0 | 50.0 | Incubator |
| Both | 312 | 77.0 | 77.0 | 0.0 | Incubator |

**What it shows.** A second liquid handler alone saves only 7 minutes, because
the incubator still limits the run. More incubator slots saves 60 minutes and
moves the bottleneck to the liquid handler. Only both changes together remove
all waiting and reach the lower bound of 312 minutes (last arrival at 235 min
plus one plate's 77 min path). Simulation shows which purchase helps before the
money is spent.

## Case 4: Traceability under variable times

**Question.** When times vary from plate to plate, can every plate's chain of
custody be reconstructed, and is a missing record detected?

**Set-up.** Liquid handler 6 +/- 1 min, incubator 60 +/- 5 min, plate reader 3 to
5 min, exponential transport with mean 1.5 min, 48 plates arriving at random
with mean spacing 5 min, seed 2026.

**Result.** The audit log gives each plate's full history. Plate P07, for
example, arrived at 22.88 min, waited in the liquid-handler queue from 23.46 to
36.46 min and completed at 118.19 min. All 48 plates pass the traceability check
(every step started and finished in workflow order, then completed). After the
plate-reader records of P19 are deleted, the check flags P19 and only P19. Mean
turnaround is 131.3 min and the 95th percentile 179.3 min.

**What it shows.** Every event carries a simulated time stamp, so a complete
chain of custody exists for each sample, and a gap in the record is caught
automatically. The 95th-percentile turnaround is 48 min above the mean, which is
the planning figure that matters when results are promised by a deadline.
