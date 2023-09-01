import openpyxl
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from selenium.common.exceptions import TimeoutException


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get('https://arbetsformedlingen.se/platsbanken/annonser?q=energi')
time.sleep(10)
try:
    element = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-search/div[2]/pb-feature-tabs/div[2]/pb-section-search-result/div/div/div/div/div/div/pb-feature-pagination/digi-navigation-pagination/div/nav/div/ol/li[6]/digi-button/button/span/span")
    inner_text = element.get_attribute("innerText")
    page_number = int(inner_text)
    print("Extracted integer:", page_number)
except:
    print("Unable to convert inner text to integer")
    page_number = 50

all_links = []
for num in range(page_number):
    url = 'https://arbetsformedlingen.se/platsbanken/annonser?q=energi&page=' + str(num + 1)
    driver.get(url)
    count = 0
    while True:
        count = count +1 
        time.sleep(2)
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/platsbanken/annonser/')]")
        if links:
            break  
        if count == 15:
            break
        print("No links found. Retrying...")
    
    for link in links:
        job_link = link.get_attribute('href')
        all_links.append(job_link)
        
def is_id_present(api_url, target_id):
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        for item in data:
            if 'td_post_theme_settings' in item:
                settings = item['td_post_theme_settings'][0]  # The settings are stored as a list
                if f"/{target_id}" in settings:
                    return True
        
        return False
    else:
        print(f"API request failed with status code: {response.status_code}")
        return False

def scrape_job_data(row):
#     try:
    driver.get(row)
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "spacing.break-title")))
        title = driver.find_element(By.CLASS_NAME, "spacing.break-title").text
    except TimeoutException:
        print("Skipping...")
        title = ''
        
#     except:
#         time.sleep(5)
#         title = driver.find_element(By.CLASS_NAME, "spacing.break-title").text
    form_of_employment = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-job/div/section/div/div[2]/div[2]/section/pb-section-job-quick-info/div[2]/div[3]/span[2]").text
    try:
        location =  driver.find_element(By.ID,'pb-job-location').text
        location = location.replace("Kommun: ", "")
    except:
        try:
            location =  driver.find_element(By.ID,'pb-job-location').text
            location = location.replace("Kommun: ", "")
        except:
            location = ''
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="pb-root"]/pb-page-job/div/section/div/div[2]/div[2]/section/pb-section-job-quick-info/div[2]/div[1]/span[2]')))
    scope = driver.find_element(By.XPATH, '//*[@id="pb-root"]/pb-page-job/div/section/div/div[2]/div[2]/section/pb-section-job-quick-info/div[2]/div[1]/span[2]').text

    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID, "pb-company-name")))
    duration = driver.find_element(By.CLASS_NAME, "upper-fist").text

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-job/div/section/div/div[2]/div[1]/div[1]/img')))
        img_element = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-job/div/section/div/div[2]/div[1]/div[1]/img')
        image_link = img_element.get_attribute("src")
    except:
        image_link =''
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-job/div/section/div/div[2]/div[2]/section/div/pb-feature-job-qualifications/div/pb-section-job-qualification/div/div/ul/li')))         
        req = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-job/div/section/div/div[2]/div[2]/section/div/pb-feature-job-qualifications/div/pb-section-job-qualification/div/div/ul/li').text
    except:
        req =''
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(( By.XPATH, "/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-job/div/section/div/div[2]/div[2]/section/pb-section-job-main-content")))                               
        about_job = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[7]/div/div/main/div[3]/div/div/div[2]/div/div/div/div/div[2]/div[2]/pb-root/div/pb-page-job/div/section/div/div[2]/div[2]/section/pb-section-job-main-content")
        about_job_html = about_job.get_attribute("outerHTML")
        extra = '<a href="Source URL" class="button">Ansök på arbetsförmedlingen</a>'
        about_job_html = about_job_html + extra
    except:
        about_job_html =''
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME,'salary-type.ng-star-inserted')))                               
    sal_type = driver.find_element(By.CLASS_NAME,'salary-type.ng-star-inserted').text
    sal_type = sal_type.split(':')[1]
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME,'salary-description.ng-star-inserted')))                               
        sal = driver.find_element(By.CLASS_NAME,'salary-description.ng-star-inserted').text
    except:
        sal =''
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME,'address-container')))                               
        address = driver.find_element(By.CLASS_NAME,'address-container').text
    except:
        address=''
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH,'//*[@id="pb-root"]/pb-page-job/div/section/div/div[2]/div[2]/aside[1]/div/pb-section-job-apply-component/div/div/div[1]/strong')))                               
    last_date= driver.find_element(By.XPATH,'//*[@id="pb-root"]/pb-page-job/div/section/div/div[2]/div[2]/aside[1]/div/pb-section-job-apply-component/div/div/div[1]/strong').text
    fixed_year = "2023"

    # Define a dictionary to map Swedish month names to numerical values
    month_mapping = {
        'januari': '01', 'februari': '02', 'mars': '03', 'april': '04',
        'maj': '05', 'juni': '06', 'juli': '07', 'augusti': '08',
        'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
    }
    # Split the input string into parts
    parts = last_date.split()

    day = parts[0]
    month = month_mapping.get(parts[1].lower(), '01')  
    last_date = f'{fixed_year}-{month}-{day}'
    print(last_date)

    job_info = {
        "title": title,
        "td_source_url": row,
        "td_via_url":row,
        "feature_image":image_link, 
        "content4": form_of_employment,
        "content5": req,
        "content1": about_job_html,
        "content2": sal_type,
        "content3": address,
        "awsm_job_expiry": last_date,
        "job_types":scope,
        "job_location": location,
        "job_duration": duration,
        "job_salary":sal,
        "job_categories":"energi"
    }


    return job_info

# Define the API endpoint
api_url_get = "https://aktuellenergi.se/wp-json/wpjobopenings/v1/job-openings"
api_url_post = "https://aktuellenergi.se/wp-json/wpjobopenings/v1/add-job"

 
for row in all_links:
    try:
        job_info = scrape_job_data(row)
        print(job_info)
        target_id = row.split('/')[-1]

        if is_id_present(api_url_get, target_id):
            print(f"ID {target_id} is present in the data.")
        else:
            print(f"ID {target_id} is not present in the data.")
            response = requests.post(api_url_post, json=job_info)

            # Check the response status
            if response.status_code == 200:
                print("Job posted successfully!")
            else:
                print("Failed to post job.")
                print("Response:", response.text)
    except:
        print('passs')
        pass
