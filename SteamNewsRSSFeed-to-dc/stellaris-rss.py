import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json

# Get the directory of the script file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to config file
config_path = os.path.join(script_dir, 'config.json')

# Load configuration from config.json
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

## Global Variables from config.json ###
dcwebhook = config['dcwebhook']
rssfeed = config['rssfeed']
embeds_color = config['embeds_color']
gamename = config['gamename']
author_icon = config['author_icon']

### Script
# Links inside this File won't get posted
links_posted = 'links_posted.txt'


def fetch_rss(url):
    """Fetch the content of the RSS feed."""
    response = requests.get(url)
    return response.content


def parse_rss(rss_content):
    """Parse the RSS content to extract the latest news item."""
    soup = BeautifulSoup(rss_content, 'lxml-xml')
    items = soup.find_all('item')

    if len(items) > 1:
        latest_item = items[0]  # Get the first/latest item
        title = latest_item.find('title').text if latest_item.find('title') else "No Title"
        description = latest_item.find('description').text if latest_item.find('description') else "No Description"
        link = latest_item.find('link').text if latest_item.find('link') else "No Link"
        pub_date = latest_item.find('pubDate').text if latest_item.find('pubDate') else "No Date"

        # Parse the date to exclude the day and timezone
        if pub_date != "No Date":
            date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            formatted_date = date_obj.strftime("%d %b %Y %H:%M:%S")
        else:
            formatted_date = ""

        # Handle <img> tags by replacing them with placeholder text
        desc_soup = BeautifulSoup(description, "html.parser")
        formatted_description = desc_soup.get_text(separator='\n\n')

        return link, title, formatted_description, formatted_date
    return None, None, None, None


def send_to_discord(webhook_url, title, description, link, pub_date):
    """Send a single message to the specified Discord webhook using embeds with careful splitting."""
    max_length = 5000
    description_chunks = []

    while len(description) > max_length:
        split_point = description.rfind('\n', 0, max_length)
        if split_point == -1 or split_point < max_length / 2:
            split_point = description.rfind(' ', 0, max_length)
        if split_point == -1:
            split_point = max_length

        description_chunks.append(description[:split_point].strip())
        description = description[split_point:].strip()

    if description:
        description_chunks.append(description)

    for desc in description_chunks:
        data = {
            "embeds": [
                {
                    "title": title,
                    "description": desc,
                    "url": link,
                    "color": embeds_color,
                    "footer": {
                        "icon_url": f"{author_icon}",
                        "text": f"{gamename} - Published on {pub_date}"
                    }
                }
            ]
        }
        response = requests.post(webhook_url, json=data)
        print("Posted to Discord:", response.status_code)


def read_last_links():
    """Read the last posted links from a file and return them as a list."""
    file_path = os.path.join(script_dir, links_posted)
    try:
        with open(file_path, "r") as file:
            return file.read().strip().split('\n')
    except FileNotFoundError:
        return []


def save_last_links(link):
    """Save the last posted links to a file, keeping only the most recent 10."""
    file_path = os.path.join(script_dir, links_posted)
    links = read_last_links()
    links.insert(0, link)  # Insert the new link at the beginning
    links = links[:10]  # Keep only the last 10 links
    with open(file_path, "w") as file:
        file.write('\n'.join(links))


def main():
    rss_url = f'{rssfeed}'
    webhook_url = f'{dcwebhook}'

    last_links = read_last_links()
    rss_content = fetch_rss(rss_url)
    link, title, description, pub_date = parse_rss(rss_content)

    if link and link not in last_links:
        send_to_discord(webhook_url, title, description, link, pub_date)
        save_last_links(link)
    else:
        print("No new link to post or duplicate found.")


if __name__ == "__main__":
    main()
