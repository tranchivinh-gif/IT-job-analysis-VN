from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from time import sleep
from datetime import datetime, timedelta
import random

# hàm thực hiện mở trang web và đăng nhập
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
    driver.get(login_url) # login_url = "https://itviec.com/sign_in"
    return driver

# hàm thực hiện chuyển đổi về kiểu datetime
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

# hàm thực hiện crawl các thông tin: tên công việc, công ty, mức lương, kinh nghiệm yêu cầu, kỹ năng, vị trí, ngày đăng
def crawling(url_crawl, driver):
    locate_names = []
    exp_skills = []
    domain_arr = []
    post_dates_text = []
    post_dates_real = []
    post_dates_formatted = []
    job_names = []
    company_names = []
    salaries = []
    position_names = []
    kind_jobs = []
    array_skills = []
# vào trang cần crawl
    driver.get(url_crawl)
# lấy địa chỉ làm việc, yêu cầu kinh nghiệm và kĩ năng, lĩnh vực làm việc, thông tin ngày đăng
    while True:
    # lấy job name
        elems = driver.find_elements(By.CSS_SELECTOR, "h3.imt-3.text-break") 
        job_names.extend([elem.text for elem in elems] )
    # lấy tên công ty
        elems = driver.find_elements(By.CSS_SELECTOR, "span.ims-2.small-text.text-hover-underline") 
        company_names.extend([elem.text for elem in elems] )
    # lấy lương
        elems = driver.find_elements(By.CSS_SELECTOR, ".salary .ips-2.fw-500") 
        salaries.extend([elem.text for elem in elems])
    # lấy vị trí công việc
        elems = driver.find_elements(By.CSS_SELECTOR, "a.ips-2") 
        position_names.extend([elem.text for elem in elems]) 
    # lấy các kỹ năng, công cụ sử dụng cơ bản
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card")
        for job in job_cards:
            skill_elems = job.find_elements(By.CSS_SELECTOR, "div.imt-4.imb-3.d-flex.igap-1 a")
            skills = [s.text for s in skill_elems]
            array_skills.append(skills)
    # lấy loại hình làm việc: remote/office
        elems = driver.find_elements(By.CSS_SELECTOR, "div.text-rich-grey.flex-shrink-0") 
        kind_jobs.extend([elem.text for elem in elems] )
        job_titles = driver.find_elements(By.CSS_SELECTOR,"div.job-card h3[data-search--job-selection-target='jobTitle']")
        for title in job_titles:
            try: 
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", title)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", title)
                time.sleep(2)
                # lấy địa chỉ làm việc
                elems = driver.find_element(By.CSS_SELECTOR, "div.d-inline-block.text-dark-grey span.small-text.text-rich-grey") 
                locate_names.append(elems.text)
                # lấy yêu cầu kinh nghiệm và kĩ năng
                elems = driver.find_element(By.CSS_SELECTOR, "section.job-experiences div.paragraph") 
                exp_skills.append(elems.text) 
                # Lấy tất cả domain
                elems = driver.find_elements(By.CSS_SELECTOR,"div.d-flex.flex-wrap.igap-2 div.itag")
                # Lấy text từng domain
                domains = [e.text.strip() for e in elems]
                domain_arr.append(domains)
                # Lấy thông tin ngày đăng
                posted_text = driver.find_element(By.CSS_SELECTOR, "div.d-inline-block.text-dark-grey.preview-header-item span.small-text.text-rich-grey").text
                post_dates_text.append(posted_text)
                dt, formatted = parse_posted_date(posted_text)
                post_dates_real.append(dt)
                post_dates_formatted.append(formatted)
                print(locate_names,
                        exp_skills,
                        domain_arr,
                        post_dates_text,
                        post_dates_real,
                        post_dates_formatted,
                        job_names,
                        company_names,
                        salaries,
                        position_names,
                        kind_jobs,
                        array_skills)
            except NoSuchElementException:
                print("chua lay duoc thong tin")    
        try: 
            pages = driver.find_element(By.CSS_SELECTOR, "div.pagination-search-jobs.d-flex.justify-content-center.ipb-16")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pages)
            time.sleep(0.2)
            nexttrang = driver.find_element(By.CSS_SELECTOR, 'div.page.next a')
            nexttrang.click()
            sleep(random.randint(1,3))
        except NoSuchElementException:
            break  
    return {
        "job_names": job_names,
        "company_names": company_names,
        "salaries": salaries,
        "position_names": position_names,
        "array_skills": array_skills,
        "locate_names": locate_names,
        "exp_skills": exp_skills,
        "domain_arr": domain_arr,
        "post_dates_text": post_dates_text,
        "post_dates_real": post_dates_real,
        "post_dates_formatted": post_dates_formatted,
        "kind_jobs": kind_jobs
    }
    
login_url = "https://itviec.com/sign_in"
def main():
    driver = dangNhap(login_url)
    a = int(input("hay nhap 1 de tiep tuc: "))
    if a == 1:
        kq = crawling("https://itviec.com/it-jobs?job_selected=cloud-database-reliability-engineer-oivan-2740",driver)
        print(kq)
    else:
        print("ban chua dang nhap!")
        
main()