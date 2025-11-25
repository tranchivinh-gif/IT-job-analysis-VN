
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from datetime import datetime, timedelta
from time import sleep
import pandas as pd
import numpy as np
import random
import time
import csv
import os

# ==========================
# GHI LOG LỖI
# ==========================
def log_error(msg):
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


# ==========================
# PARSE NGÀY ĐĂNG
# ==========================
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
    except Exception as e:
        log_error("Parse date error: " + str(e))
        dt = None
    formatted = dt.strftime("%d/%m/%Y %H:%M") if dt else "N/A"
    return dt, formatted


# ==========================
# ĐĂNG NHẬP
# ==========================
def dangNhap(login_url):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(login_url)
    return driver


# ==========================
# LẤY DANH SÁCH JOB ĐÃ CRAWL
# ==========================
def get_crawled_jobs(csv_path):
    if not os.path.exists(csv_path):
        return set()
    df = pd.read_csv(csv_path)
    return set(df["job_names"].astype(str))


# ==========================
# LƯU DÒNG CSV
# ==========================
def save_row(row_dict, file_path):
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=row_dict.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)


# ==========================
# LƯU TRANG HIỆN TẠI
# ==========================
def save_current_page(page_num):
    with open("current_page.txt", "w") as f:
        f.write(str(page_num))


def load_last_page():
    if not os.path.exists("current_page.txt"):
        return 1
    try:
        with open("current_page.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 1


# ==========================
# CRAWL 1 JOB — RETRY 3 LẦN
# ==========================
def crawl_one_job(driver, title, crawled_jobs, csv_path):
    retries = 3
    for attempt in range(retries):

        try:
            job_title_text = title.text.strip()

            if job_title_text in crawled_jobs:
                print("Bỏ qua job đã crawl:", job_title_text)
                return

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", title)
            sleep(0.2)
            driver.execute_script("arguments[0].click();", title)
            sleep(2)

            # ==========================
            # BẮT ĐẦU LẤY DỮ LIỆU
            # ==========================
            job_name = driver.find_element(By.CSS_SELECTOR, 
                "h2.text-it-black.text-hover-red.cursor-pointer.transition-duration-300.text-break"
            ).text.strip()

            company_name = driver.find_element(By.CSS_SELECTOR, 
                "div.d-flex.flex-column.gap-2.fw-600 span a"
            ).text.strip()

            # loại hình làm việc
            kind_job = "N/A"
            preview_items = driver.find_elements(By.XPATH, "//div[contains(@class,'preview-header-item')]")
            for item in preview_items:
                try:
                    svg = item.find_element(By.TAG_NAME, "svg")
                    paths = svg.find_elements(By.TAG_NAME, "path")
                    if len(paths) > 3:
                        kind_job = item.find_element(By.TAG_NAME, "span").text.strip()
                        break
                except:
                    pass

            # skills
            skills = []
            job_cards = driver.find_elements(By.CSS_SELECTOR, "section.preview-job-overview")
            for job in job_cards:
                skill_elems = job.find_elements(By.CSS_SELECTOR, "div.d-flex.flex-wrap.igap-2 a")
                skills = [s.text.strip() for s in skill_elems]

            # lương
            salary = driver.find_element(By.CSS_SELECTOR, 
                "div.d-flex.align-items-center.gap-3 div.salary span.ips-2.fw-500"
            ).text.strip()

            # expertise
            expertise = driver.find_element(
                By.XPATH, "//div[div[text()='Job Expertise:']]//a"
            ).text.strip()

            # location
            location = driver.find_element(By.CSS_SELECTOR,
                "div.d-inline-block.text-dark-grey span.small-text.text-rich-grey"
            ).text.strip()

            # experience
            experience = driver.find_element(By.CSS_SELECTOR,
                "section.job-experiences div.paragraph"
            ).text.strip()

            # domain
            elems = driver.find_elements(By.CSS_SELECTOR,"div.d-flex.flex-wrap.igap-2 div.itag")
            domains = [e.text.strip() for e in elems]

            # ngày đăng
            posted_text = "N/A"
            posted_formatted = "N/A"
            items = driver.find_elements(By.CSS_SELECTOR, "div.preview-header-item")
            for item in items:
                try:
                    svg_use = item.find_element(By.CSS_SELECTOR, "svg use")
                    href = svg_use.get_attribute("href")
                    if href and "#clock" in href:
                        posted_text = item.find_element(By.TAG_NAME, "span").text.strip()
                        _, posted_formatted = parse_posted_date(posted_text)
                        break
                except:
                    pass

            # ==========================
            # LƯU FILE
            # ==========================
            row = {
                "job_names": job_name,
                "company_names": company_name,
                "salaries": salary,
                "position_names": expertise,
                "kind_jobs": kind_job,
                "array_skills": skills,
                "locate_names": location,
                "exp_skills": experience,
                "domain_arr": domains,
                "post_dates_formatted": posted_formatted
            }

            save_row(row, csv_path)
            print("✔ Đã lưu:", job_name)

            return  # thành công → thoát hàm

        except Exception as e:
            log_error(f"Job retry {attempt+1}/3 error: {str(e)}")
            sleep(1)

    print("Bỏ qua job do lỗi 3 lần.")


# ==========================
# HÀM CRAWL CHÍNH
# ==========================
def crawling_def(driver, url):

    csv_path = r"D:\I. KhongPhanLoai\IT-job-analysis-VN\data_raw\ITViec_data.csv"
    crawled_jobs = get_crawled_jobs(csv_path)
    print("Đã crawl:", len(crawled_jobs), "job")

    driver.get(url)
    sleep(2)

    start_page = load_last_page()
    print("Tiếp tục từ trang:", start_page)

    i = 1
    while i <= 48:

        # bỏ qua các trang đã crawl
        if i < start_page:
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, 'div.page.next a')
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)
                sleep(2)  
                next_btn.click()
                sleep(2)
                i += 1
                continue
            except:
                break

        save_current_page(i)

        job_titles = driver.find_elements(By.CSS_SELECTOR,
            "div.job-card h3[data-search--job-selection-target='jobTitle']"
        )

        for title in job_titles:
            crawl_one_job(driver, title, crawled_jobs, csv_path)

        # next page
        try:
            for i in range(18):
                driver.execute_script("window.scrollBy(0, 500);")
                sleep(0.2)
            next_btn = driver.find_element(By.CSS_SELECTOR, 'div.page.next a')
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)
            next_btn.click()
            
            sleep(random.randint(1,3))
            i += 1
        except NoSuchElementException:
            print("Hết trang")
            break

    df = pd.read_csv(csv_path)
    return df


# ==========================
# MAIN
# ==========================

def main():
    url = "https://itviec.com/it-jobs?job_selected=cloud-database-reliability-engineer-oivan-2740"
    login_url = "https://itviec.com/sign_in"
    driver = dangNhap(login_url)
    input("Nhấn ENTER để bắt đầu crawl...")
    df = crawling_def(driver, url)
    return df

main()