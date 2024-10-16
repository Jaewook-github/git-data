import sqlite3
import requests
from bs4 import BeautifulSoup

main_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
basic_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo="


def GetLast():
    resp = requests.get(main_url)
    soup = BeautifulSoup(resp.text, "lxml")
    result = str(soup.find("meta", {"id": "desc", "name": "description"})['content'])
    s_idx = result.find(" ")
    e_idx = result.find("회")
    return int(result[s_idx + 1: e_idx])


def create_lotto_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotto_results (
            draw_number INTEGER PRIMARY KEY,
            num1 INTEGER,
            num2 INTEGER,
            num3 INTEGER,
            num4 INTEGER,
            num5 INTEGER,
            num6 INTEGER,
            bonus INTEGER,
            money1 INTEGER,
            money2 INTEGER,
            money3 INTEGER,
            money4 INTEGER,
            money5 INTEGER
        )
    ''')
    conn.commit()


def insert_into_db(data):
    cursor.execute('''
        INSERT OR IGNORE INTO lotto_results (
            draw_number, num1, num2, num3, num4, num5, num6, bonus, 
            money1, money2, money3, money4, money5) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
    conn.commit()


def Crawler(s_count, e_count):
    for i in range(s_count, e_count + 1):
        crawler_url = basic_url + str(i)
        resp = requests.get(crawler_url)
        soup = BeautifulSoup(resp.text, "html.parser")

        text = soup.text

        s_idx = text.find(" 당첨결과")
        s_idx = text.find("당첨번호", s_idx) + 4
        e_idx = text.find("보너스", s_idx)
        numbers = text[s_idx:e_idx].strip().split()

        s_idx = e_idx + 3
        e_idx = s_idx + 3
        bonus = text[s_idx:e_idx].strip()

        # Parsing the money fields can be simplified using a loop
        money = []
        for j in range(1, 6):
            s_idx = text.find(f"{j}등", e_idx) + 2
            e_idx = text.find("원", s_idx) + 1
            e_idx = text.find("원", e_idx)
            money.append(int(text[s_idx:e_idx].strip().replace(',', '').split()[2]))

        # construct data tuple and insert into the DB
        data = (i,) + tuple(int(num) for num in numbers) + (int(bonus),) + tuple(money)
        insert_into_db(data)

        print(f"Data for draw {i} inserted into the DB.")


# Database setup
conn = sqlite3.connect('lotto.db')
cursor = conn.cursor()

# Create table
create_lotto_table()

# Get the last and start crawling
last = GetLast()
Crawler(1, last)

# Always remember to close the database connection
conn.close()
