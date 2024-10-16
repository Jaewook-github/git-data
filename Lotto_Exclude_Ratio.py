# lotto 생성기 제외수를 제외한 랜덤

# 제외수를 생성하는 함수
def get_excluded_numbers():
    import sqlite3
    from collections import Counter

    def get_excluded_numbers_based_on_last_digit(bonus):
        """보너스 번호의 끝수를 기반으로 제외수 리스트를 반환합니다."""
        if bonus < 10 or bonus % 10 == 0:
            return []
        last_digit = bonus % 10
        return [i for i in range(1, 46) if i % 10 == last_digit]

    # 데이타베이스 연결
    conn = sqlite3.connect('lotto.db')
    cursor = conn.cursor()

    # 마지막 회차 추출
    cursor.execute("SELECT * FROM lotto_results ORDER BY draw_number DESC LIMIT 1")
    latest_draw = cursor.fetchone()

    # 직전 회차 보너스 번로 끝수 추출
    bonus = latest_draw[7]
    excluded_from_last_digit = get_excluded_numbers_based_on_last_digit(bonus)
    print(f"직전 회차 끝수: {excluded_from_last_digit}")

    # 4회 이내 2번 이상 추출
    cursor.execute("SELECT * FROM lotto_results ORDER BY draw_number DESC LIMIT 4")
    recent_4_draws = cursor.fetchall()
    numbers_4_draws = [num for draw in recent_4_draws for num in draw[1:7]]
    count_4_draws = Counter(numbers_4_draws)
    excluded_from_4_draws = [num for num, count in count_4_draws.items() if count >= 2]
    print(f"4회 이내 2번 이상: {', '.join(map(str, excluded_from_4_draws))}")

    # 10회 이내 4번 이상 추출
    cursor.execute("SELECT * FROM lotto_results ORDER BY draw_number DESC LIMIT 10")
    recent_10_draws = cursor.fetchall()
    numbers_10_draws = [num for draw in recent_10_draws for num in draw[1:7]]
    count_10_draws = Counter(numbers_10_draws)
    excluded_from_10_draws = [num for num, count in count_10_draws.items() if count >= 4]
    print(f"10회 이내 4번 이상: {', '.join(map(str, excluded_from_10_draws))}")

    # 데이터 베이스 연결 종료
    conn.close()

    # Combine the excluded numbers
    excluded_numbers = set(excluded_from_last_digit + excluded_from_4_draws + excluded_from_10_draws)

    return excluded_numbers


def generate_lotto(excluded_numbers=set()):
    """제외된 번호를 고려하여 로또 번호를 생성합니다."""
    import random
    # 로또 번호 리스트 초기화
    my_number = []

    # 6개의 고유한 로또 번호를 생성합니다.
    while len(my_number) < 6:
        number = random.randint(1, 45)
        if number not in excluded_numbers and number not in my_number:
            my_number.append(number)

    my_number.sort()  # 번호 정렬
    return my_number


def main():
    excluded_numbers = get_excluded_numbers()
    print(f"제외된 번호: {sorted(excluded_numbers)}")

    for i in range(5):  # 5게임의 로또 번호 생성
        numbers = generate_lotto(excluded_numbers)
        print(f'게임 {i + 1}: {numbers}')


if __name__ == "__main__":
    main()