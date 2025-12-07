# Who-is-UCL-winner-
해외 축구 중, 유럽 리그의 가장 높은 리그인 UEFA CHAMPIONS LEAGUE를 예측하는 시스템입니다.

<데이터 구조>

data/
    ucl_teams_2025_26.csv
src/
    data_loader.py          // 데이터 불러오는 코드
    features.py             // 특징 만드는 코드
    model.py                // 학습, 예측 코드
    simulate_league.py      // 리그페이즈 순위 시뮬레이션
    simulate_knockout.py    // 녹아웃 스테이지(리그페이즈 후, 플레이오프, 16강, 8강, 4강, 결승 등등 해당) 시뮬레이션
readme.md
requirements.txt
gitignore
