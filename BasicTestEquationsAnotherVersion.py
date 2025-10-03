import pandas as pd
import numpy as np

# Load dataset
df = pd.read_excel("School Totals by Ethnicity and GenderSY2024 1.xlsx")

# Clean column names
df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)

# Compute racial totals
df["Hispanic"] = df["His M"] + df["His F"]
df["American Indian"] = df["AmInd M"] + df["AmInd F"]
df["Asian"] = df["Asian M"] + df["Asian F"]
df["Black"] = df["Black M"] + df["Black F"]
df["Pacific Islander"] = df["Pac Is M"] + df["Pac Is F"]
df["White"] = df["White M"] + df["White F"]
df["Multi"] = df["Multi M"] + df["Multi F"]

# Compute total enrollment
race_cols = ["Hispanic", "American Indian", "Asian", "Black", "Pacific Islander", "White", "Multi"]
df["total"] = df[race_cols].sum(axis=1)

# Compute proportions
for col in race_cols:
    df[f"p_{col}"] = df[col] / df["total"]

# Diversity metrics
p_cols = [f"p_{col}" for col in race_cols]
df["simpson"] = 1 - (df[p_cols] ** 2).sum(axis=1)
df["entropy"] = - (df[p_cols] * np.log(df[p_cols] + 1e-10)).sum(axis=1)

# Lowercase county column for robust searching
df["County_lower"] = df["County"].str.lower().str.strip()
df["District_lower"] = df["District"].str.lower().str.strip()

# Helper function to filter schools (remove "Epic" and minimum total)
def filter_schools(df_in, min_total=70):
    return df_in[~df_in["School Name"].str.contains("Epic", case=False) & (df_in["total"] > min_total)]

# Menu loop
while True:
    print("\nOklahoma School Diversity Menu (by County)")
    print("1. View schools in a county")
    print("2. Sort schools by total enrollment (largest first)")
    print("3. Sort schools by Simpson diversity index (highest first)")
    print("4. Sort schools by Simpson diversity index (lowest first)")
    print("5. Average Simpson index by district")
    print("6. Average Simpson index by county")
    print("7. Exit")
    print("8. View schools in a district")
    print("9. Search for a school by name")

    choice = input("\nEnter your choice (1-6): ").strip()

    if choice == "1":
        county_input = input("Enter county name (or part of it): ").strip().lower()
        matches = df["County"].loc[df["County_lower"].str.contains(county_input, na=False)].unique()
        if len(matches) == 0:
            print(f"No counties match '{county_input}'.")
            continue
        elif len(matches) > 1:
            print("Matching counties found:")
            for i, name in enumerate(matches):
                print(f"{i+1}. {name}")
            selection = int(input(f"Enter the number of the county to view (1-{len(matches)}): "))
            selected_county = matches[selection-1]
        else:
            selected_county = matches[0]

        county_data = df[df["County"] == selected_county]
        county_data = filter_schools(county_data)
        print(county_data[["School Name", "County", "total", "simpson", "entropy"]].head(75))

    elif choice == "2":
        df_filtered = filter_schools(df)
        print("\nTop Schools by Enrollment:")
        print(df_filtered[["School Name", "County", "total"]].sort_values("total", ascending=False).head(20))

    elif choice == "3":
        df_filtered = filter_schools(df)
        print("\nTop Schools by Simpson Diversity:")
        print(df_filtered[["School Name", "County", "simpson"]].sort_values("simpson", ascending=False).head(40))

    elif choice == "4":
        df_filtered = filter_schools(df, min_total=10)
        print("\nWorst Schools by Simpson Diversity:")
        print(df_filtered[["School Name", "County", "simpson"]].sort_values("simpson", ascending=True).head(40))

    elif choice == "7":
        print("Exiting program. Goodbye!")
        break

    elif choice == "6":
        county_input = input("Enter county name (or part of it): ").strip().lower()
        matches = df["County"].loc[df["County_lower"].str.contains(county_input, na=False)].unique()
        if len(matches) == 0:
            print(f"No counties match '{county_input}'.")
            continue
        elif len(matches) > 1:
            print("Matching counties found:")
            for i, name in enumerate(matches):
                print(f"{i+1}. {name}")
            selection = int(input(f"Enter the number of the county to analyze (1-{len(matches)}): "))
            selected_county = matches[selection-1]
        else:
            selected_county = matches[0]

        county_data = df[df["County"] == selected_county]
        county_data = filter_schools(county_data)
        avg_simpson = county_data["simpson"].mean()
        print(f"Average Simpson Diversity Index for '{selected_county}': {avg_simpson:.4f}")

    elif choice == "5":
        district_input = input("Enter district name (or part of it): ").strip().lower()
        matches = df["District"].loc[df["District_lower"].str.contains(district_input, na=False)].unique()

        if len(matches) == 0:
            print(f"No districts match '{district_input}'.")
        else:
            if len(matches) > 1:
                print("Matching districts found:")
                for i, name in enumerate(matches):
                    print(f"{i+1}. {name}")
                selection = int(input(f"Enter the number of the district to analyze (1-{len(matches)}): "))
                selected_district = matches[selection-1]
            else:
                selected_district = matches[0]

            district_data = df[df["District"] == selected_district]
            district_data = district_data[~district_data["School Name"].str.contains("Epic", case=False)]
            district_data = district_data[district_data["total"] > 70]

            if district_data.empty:
                print(f"No valid schools in district '{selected_district}' after filtering.")
            else:
                avg_simpson = district_data["simpson"].mean()
                print(f"Average Simpson Diversity Index for '{selected_district}': {avg_simpson:.4f}")
    if choice == "8":
        district_input = input("Enter district name (or part of it): ").strip().lower()
        matchesD = df["District"].loc[df["District_lower"].str.contains(district_input, na=False)].unique()
        if len(matchesD) == 0:
            print(f"No districts match '{district_input}'.")
            continue
        elif len(matchesD) > 1:
            print("Matching districts found:")
            for i, name in enumerate(matchesD):
                print(f"{i+1}. {name}")
            selection = int(input(f"Enter the number of the districts to view (1-{len(matchesD)}): "))
            selected_district = matchesD[selection-1]
        else:
            selected_district = matchesD[0]

        district_data = df[df["District"] == selected_district]
        district_data = filter_schools(district_data)
        print(district_data[["School Name", "District", "total", "simpson", "entropy"]].head(30))
    elif choice == "9":
        school_input = input("Enter the exact or partial school name: ").strip().lower()
        matches = df["School Name"].loc[df["School Name"].str.lower().str.contains(school_input, na=False)].unique()
        
        if len(matches) == 0:
            print(f"No schools match '{school_input}'.")
            continue
        elif len(matches) > 1:
            print("Matching schools found:")
            for i, name in enumerate(matches):
                print(f"{i+1}. {name}")
            selection = int(input(f"Enter the number of the school to view (1-{len(matches)}): "))
            selected_school = matches[selection-1]
        else:
            selected_school = matches[0]

        # Display data for the selected school
        school_data = df[df["School Name"] == selected_school]
        print(school_data[["School Name", "District", "County", "total", "simpson", "entropy"]])
    else:
        print("Invalid choice. Please select 1-6.")