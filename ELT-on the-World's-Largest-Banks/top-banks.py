# Code for ETL operations data

# Importing the required libraries

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime 


def extract(url, table_attribs):
    '''Extract the tabular information from the given URL under the heading 'By market capitalization' and save it to a dataframe.
      a. Inspect the webpage and identify the position and pattern of the tabular information in the HTML code
      b. Write the code for a function extract() to perform the required data extraction.
      c. Execute a function call to extract() to verify the output.
      This function extracts the required information from the website and saves it to a dataframe. 
      The function returns the dataframe for further processing. '''

    page = requests.get(url).text
    data = BeautifulSoup(page,'html.parser')
    df = pd.DataFrame(columns=table_attribs)

    tables = data.find_all('tbody')
    rows = tables[0].find_all('tr')

    for row in rows:
        col = row.find_all('td')
        if len(col)!=0:
            all_links = col[1].find_all('a')
            second_link = all_links[1]   
            data_dict = {"Name": str(second_link['title']),
                         "MC_USD_Billion": str(col[2].contents[0]).replace("\n", "")}              
            df1 = pd.DataFrame(data_dict, index=[0])
            df = pd.concat([df,df1], ignore_index=True)
    return df

def transform(df):
    ''' This function converts the GDP information from Currency
    format to float value, transforms the information of GDP from
    USD (Millions) to USD (Billions) rounding to 2 decimal places.
    The function returns the transformed dataframe.'''
    
   # Load the exchange rate data
    exchange_rates = pd.read_csv(exchange_rates_path)

    # Display exchange rate data to ensure correctness
    #print("Exchange Rate Data:\n", exchange_rates)
    #bank_list = df["MC_USD_Billion"].tolist()

    # Extract relevant exchange rates
    usd_to_gbp = exchange_rates.loc[exchange_rates["Currency"] == "GBP", "Rate"].values[0]
    usd_to_eur = exchange_rates.loc[exchange_rates["Currency"] == "EUR", "Rate"].values[0]
    usd_to_inr = exchange_rates.loc[exchange_rates["Currency"] == "INR", "Rate"].values[0]

    # Transform the DataFrame by adding new columns
    df["MC_GBP_Billion"] = (df["MC_USD_Billion"].astype(float) * usd_to_gbp).round(2)
    df["MC_EUR_Billion"] = (df["MC_USD_Billion"].astype(float) * usd_to_eur).round(2)
    df["MC_INR_Billion"] = (df["MC_USD_Billion"].astype(float) * usd_to_inr).round(2)

    #bank_list = [float("".join(x.split(','))) for x in bank_list]
    #bank_list = [np.round(x/1000,2) for x in bank_list] 
    #df["MC_USD_Billion"] = bank_list
    #df=df.rename(columns = {"MC_USD_Billion":"MC_USD_Billion"})
    return df

def load_to_csv(df, csv_path):
    ''' This function saves the final dataframe as a `CSV` file 
    in the provided path. Function returns nothing.'''

    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
    ''' This function saves the final dataframe as a database table
    with the provided name. Function returns nothing.'''

    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)


def run_query(query_statement, sql_connection):
    ''' This function runs the stated query on the database table and
    prints the output on the terminal. Function returns nothing. '''

    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)


def log_progress(message):
    '''Write a function log_progress() to log the progress of the code at different stages in a file code_log.txt. Use the list of log points provided to create log entries as every stage of the code.'''
    ''' This function logs the mentioned message at a given stage of the code execution to a log file. Function returns nothing'''
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now() # get current timestamp 
    timestamp = now.strftime(timestamp_format) 
    with open("./code_log.txt","a") as f: 
        f.write(timestamp + ' : ' + message + '\n')   



''' Here, you define the required entities and call the relevant 
functions in the correct order to complete the project. Note that this
portion is not inside any function.'''

url='https://web.archive.org/web/20230908091635%20/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["Name", "MC_USD_Billion"]
db_name = 'Banks.db'
table_name = 'Largest_banks'
csv_path = './Largest_banks_data.csv'
exchange_rates_path = './exchange_rate.csv'

log_progress('Preliminaries complete. Initiating ETL process')

df = extract(url, table_attribs)

log_progress('Data extraction complete. Initiating Transformation process')

df = transform(df)

log_progress('Data transformation complete. Initiating loading process')

load_to_csv(df, csv_path)

log_progress('Data saved to CSV file')

sql_connection = sqlite3.connect('World_Economies.db')

log_progress('SQL Connection initiated.')

load_to_db(df, sql_connection, table_name)

log_progress('Data loaded to Database as table. Running the query')

query_statement = f"SELECT * from {table_name}"
run_query(query_statement, sql_connection)

log_progress('Process Complete.')

sql_connection.close()
