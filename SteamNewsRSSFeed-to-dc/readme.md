# Cavemen Python RSS Feed Script

A Python script to fetch Steam news from an RSS feed and post it to a Discord channel via a webhook.

## Features

- Fetches Game news from a Steam RSS feed.
- Saves the last 10 posted links.
- Posts news updates to a specified Discord channel using a webhook.
- Configuration managed through a `config.json` file for easy setup.

## Configuration

The script uses a `config.json` file for settings, which includes the Discord webhook URL, RSS feed link, embed color, game name, and author icon URL.

## Sample `config.json`

```json
{
  "dcwebhook": "your_discord_webhook_url",  // The URL of the Discord webhook
  "rssfeed": "steam_rss_feed_url",          // The URL of the Steam RSS feed
  "embeds_color": 16750848,                 // The color of the embed's sideline in decimal value (use SpyColor.com for conversion)
  "gamename": "gamename_below_embed",       // The game name to display at the end of the embed along with the post date
  "author_icon": "direct_image_link"        // A direct URL to an image (ending in .jpg, .jpeg, or .png) to show as an author icon
}
