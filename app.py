from bs4 import BeautifulSoup
import requests
import os
import shutil

BASE_URL = "https://apps.irs.gov/app/picklist/list/priorFormPublication.html"


def prompt_input():
    try:
        while True:
            query = [q.strip() for q in input(
                "Enter a tax form name (ex, Form W-2) and a range of years(ex, 2018-2020) separated by comma. (exmaple valid input: Form W-2, 2018-2020) >> ").split(",")]
            if len(query) == 2:
                break
            if len(query) > 2 or len(query) < 2:
                print("Wrong argument count")
        file_info = query_to_file_info(query)
        download_files(file_info)

    except Exception as e:
        print(e)


def query_to_file_info(query):
    try:
        file_name = query[0]
        years = query[1].split("-")

        start_year = int(years[0])
        end_year = int(years[len(years)-1])

        return {"file_name": file_name,
                "start_year": start_year,
                "end_year": end_year}

    except Exception as e:
        print(e)


def download_files(file_info):
    try:
        file_name = file_info["file_name"]
        start_year = file_info["start_year"]
        end_year = file_info["end_year"]

        start = 0
        count = 0
        while True:
            response = requests.get(
                f"{BASE_URL}?indexOfFirstRow={start}&sortColumn=sortOrder&value={file_name}&criteria=formNumber&resultsPerPage=200&isDescending=false")
            soup = BeautifulSoup(response.text, "lxml")

            if is_error(soup):
                break

            product_numbers = soup.find_all("td", class_="LeftCellSpacer")

            for product_number in product_numbers:
                product_text = product_number.a.text.strip()
                if product_text.lower() == file_name.lower():
                    year = product_number.findNext("td").findNext("td").text.strip()
                    if int(year) in range(start_year, end_year+1):
                        if count == 0:
                            create_folder(product_text)
                        write_file(
                            product_text, product_number.a["href"], year)
                        count += 1
            start += 200

        if count == 0:
            print(
                f"No files existed for {file_name} from year {start_year} to {end_year}")
            return

        print(
            f"Successfully downloaded {file_name} from year {start_year} to {end_year}")
        return

    except Exception as e:
        print(e)


def is_error(soup):
    if soup.find("div", class_="errorBlock"):
        return True
    return False


def create_folder(folder_name):
    try:
        path = os.path.join(os.getcwd(), folder_name)
        if(os.path.exists(path)):
            shutil.rmtree(path)
        os.mkdir(path)
        os.chdir(path)
    except Exception as e:
        print(e)


def write_file(file_name, file_url, year):
    try:
        with open(f"{file_name}-{year}.pdf", 'wb') as f:
            file_response = requests.get(file_url)
            f.write(file_response.content)
    except Exception as e:
        print(e)


prompt_input()
