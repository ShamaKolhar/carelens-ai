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
