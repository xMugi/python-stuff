import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_rss(url):
    """Fetch the content of the RSS feed."""
    response = requests.get(url)
    return response.content

def parse_rss(rss_content):
    """Parse the RSS content to extract the latest news item."""
    soup = BeautifulSoup(rss_content, 'lxml-xml')
    latest_item = soup.find('item')
    if latest_item:
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

        desc_soup = BeautifulSoup(description, "lxml")
        list_items = desc_soup.find_all('li')
        if list_items:
            formatted_description = '\n\n'.join('' + li.text for li in list_items)
        else:
            formatted_description = desc_soup.text

        return link, title, formatted_description, formatted_date
    return None, None, None, None

def send_to_discord(webhook_url, title, description, link, pub_date):
    """Send a single message to the specified Discord webhook using embeds with careful splitting."""
    max_length = 1900
    description_chunks = []

    while len(description) > max_length:
        split_point = description.rfind('</li>', 0, max_length) + 5
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
                    "color": 5814783,
                    "footer": {
                        "icon_url": "https://vectorified.com/images/counter-strike-global-offensive-icon-18.jpg",
                        "text": f"CS2 News feed - Published on {pub_date}"
                    }
                }
            ]
        }
        response = requests.post(webhook_url, json=data)
        print("Posted to Discord:", response.status_code)

def read_last_link():
    """Read the last posted link from a file."""
    try:
        with open("last_link.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def save_last_link(link):
    """Save the last posted link to a file."""
    with open("last_link.txt", "w") as file:
        file.write(link)

def main():
    rss_url = 'https://store.steampowered.com/feeds/news/app/730/?cc=DE&l=english'
    webhook_url = 'dc_webhook'

    last_link = read_last_link()
    rss_content = fetch_rss(rss_url)
    link, title, description, pub_date = parse_rss(rss_content)

    if link and link != last_link:
        send_to_discord(webhook_url, title, description, link, pub_date)
        save_last_link(link)
    else:
        print("No new link to post or duplicate found.")

if __name__ == "__main__":
    main()
