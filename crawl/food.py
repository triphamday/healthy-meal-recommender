import random
import pandas as pd
import requests
from time import sleep
import os
import re
from fractions import Fraction  # Thêm import này

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_image(url, save_path):
# url: URL của hình ảnh cần tải xuống
# save_path: đường dẫn tệp cục bộ nơi mà hình ảnh sau khi tải xuống sẽ được lưu
    try:
        # gửi một yêu cầu HTTP GET đến 'url'
        # + 'url': biến chứa địa chỉ URL của tệp cần tải xuống
        # + 'stream=True': tải xuống từng nội dung của phản hồi theo từng phần nhỏ. đỡ nặng :)))
        response = requests.get(url, stream=True)
        # Kiểm tra mã nếu bằng 200 thì có nghĩa yêu cầu đã thành công
        if response.status_code == 200:
            # Mở tệp đã ghi
            # open(save_path, 'wb'): mở tệp ở đường dẫn save_path đã lưu trong chế độ nhị phân
            # + 'save_path': đường dẫn nơi tệp sẽ được lưu vào
            # + 'wb': chế độ nhị phân, chế độ này sẽ được sử dụng khi làm việc với các tệp không phải văn bản
            # 'with ... as file':  Sử dụng cú pháp with để đảm bảo tệp được đóng đúng cách sau khi hoàn thành việc ghi,
            #                       ngay cả khi có lỗi xảy ra trong quá trình ghi.
            with open(save_path, 'wb') as file:
                # Ghi nội dung phản hồi vào tệp theo từng phần
                for chunk in response.iter_content(1024):
                    file.write(chunk)
    except Exception as e:
        print(f"Error downloading {url}: {e}")


# Initialize WebDriver
service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Open URL
driver.get('https://www.food.com/ideas/gluten-free-essentials-6320#c-20426')
sleep(random.randint(5, 10))

# Wait for all elements to load
wait = WebDriverWait(driver, 10)

elems = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.smart-content')))

titles = []
links = []
descriptions = []
images = []
image_paths = []

# Create directory to save images
os.makedirs('images', exist_ok=True)


# Clean title function
def clean_title(title):
    return re.sub(r'[^a-zA-Z0-9]', '_', title)


for index, elem in enumerate(elems, start=1): # index bắt đầu từ 1
    # Get title
    try:
        title_elem = elem.find_element(By.CSS_SELECTOR, 'h2.title a')
        title = title_elem.text.strip() if title_elem else ''
    except:
        title = ''
    titles.append(title)

    # Get link
    try:
        link_elem = title_elem.get_attribute('href') if title_elem else ''
    except:
        link_elem = ''
    links.append(link_elem)

    # Get description
    try:
        description_elem = elem.find_element(By.CSS_SELECTOR, 'p.description')
        description = description_elem.text.strip() if description_elem else ''
    except:
        description = ''
    descriptions.append(description)

    # Get image
    try:
        image_elem = elem.find_element(By.CSS_SELECTOR, 'div.smart-photo-inner img')
        image_url = image_elem.get_attribute('src') or image_elem.get_attribute('data-src')
    except:
        image_url = ''
    images.append(image_url)

    # Download image and save locally
    if image_url:
        # dọn sạch title
        cleaned_title = clean_title(title)
        # tạo tên tệp bằng cách sử dụng định dạng chuỗi
        # {index:02d}: định dạng index thành 1 số nguyên 2 chữ số
        # + '0': nếu có ít hơn 2 chữ số, nó sẽ được đệm bằng số 0 phía trước
        # + '2': là độ dài tối thiểu của chuỗi kết quả
        # + 'd': giá trị sẽ được định dạng như một số nguyên (d=decimal)
        # f: formatted string literal
        image_name = f"{index:02d}_{cleaned_title}.jpg"
        # tạo đường dẫn
        # os.path.join: đảm bảo đường dẫn được tạo ra đúng theo hệ điều haành trên máy

        save_path = os.path.join('images', image_name)
        download_image(image_url, save_path)
        image_paths.append(save_path)
    else:
        image_paths.append('')

nutritions = []
times = []
authors = []
ingredients = []
directions = []

elems_offers = driver.find_elements(By.CLASS_NAME, 'smart-card.container-sm.recipe')
length = len(elems_offers)

for offer in elems_offers:
    driver.switch_to.window(driver.window_handles[0])
    offer.click()
    sleep(3)
    driver.switch_to.window(driver.window_handles[1])

    # Get times
    try:
        time_elem = driver.find_element(By.CSS_SELECTOR, 'dd.facts__value.svelte-1dqq0pw')
        time = time_elem.text if time_elem else ''
    except:
        time = ''
    times.append(time)

    # Get authors
    try:
        author_elem = driver.find_element(By.CSS_SELECTOR, '.byline.svelte-176rmbi a')
        author = author_elem.text if author_elem else ''
    except:
        author = ''
    authors.append(author)

    # Get ingredients
    li_elems = driver.find_elements(By.CSS_SELECTOR, 'ul.ingredient-list.svelte-1dqq0pw li')
    content = ''
    for li in li_elems:
        # Check span structure
        if li.find_elements(By.XPATH, ".//span[@class='ingredient-quantity svelte-1dqq0pw']") and li.find_elements(
                By.XPATH, ".//span[@class='ingredient-text svelte-1dqq0pw']"):
            quantity_elem = li.find_element(By.CSS_SELECTOR, '.ingredient-quantity.svelte-1dqq0pw')
            ingredient_elem = li.find_element(By.CSS_SELECTOR, '.ingredient-text.svelte-1dqq0pw')

            quantity = quantity_elem.text.strip() if quantity_elem else ''
            ingredient = ingredient_elem.text.strip() if ingredient_elem else ''
            if quantity and ingredient:
                if content:
                    content += ' --> '
                content += f"{quantity} {ingredient}"
        else:
            continue
    ingredients.append(content)

    # Get directions
    li_elems_direct = driver.find_elements(By.CSS_SELECTOR, 'ul.direction-list.svelte-1dqq0pw li')
    content = ''
    for li in li_elems_direct:
        direction = li.text.strip() if li else ''
        if direction:
            if content:
                content += ' --> '
            content += f'{direction}'
    directions.append(content)

        # Click on the 'Nutrition information' button
    try:
        nutrition_button = driver.find_element(By.CSS_SELECTOR, 'button.facts__nutrition')
        nutrition_button.click()
        sleep(3)  # Wait for 5 seconds for the element to display
    except:
        print("Error clicking on 'Nutrition information' button")
    # Get nutrition information
    nutrition_info = ""
    try:
        nutrition_elem = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'section.recipe-nutrition__info.svelte-epeb0m'))
        )
        nutrition_info = nutrition_elem.text.strip()
    except:
        nutrition_info = "Nutrition information not found"
    nutritions.append(nutrition_info)

    driver.close()

driver.switch_to.window(driver.window_handles[0])
driver.close()

# Ensure all lists have the same length by adding default values
while len(times) < len(titles):
    times.append('')
while len(authors) < len(titles):
    authors.append('')
while len(ingredients) < len(titles):
    ingredients.append('')
while len(directions) < len(titles):
    directions.append('')
while len(nutritions) < len(titles):
    nutritions.append('')

# List to store nutrition columns
nutrition_columns = [
    "Calories",
    "Calories from Fat",
    "Total Fat",
    "Saturated Fat",
    "Cholesterol",
    "Sodium",
    "Total Carbohydrate",
    "Dietary Fiber",
    "Sugars",
    "Protein"
]

# Function to extract nutrition information
def extract_nutrition_info(text):

    lines = text.strip().split('\n')

    # Tạo một từ điển để lưu trữ dữ liệu dinh dưỡng
    nutrition_dict = {}

    # Duyệt qua từng dòng và chia thành các phần tử của từ điển
    for line in lines:
        # Check if the line contains a colon
        if ':' in line:
            parts = line.split(':')
            key = parts[0].strip()
            value = parts[1].strip()
        else:
            parts = line.rsplit(' ', 2)  # Split from the right twice
            if len(parts) == 3:
                key = parts[0]
                value = parts[1] + ' ' + parts[2]
            else:
                continue
        nutrition_dict[key] = value

    return nutrition_dict


nutrition_data_list = []


# Trích xuất thông tin dinh dưỡng từ dữ liệu văn bản
for nutrition_info in nutritions:
    nutrition_data = extract_nutrition_info(nutrition_info)
    nutrition_data_list.append(nutrition_data)

print(f"Titles: {len(titles)}")
print(f"Links: {len(links)}")
print(f"Descriptions: {len(descriptions)}")
print(f"Images: {len(images)}")
print(f"Image Paths: {len(image_paths)}")
print(f"Times: {len(times)}")
print(f"Authors: {len(authors)}")
print(f"Ingredients: {len(ingredients)}")
print(f"Directions: {len(directions)}")
print(f"Nutritions: {len(nutrition_data_list)}")

# Combining nutrition information with other recipe data
df = pd.DataFrame({
    'Title': titles,
    'Link': links,
    'Description': descriptions,
    'Image URL': images,
    'Image Path': image_paths,
    'Time': times,
    'Author': authors,
    'Ingredient': ingredients,
    'Direction': directions,
    'Nutrition': nutrition_data_list
})

# Split nutrition information into separate columns
for col in nutrition_columns:
    df[col] = df['Nutrition'].apply(lambda x: x.get(col, None))

# Drop the original 'Nutrition' column
df.drop(columns=['Nutrition'], inplace=True)

# Create DataFrame
print(df)
df.to_csv('gluten_free_recipes.csv', index=False)

# Quit the browser
driver.quit()
