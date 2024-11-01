import numpy as np
from itertools import combinations

# OD 시계열 데이터 예시: 각 OD 쌍의 시간대별 이동량 시계열이 담긴 딕셔너리
od_time_series = {
    'OD_1': np.array([10, 20, 30, 40, 50]),
    'OD_2': np.array([15, 25, 35, 45, 55]),
    # 추가 데이터...
}

# 피어슨 상관계수로 OD 쌍 간 유사도 계산
od_pairs = list(combinations(od_time_series.keys(), 2))
pearson_correlations = {}
for (od1, od2) in od_pairs:
    corr = np.corrcoef(od_time_series[od1], od_time_series[od2])[0, 1]
    pearson_correlations[(od1, od2)] = corr


import networkx as nx
from community import community_louvain

# 그래프 생성
G = nx.Graph()
for (od1, od2), corr in pearson_correlations.items():
    if corr > 0.6:  # 임계값 예시
        G.add_edge(od1, od2, weight=corr)

# 커뮤니티 탐지
partition = community_louvain.best_partition(G)

# 각 커뮤니티 확인
communities = {}
for node, comm_id in partition.items():
    if comm_id not in communities:
        communities[comm_id] = []
    communities[comm_id].append(node)
print("커뮤니티:", communities)
