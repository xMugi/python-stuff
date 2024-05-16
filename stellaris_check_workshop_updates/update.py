import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import os

# change id to your game, get from steam-db then AppID of the game
game_id = "281990"

colors = dict(END='\033[0m', BLACK='\033[30m', RED='\033[31m', GREEN='\033[32m', YELLOW='\033[33m', BLUE='\033[34m',
              MAGENTA='\033[35m', CYAN='\033[36m', WHITE='\033[37m', BT_BLACK='\033[90m', BT_RED='\033[91m',
              BT_GREEN='\033[92m', BT_YELLOW='\033[93m', BT_BLUE='\033[94m', BT_MAGENTA='\033[95m', BTCYAN='\033[96m',
              BT_WHITE='\033[97m')

# File paths
url_collection = 'url_mod_collection.json'
last_updated_file = 'updated_entrys.json'
updated_file = 'updated.txt'


def format_title(title):
    return f"{colors['BT_MAGENTA']}{title}{colors['END']}"


def format_workshop_id(workshop_id):
    return f"{colors['BT_MAGENTA']}{workshop_id}{colors['END']}"


def format_url(url):
    return f"{colors['BT_MAGENTA']}{url}{colors['END']}"


def get_last_updated():
    if not os.path.exists(last_updated_file):
        with open(last_updated_file, 'w') as f:
            json.dump({}, f)
        return {}

    try:
        with open(last_updated_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_updated_ids():
    if not os.path.exists(updated_file):
        print(colors['RED'] + f"Error: {updated_file} file not found. Creating a new file." + colors['END'])
        with open(updated_file, 'w') as f:
            f.write('')
        return {}

    try:
        with open(updated_file, 'r') as f:
            data = f.read().strip()
            if data:  # Check if the file is not empty
                updated_ids = {}
                for line in data.split('\n'):
                    updated_ids[line.strip()] = None  # Assuming each line is a key
                return updated_ids
            else:
                return {}
    except Exception as e:
        print(colors['RED'] + f"Error: {e}" + colors['END'])
        return {}


def update_updated_ids(updated_ids):
    with open(updated_file, 'w') as f:
        for key in updated_ids.keys():
            f.write(f'{key}\n')


def update_last_updated(updated_data):
    try:
        with open(last_updated_file, 'r') as file:
            last_updated = json.load(file)
    except FileNotFoundError:
        last_updated = {}
    # Update last_updated with the data from updated_data
    for url, data in updated_data.items():
        last_updated[url] = data  # Assuming data is already a dictionary with 'date' and 'name'

    # Save the updated last_updated dictionary to the JSON file
    with open(last_updated_file, 'w') as file:
        json.dump(last_updated, file, indent=4)


def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def parse_title(content):
    soup = BeautifulSoup(content, 'html.parser')
    title_element = soup.find(class_='workshopItemTitle')
    if title_element:
        return title_element.text.strip()
    else:
        print("Workshop item title not found.")
        return None


def parse_update_details(content):
    soup = BeautifulSoup(content, 'html.parser')
    details_right = soup.find('div', class_='detailsStatsContainerRight')
    if details_right:
        details_stat_right = details_right.find_all('div', class_='detailsStatRight')
        if len(details_stat_right) >= 3:
            return details_stat_right[2].text.strip()
        elif len(details_stat_right) == 2:
            return details_stat_right[1].text.strip()
    return None


def parse_date(date_str):
    current_year = datetime.now().year
    # Normalize spaces and correct AM/PM casing
    date_str = date_str.strip().replace('am', 'AM').replace('pm', 'PM')

    # Caveman fix: Replace "29 Feb" with "27 Feb" directly without considering leap year status
    date_str = date_str.replace("29 Feb", "28 Feb")

    formats = [
        '%d %b, %Y @ %I:%M%p',  # Date with year
        '%d %b @ %I:%M%p'  # Date without year
    ]
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # If the year is not in the format, add the current year
            if '%Y' not in fmt:
                parsed_date = parsed_date.replace(year=current_year)
            return parsed_date
        except ValueError:
            continue

    # If all formats fail, log the error and return None
    print("Error: Unable to parse date from the string '{}'. Please check the format.".format(date_str))
    return None


def load_urls():
    try:
        with open(url_collection, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(colors['RED'] + f"Error: {url_collection} file not found." + colors['END'])
        return None


def update_records(last_updated, updated_dates, updated_ids):
    last_updated.update(updated_dates)
    update_last_updated(last_updated)
    update_updated_ids(updated_ids)


def check_and_update(url):
    content = fetch_page(url)
    if content:
        title = parse_title(content) or "Unknown Title"  # Ensure title is set even if parsing fails
        update_str = parse_update_details(content)
        update_date = parse_date(update_str) if update_str else None
        return {"date": update_date.strftime('%Y-%m-%d %H:%M:%S') if update_date else None, "name": title}
    return {"date": None, "name": None}  # Default values if content fetch fails


def log_update_message(is_success, title, workshop_id):
    if is_success:
        print(colors['GREEN'] +
              f"✓ Updated: {format_title(title)}"
              + colors['GREEN'] +
              f" - Workshop ID: {format_workshop_id(workshop_id)}\n"
              + colors['END'])
    else:
        print(colors['RED'] +
              f"? Failed to check: {format_title(title)}"
              + colors['RED'] +
              f" - Workshop ID: {format_workshop_id(workshop_id)}\n"
              + colors['END'])


def process_url(url, last_updated, updated_dates, updated_ids):
    workshop_id = url.split('=')[-1]
    result = check_and_update(url)
    title = result['name']
    if result['date']:
        if last_updated.get(url) and last_updated[url].get('date') == result['date']:
            return False, False  # No update
        updated_dates[url] = {"date": result['date'], "name": title}
        process_update(url, workshop_id, result, updated_dates, updated_ids)
        return True, True  # Successful update
    else:
        return True, False  # Failed check


def check_updates(urls, last_updated):
    updated_ids = get_updated_ids()
    updated_dates = {}
    upd_cnt = 0  # Initialize the counter for updated URLs
    upd_cnt_err = 0  # Initialize the counter for failed checks

    if not last_updated:
        print(colors['GREEN'] + "No previous update records found. Marking all URLs as updated." + colors['END'])
        for url in urls:
            updated_dates[url] = {"date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "name": None}
    else:
        for url in urls:
            print(colors['CYAN'] + f"Checking {format_url(url)}..." + colors['END'])
            processed, is_success = process_url(url, last_updated, updated_dates, updated_ids)
            if processed:
                if is_success:
                    upd_cnt += 1
                else:
                    upd_cnt_err += 1
                log_update_message(is_success, updated_dates[url]['name'], url.split('=')[-1])

    if upd_cnt_err > 0:  # Only print if there were failed checks
        print(colors['RED'] + f"{upd_cnt_err} Mods Failed to check ✘" + colors['END'])
    if upd_cnt > 0:  # Only print if there were updates
        print(colors['GREEN'] + f"{upd_cnt} Mod{'s' if upd_cnt > 1 else ''} got an Update ✓\n" + colors['END'])

    return updated_dates, updated_ids


def process_update(url, workshop_id, result, updated_dates, updated_ids):
    # Assuming `result['date']` is available here, if not, this should be handled earlier
    updated_dates[url] = {"date": result['date'], "name": result['name']}
    workshop_key = f'workshop_download_item {game_id} {workshop_id}'
    updated_ids[workshop_key] = workshop_id


def main():
    print(colors['CYAN'] + "Loading URLs..." + colors['END'])
    urls = load_urls()
    if not urls:
        return

    print(colors['CYAN'] + "Checking for updates..." + colors['END'])
    last_updated = get_last_updated()

    updated_dates, updated_ids = check_updates(urls, last_updated)

    print(colors['CYAN'] + "Updating records..." + colors['END'])
    update_records(last_updated, updated_dates, updated_ids)

    print(colors['GREEN'] + "Update check completed." + colors['END'])


if __name__ == "__main__":
    main()
