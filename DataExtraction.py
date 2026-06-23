
import pandas as pd
import numpy as np
import warnings 
import time


STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY",
]

#Fred series ID categories:
minwage_id = "STTMINWG{st}"       
employment_id = "{st}LEIH"      #leisure and hosp. jobs
federal_id = "FEDMINNFRWG"   

start_year = 2000
end_year = 2023







def read_fred_series(series_id):
    url = ("https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id={series_id}&cosd={start_year}-01-01&coed={end_year}-12-31")
    
    try: 
        raw_data = pd.read_csv(url, na_values=["."])

    except Exception as e:
        warnings.warn(f"Failed to read series {series_id}, error: {e}")
        return None


    date_col = raw_data.columns[0]
    value_col = raw_data.columns[1]

    state_table = pd.DataFrame()
    state_table["year"] = pd.to_datetime(raw_data[date_col]).dt.year
    state_table["value"] = raw_data[value_col]

    return state_table








def main():
    
    minwage_tables = []         #list of tables from each state
    
    for state in STATES:
        print(f"downloading min wage for {state}")
        table = read_fred_series(minwage_id.format(st=state))  #columns observation date and value
        
        if table is None:
            continue

        
        table["state"] = state
        
        yearly = table.groupby("year", as_index=False)["value"].max()        
        yearly=yearly.rename(columns={"value":"state_min_wage"})
        yearly["state"] = state                 
        
        minwage_tables.append(yearly)
    
    min_wage = pd.concat(minwage_tables, ignore_index=True)         #all tables into one big table
    

    
    
    
    
    
    
    
    
    employment_tables = []

    for state in STATES:
        print(f"downloading employment for {state}")

        table2 = read_fred_series(employment_id.format(st=state))

        time.sleep(0.1)      #maybe fred dosn't like me anymore

        
        if table2 is None:
            continue

        yearly = table2.groupby("year", as_index=False)["value"].mean()
        yearly=yearly.rename(columns={"value":"lh_employment"})
        yearly["state"] = state

        employment_tables.append(yearly)
    
    employment = pd.concat(employment_tables, ignore_index=True)              #all tables into one big table

    
    
    
    
    
    
    federal = read_fred_series(federal_id)
    
    federal=federal.groupby("year", as_index=False)["value"].max()      
    
    federal = federal.rename(columns={"value":"federal_min_wage"})

    
   
   
    #full table with dataframes min_wage, employment, federal
    
    
    
    full= min_wage.merge(employment, on=["state","year"], how="inner")

    full = full.merge(federal, on=["year"], how = "left")

    full = full.sort_values(["state","year"]).reset_index(drop=True)          #orders by state then year, resets index

    
    
    
    
    #make the table nice by adding useful columns:
    
    
    
    
    
    
    full["eff_min_wage"] = full[["state_min_wage","federal_min_wage"]].max(axis=1)   
    
    #LOGS
    full["log_min_wage"] = np.log(full["eff_min_wage"]) 
    full["log_employment"] = np.log(full["lh_employment"])


    full["minwage_change"] = full.groupby("state")["eff_min_wage"].diff()         #change in min wage each yar by state


    #SAVE AS CSV!!!!

    full.to_csv("minwage_employment_data.csv", index= False)

    print(full.head(30))

main()


import os 

file_path = os.path.abspath("minwage_employment_data.csv")

print(f"path: {file_path}")
   