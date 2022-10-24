import requests
from bs4 import BeautifulSoup as bs
import argparse
from tqdm import tqdm
import csv
import os

def get_url(url):
    """
        Render html page from target url
        :param url: str -> target url
        :return page object : bs4 object html
    """

    hearders = { "User-Agent" : 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"}

    res = requests.get(url,headers=hearders)

    if res :
        return bs(res.text, "html.parser")
    return False


def get_data(year):
    """
        Fetch data from target url and construct the data to list
        :param year: str or int -> year target url
        :return : list : 500 list object data company
    """

    index = [1+i*100 for i in range(5)]
    company_data = []
    for i in index:
        url = f"https://money.cnn.com/magazines/fortune/fortune500_archive/full/{year}/{i}.html"
        res = get_url(url)
        try :
            data = res.find("table",class_="maglisttable").find_all("tr",id="tablerow")
        except:
            data = None

        base_url = "https://money.cnn.com/magazines/fortune/fortune500_archive/"
        if data :
            for d in data :
                row_data =  d.find_all("td")
                url = row_data[1].find("a").get("href")                
                company_data.append({
                    "rank" :  row_data[0].get_text(),
                    "Company Name" : row_data[1].get_text(),
                    "Revenues($ millions)" : row_data[2].get_text(),
                    "Profits($ millions)" : row_data[3].get_text(),
                    "Company ID" : url.split("/")[-1].strip(".html"),                    
                    "URL" : base_url + url.strip("../.."),
                    "Year" : year
                })
                
    return company_data


def write_csv(data, years):
    """
        Write data into csv file
        :param data: list -> list of companies data object
        :param years : tupple -> start year and end year data
    """
    start, end = years
    file_name = f"500_fortune_company_from_{start}_end_{end}.csv"
    file_path = os.path.join("csv_output",file_name)

    with open(file_path,"w",newline="",encoding='UTF8') as csvfile:
        writer = csv.writer(csvfile,delimiter=",")
        
        # write header data 
        writer.writerow(["rank","Company Name","Revenues($ millions)","Profits($ millions)","Company ID","URL","Year"])
        
        for row in data:
            for r in row:
                writer.writerow(list(r.values()))        


if "__main__" == __name__:
    parser = argparse.ArgumentParser(description="Scrape fortune 500 companies")
    parser.add_argument("--start_year", type=int, help="Start year scraping data")
    parser.add_argument("--end_year", type=int, help="End year scraping data")

    args = parser.parse_args()
    start_year, end_year = args.start_year, args.end_year  

    #check and create forlder csv_output to store csv file
    if not os.path.exists("csv_output"):
        os.mkdir("csv_output")
    
    data = [get_data(year) for year in tqdm(range(start_year, end_year+1),f"Start scraping data from {start_year} end {end_year}")]
    
    write_csv(data,(start_year,end_year))

    print("Finished running scraping 500 fortune companies")