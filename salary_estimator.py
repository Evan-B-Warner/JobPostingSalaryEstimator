import json
import numpy as np
import pandas as pd


def json2df(json_path):
    """Loads scraped json data into a Pandas DF
    
    """
    # load data from json
    with open(json_path) as f:
        data = json.load(f)

    # preprocess json data and convert to df
    all_postings = []
    for search_term in data:
        all_postings.extend(data[search_term])
    df = pd.DataFrame(all_postings)
    
    # drop duplicate postings by link
    df = df.drop_duplicates(subset='url')
    return df


def process_location(df):
    df["city"] = np.where(df.location.str.contains(","), df.location.str.split(",").str.get(0).str.strip(), None)
    df["province"] = np.where(df.location.str.contains(","), df.location.str.split(",").str.get(1).str.strip(), None)
    df["country"] = np.where(df.location == "Canada", "Canada", None)
    df.loc[df.province.isin(["ON", "BC", "QC", "AB", "SK", "MB", "NS", "NB", "PE", "YT", "NL"]), "country"] = "Canada"
    df = df.drop("location", axis=1)
    return df


def process_num_applicants(df):
    df.num_applicants = np.where(df.num_applicants.str.split(" ").str.get(0).str.isdigit(), 
        df.num_applicants.str.split(" ").str.get(0), df.num_applicants)
    df.num_applicants = np.where(df.num_applicants.str.split(" ").str.get(0) == "Over", 100, df.num_applicants)
    df.num_applicants = df.num_applicants.astype("float64")
    return df


def salary_string2annual(salary):
    try:
        amount = salary.split("/")[0].split("$")[-1].replace("$", "")
        if "K" in amount:
            amount = amount.replace("K", "")
            amount = float(amount)*1000
        amount = float(amount)
        term = salary.split("/")[1].split(" ")[0]
        if term == 'hr':
            amount = amount*2000
    except Exception as e:
        #print(e)
        amount = salary
    return amount


def process_salary(df):
    df.salary = np.where(df.salary.str.contains("$", regex=False), df.salary, None)
    salaries = []
    for i in range(len(df)):
        salary = df.iloc[i].salary
        if salary is not None:
            try:
                if salary.count("$") == 1:
                    # the salary is not a range
                    salaries.append(salary_string2annual(salary))
                else:
                    split_salary_string = salary.split(" ")
                    lower, upper = "", ""
                    for word in split_salary_string:
                        if "$" in word:
                            if lower == "":
                                lower = word
                            else:
                                upper = word
                                break
                    mean_amount = (salary_string2annual(lower) + salary_string2annual(upper))/2
                    salaries.append(mean_amount)
            except Exception as e:
                print(e)
                pass
        else:
            salaries.append(None)
    df["annual_salary"] = salaries
    df = df.drop("salary", axis=1)
    return df


def preprocess_scraped_data(json_path):
    df = json2df(json_path)
    df = process_location(df)
    df = process_num_applicants(df)
    df = process_salary(df)
    df.to_pickle("linkedin_scraped_posts_0407_processed.pkl")


def cross_with_annual_salary(df, other_column, num_cuts):
    percentiles = []
    for i in range(num_cuts):
        next_percentile = round(np.nanpercentile(df[other_column], i*100/(num_cuts)), 2)
        if next_percentile not in percentiles:
            percentiles.append(next_percentile)
    percentiles.append(max(df[other_column]))

    formatted_ranges, mean_salaries = [], []
    for i in range(1, len(percentiles)):
        if i != len(percentiles)-1:
            formatted_ranges.append(f"[{percentiles[i-1]}-{percentiles[i]})")
            mean_salaries.append(round(df[(df[other_column] >= percentiles[i-1]) & (df[other_column] < percentiles[i])].annual_salary.mean(), 2))
        else:
            formatted_ranges.append(f"[{percentiles[i-1]}-{percentiles[i]}]")
            mean_salaries.append(round(df[(df[other_column] >= percentiles[i-1]) & (df[other_column] <= percentiles[i])].annual_salary.mean(), 2))
    
    display_df = pd.DataFrame()
    display_df[other_column] = formatted_ranges
    display_df["Mean Annual Salary"] = mean_salaries
    return display_df

if __name__ == "__main__":
    # preprocess data into usable fields
    #preprocess_scraped_data("data/linkedin_scraped_posts_0407.json")

    # simple analysis on processed data
    df = pd.read_pickle("linkedin_scraped_posts_0407_processed.pkl")
    #print(len(df), len(df[~df.annual_salary.isnull()]))
    #print(df.head())
    #print(cross_with_annual_salary(df, "num_applicants", 5))
    #print(df.groupby("province").annual_salary.agg(['count', 'mean']))
    print(df[['employer', 'title']].head())