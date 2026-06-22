import pandas as pd
print(pd.read_csv("results/baseline.csv").tail())
print(pd.read_csv("results/attack_fedavg.csv").tail())
print(pd.read_csv("results/attack_securefedavg.csv").tail())

print(pd.read_csv("results/baseline_eval.csv").tail())
print(pd.read_csv("results/attack_fedavg_eval.csv").tail())
print(pd.read_csv("results/attack_securefedavg_eval.csv").tail())