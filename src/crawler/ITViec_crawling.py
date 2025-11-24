from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
from time import sleep
import pandas as pd
import numpy as np
import random
import time

# Hàm convert text thành datetime và format đẹp
def parse_posted_date(text):
    now = datetime.now()
    text = text.lower().strip()
    dt = None
    try:
        if "hour" in text:
            n = int(text.split()[0])
            dt = now - timedelta(hours=n)
        elif "day" in text:
            n = int(text.split()[0])
            dt = now - timedelta(days=n)
        elif "minute" in text:
            n = int(text.split()[0])
            dt = now - timedelta(minutes=n)
        else:
            dt = datetime.strptime(text + f" {now.year}", "%b %d %Y")
    except:
        dt = None
    # Trả về cả datetime object và string format đẹp
    formatted = dt.strftime("%d/%m/%Y %H:%M") if dt else "N/A"
    return dt, formatted

def dangNhap(login_url):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # lấy và tới địa chỉ trang đăng nhập
    driver.get(login_url)
    return driver

def crawling(driver, url):
    # vào trang cần crawl
    driver.get(url)
    i = 1
    job_names = []
    company_names = []
    salaries = []
    position_names = []
    kind_jobs = []
    array_skills = []
    locate_names = []
    exp_skills = []
    domain_arr = []
    post_dates_text = []
    post_dates_real = []
    post_dates_formatted = []
    while i <= 1:
        # lấy job name
        elems = driver.find_elements(By.CSS_SELECTOR, "h3.imt-3.text-break") 
        job_names.extend([elem.text for elem in elems])
        # lấy tên công ty
        elems = driver.find_elements(By.CSS_SELECTOR, "span.ims-2.small-text.text-hover-underline") 
        company_names.extend([elem.text for elem in elems]) 
        # lấy loại hình làm việc: remote/office
        elems = driver.find_elements(By.CSS_SELECTOR, "div.text-rich-grey.flex-shrink-0") 
        kind_jobs.extend([elem.text for elem in elems]) 
        # lấy các kỹ năng, công cụ sử dụng cơ bản
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card")
        for job in job_cards:
            skill_elems = job.find_elements(By.CSS_SELECTOR, "div.imt-4.imb-3.d-flex.igap-1 a")
            skills = [s.text for s in skill_elems]
            array_skills.append(skills)
        # lấy địa chỉ làm việc
        job_titles = driver.find_elements(By.CSS_SELECTOR,"div.job-card h3[data-search--job-selection-target='jobTitle']")
        for title in job_titles:
            try: 
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", title)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", title)
                time.sleep(2)
                # lấy lương
                elems = driver.find_element(By.CSS_SELECTOR, "div.d-flex.align-items-center.gap-3 div.salary span.ips-2.fw-500") 
                salaries.append(elems.text)  
                # lấy vị trí công việc
                job_expertise = driver.find_element(By.XPATH,"//div[div[text()='Job Expertise:']]//a").text.strip()
                position_names.append(job_expertise)
                elems = driver.find_element(By.CSS_SELECTOR, "div.d-inline-block.text-dark-grey span.small-text.text-rich-grey") 
                locate_names.append(elems.text)
                elems = driver.find_element(By.CSS_SELECTOR, "section.job-experiences div.paragraph") 
                exp_skills.append(elems.text)
                # Lấy tất cả domain
                elems = driver.find_elements(By.CSS_SELECTOR,"div.d-flex.flex-wrap.igap-2 div.itag")
                # Lấy text từng domain
                domains = [e.text.strip() for e in elems]
                domain_arr.append(domains)
                # Lấy thông tin ngày đăng
                items = driver.find_elements(By.CSS_SELECTOR, "div.preview-header-item")
                for item in items:
                    try:
                        # Kiểm tra xem div có svg icon #clock không
                        svg_use = item.find_element(By.CSS_SELECTOR, "svg use")
                        href = svg_use.get_attribute("href")
                        if href and "#clock" in href:
                            # Lấy text của span chứa thời gian
                            posted_text = item.find_element(By.TAG_NAME, "span").text.strip()
                            post_dates_text.append(posted_text)
                            dt, formatted = parse_posted_date(posted_text)
                            post_dates_real.append(dt)
                            post_dates_formatted.append(formatted)
                    except:
                        continue
            except NoSuchElementException:
                print("chua lay duoc thong tin")   
        try:
            pages = driver.find_element(By.CSS_SELECTOR, "div.pagination-search-jobs.d-flex.justify-content-center.ipb-16")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pages)
            time.sleep(0.2)
            nexttrang = driver.find_element(By.CSS_SELECTOR, 'div.page.next a')
            nexttrang.click()
            sleep(random.randint(1,3))
            i += 1
        except NoSuchElementException:
            print("khong dung dia chi")
    return job_names, company_names, salaries, position_names, kind_jobs, array_skills, locate_names, exp_skills, domain_arr, post_dates_formatted

# hàm main
def main():
    url = "https://itviec.com/it-jobs?job_selected=cloud-database-reliability-engineer-oivan-2740"
    login_url = "https://itviec.com/sign_in"
    driver = dangNhap(login_url)
    a = input("nhap enter de tiep tuc: ")
    if a == "":
        job_names, company_names, salaries, position_names, kind_jobs, array_skills, locate_names, exp_skills, domain_arr, post_dates_formatted = crawling(driver,url)
        
        df = pd.DataFrame({
            "job_names": job_names,
            "company_names": company_names,
            "salaries": salaries,
            "position_names": position_names,
            "kind_jobs": kind_jobs,
            "array_skills": array_skills,
            "locate_names": locate_names,
            "exp_skills": exp_skills,
            "domain_arr": domain_arr,
            "post_dates_formatted": post_dates_formatted
        })
        df.to_csv("D:/I. KhongPhanLoai/IT-job-analysis-VN/data_raw/ITViec_crawling_data.csv", index=False, encoding="utf-8-sig")
    else:
        print("tam dung ham!")
        return None
main()