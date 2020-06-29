from bs4 import BeautifulSoup
import csv
from os.path import isfile
from requests import get

if not isfile("defects.csv"):
    print("Creating defects file...")
    url = "http://www.surfacemountprocess.com/surface-mount-troubleshooting-guide.html"
    defect_guide_page = get(url)

    soup = BeautifulSoup(defect_guide_page.text, 'html.parser')

    defects = soup.find_all('h2', attrs={'class': 'wsite-content-title'})[:-2]
    page_text = soup.find_all('div', attrs={'class': 'paragraph'})[:-3]

    defects = [title.contents[0] for title in defects if isinstance(title.contents[0], str)]
    causes = [paragraph.contents[1][1:] for paragraph in page_text]
    prevent_actions = [paragraph.contents[4] for paragraph in page_text]

    data = list(zip(defects, causes, prevent_actions))
    print(data)

    f = csv.writer(open("defects.csv", "w"))
    f.writerow(["Defect", "Cause", "Preventable Action"])
    f.writerows(data)
