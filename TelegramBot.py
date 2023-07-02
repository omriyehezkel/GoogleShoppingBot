import os
import telebot
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
from PIL import Image
from io import BytesIO
import re
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from urllib.parse import unquote

# Bot token
TOKEN = 'YOUR TOKEN'

# Creating an instance of the bot
bot = telebot.TeleBot(TOKEN)

# Set Chrome options
options = Options()
# options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)

# File path for saving the image
image_path = r'YOUR IMAGE PATH'

# Global variable to store the waiting state
waiting_for_product_name = False

# Handler for the /start command


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(
        message, "Welcome to the Product Price Search Bot! Please use the /search command to search for product prices.")

# Handler for the /search command


@bot.message_handler(commands=['search'])
def search_handler(message):
    global waiting_for_product_name
    waiting_for_product_name = True
    bot.reply_to(
        message, "Please enter the product name or send an image of the product")

# Wait for user input (text or image)


@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_message(message):
    global waiting_for_product_name

    if waiting_for_product_name:
        if message.content_type == 'text':
            product_name = message.text
            result = search_product_price_text(product_name)
            bot.reply_to(message, result)
            waiting_for_product_name = False
        elif message.content_type == 'photo':
            print(f"Received image from user: {message.from_user.username}")
            bot.send_message(message.chat.id, "Performing image search...")
            # Get the photo file_id
            file_id = message.photo[-1].file_id
            # Get the file path
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path
            # Download the photo
            image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            # Perform image search
            result = search_product_price_image(image)
            bot.reply_to(message, result)
            waiting_for_product_name = False
        elif message.content_type == 'document':
            if message.document.mime_type.startswith('image/'):
                print(
                    f"Received image from user: {message.from_user.username}")
                bot.send_message(message.chat.id, "Performing image search...")
                # Download the image
                file_info = bot.get_file(message.document.file_id)
                image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
                response = requests.get(image_url)
                image = Image.open(BytesIO(response.content))
                # Perform image search
                result = search_product_price_image(image)
                bot.reply_to(message, result)
                waiting_for_product_name = False
            else:
                bot.reply_to(
                    message, "Invalid document type. Please send a valid image.")
    else:
        bot.reply_to(
            message, "Invalid input. Please enter the product name or send an image of the product.")


def clean_link(link):
    parsed_link = urlparse(link)
    query_params = parse_qs(parsed_link.query)
    cleaned_link = query_params.get('url', [''])[0]
    return cleaned_link


def search_product_price_text(product_name):
    driver_path = r"CHROME DRIVER PATH"
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # URL for Google Shopping search
    url = f'https://www.google.com/search?q={product_name}&tbm=shop&tbs=vw:l'

    # Get the HTML content of the page
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all products listed on the page
    products = soup.find_all('div', {'class': 'sh-dlr__list-result'})

    if not products:
        driver.quit()
        return "Sorry, I couldn't find any results for that product."

    # Get the product name, price, and link for each product
    product_data = []
    for product in products:
        name_element = product.find('div', {'class': 'translate-content'})
        name = 'שם המוצר -' + name_element.text.strip() if name_element else "N/A"

        price_element = product.find('span', class_='a8Pemb OFFNJ')
        price = price_element.text.strip() if price_element else "N/A"

        link_element = product.find('a', class_='shntl')
        link = link_element['href'] if link_element else "N/A"
        link = clean_link(link)

        search_words = product_name.lower().split()
        if all(word in name.lower() or word in name.lower()[:len(name)//2] for word in search_words):
            # Extract the price value from the string and convert it to a float
            price_match = re.search(r'\d+\.?\d*', price)
            price_value = float(price_match.group()
                                ) if price_match else float('inf')

            product_data.append(
                {'name': name, 'price': price_value, 'link': link})

    driver.quit()

    # Sort the products by price (lowest to highest)
    product_data.sort(key=lambda x: x['price'])

    # Generate the response message with the top 3 results
    response = "Here are the top 3 results:\n"
    for i, product in enumerate(product_data[:3], start=1):
        response += f"\n{i}. {product['name']}\nPrice: {product['price']} USD\nLink: {unquote(product['link'])}\n"

    return response


def search_product_price_image(image):
    driver_path = r"CHROME DRIVER PATH"
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Open Google Images
    driver.get("https://images.google.com/")

    # Click on the camera icon
    camera_button = driver.find_element(By.CLASS_NAME, 'Gdd5U')
    camera_button.click()

    # Upload the image
    upload_button = None
    tries = 0
    while tries < 3:
        try:
            upload_button = driver.find_element(
                By.CSS_SELECTOR, "input[type='file']")
            break
        except NoSuchElementException:
            tries += 1
            time.sleep(1)

  #  if not upload_button:
   #     driver.quit()
    #    return "Failed to find the upload button."

    image.save(image_path)
    upload_button.send_keys(image_path)

    # Wait for search results to load
    driver.implicitly_wait(20)

    driver.get(driver.current_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all products listed on the page
    products = soup.find_all()

    product_data = []

    for result in products:
        # Get product name
        name_element = result.find("div", class_='UAiK1e')
        name = name_element.text.strip() if name_element else "N/A"

        # Get price
        price_element = result.find("span", class_="DdKZJb")
        price = price_element.text.strip() if price_element else "N/A"

        # Get page URL
        link_element = result.find("a", class_="GZrdsf lXbkTc")
        link = link_element.get("href") if link_element else "N/A"

        if price != 'N/A' and link not in [product['link'] for product in product_data]:
            product_data.append(
                {'name': name, 'price': price, 'link': link})



    # Sort the products by price (lowest to highest)
    product_data = sorted(product_data, key=lambda x: float(
        re.sub(r'[^\d.]', '', x['price'])))



    # Generate the response message with the top 10 results
    response = "Here are the top 10 results:\n"
    for i, product in enumerate(product_data[:10], start=1):
        response += f"\n{i}. Name: {product['name']}\n   Price: {product['price']} USD\n   Link: {unquote(product['link'])}\n"

    return response


# Start the bot
bot.polling()
