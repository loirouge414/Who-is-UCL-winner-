import pandas as pd
import numpy as np

def compute_power_score(teams_df: pd.DataFrame) -> pd.DataFrame:
    """
    teams_df: 최소한 'team', 'elo' 컬럼을 포함한 DataFrame
              (이미 data_loader에서 ClubElo랑 merge된 상태라고 가정)

    반환: 'power' 컬럼이 추가된 DataFrame
    """
    df = teams_df.copy()

    # Elo가 없는 팀이 있으면 일단 제거하거나 적당히 대체
    df = df.dropna(subset=["elo"])

    # 0~1 구간으로 정규화
    elo_min = df["elo"].min()
    elo_max = df["elo"].max()
    df["power"] = (df["elo"] - elo_min) / (elo_max - elo_min)

    return df