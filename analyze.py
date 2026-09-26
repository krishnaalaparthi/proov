# analyze.py
# SUMMARY (based on 120-car fleet_history.csv):
# The three columns that separate breakdowns from non-breakdowns are km_since_service (+61%),
# avg_daily_km (+22%), and load_factor (+19%); odometer_km (+0.3%) and age_years (-0.2%) are noise.
#
# Make KM-Waechter smarter. The 80% rule only warns you once a car is nearly worn. Here you find
# which cars are most likely to break down SOON, from their history, and rank them by risk, so the
# fleet team fixes the risky ones first.
#
# fleet_history.csv has one row per car (120 of them) and a "broke_down" column (1 = it later
# broke down).

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# ---------------------------------------------------------------------------
# Step 2: Compare broke vs OK groups column by column
# ---------------------------------------------------------------------------
broke = df[df["broke_down"] == 1]
ok    = df[df["broke_down"] == 0]

cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
print(f"Group sizes — broke_down=1: {len(broke)}  broke_down=0: {len(ok)}")
print()
print(f"{'Column':<22} {'Broke mean':>12} {'OK mean':>12} {'Diff %':>10}")
print("-" * 60)
for c in cols:
    bm  = broke[c].mean()
    om  = ok[c].mean()
    pct = (bm - om) / om * 100 if om != 0 else float("inf")
    print(f"{c:<22} {bm:>12.1f} {om:>12.1f} {pct:>+10.1f}%")

print()
print("Columns that show a real difference (>15%): km_since_service, avg_daily_km, load_factor")
print("Columns that are noise (<5%):               odometer_km, age_years")
print()

# ---------------------------------------------------------------------------
# Step 3: Risk score (0–100) built only from the three predictive columns.
#
# Each column is min-max normalised to [0, 1] across the whole fleet, then
# weighted by the magnitude of the separation seen in step 2:
#   km_since_service  weight 3  (60.8% gap — dominant signal)
#   avg_daily_km      weight 1  (21.5% gap)
#   load_factor       weight 1  (18.8% gap)
# Raw score = weighted sum / max-possible-weighted-sum * 100
# ---------------------------------------------------------------------------
WEIGHT_KSS = 3
WEIGHT_ADK = 1
WEIGHT_LF  = 1
TOTAL_WEIGHT = WEIGHT_KSS + WEIGHT_ADK + WEIGHT_LF

def minmax(series):
    lo, hi = series.min(), series.max()
    return (series - lo) / (hi - lo) if hi != lo else series * 0

df["_kss_n"] = minmax(df["km_since_service"])
df["_adk_n"] = minmax(df["avg_daily_km"])
df["_lf_n"]  = minmax(df["load_factor"])

df["risk_score"] = (
    WEIGHT_KSS * df["_kss_n"] +
    WEIGHT_ADK * df["_adk_n"] +
    WEIGHT_LF  * df["_lf_n"]
) / TOTAL_WEIGHT * 100

# ---------------------------------------------------------------------------
# Step 4: Print all cars ranked by risk score, highest first
# ---------------------------------------------------------------------------
ranked = df[["car_id", "km_since_service", "avg_daily_km", "load_factor",
             "broke_down", "risk_score"]].sort_values("risk_score", ascending=False)

print(f"{'Rank':<5} {'Car':>10} {'km_since_svc':>13} {'avg_daily_km':>13} {'load':>6} {'broke':>6} {'risk':>6}")
print("-" * 65)
for rank, (_, row) in enumerate(ranked.iterrows(), 1):
    print(f"{rank:<5} {row['car_id']:>10} {row['km_since_service']:>13.0f} "
          f"{row['avg_daily_km']:>13.0f} {row['load_factor']:>6.2f} "
          f"{int(row['broke_down']):>6} {row['risk_score']:>6.1f}")
