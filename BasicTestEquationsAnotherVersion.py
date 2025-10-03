import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
df = pd.read_excel('ORR ALL Grids Oct 1 2024 SY2025_Format.xlsx')
dp = pd.read_excel('District Demographic Data.xlsx')

# Clean column names
df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)
dp.columns = dp.columns.str.strip().str.replace(r"\s+", " ", regex=True)

# Race mapping for Oklahoma file
race_map = {
    "Hispanic": ["His M", "His F"],
    "American Indian": ["AmInd M", "AmInd F"],
    "Asian": ["Asian M", "Asian F"],
    "Black": ["Black M", "Black F"],
    "Pacific Islander": ["Pac Is M", "Pac Is F"],
    "White": ["White M", "White F"],
    "Multi": ["Multi M", "Multi F"]
}

for race, cols in race_map.items():
    df[race] = df[cols].sum(axis=1)

# Oklahoma totals + proportions
df["total"] = df[list(race_map.keys())].sum(axis=1)
for col in race_map.keys():
    df[f"p_{col}"] = df[col] / df["total"]

p_cols = [f"p_{col}" for col in race_map.keys()]
df["simpson"] = 1 - (df[p_cols] ** 2).sum(axis=1)
df["entropy"] = - (df[p_cols] * np.log(df[p_cols] + 1e-10)).sum(axis=1)

# Arkansas data
dp_keep = [
    "YEAR", "COUNTY_DISTRICT_CODE", "DISTRICT_NAME",
    "ENROLLMENT_GRADES_K_12",
    "ENROLLMENT_ASIAN", "ENROLLMENT_BLACK", "ENROLLMENT_HISPANIC",
    "ENROLLMENT_INDIAN", "ENROLLMENT_MULTIRACIAL",
    "ENROLLMENT_PACIFIC_ISLANDER", "ENROLLMENT_WHITE"
]
dp_clean = dp[dp_keep].copy()

dp_clean = dp_clean.rename(columns={
    "ENROLLMENT_HISPANIC": "Hispanic",
    "ENROLLMENT_INDIAN": "American Indian",
    "ENROLLMENT_ASIAN": "Asian",
    "ENROLLMENT_BLACK": "Black",
    "ENROLLMENT_PACIFIC_ISLANDER": "Pacific Islander",
    "ENROLLMENT_WHITE": "White",
    "ENROLLMENT_MULTIRACIAL": "Multi",
    "ENROLLMENT_GRADES_K_12": "total"
})

# Keep only 2024 rows
arkansas_2024 = dp_clean[dp_clean["YEAR"] == 2024].copy()
# Now add proportions + diversity metrics
num_cols = ["Hispanic","American Indian","Asian","Black",
            "Pacific Islander","White","Multi","total"]

# Turn strings like '*' into NaN, then fill with 0, then cast to float
arkansas_2024[num_cols] = arkansas_2024[num_cols].apply(
    pd.to_numeric, errors="coerce"
).fillna(0).astype(float)

# Now add proportions + diversity metrics
for col in ["Hispanic","American Indian","Asian","Black","Pacific Islander","White","Multi"]:
    arkansas_2024[f"p_{col}"] = arkansas_2024[col] / arkansas_2024["total"]

p_cols = [f"p_{col}" for col in race_map.keys()]
arkansas_2024["simpson"] = 1 - (arkansas_2024[p_cols] ** 2).sum(axis=1)
arkansas_2024["entropy"] = - (arkansas_2024[p_cols] * np.log(arkansas_2024[p_cols] + 1e-10)).sum(axis=1)

# Menu loop
while True:
    print("\nChoose State:")
    print("1. Oklahoma")
    print("2. Arkansas 2024")
    print("3. Exit")

    schoice = input("\nEnter your choice (1-3): ").strip()

    if schoice == "1":  # Oklahoma, use df
        data = df
        name_col = "District"
        id_cols = ["School Name", "District"]
    elif schoice == "2":  # Arkansas 2024 only
        data = arkansas_2024
        name_col = "DISTRICT_NAME"
        id_cols = ["DISTRICT_NAME", "YEAR"]
    elif schoice == "3":
        print("Exiting program. Goodbye!")
        break
    else:
        print("Invalid state choice. Please select 1-3.")
        continue

    # Shared menu
    print("\nMenu Options:")
    print("1. View data for a district")
    print("2. Sort by total enrollment (largest first)")
    print("3. Sort by Simpson diversity index (highest first)")
    print("4. Sort by Simpson diversity index (lowest first)")
    print("5. Back to state menu")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        district_name = input("Enter district name: ").strip()
        district_data = data[data[name_col].str.contains(district_name, case=False, na=False)]
        if district_data.empty:
            print(f"No results found for '{district_name}'.")
        else:
            print(district_data[id_cols + ["total", "simpson", "entropy"]])

    elif choice == "2":
        print("\nTop by Enrollment:")
        print(data[id_cols + ["total"]].sort_values("total", ascending=False).head(10))

    elif choice == "3":
        print("\nTop by Simpson Diversity:")
        print(data[id_cols + ["simpson"]].sort_values("simpson", ascending=False).head(10))
    elif choice == "4":
        print("\nBottom by Simpson Diversity:")
        print(data[id_cols + ["simpson"]].sort_values("simpson", ascending=False).tail(10))
    elif choice == "5":
        continue
    else:
        print("Invalid choice. Please select 1-4.")
