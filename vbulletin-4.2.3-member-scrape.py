from bs4 import BeautifulSoup
from time import sleep
import requests
import json

url = 'http://www.targetsite.com/boards/memberlist.php' # Full URL to vBulletin 4.2.3 memberlist page
testing = False # Enable this to test the first 3 memberlist pages to confirm results

data = [] # List to hold user data before writing to json

def get_total_member_pages(url):

    # Get total number of memberlist pages so we can paginate through them

    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')

    total_pages = int(soup.find(id='pagination_top').find('span').text.split()[-1])
    return total_pages

def scrape_usernames(url):

    # Scrape the username and some basic data on each memberlist page, and append data to list

    success = False     # Boolean so we can break the retry loop on successful request
    wait_time = 1       # Initial wait time if a request fails

    while not success:

        try:
            r = requests.get(url).text
            success = True
        except:
            print(f"Request failed...re-trying in {wait_time} seconds...")
            sleep(wait_time)
            wait_time += wait_time * 1.5    # Increment wait time by 50%

    soup = BeautifulSoup(r, 'html.parser')

    usernames = soup.find_all('a', class_='username')
    postcounts = soup.find_all('td', class_='postcount')
    joindates = soup.find_all('td', class_='joindate')
    lastvisits = soup.find_all('td', class_='lastvisit')

    for i in range(len(usernames)):
        data.append({
            'username': usernames[i].text.lstrip(' '),
            'postcount': postcounts[i].text,
            'joindate': joindates[i].text,
            'lastvisit': lastvisits[i].text.split()[0]   
        })

def write_to_json(data, filename):

    # Dump contents to json file

    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
    except:
        print(f"Could not load {filename}")

def load_from_json(filename):

    # Return data from json file

    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        print("Could not load {filename}")

def update_json(data, filename):

    # Update an existing json with a new dictionary entry

    try:
        existing_data = load_from_json(filename)
    except:
        print(f"Could not load {filename}")
        
    existing_data.update(data)
    write_to_json(existing_data, filename)


def main():

    total_pages = 3 if testing else get_total_member_pages(url)
    current_page = 1

    while current_page <= total_pages:
        memberlist_url = url + '?page=' + str(current_page) + '&order=asc&sort=username'

        scrape_usernames(memberlist_url)

        print(f"Scraped page {current_page} of {total_pages}")
        sleep(1)

        current_page += 1

if __name__ == "__main__":
    main()