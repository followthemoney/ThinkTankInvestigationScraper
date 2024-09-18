import pdfplumber
import pandas as pd
import requests
import os
from scraper import get_proxies
import random

PROXIES = get_proxies()



# Extract table from pdf
def extract_tables_from_pdf(pdf_path):
 
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []
        headers = None  

        # Iterate through each page
        for page_num, page in enumerate(pdf.pages):
            # Extract tables from the page
            tables = page.extract_tables()

            for table in tables:
                if table:
                    if headers is None:
                        # Find header
                        headers = table[0]
                        # keep header
                        df = pd.DataFrame(table[1:], columns=headers)
                    else:
                        # Use previously stored headers for the following pages
                        df = pd.DataFrame(table, columns=headers)
                    all_tables.append(df)

        # Concatenate all df
        if all_tables:
            final_table = pd.concat(all_tables, ignore_index=True)
            return final_table
        else:
            return None



def clean(df):
    # merge tables that are on two pages
    for i in range(1,len(df)):
        if df.at[i,'Nr'] == '':
            df.at[i,'Nr'] = df.at[i-1,'Nr']

    df = df.groupby('Nr', as_index=False).agg(lambda x: ' '.join(x.dropna().astype(str)))
    df.replace(r'\n', ' ', regex=True, inplace=True)  #replace \n found
    df['Nr'] = df['Nr'].astype(int) #resort by n (= sorting by date)
    df = df.sort_values(by='Nr')
    df.columns = ['Nr', 'Commission_representatives', 'Date', 'Location', 'Subjects'] #change names 
    df['Date'] = df['Date'].str.replace(' ', '')
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')

    return df


def get_comm_meetings(url):
    # Download the file and name
    proxy = random.choice(PROXIES)
    proxies = {
    'http': f'socks5://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}',
    'https': f'socks5://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
    }
    response = requests.get(url, proxies=proxies)
    local_filename = 'downloaded_file.pdf'
    with open(local_filename, 'wb') as f:
        f.write(response.content)

    # launch extraction code
    table_data = extract_tables_from_pdf(local_filename)
    


    # Clean 
    table_data_cleaned = clean(table_data)

    if table_data is None:
        print('Error')
        return 0, pd.DataFrame()
    if len(table_data)<2:
        return 1, pd.DataFrame()

    os.remove(local_filename)
    return 2, table_data_cleaned



def get_parl_meetings(url):
    # Download the file and name
    proxy = random.choice(PROXIES)
    proxies = {
    'http': f'socks5://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}',
    'https': f'socks5://{proxy["username"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
    }
    response = requests.get(url, proxies=proxies)
    local_filename = 'downloaded_file.csv'
    with open(local_filename, 'wb') as f:
        f.write(response.content)

    # just read csv
    table_data = pd.read_csv(local_filename)
    #table_data.columns = ['Nr', 'Commission_representatives', 'Date', 'Location', 'Subjects'] #change names 
    table_data['meeting_date'] = table_data['meeting_date'].str.replace(' ', '')
    table_data['Date'] = pd.to_datetime(table_data['meeting_date'], format='%Y-%m-%d', errors='coerce')
    table_data.drop(columns=['meeting_date'], inplace=True)
    #table_data['meeting_date'] = pd.to_datetime(table_data['meeting_date'], errors='coerce')
    if table_data is None:
        print('Error')
        return 0, pd.DataFrame()
    if len(table_data)<2:
        return 1, pd.DataFrame()
    
    os.remove(local_filename)
    return 2, table_data

def check_recent(df, years):
    recent_date_threshold = pd.Timestamp.now() - pd.DateOffset(years=years)
    recent_entries = df[df['Date'] >= recent_date_threshold]
    return not recent_entries.empty

