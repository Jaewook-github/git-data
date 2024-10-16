import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

main_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
basic_url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo="


def GetLast():
    resp = requests.get(main_url)
    soup = BeautifulSoup(resp.text, "lxml")
    result = str(soup.find("meta", {"id": "desc", "name": "description"})['content'])  # meta
    s_idx = result.find(" ")
    e_idx = result.find("회")
    return int(result[s_idx + 1: e_idx])


def Crawler(s_count, e_count, fp):
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

        s_idx = text.find("1등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money1 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("2등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money2 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("3등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money3 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("4등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money4 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        s_idx = text.find("5등", e_idx) + 2
        e_idx = text.find("원", s_idx) + 1
        e_idx = text.find("원", e_idx)
        money5 = text[s_idx:e_idx].strip().replace(',', '').split()[2]

        line = str(i) + ',' + numbers[0] + ',' + numbers[1] + ',' + numbers[2] + ',' + numbers[3] + ',' + numbers[4] \
               + ',' + numbers[
                   5] + ',' + bonus + ',' + money1 + ',' + money2 + ',' + money3 + ',' + money4 + ',' + money5
        print(line)
        line += '\n'
        fp.write(line)


def get_last_saved_draw():
    if not os.path.exists('lotto.csv'):
        return 0
    df = pd.read_csv('lotto.csv', header=None)
    return df.iloc[-1, 0] if not df.empty else 0


last = GetLast()
last_saved = get_last_saved_draw()

if last_saved < last:
    mode = 'a' if last_saved > 0 else 'w'
    with open('lotto.csv', mode) as fp:
        if mode == 'w':
            # CSV 파일이 새로 생성되는 경우, 헤더를 추가합니다.
            header = "회차,번호1,번호2,번호3,번호4,번호5,번호6,보너스,1등당첨금,2등당첨금,3등당첨금,4등당첨금,5등당첨금\n"
            fp.write(header)

        print(f"크롤링 시작: {last_saved + 1}회차부터 {last}회차까지")
        Crawler(last_saved + 1, last, fp)
    print("크롤링 완료")
else:
    print("이미 최신 데이터가 저장되어 있습니다. 크롤링할 새로운 데이터가 없습니다.")