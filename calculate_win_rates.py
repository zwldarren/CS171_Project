import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

def run_game(log_filename="log.txt"):
    try:
        command = [
            "python",
            "main.py",
            "7",
            "7",
            "2",
            "l",
            "main.py",
            "Sample_AIs/Average_AI/main.py",
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_text = result.stdout.decode("utf-8")

        # Write the result to the log file

        if "player 1 wins" in stdout_text:
            with open(log_filename, "a") as log_file:
                log_file.write("player 1 wins\n")
            return "player 1"
        elif "player 2 wins" in stdout_text:
            with open(log_filename, "a") as log_file:
                log_file.write("player 2 wins\n")
            return "player 2"
        elif "Tie" in stdout_text:
            with open(log_filename, "a") as log_file:
                log_file.write("ties\n")
            return "ties"
        else:
            raise Exception("Error: no result found")
    except Exception as e:
        stdout_text = result.stdout.decode("utf-8")
        with open(log_filename, "a") as log_file:
            log_file.write(stdout_text + "\n" + str(e) + "\n")
        return "error"


def calculate_win_rates(rounds=100, workers=4):
    wins = Counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_game = {executor.submit(run_game): i for i in range(rounds)}
        for future in as_completed(future_to_game):
            result = future.result()
            wins[result] += 1

    return "player 1: {:.2f}%\nplayer 2: {:.2f}%\nties: {:.2f}%".format(
        wins["player 1"] / rounds * 100,
        wins["player 2"] / rounds * 100,
        wins["ties"] / rounds * 100,
        wins["error"] / rounds * 100,
    )


if __name__ == "__main__":
    print("Calculating win rates...")
    start = time.time()
    # 修改workers可以调整多线程数量，推荐不要超过CPU核心数
    print(calculate_win_rates(rounds=100, workers=12))
    end = time.time()
    print(
        "Time elapsed: {}min {}s".format(
            int((end - start) / 60), int((end - start) % 60)
        )
    )

    # python main.py 7 7 2 l Sample_AIs/Random_AI/main.py main.py
    # python3 main.py 7 7 2 l Sample_AIs/Poor_AI/main.py main.py
    # python3 main.py 7 7 2 l Sample_AIs/Average_AI/main.py main.py

    # 以下为测试时输入顺序
    # module load python/3.5.2
    # python3 calculate_win_rates.py
