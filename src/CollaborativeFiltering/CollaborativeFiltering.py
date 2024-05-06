import os
import json
import numpy as np
import random

def load_data(base_path):
    user_data = {}
    
    # 读取所有用户名命名的json文件
    for user_file in os.listdir(base_path):
        if user_file.endswith(".json") and not user_file.startswith("followers"):
            with open(os.path.join(base_path, user_file), 'r') as file:
                data = json.load(file)
                user_data[user_file[:-5]] = data  
    
    # 读取followers数据
    followers_path = os.path.join(base_path, 'followers')
    followers_data = {}
    if os.path.exists(followers_path):
        for follower_file in os.listdir(followers_path):
            if follower_file.endswith(".json"):
                with open(os.path.join(followers_path, follower_file), 'r') as file:
                    data = json.load(file)
                    followers_data[follower_file[:-5]] = data  

    return user_data, followers_data


def create_user_follow_matrix(user_data, followers_data):
    user_follow_matrix = {}
    all_followed = set()

    for user, data in user_data.items():
        
        follows = set(follower['name'] for follower in data.get('followers', []))
        
        valid_follows = {name for name in follows if name in followers_data}
        user_follow_matrix[user] = valid_follows
        all_followed.update(valid_follows)

    return user_follow_matrix, all_followed


def pearson_correlation(user1, user2, user_follow_matrix):
    # 皮尔逊相关系数计算
    follows1 = user_follow_matrix[user1]
    follows2 = user_follow_matrix[user2]
    all_items = set(follows1).union(set(follows2))

    # 确保至少有一个共同项
    if not all_items:
        #print(f"all_items is empty , {user1} {user2}")
        return 0

    # 计算两个用户的评分向量
    # 假设每个用户对他们关注的用户的“评分”为1，对不关注的为0
    ratings1 = np.array([1 if item in follows1 else 0 for item in all_items])
    ratings2 = np.array([1 if item in follows2 else 0 for item in all_items])


    if np.all(ratings1 == 0) or np.all(ratings2 == 0):
        return 0


    mean1 = ratings1.mean()
    mean2 = ratings2.mean()


    denominator = np.sqrt(np.sum((ratings1 - mean1) ** 2)) * np.sqrt(np.sum((ratings2 - mean2) ** 2))
    if denominator == 0:
        return 0

    numerator = np.sum((ratings1 - mean1) * (ratings2 - mean2))
    
    return numerator / denominator if denominator != 0 else 0


def recommend_tweets(user, user_follow_matrix, all_users, user_data, num_recommendations=5):
    # 计算相似度并保留相关系数
    similarities = {other: pearson_correlation(user, other, user_follow_matrix) for other in all_users if other != user}
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    recommendations = set()
    correlations = {}
    for similar_user, similarity in sorted_similarities:
        if len(recommendations) >= num_recommendations:
            break
        correlations[similar_user] = similarity
        if 'tweets' in user_data[similar_user]:
            for tweet in user_data[similar_user]['tweets']:
                if 'mblog' in tweet and 'user' in tweet['mblog'] and 'screen_name' in tweet['mblog']['user']:
                    screen_name = tweet['mblog']['user']['screen_name']
                    recommendations.add(screen_name)
    return list(recommendations)[:num_recommendations], correlations

def format_and_save_recommendations(user_recommendations, filename="recommendations.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        for user, data in user_recommendations.items():
            recommendations, correlations = data
            
            rec_with_scores = [(rec, correlations.get(rec, float('-inf'))) for rec in recommendations]
            
            rec_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            file.write(f"[!] target user: {user}\n")
            file.write("Preference ranking:\n")
            for idx, (rec, score) in enumerate(rec_with_scores, start=1):
                
                score_display = 'N/A' if score == float('-inf') else f"{score:.6f}"
                file.write(f"{idx}. {rec} : {score_display}\n")
            file.write("\n")







if __name__ == "__main__":
    base_path = "/Users/zhangyunhe/Files/homework/数据挖掘/BIT-DataMining/data"

    print("[!] load user data")
    user_data, followers_data = load_data(base_path)

    # 获取用户-关注矩阵和所有用户列表
    user_follow_matrix, all_followed = create_user_follow_matrix(user_data, followers_data)
    all_users = list(user_follow_matrix.keys())

    # for user, data in user_data.items():
    #     print(f"{user} ")

    # # 打印完整的用户关注矩阵
    # print("Complete User-Follow Matrix:")
    # for user, follows in user_follow_matrix.items():
    #     print(f"{user}: {list(follows)}\n")

    print("[!] test")
    tweet_recommendations = {}
    for user in all_users:
        recommendations, correlations = recommend_tweets(user, user_follow_matrix, all_users, user_data, num_recommendations=10)
        tweet_recommendations[user] = (recommendations, correlations)

    format_and_save_recommendations(tweet_recommendations)
    
    