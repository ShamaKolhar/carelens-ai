import pandas as pd

df = pd.read_csv("data/raw/diabetic_data.csv")

print("shape:", df.shape)
print()

print("readmitted value counts:")
print(df["readmitted"].value_counts())
print()
print("readmitted value counts (%):")
print((df["readmitted"].value_counts(normalize=True) * 100).round(2))
print()

print("isna().sum() total across all columns:", df.isna().sum().sum())
print("columns with any isna():")
na_counts = df.isna().sum()
print(na_counts[na_counts > 0])
print()

print("'?' counts per column (top 15):")
question_mark_counts = (df == "?").sum().sort_values(ascending=False)
print(question_mark_counts[question_mark_counts > 0].head(15))
