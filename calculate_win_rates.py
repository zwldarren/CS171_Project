import subprocess
import time
import threading
from collections import Counter


def run_game(wins):
    command = [
        "python",
        "main.py",
        "7",
        "7",
        "2",
        "l",
        "main.py",
        # "Sample_AIs/Random_AI/main.py",
        "Sample_AIs/Poor_AI/main.py",
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_text = result.stdout.decode("utf-8")
    if "player 1 wins" in stdout_text:
        wins["player 1"] += 1
    elif "player 2 wins" in stdout_text:
        wins["player 2"] += 1
    elif "Tie" in stdout_text:
        wins["ties"] += 1


def calculate_win_rates(rounds=100, num_threads=1):
    wins = Counter({"player 1": 0, "player 2": 0, "ties": 0})
    threads = []

    for _ in range(num_threads):
        thread = threading.Thread(target=run_game, args=(wins,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return "player 1: {:.2f}%\nplayer 2: {:.2f}%\nties: {:.2f}%".format(
        wins["player 1"] / rounds * 100,
        wins["player 2"] / rounds * 100,
        wins["ties"] / rounds * 100,
    )


if __name__ == "__main__":
    print("Calculating win rates...")
    start = time.time()
    # 修改num_threads可以调整多线程数量，推荐不要超过CPU核心数
    print(calculate_win_rates(rounds=100, num_threads=4))
    end = time.time()
    print(
        "Time elapsed: {}min {}s".format(
            int((end - start) / 60), int((end - start) % 60)
        )
    )

    # python main.py 7 7 2 l Sample_AIs/Random_AI/main.py main.py
    # python3 main.py 7 7 2 l Sample_AIs/Poor_AI/main.py main.py

    # 以下为测试时输入顺序
    # module load python/3.5.2
    # python3 calculate_win_rates.py
