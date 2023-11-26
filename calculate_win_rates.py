import subprocess

# pip install tqdm
# from tqdm import tqdm

import time


def run_game():
    command = [
        "python",
        "main.py",
        "7",
        "7",
        "2",
        "l",
        "main.py",
        "Sample_AIs/Random_AI/main.py",
        # "Sample_AIs/Poor_AI/main.py",
    ]

    # python 3.5.2不支持
    """
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout
    """
    result = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout_text = result.stdout.decode('utf-8')
    return stdout_text


def calculate_win_rates(rounds = 100):
    wins = {"player 1": 0, "player 2": 0, "ties": 0}

    # module load python/3.5.2后无法使用，推测是tqdm并没有被下载到python 3.5.2中
    """
    for i in tqdm(range(rounds), desc="Running games"):
        output = run_game()
        if "player 1 wins" in output:
            wins["player 1"] += 1
        elif "player 2 wins" in output:
            wins["player 2"] += 1
        elif "Tie" in output:
            wins["ties"] += 1
    """

    for i in range(rounds):
        output = run_game()
        if "player 1 wins" in output:
            wins["player 1"] += 1
        elif "player 2 wins" in output:
            wins["player 2"] += 1
        elif "Tie" in output:
            wins["ties"] += 1

        # 手动显示进度
        progress = (i + 1) / rounds * 100
        print("Progress: %.2f%%" % progress)

    # 不适用于python3.5.2
    """
    win_rates = {
        "player 1": f"{wins['player 1'] / rounds * 100:.2f}%",
        "player 2": f"{wins['player 2'] / rounds * 100:.2f}%",
        "ties": f"{wins['ties'] / rounds * 100:.2f}%",
    }
    """

    win_rates = {
        "player 1": "{:.2f}%".format(wins['player 1'] / rounds * 100),
        "player 2": "{:.2f}%".format(wins['player 2'] / rounds * 100),
        "ties": "{:.2f}%".format(wins['ties'] / rounds * 100),
    }

    # 不适用于python3.5.2
    """
    return f"player 1: {win_rates['player 1']}\nplayer 2: {win_rates['player 2']}\nties: {win_rates['ties']}"
    """
    return "player 1: {:.2f}%\nplayer 2: {:.2f}%\nties: {:.2f}%".format(
        wins['player 1'] / rounds * 100,
        wins['player 2'] / rounds * 100,
        wins['ties'] / rounds * 100
    )


if __name__ == "__main__":
    print("test 1\n")
    print(calculate_win_rates(10))
    # print("test 2\n")
    # print(calculate_win_rates(10))
    # print("test 3\n")
    # print(calculate_win_rates(10))
    # print("\n")
    print("\n")
    # python main.py 7 7 2 l Sample_AIs/Random_AI/main.py main.py
    # python3 main.py 7 7 2 l Sample_AIs/Poor_AI/main.py main.py

    # 以下为测试时输入顺序
    # module load python/3.5.2
    # python3 calculate_win_rates.py

# 旧版
"""
import subprocess

# pip install tqdm
from tqdm import tqdm


def run_game():
    command = [
        "python",
        "main.py",
        "7",
        "7",
        "2",
        "l",
        "main.py",
        "Sample_AIs/Random_AI/main.py",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout


def calculate_win_rates(rounds=100):
    wins = {"player 1": 0, "player 2": 0, "ties": 0}

    for i in tqdm(range(rounds), desc="Running games"):
        output = run_game()
        if "player 1 wins" in output:
            wins["player 1"] += 1
        elif "player 2 wins" in output:
            wins["player 2"] += 1
        elif "Tie" in output:
            wins["ties"] += 1

    win_rates = {
        "player 1": f"{wins['player 1'] / rounds * 100:.2f}%",
        "player 2": f"{wins['player 2'] / rounds * 100:.2f}%",
        "ties": f"{wins['ties'] / rounds * 100:.2f}%",
    }
    return f"player 1: {win_rates['player 1']}\nplayer 2: {win_rates['player 2']}\nties: {win_rates['ties']}"


if __name__ == "__main__":
    print(calculate_win_rates(10))
"""