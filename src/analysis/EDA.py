import ast
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

# đọc dữ liệu
df = pd.read_csv(r"D:\I. KhongPhanLoai\IT-job-analysis-VN\data_clean\clean_data.csv")


# ==================================================
# 1. JOB GROUP ĐANG TUYỂN NHIỀU NHẤT
# ==================================================
def most_job_groups(df):
    value_counts = df['job_group'].value_counts()

    plt.figure(figsize=(20, 10))
    ax = value_counts.plot(kind='barh', color='skyblue')

    plt.xlabel("Count")
    plt.ylabel("Job group")
    plt.title("Job groups with the most job postings")

    # thêm số lượng vào cuối thanh bar
    for i, v in enumerate(value_counts):
        ax.text(v + 1, i, str(v), va='center')

    plt.tight_layout()
    plt.show()

# ==================================================
# 2. JOB GROUP — GROUP BY LEVEL
# ==================================================
def job_group_grouped_by_level(df):
    df_filtered = df[df['level'] != "Unknown"]

    grouped = df_filtered.groupby(['job_group', 'level']).size().unstack(fill_value=0)

    ax = grouped.plot(kind='bar', figsize=(20, 10))
    plt.xlabel("Job group")
    plt.ylabel("Count")
    plt.title("Job group grouped by level (excluding Unknown)")
    plt.xticks(rotation=45)

    # thêm số lên từng bar
    for c in ax.containers:
        ax.bar_label(c, label_type='edge')

    plt.tight_layout()
    plt.show()

# ==================================================
# 3. PHÂN TÍCH PROGRAMMING LANGUAGE / FRAMEWORK / TOOLS
# ==================================================
def extract_list_safe(x):
    try:
        return ast.literal_eval(x)
    except:
        return []


def plot_top_pie(counter, title):
    top_10 = counter.most_common(10)
    if not top_10:
        print(f"[WARNING] Không có dữ liệu cho biểu đồ: {title}")
        return

    labels = [f"{item[0]} ({item[1]})" for item in top_10]   # thêm số lượng vào label
    sizes = [item[1] for item in top_10]

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%")
    plt.title(title)
    plt.show()


def analyze_skills_by_job(df, job_group_name):
    df_job = df[df['job_group'] == job_group_name]

    # 1. Languages
    counter_lang = Counter()
    for row in df_job['programming_languages']:
        counter_lang.update(extract_list_safe(row))

    plot_top_pie(counter_lang, f"Top 10 Programming Languages — {job_group_name}")

    # 2. Frameworks
    counter_fw = Counter()
    for row in df_job['frameworks']:
        counter_fw.update(extract_list_safe(row))

    plot_top_pie(counter_fw, f"Top 10 Frameworks — {job_group_name}")

    # 3. Tools
    counter_tools = Counter()
    for row in df_job['tools']:
        counter_tools.update(extract_list_safe(row))
        
    # 4. Lib
    counter_lib = Counter()
    for row in df_job['libraries']:
        counter_lib.update(extract_list_safe(row))

    plot_top_pie(counter_lib, f"Top 10 library — {job_group_name}")


# ==================================================
# 4. LƯƠNG THEO LEVEL
# ==================================================
def clean_salary_column(df):
    df = df.copy()

    df['salary_clean'] = (
        df['salary']
        .str.replace('Up to \$', '', regex=True)
        .str.replace(',', '', regex=True)
        .replace('Unknown', np.nan)
        .astype(float)
    )
    return df

def average_salary_by_level(df, job_group_name):
    df_job = df[df['job_group'] == job_group_name].copy()
    df_job = clean_salary_column(df_job)
    df_job = df_job[df_job['level'] != 'Unknown']

    salary_by_level = (
        df_job.dropna(subset=['salary_clean'])
        .groupby('level')['salary_clean']
        .mean()
        .sort_values(ascending=False)
    )

    if salary_by_level.empty:
        print(f"[WARNING] Không có dữ liệu lương cho: {job_group_name}")
        return

    ax = salary_by_level.plot(kind='bar', color="orange", figsize=(12, 6))
    plt.xlabel("Level")
    plt.ylabel("Average Salary ($)")
    plt.title(f"Average Salary by Level — {job_group_name}")
    plt.xticks(rotation=45)

    # thêm số lên từng bar
    for c in ax.containers:
        ax.bar_label(c, fmt="%.0f")

    plt.tight_layout()
    plt.show()


# ============================
# MENU CHỌN CHỨC NĂNG
# ============================

def menu():
    while True:
        print("\n================= MENU =================")
        print("1. Xem số lượng job_group đang tuyển (most_job_groups)")
        print("2. Xem biểu đồ job_group grouped by level")
        print("3. Xem phân tích kỹ năng của 1 job_group (analyze_skills_by_job)")
        print("4. Xem biểu đồ lương trung bình theo level (average_salary_by_level)")
        print("0. Thoát")
        print("========================================")

        choice = input("Nhập lựa chọn (0-4): ")

        # -----------------------------
        if choice == "1":
            most_job_groups(df)

        elif choice == "2":
            job_group_grouped_by_level(df)

        elif choice == "3":
            print("\nDanh sách job_group có trong dữ liệu:")
            print(df['job_group'].unique())

            job = input("Nhập đúng tên job_group cần phân tích: ")
            if job in df['job_group'].unique():
                analyze_skills_by_job(df, job)
            else:
                print("[ERROR] Job group không tồn tại!")

        elif choice == "4":
            print("\nDanh sách job_group có trong dữ liệu:")
            print(df['job_group'].unique())

            job = input("Nhập đúng tên job_group để xem lương: ")
            if job in df['job_group'].unique():
                average_salary_by_level(df, job)
            else:
                print("[ERROR] Job group không tồn tại!")

        elif choice == "0":
            print("Thoát chương trình.")
            break

        else:
            print("Lựa chọn không hợp lệ! Vui lòng nhập từ 0-4.")

# ============================
# CHẠY MENU
# ============================
menu()
