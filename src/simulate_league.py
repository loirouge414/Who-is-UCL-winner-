import numpy as np
import pandas as pd

RNG = np.random.default_rng()

def simulate_league_table(teams_df: pd.DataFrame,
                          noise_std: float = 0.15) -> pd.DataFrame:
    """
    teams_df: 'team', 'power' 컬럼 포함
    noise_std: 시즌 운빨(변동성) 정도. 값이 클수록 이변이 많이 생김.

    반환: 'league_pos'와 'performance'가 추가된 DataFrame
    """
    df = teams_df.copy()

    # 각 팀의 시즌 퍼포먼스를 샘플링
    noise = RNG.normal(loc=0.0, scale=noise_std, size=len(df))
    df["performance"] = df["power"] + noise

    # performance 높은 순으로 정렬 → 순위 부여
    df = df.sort_values("performance", ascending=False).reset_index(drop=True)
    df["league_pos"] = np.arange(1, len(df) + 1)

    return df