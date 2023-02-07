from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


def scrape_seaports_cordinates():
    """
    Scrapes the site (https://www.gccports.com/ports/latitude-longitude) to get
    all the seaports coordinates into a Dataframe.
    :return: seaports coordinates dataframe
    """

    # Autoinstall ChromeDriver
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Open the site
    url = "https://www.gccports.com/ports/latitude-longitude"
    driver.get(url)

    # Total number of pages is 97
    n = 4

    # Open each page, get the table with the data and merge with the others.
    data = []
    for i in range(2, n):
        print(i)
        url = f"https://www.gccports.com/ports/latitude-longitude/{i}"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")[1:]

        for row in rows:
            cells = row.find_all("td")
            port_name = cells[0].text.strip()
            port_code = cells[1].text.strip()
            country = cells[2].text.strip()
            lat = cells[3].text.strip()
            lon = cells[4].text.strip()
            data.append([port_name, port_code, country, lat, lon])

        time.sleep(1)

    # Close the browser
    driver.quit()

    # Transform the collected data in a Dataframe and returns it
    return pd.DataFrame(
        data, columns=["port_name", "port_code", "country", "lat", "lon"]
    )


def get_seaports_converted_cordinates():
    """
    Returns a Dataframe containing all seaports of the world and the
    latitude and longitude in degrees and float formats.
    The data used was scraped from this site: https://www.gccports.com/ports/latitude-longitude
    :return: seaports dataframe
    """

    df = scrape_seaports_cordinates()

    def apply_conversor_cordinates(coordinate_degrees):
        """
        Convert the degrees coordinate in a float number.
        :param coordinate_degrees:
        :return: the coordinate converted to float
        """
        side = coordinate_degrees[-1]
        cordinate_full = f"{coordinate_degrees[:-1]}00.00{side}"
        dm_str = re.sub(r"\s", "", cordinate_full)

        sign = -1 if re.search("[swSW]", dm_str) else 1

        numbers = [*filter(len, re.split("\D+", dm_str, maxsplit=4))]

        degree = numbers[0]
        minute = numbers[1] if len(numbers) >= 2 else "0"
        converted = sign * (int(degree) + float(minute) / 60)
        return str(round(converted, 5))

    # Converts latitude and longitude to float
    df["lat_float"] = df["lat"].apply(apply_conversor_cordinates)
    df["lon_float"] = df["lon"].apply(apply_conversor_cordinates)

    df["porto_id"] = df["port_code"] + "_" + df["port_name"]
    df["porto_id"] = df["porto_id"].apply(lambda x: x.replace(" ", ""))
    return df


# test
get_seaports_converted_cordinates().to_excel("portos.xlsx", index=False)
