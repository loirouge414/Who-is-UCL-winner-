import pandas as pd

from data_loader import load_clubelo_snapshot, load_ucl_teams   # 네가 이미 만든 모듈
from ratings import compute_power_score
from simulate_league import simulate_league_table
from simulate_knockout import simulate_ucl_knockout


def build_ucl_teams_with_elo(date_str: str, teams_csv: str) -> pd.DataFrame:
    """
    1) ClubElo에서 date_str 기준 Elo 스냅샷 불러오고
    2) UCL 36팀 CSV와 merge해서
    3) team, country, elo, power 등이 들어간 DataFrame을 반환
    """
    # 1. ClubElo 전체 데이터
    elo_df = load_clubelo_snapshot(date_str)

    # 2. UCL 36팀 목록
    ucl_df = load_ucl_teams(teams_csv)  # 컬럼: team, elo_club_name, country

    # 3. merge (네 CSV에 elo_club_name이 있다고 가정)
    merged = ucl_df.merge(
        elo_df,
        left_on="elo_club_name",   # 네가 CSV에 만든 ClubElo 기준 이름
        right_on="Club",           # ClubElo CSV의 팀 이름 컬럼
        how="left"
    )

    # Club, Country 등 원본 컬럼 이름이 섞여 있을 수 있으니 정리
    merged = merged.rename(columns={"Elo": "elo"})

    return merged


def main():
    # 1. 36팀 + Elo + power 준비
    teams = build_ucl_teams_with_elo(
        date_str="2025-09-01",                # 시즌 시작 즈음 날짜로 나중에 조정
        teams_csv="../data/ucl_teams_2025_26.csv"
    )

    teams = compute_power_score(teams)

    # 2. 리그 페이즈 한 번 시뮬레이션
    league_table = simulate_league_table(teams, noise_std=0.15)

    # 보기 좋게 출력
    pd.set_option("display.max_rows", None)
    print("=== 리그 페이즈 최종 순위 (1~36위) ===")
    print(league_table[["league_pos", "team", "country", "elo", "power", "performance"]])

    # 3. 16강 직행 / 플레이오프 / 탈락 팀 나눠 보기
    direct_r16 = league_table[league_table["league_pos"] <= 8]
    playoff = league_table[(league_table["league_pos"] >= 9) & (league_table["league_pos"] <= 24)]
    eliminated = league_table[league_table["league_pos"] >= 25]

    print("\n=== 16강 직행 (1~8위) ===")
    print(direct_r16[["league_pos", "team", "power"]])

    print("\n=== 플레이오프 진출 (9~24위) ===")
    print(playoff[["league_pos", "team", "power"]])

    print("\n=== 리그 페이즈 탈락 (25~36위) ===")
    print(eliminated[["league_pos", "team", "power"]])

    # 4) 토너먼트(플레이오프~결승) 시뮬레이션
    results = simulate_ucl_knockout(league_table)

    print("\n=== [플레이오프 경기 결과] ===")
    print(results["playoff_matches"][["team_a", "team_b", "winner"]])

    print("\n=== [16강 경기 결과] ===")
    print(results["r16_matches"][["team_a", "team_b", "winner"]])

    print("\n=== [8강 경기 결과] ===")
    print(results["qf_matches"][["team_a", "team_b", "winner"]])

    print("\n=== [4강 경기 결과] ===")
    print(results["sf_matches"][["team_a", "team_b", "winner"]])

    print("\n=== [결승 경기 결과] ===")
    print(results["final_matches"][["team_a", "team_b", "winner"]])

    print("\n=== 🏆 우승팀 예측 ===")
    champion = results["final_winner"].iloc[0]["team"]
    print(f"Predicted Champion: {champion}")


if __name__ == "__main__":
    main()