from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
from selenium.webdriver.chrome.options import Options
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date


def card_data():
    product_data = []
    file_content = []
    with open('products.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if len(row) == 0:
                break
            if line_count == 0:
                line_count += 1
            else:
                if row[0].strip() == "":
                    continue
                if row[0].strip() in file_content:
                    continue
                product_data.append(row)
                line_count += 1
        return product_data

def brac_clean(data):
    new_data = []
    for i in data:
        if "(" in i:
            i = i.replace(")", "")
            i = i.split("(")
            new_data = new_data + i
        elif "paper" in i.lower() or "bundle" in i.lower() or "cover" in i.lower():
            continue
        else:
            new_data.append(i)
    return new_data


def swap(newList):
    newList[0], newList[-1] = newList[-1], newList[0]

    return newList


def swap_price(data):
    new = []
    first = int(data[0].replace("₹","").replace(",",""))
    second = int(data[1].replace("₹","").replace(",",""))
    if first > second:
        data[0], data[1] = data[1], data[0]
    return data


def scrape():
    scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('keyss.json', scope)
    client = gspread.authorize(credentials)
    sheet = client.open('jaypee_data')
    sh = sheet.worksheets()
    for s in sh:
        if str(date.today()) == s.title:
            sheet.del_worksheet(s)
    worksheet = sheet.add_worksheet(title="{}".format(date.today()), rows="800", cols="25")
    data = card_data()
    worksheet.insert_row(["ISBN","AUTHOR","TITLE","ED","YEAR","DIS", "CURR", "PRICE", "STREAM", "SUBJECT", "LEVEL", "Amazon_data"],1)
    for i in data:
        try:
            options = Options()
            # options.add_argument('--headless')
            # options.add_argument(
            #     "user-agent=Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19")
            driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
            driver.maximize_window()
            driver.implicitly_wait(20)
            driver.get("https://www.amazon.in/")
            driver.find_element(By.CSS_SELECTOR, '#twotabsearchtextbox').send_keys(i[0])
            driver.find_element(By.CSS_SELECTOR, '#nav-search-submit-button').click()
            res = driver.find_elements(By.XPATH, "//div[@class='sg-col-inner']//div[@class='a-section a-spacing-none a-spacing-top-small s-price-instructions-style']")
            for re in res:
                if re.text == "Product Bundle":
                    continue
                else:
                    if "kindle edition" in re.text.lower():
                        ren = driver.find_element(By.XPATH,
                                             "//div[@class='sg-col-inner']//div[@class='a-section a-spacing-none a-spacing-top-mini']//div[@class='a-row a-size-base a-color-base'][2]")
                        if "(" in ren.text:
                            temp_data = ren.text.split("\n")
                            temp_data = brac_clean(temp_data)
                        else:
                            temp_data = ren.text.split("\n")
                            if "-" in temp_data[0] or "%" in temp_data[0]:
                                temp_data = swap(temp_data)
                            elif "paper" in temp_data[0].lower or "bundle" in temp_data[0].lower or "cover" in temp_data[0].lower:
                                temp_data = temp_data[1:]
                        swap_price(temp_data)
                        i = i + temp_data
                    else:
                        if "(" in re.text:
                            temp_data = re.text.split("\n")
                            temp_data = brac_clean(temp_data)
                        else:
                            temp_data = re.text.split("\n")[1:]
                            if "-" in temp_data[0] or "%" in temp_data[0]:
                                temp_data = swap(temp_data)
                        swap_price(temp_data)
                        i = i + temp_data
                    break
            driver.quit()
            worksheet.insert_row(i, 2)
        except Exception as e:
            print(e)
            driver.quit()
            i.append("error")
            worksheet.insert_row(i, 2)

scrape()






