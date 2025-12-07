import numpy as np
import pandas as pd

RNG = np.random.default_rng()


def win_prob(power_a: float, power_b: float, k: float = 5.0) -> float:
    """
    두 팀 power 차이로 A가 이길 확률을 추정하는 함수.
    k가 클수록 rating 차이를 더 민감하게 반영.
    """
    diff = power_a - power_b
    return 1.0 / (1.0 + np.exp(-k * diff))


def simulate_single_match(row_a: pd.Series, row_b: pd.Series) -> pd.Series:
    """
    단판 승부 한 경기 시뮬레이션.
    row_a / row_b: team, power 등을 가진 한 행(Series)
    return: 승리한 팀의 row (Series)
    """
    p_a = win_prob(row_a["power"], row_b["power"])
    if RNG.random() < p_a:
        return row_a
    else:
        return row_b


def simulate_playoff_round(league_table: pd.DataFrame):
    """
    리그 페이즈 결과(league_pos 포함)를 받아서
    9~24위 플레이오프를 시뮬레이션.

    매칭 규칙:
      9 vs 24, 10 vs 23, ..., 16 vs 17

    return:
      winners_df: 플레이오프 승자 8팀 DataFrame
      matches_df: 각 경기 결과 로그 DataFrame
    """
    df = league_table.set_index("league_pos")

    pairings = [
        (9, 24),
        (10, 23),
        (11, 22),
        (12, 21),
        (13, 20),
        (14, 19),
        (15, 18),
        (16, 17),
    ]

    winners = []
    records = []

    for a_pos, b_pos in pairings:
        team_a = df.loc[a_pos]
        team_b = df.loc[b_pos]

        winner = simulate_single_match(team_a, team_b)
        winners.append(winner)

        records.append(
            {
                "round": "Playoff",
                "pos_a": a_pos,
                "team_a": team_a["team"],
                "power_a": team_a["power"],
                "pos_b": b_pos,
                "team_b": team_b["team"],
                "power_b": team_b["power"],
                "winner": winner["team"],
            }
        )

    winners_df = pd.DataFrame(winners).reset_index(drop=True)
    matches_df = pd.DataFrame(records)

    return winners_df, matches_df


def simulate_round(teams_df: pd.DataFrame, round_name: str):
    """
    8강, 4강, 결승처럼 '그냥 남은 팀들끼리' 싸우는 라운드.

    teams_df: 참가 팀들 (행 개수는 짝수여야 함)
    round_name: "R16", "QF", "SF", "Final" 등

    return:
      winners_df: 다음 라운드로 진출하는 팀들
      matches_df: 경기 결과 로그
    """
    df = teams_df.copy().reset_index(drop=True)
    # 매 라운드마다 랜덤 매칭
    RNG.shuffle(df.values)

    winners = []
    records = []

    for i in range(0, len(df), 2):
        team_a = df.iloc[i]
        team_b = df.iloc[i + 1]

        winner = simulate_single_match(team_a, team_b)
        winners.append(winner)

        records.append(
            {
                "round": round_name,
                "team_a": team_a["team"],
                "power_a": team_a["power"],
                "team_b": team_b["team"],
                "power_b": team_b["power"],
                "winner": winner["team"],
            }
        )

    winners_df = pd.DataFrame(winners).reset_index(drop=True)
    matches_df = pd.DataFrame(records)

    return winners_df, matches_df


def simulate_r16(league_table: pd.DataFrame, playoff_winners: pd.DataFrame):
    """
    16강:
      - league_pos 1~8 직행 팀
      - 플레이오프 승자 8팀

    규칙:
      1~8위 팀과 플레이오프 승자 8팀이 각각 한 팀씩 만나도록 매칭.
      (플옵승자 순서는 랜덤)
    """
    direct_r16 = league_table[league_table["league_pos"] <= 8].copy()
    direct_r16 = direct_r16.sort_values("league_pos").reset_index(drop=True)

    pw = playoff_winners.copy().reset_index(drop=True)
    RNG.shuffle(pw.values)  # 플레이오프 승자 순서 랜덤

    winners = []
    records = []

    for i in range(len(direct_r16)):
        team_a = direct_r16.iloc[i]  # 리그 상위 팀
        team_b = pw.iloc[i]          # 플레이오프 승자 팀

        winner = simulate_single_match(team_a, team_b)
        winners.append(winner)

        records.append(
            {
                "round": "R16",
                "team_a": team_a["team"],
                "power_a": team_a["power"],
                "team_b": team_b["team"],
                "power_b": team_b["power"],
                "winner": winner["team"],
            }
        )

    winners_df = pd.DataFrame(winners).reset_index(drop=True)
    matches_df = pd.DataFrame(records)

    return winners_df, matches_df


def simulate_ucl_knockout(league_table: pd.DataFrame):
    """
    전체 토너먼트 시뮬레이션:
      1) 플레이오프 (9~24위)
      2) 16강 (직행 8팀 + 플옵 8팀)
      3) 8강
      4) 4강
      5) 결승

    return:
      results: dict 형태로 각 라운드별 결과 DataFrame 모음
    """
    results = {}

    # 1) 플레이오프
    playoff_winners, playoff_matches = simulate_playoff_round(league_table)
    results["playoff_winners"] = playoff_winners
    results["playoff_matches"] = playoff_matches

    # 2) 16강
    r16_winners, r16_matches = simulate_r16(league_table, playoff_winners)
    results["r16_winners"] = r16_winners
    results["r16_matches"] = r16_matches

    # 3) 8강
    qf_winners, qf_matches = simulate_round(r16_winners, "QF")
    results["qf_winners"] = qf_winners
    results["qf_matches"] = qf_matches

    # 4) 4강
    sf_winners, sf_matches = simulate_round(qf_winners, "SF")
    results["sf_winners"] = sf_winners
    results["sf_matches"] = sf_matches

    # 5) 결승
    final_winner_df, final_matches = simulate_round(sf_winners, "Final")
    results["final_winner"] = final_winner_df
    results["final_matches"] = final_matches

    return results
