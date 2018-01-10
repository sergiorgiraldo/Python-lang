from bs4 import BeautifulSoup
import urllib3
import shutil


def getCheatSheet(baseurl):
    http = urllib3.PoolManager()
    html_page = http.request("GET", baseurl)
    soup = BeautifulSoup(html_page.data.decode("utf-8"), "html.parser")
    for link in soup.findAll("a"):
        address = link.get("href")
        if address.endswith("pdf"):
            fileName = "c:\\temp\\" + address.split("/")[len(address.split("/")) - 1]
            with http.request("GET", address, preload_content=False) as resp, open(fileName, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
    return


urls = ["https://www.kdnuggets.com/2017/09/essential-data-science-machine-learning-deep-learning-cheat-sheets.html",
        "https://www.kdnuggets.com/2017/09/essential-data-science-machine-learning-deep-learning-cheat-sheets.html/2",
        "https://www.kdnuggets.com/2017/09/essential-data-science-machine-learning-deep-learning-cheat-sheets.html/3"]

for url in urls:
    getCheatSheet(url)