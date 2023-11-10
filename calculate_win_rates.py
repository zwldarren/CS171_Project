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
