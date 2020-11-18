import requests
from bs4 import BeautifulSoup


def get_win():
    r = requests.get("https://www.dhlottery.co.kr/gameResult.do?method=byWin").text
    soup = BeautifulSoup(r, "html.parser")
    round_num = soup.find("h4").find("strong").text
    w_nums = []
    balls = soup.find(class_="num win").find_all(class_="ball_645")
    for i in balls:
        w_nums.append(int(i.text))
    bonus = int(soup.find(class_="num bonus").find(class_="ball_645").text)
    return round_num, w_nums, bonus
