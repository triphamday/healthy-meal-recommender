import random
import pandas as pd
import requests
from time import sleep
import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

names = []
descriptions = []
images = []
image_paths = []
times = []
ingredients = []
directions = []
nutritions = []  # calories, total_fat, saturated fat, cholesterol, sodium, total cacbonhydrate, dietary fiber, sugars, protein

# Initialize WebDriver
service = Service(r'D:\UIT\SEMESTER\3. TIỀN XỬ LÍ VÀ XÂY DỰNG BỘ DỮ LIỆU\Đồ án\EatingWell\Salad\msedgedriver.exe')
driver = webdriver.Edge(service=service)

# Open URL
driver.get(r'https://www.eatingwell.com/easy-15-minute-make-ahead-appetizer-recipes-8404225')
sleep(random.randint(5, 10))

# Wait for all elements to load
wait = WebDriverWait(driver, 5)
elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.comp.list-sc-item.mntl-block.mntl-sc-list-item")))

unicode_fractions = {
    '½': 0.5,
    '⅓': 1/3,
    '⅔': 2/3,
    '¼': 0.25,
    '¾': 0.75,
    '⅕': 0.2,
    '⅖': 0.4,
    '⅗': 0.6,
    '⅘': 0.8,
    '⅙': 1/6,
    '⅚': 5/6,
    '⅐': 1/7,
    '⅛': 1/8,
    '⅜': 3/8,
    '⅝': 5/8,
    '⅞': 7/8,
    '⅑': 1/9,
    '⅒': 0.1,
}

def convert_fractions(text):
    # Thay thế các phân số Unicode bằng giá trị số tương ứng từ từ điển
    for fraction, value in unicode_fractions.items():
        text = text.replace(fraction, str(value))
    return text

def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        else:
            print(f"Failed to download image from {url} - Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")


# Create directory to save images
image_folder = r"10_Easy,_15-Minute_Appetizers_You_Can_Make_Ahead"
os.makedirs(image_folder, exist_ok=True)


# Clean title function
def clean_title(title):
    return re.sub(r'[^a-zA-Z0-9]', '_', title)


# MAIN PAGE
for index, elem in enumerate(elems, start=1):
    # GET name
    try:
        name_elem = elem.find_element(By.CSS_SELECTOR, "span.mntl-sc-block-heading__text")
        name = name_elem.text.strip() if name_elem else ''
    except:
        name = ''
    names.append(name)

    # GET image
    try:
        image_elem = elem.find_element(By.CSS_SELECTOR, 'div.img-placeholder img')
        image_url = image_elem.get_attribute('src') or image_elem.get_attribute('data-src')
    except:
        image_url = ''
    images.append(image_url)

    # download and save locally
    if image_url:
        cleaned_title = clean_title(name)
        image_name = f"{index:02d}_{cleaned_title}.jpg"
        save_path = os.path.join(image_folder, image_name)
        download_image(image_url, save_path)
        image_paths.append(save_path)
    else:
        image_paths.append('')

elems_offers = driver.find_elements(By.CSS_SELECTOR,
                                    'a.mntl-sc-block-universal-featured-link__link.mntl-text-link.button--contained-standard.type--squirrel')
length = len(elems_offers)

i=1
for offer in elems_offers:
    print(i)
    i = i + 1
    offer_link = offer.get_attribute('href')

    # Open the link in a new tab
    driver.execute_script("window.open('{}', '_blank');".format(offer_link))
    sleep(5)

    # Switch to the newly opened tab
    driver.switch_to.window(driver.window_handles[-1])

    # GET description
    try:
        desc_elem = driver.find_element(By.CSS_SELECTOR, "p.article-subheading.type--dog")
        desc = desc_elem.text.strip() if desc_elem else ''
    except:
        desc = ''
    descriptions.append(desc)

    # GET time
    try:
        time_elem = driver.find_element(By.CSS_SELECTOR, 'div.mntl-recipe-details__value')
        time = time_elem.text.strip() if time_elem else ''
    except:
        time = ''
    times.append(time)

    # GET ingredients
    ingredient_elems = driver.find_elements(By.CSS_SELECTOR, "ul.mntl-structured-ingredients__list li")
    recipe_ingredients = []
    for ingredient_elem in ingredient_elems:
        try:
            quantity_elem = ingredient_elem.find_element(By.CSS_SELECTOR, 'span[data-ingredient-quantity="true"]')
            quantity = convert_fractions(quantity_elem.text.strip()) if quantity_elem else ''
        except:
            quantity = 'error'

        try:
            unit_elem = ingredient_elem.find_element(By.CSS_SELECTOR, 'span[data-ingredient-unit="true"]')
            unit = unit_elem.text.strip() if unit_elem else ''
        except:
            unit = ''

        try:
            name_elem = ingredient_elem.find_element(By.CSS_SELECTOR, 'span[data-ingredient-name="true"]')
            ingredient_name = name_elem.text.strip() if name_elem else ''
        except:
            ingredient_name = ''

        ingredient = f"{quantity} {unit} {ingredient_name}".strip()
        recipe_ingredients.append(ingredient)
    ingredients.append(recipe_ingredients)

    # GET directions
    directions_elems = driver.find_elements(By.CSS_SELECTOR,
                                            "ol.comp.mntl-sc-block.mntl-sc-block-startgroup.mntl-sc-block-group--OL li.comp.mntl-sc-block.mntl-sc-block-startgroup.mntl-sc-block-group--LI")
    direction = []  # Tạo danh sách để lưu trữ nội dung của tất cả các bước hướng dẫn
    step_number = 1
    for elem in directions_elems:
        direction_content = elem.text.strip() if elem else ''
        direction_content = f"Step {step_number}: {direction_content}"
        direction.append(direction_content)  # Thêm nội dung của từng bước vào danh sách directions
        step_number = step_number + 1
    directions.append(direction)

    # GET nutrition
    nutrition_content = []
    try:
        # Check if nutrition button exists
        nutrition_button = driver.find_elements(By.CSS_SELECTOR, 'button.mntl-nutrition-facts-label__button.type--dog')
        if nutrition_button:
            # Click the button to show full nutrition label
            nutrition_button[0].click()
            sleep(5)  # Wait for the nutrition label to expand

            # Find and extract nutrition information
            nutrition_head = driver.find_element(By.CSS_SELECTOR, 'thead.mntl-nutrition-facts-label__table-head')
            calories_elem = nutrition_head.find_element(By.CSS_SELECTOR, 'tr.mntl-nutrition-facts-label__calories')
            calories_content = calories_elem.text.strip()
            nutrition_content.append(calories_content)

            # Find the nutrition body element
            nutrition_body = driver.find_element(By.CSS_SELECTOR, 'tbody.mntl-nutrition-facts-label__table-body')
            rows = nutrition_body.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                # Ignore the row with class "mntl-nutrition-facts-label__table-dv-row type--dog"
                if 'mntl-nutrition-facts-label__table-dv-row' in row.get_attribute('class'):
                    continue

                # Find the first td element in the row
                td_elements = row.find_elements(By.TAG_NAME, 'td')
                if td_elements:
                    # Get the text of the first td element
                    nutrient_name = td_elements[0].text.strip()
                    nutrition_content.append(nutrient_name)
                else:
                    nutrition_content.append("")
        else:
            # If no button, check for nutrition info in div
            nutrition_div = driver.find_element(By.CSS_SELECTOR, 'div.mntl-sc-block-universal-callout__body')
            nutrition_paragraphs = nutrition_div.find_elements(By.TAG_NAME, 'p')
            for paragraph in nutrition_paragraphs:
                nutrition_content.append(paragraph.text.strip())
    except NoSuchElementException:
        print("Nutrition information not available")
    nutritions.append(nutrition_content)

    # Close the current tab
    driver.close()

    # Switch back to the main tab
    driver.switch_to.window(driver.window_handles[0])

print(len(names))
print(len(descriptions))
print(len(times))
print(len(ingredients))
print(len(directions))
print(len(nutritions))

# Create a DataFrame to store all the data
data = {
    'Name': names,
    'Description': descriptions,
    'Time': times,
    'Ingredients': ingredients,
    'Directions': directions,
    'Nutrition': nutritions
}

df = pd.DataFrame(data)
print(df.head())

def clean_filename(filename):
    # Replace spaces with hyphens
    filename = filename.replace(' ', '_')
    # Remove any characters that are not alphanumeric, hyphens, or underscores
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '', filename)
    return filename

# Your desired filename
filename = "10_Easy,_15-Minute_Appetizers_You_Can_Make_Ahead"

# Clean the filename
cleaned_filename = clean_filename(filename) + ".csv"

# Save the DataFrame to a CSV file with the cleaned filename
df.to_csv(cleaned_filename, index=False)
