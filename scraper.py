from bs4 import BeautifulSoup
import requests
import re
import os
import shutil
import json


data_folder_path = 'data'
if not os.path.isdir(data_folder_path):
    os.makedirs(data_folder_path)

result = []

pages = ['1', '2', '3', '4']
for page in pages:

    first_truck_url = ''
    title = ''
    price_int = 0
    mileage_int = 0
    #color = ''
    power_int = 0
    description = ''

    url = 'https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault?currentpage=' + page

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    first_truck = soup.find('div', class_='ls-elem ls-elem-gap')

    first_truck_id = first_truck.find('div', attrs={'class': 'ls-full-item'})['id']
    id_int = int(re.sub(r'listItem_', '', first_truck_id))

    truck_gallery_folder = os.path.join(data_folder_path, first_truck_id)
    if not os.path.isdir(truck_gallery_folder):
        os.makedirs(truck_gallery_folder)

    first_truck_href = first_truck.find('a', attrs={'data-item-name': "detail-page-link"})['href']

    first_truck_url = 'https://www.truckscout24.de' + first_truck_href

    first_truck_soup = BeautifulSoup(requests.get(first_truck_url).content, 'html.parser')

    gallery = first_truck_soup.find_all('div', attrs={'class': 'gallery-picture'})
    for i in range(3):
        url = gallery[i].find('img')['data-src']

        response = requests.get(url, stream=True)
        picture_path = os.path.join(truck_gallery_folder, str(i) + '.jpg')
        if response.status_code == 200:
            with open(picture_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            print('Image sucessfully downloaded')
        else:
            print('Image couldn\'t be retrieved')

    title = first_truck_soup.find('h1').text

    price_str = first_truck_soup.find('div', class_='d-price sc-font-xl').text
    price_int = int(re.sub(r'[^\d.]', '', price_str).replace('.', ''))

    is_mileage = first_truck_soup.find(class_='itemlbl', string='Kilometer').next_sibling.next_sibling.text
    if is_mileage:
            # ПАРСИТЬ ДЛЯ ЯЗЫКА ДОЙЧ ИЛИ ПО РЕГЕКС КИЛОМЕТРОВ
        mileage_str = first_truck_soup.find(class_='itemlbl', string='Kilometer').next_sibling.next_sibling.text
        mileage_int = int(re.sub(r'[^\d.]', '', mileage_str).replace('.', ''))

    try:
        first_truck_soup.find('div', string='Farbe').next_sibling.next_sibling.text
    except:
        color = ''
    else:
        color = first_truck_soup.find('div', string='Farbe').next_sibling.next_sibling.text
    # ИЛИ color = is_color
    is_power = first_truck_soup.find('div', string='Leistung').next_sibling.next_sibling.text
    if is_power:
        # ИЛИ power_str = is_power
        power_str = first_truck_soup.find('div', string='Leistung').next_sibling.next_sibling.text
        power_int = int(re.match(r'(\d+).kW', power_str).group(1))

    desc_title = first_truck_soup.find(attrs={'data-item-name': "description"}).h3.text

    desc_main = first_truck_soup.find('div', attrs={'class': 'short-description'}).text

    description_unformatted = desc_title + ' ' + desc_main
    description = re.sub('\s+', ' ', description_unformatted)

    truck_data = {'id': id_int, 'href': first_truck_url,
                  'title': title, 'price': price_int,
                  'mileage': mileage_int, 'color': color,
                  'power': power_int, 'description': description}

    result.append(truck_data)

json_file = 'data.json'
json_file_path = os.path.join(data_folder_path, json_file)
with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=8, ensure_ascii=False)
print('json created')
