# Steam Workshop Updater

A Python script to check if items from a list of Steam Workshop URLs have been updated.

## Installation

1. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### Files

- **`update.py`**: 
    - On line 6, replace `game_id` with the Steam AppID from the Game. The default ID is set for Stellaris.
- **`url_mod_collection.json`**: 
    - Supports multiple URLs. Expand the list and ensure each URL is enclosed in `""`.
- **`updated_entrys.json`**:
    - This files saves all Workshop Entrys with their names and Dates when they got Last Updated.
    - Must include `{}` as its content. Do not make any changes to this structure.

### Important

- The script will crash if any of the following files are missing:
  - `url_mod_collection.json`

## Usage

1. Ensure the following files are present and correctly configured:
    - `url_mod_collection.json`

2. Run the script:
    ```bash
    python update.py
    ```

## Example `url_mod_collection.json`

```json
[
    "http://steamcommunity.com/sharedfiles/filedetails/?id=123456789",
    "http://steamcommunity.com/sharedfiles/filedetails/?id=987654321",
    "http://steamcommunity.com/sharedfiles/filedetails/?id=987654321"
]
