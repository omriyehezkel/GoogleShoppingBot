# GoogleShoppingBot
This is a Telegram bot written in Python that allows users to search and compare prices of products on Google Shopping. The bot supports searching by product name or by sending an image of the product.

## Getting Started

To use the bot, you need to have the following installed:

- Python 3.x
- Selenium
- BeautifulSoup
- requests
- Pillow
- telebot

You also need to have the Chrome web browser installed and the ChromeDriver executable.

### Installation

1. Clone the GitHub repository:

   ```bash
   git clone https://github.com/omriyehezkel/GoogleShoppingBot/tree/main)https://github.com/omriyehezkel/GoogleShoppingBot/tree/main

2. Install the required Python packages:
 
   ```bash
   pip install selenium beautifulsoup4 requests pillow telebot

3. Download the ChromeDriver executable and place it in the project directory.

### Configuration

1. Create a new bot on Telegram and obtain the bot token.

2. Open the `bot.py` file and replace `'YOUR_BOT_TOKEN'` with your actual bot token.

3. Update the `driver_path` variable in both the `search_product_price_text` and `search_product_price_image` functions with the correct path to the ChromeDriver executable.

### Usage

1. Start the bot by running the `bot.py` script:
   
   ```bash
    python bot.py


2. Open Telegram and search for your bot.

3. Send the `/search` command to initiate a product search.

4. Enter the product name or send an image of the product.

5. The bot will search for the product on Google Shopping and return the top 3 results with links and prices.

