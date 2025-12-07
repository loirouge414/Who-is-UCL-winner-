import io
import requests
import pandas as pd

def load_clubelo_snapshot(date_str: str = '2025-09-01') -> pd.DataFrame:
    
    url = f"http://api.clubelo.com/{date_str}"
    resp = requests.get(url)
    resp.raise_for_status()
    # ClubElo는 CSV 텍스트로 반환
    df = pd.read_csv(io.StringIO(resp.text))
    # 컬럼 예: Club, Country, Elo, From, To ...
    return df

def load_ucl_teams(csv_path: str) -> pd.DataFrame:
    teams = pd.read_csv(csv_path)
    return teams

if __name__ == "__main__":
    elo_df = load_clubelo_snapshot("2025-09-01")
    ucl_df = load_ucl_teams("data/ucl_teams_2025_26.csv")

    merged = ucl_df.merge(
        elo_df,
        left_on="elo_club_name",
        right_on="Club",
        how="left"
    )

    pd.set_option("display.max_rows", None)
    print(merged)
