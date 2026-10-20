import pandas as pd

df = pd.read_csv("data/raw/diabetic_data.csv")

print("original shape:", df.shape)

drop_weight_df = df.drop(columns=["weight"])

print("after dropping weight:", drop_weight_df.shape)
print("'weight' still in df.columns:", "weight" in df.columns)
print("'weight' in drop_weight_df.columns:", "weight" in drop_weight_df.columns)
print("exactly one column removed:", drop_weight_df.shape[1] == df.shape[1] - 1)
print()

clean_df = drop_weight_df.copy()
clean_df["medical_specialty"] = clean_df["medical_specialty"].replace(
    "?", "Missing"
)

print("medical_specialty '?' count before:", (drop_weight_df["medical_specialty"] == "?").sum())
print("medical_specialty '?' count after:", (clean_df["medical_specialty"] == "?").sum())
print("medical_specialty 'Missing' count after:", (clean_df["medical_specialty"] == "Missing").sum())
print()

clean_df["payer_code"] = clean_df["payer_code"].replace("?", "Missing")

print("payer_code '?' count before:", (drop_weight_df["payer_code"] == "?").sum())
print("payer_code '?' count after:", (clean_df["payer_code"] == "?").sum())
print("payer_code 'Missing' count after:", (clean_df["payer_code"] == "Missing").sum())
print()


clean_df["race"] = clean_df["race"].replace("?", "Missing")

print("race '?' count before:", (drop_weight_df["race"] == "?").sum())
print("race '?' count after:", (clean_df["race"] == "?").sum())
print("race 'Missing' count after:", (clean_df["race"] == "Missing").sum())
print()

diag_cols = ["diag_1", "diag_2", "diag_3"]
for col in diag_cols:
    clean_df[col] = clean_df[col].replace("?", "Missing")

for col in diag_cols:
    before = (drop_weight_df[col] == "?").sum()
    after_qmark = (clean_df[col] == "?").sum()
    after_missing = (clean_df[col] == "Missing").sum()
    print(f"{col} '?' count before: {before}")
    print(f"{col} '?' count after: {after_qmark}")
    print(f"{col} 'Missing' count after: {after_missing}")
print()

print("final clean_df shape:", clean_df.shape)
print("any remaining '?' anywhere:", (clean_df == "?").sum().sum())
print()

# Target: readmitted has 3 raw values (<30, >30, NO). Positive class = <30
# (matches the CMS 30-day readmission definition and the actual business
# question). >30 is merged into the negative class alongside NO: from the
# perspective of "who needs follow-up in the next 30 days", a day-45
# readmission and no readmission lead to the same action, so modeling a
# third class would add complexity without changing the decision. This is
# a documented scope choice: longer-horizon readmission risk is out of
# scope, not something the model is blind to by accident.
clean_df["readmitted_30d"] = (clean_df["readmitted"] == "<30").astype(int)

print("readmitted_30d value counts:")
print(clean_df["readmitted_30d"].value_counts())
print()

# Exclusions: discharge_disposition_id 11/19/20/21 = expired. These rows
# would be labeled readmitted_30d=0, but that 0 means "cannot be
# readmitted" (died), not "low risk" -- leaving them in would teach the
# model that signs of critical illness predict low readmission risk,
# which is backwards. IDs 13/14 = hospice: patients are alive, but hospice
# care plans actively avoid further hospitalization regardless of
# clinical trajectory. Verified empirically: hospice rows have a <30
# readmission rate of 5.58% vs 11.16% overall -- a confound, not a
# genuine low-risk signal. Both groups are excluded.
expired_ids = [11, 19, 20, 21]
hospice_ids = [13, 14]
exclude_ids = expired_ids + hospice_ids

before_exclusion = len(clean_df)
model_df = clean_df[~clean_df["discharge_disposition_id"].isin(exclude_ids)].copy()
after_exclusion = len(model_df)

print("rows before exclusion:", before_exclusion)
print("rows after exclusion:", after_exclusion)
print("rows excluded:", before_exclusion - after_exclusion)
print(
    "expired + hospice row count (expected excluded):",
    clean_df["discharge_disposition_id"].isin(exclude_ids).sum(),
)
print(
    "any excluded discharge_disposition_id remaining in model_df:",
    model_df["discharge_disposition_id"].isin(exclude_ids).any(),
)
print()
print("final model_df shape:", model_df.shape)
print("readmitted_30d rate in model_df:", model_df["readmitted_30d"].mean().round(4))
