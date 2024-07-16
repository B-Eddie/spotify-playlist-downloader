import requests
from bs4 import BeautifulSoup

def numsongs(link):
    class_name = "IjYxRc5luMiDPhKhZVUH UpiE7J6vPrJIa59qxts4"
    url = link

    # Send a GET request to the URL
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Use BeautifulSoup to extract the desired data from the HTML
    # Example: Extract all the links on the page
    print(soup)
    class_names = soup.find_all(class_="IjYxRc5luMiDPhKhZVUH")
    print(class_names)
    for class_name in class_names:
        print(class_name)

numsongs("https://open.spotify.com/album/7aJuG4TFXa2hmE4z1yxc3n?si=sXqKQr_7RMeYEpdxrhO81Q&nd=1&dlsi=028b2e07b97444ce")