import pandas as pd
import numpy as np

# Load dataset
df = pd.read_excel("ORR ALL Grids Oct 1 2024 SY2025_Format.xlsx")

# Clean column names
df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)

# --- Map race columns from df ---
race_map = {
    "Hispanic": ["His M", "His F"],
    "American Indian": ["AmInd M", "AmInd F"],
    "Asian": ["Asian M", "Asian F"],
    "Black": ["Black M", "Black F"],
    "Pacific Islander": ["Pac Is M", "Pac Is F"],
    "White": ["White M", "White F"],
    "Multi": ["Multi M", "Multi F"]
}

# Add summed race columns
for race, cols in race_map.items():
    df[race] = df[cols].sum(axis=1)

# Add totals
df["total"] = df[list(race_map.keys())].sum(axis=1)

# Add proportions
for col in race_map.keys():
    df[f"p_{col}"] = df[col] / df["total"]

# Diversity metrics
p_cols = [f"p_{col}" for col in race_map.keys()]
df["simpson"] = 1 - (df[p_cols] ** 2).sum(axis=1)
df["entropy"] = - (df[p_cols] * np.log(df[p_cols] + 1e-10)).sum(axis=1)

while True:
    print("\nOklahoma School Diversity Menu (no 'epic')")
    print("1. View schools in a district")
    print("2. Sort schools by total enrollment (largest first)")
    print("3. Sort schools by Simpson diversity index (highest first)")
    print("4. Sort schools by Simpson diversity index (lowest first)")
    print("5. Exit")

    choice = input("\nEnter your choice (1-5): ").strip()

    if choice == "1":
        district_name = input("Enter district name: ").strip()
        district_data = df[df["District"].str.contains(district_name, case=False, na=False)]
        if district_data.empty:
            print(f"No schools found for district '{district_name}'.")
        else:
            df_filtered = df[~df["School Name"].str.contains("Epic", case=False, na=False)]
            df_filtered = df_filtered[df_filtered["total"] > 70]
            print(district_data[["School Name", "District", "total", "simpson", "entropy"]].head(30))

    elif choice == "2":
        print("\nTop Schools by Enrollment:")
        df_filtered = df[~df["School Name"].str.contains("Epic", case=False, na=False)]
        df_filtered = df_filtered[df_filtered["total"] > 70]
        print(df_filtered[["School Name", "District", "total"]]
              .sort_values("total", ascending=False).head(20))

    elif choice == "3":
        print("\nTop Schools by Simpson Diversity:")
        df_filtered = df[~df["School Name"].str.contains("Epic", case=False, na=False)]
        df_filtered = df_filtered[df_filtered["total"] > 70]
        print(df_filtered[["School Name", "District", "simpson"]]
              .sort_values("simpson", ascending=False).head(40))

    elif choice == "4":
        print("\nWorst Schools by Simpson Diversity:")
        df_filtered = df[~df["School Name"].str.contains("Epic", case=False, na=False)]
        df_filtered = df_filtered[df_filtered["total"] > 10]
        print(df_filtered[["School Name", "District", "simpson"]]
              .sort_values("simpson", ascending=False).tail(40))

    elif choice == "5":
        print("Exiting program. Goodbye!")
        break
    elif choice == "6":
        district_name = input("Enter district name to compute average Simpson index: ").strip()
        district_data = df[df["District"].str.contains(district_name, case=False, na=False)]
        district_data = district_data[~district_data["School Name"].str.contains("Epic", case=False, na=False)]
        district_data = district_data[district_data["total"] > 70]

        if district_data.empty:
            print(f"No schools found for district '{district_name}'.")
        else:
            avg_simpson = district_data["simpson"].mean()
            print(f"Average Simpson Diversity Index for district '{district_name}': {avg_simpson:.4f}")
    else:
        print("Invalid choice. Please select 1-5.")