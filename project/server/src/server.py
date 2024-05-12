import os
import re
import json
from flask import Flask, request, jsonify
import random
from flask_cors import CORS
from ContentBased.content_based_matching import get_user_preference_embedding,cosine_similarity_matching
import torch

def load_user_info(user_dir: os.PathLike):
    user_files = {}
    for entry in os.listdir(user_dir):
        abs_path = os.path.join(user_dir, entry)
        if os.path.isfile(abs_path) and abs_path.endswith('.json'):
            user_name = entry.split('.')[0]
            user_files[user_name] = abs_path
    
    user_info = {}
    for user_name, user_file in user_files.items():
        with open(user_file, 'r+', encoding='utf-8') as f:
            info = json.load(f)
            user_info[user_name] = info
    
    return user_info


def load_user_feature_text(user_dir: os.PathLike):
    user_info = load_user_info(user_dir)
    
    feature_dict = {}
    invalid_counter = 0
    total_counter = 0
    for user, info in user_info.items():
        feature_dict[user] = []
        total_counter += len(info['tweets'])
        for item in info['tweets']:
            if item is None:
                continue
            try:
                data = item['mblog']['page_info']
                if data['title'] is None:
                    data['title'] = ''
                if data['content2'] is None:
                    data['content2'] = ''
                profile_text = data['title'] + data['content2']
            except KeyError:
                try:
                    data = item['mblog']['text']
                    profile_text = re.sub('\<.*?\>', '', data)
                except KeyError:
                    invalid_counter += 1
                    profile_text = ''

            # Build user feature text
            feature_dict[user].append(profile_text)

    print(f"[!] Invalid records in {user_dir}: {invalid_counter} / {total_counter}")
    return feature_dict

app = Flask(__name__)
CORS(app)

sims = {"users": [], "sims": []}

# 路由：接收前端发送的被点赞用户信息，并将其添加到 JSON 文件中
@app.route('/api/save_liked_users', methods=['POST'])
def save_liked_users():
    data = request.get_json()
    liked_users = data.get('followers', [])

    # 读取 JSON 文件
    filename = 'liked_users.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:  # 修改这里的编码为 UTF-8
            liked_data = json.load(file)
    else:
        liked_data = {"profile": {"screen_name": "test"}, "followers": []}

    # 将新的被点赞用户信息添加到 followers 列表中
    for user in liked_users:
        liked_data['followers'].append(user)

    # 将更新后的数据写入 JSON 文件
    with open(filename, 'w', encoding='utf-8') as file:  # 修改这里的编码为 UTF-8
        json.dump(liked_data, file, ensure_ascii=False)

    return jsonify({'message': 'Liked users saved successfully'})


@app.route('/api/recommend_users', methods=['GET'])
def recommend_users():
    feature_dict = load_user_feature_text("data/followers")

    user_file = 'liked_users.json'
    vectorized_follower_dir = 'src/embeds/vectorized'
    num_recommend = 10
    topn = 10
    
    # 读取用户信息
    with open(user_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
        followers = [follower['name'] for follower in info['followers']]
        
    # 获取用户偏好推荐
    pref_embed = get_user_preference_embedding(followers, vectorized_follower_dir)
    sims = cosine_similarity_matching(pref_embed, vectorized_follower_dir)

    # 构建推荐列表，一半偏好推送，一半随机推送
    recommend_posts = []
    
    #偏好推送
    recommend_users = []
    rank = torch.argsort(torch.tensor(sims['sims']), descending=True).numpy().tolist()
    counter = 0

    for i, index in enumerate(rank):
        recommend_users.append(sims['users'][index])
        counter += 1
        if counter >= topn:
            break
    recommend_users = random.sample(recommend_users,min(len(recommend_users),num_recommend//2))

    for user in recommend_users:
        posts = feature_dict[user]
        if not posts:
            continue
        one_post = random.choice(posts)
        recommend_posts.append({"user":user,"post":one_post})

    # 随机推送
    random_recommend_num = num_recommend - num_recommend//2
    users = list(feature_dict.keys())
    random_users = random.sample(users, min(len(users), random_recommend_num))
    for user in random_users:
        posts = feature_dict[user]
        if not posts:
            continue
        random_post = random.choice(posts)
        recommend_posts.append({"user": user, "post": random_post})
    
    return jsonify(recommend_posts)

# 路由：获取点赞用户数据
@app.route('/api/liked_users', methods=['GET'])
def get_liked_users():
    try:
        # 读取点赞用户数据
        with open('liked_users.json', 'r', encoding='utf-8') as file:
            liked_users_data = json.load(file)
            return jsonify(liked_users_data)
    except FileNotFoundError:
        # 如果文件不存在，返回空列表
        return jsonify({'followers': []})
    
# 路由：获取推荐用户的分数
@app.route('/api/similarity_scores', methods=['GET'])
def get_recommend_user_score():
    try:
        recommend_users_list=[]
        # 获取用户偏好推荐
        user_file = 'liked_users.json'
        vectorized_follower_dir = 'src/embeds/vectorized'

        # 读取用户信息
        with open(user_file, 'r', encoding='utf-8') as f:
            info = json.load(f)
            followers = [follower['name'] for follower in info['followers']]

        pref_embed = get_user_preference_embedding(followers, vectorized_follower_dir)
        sims = cosine_similarity_matching(pref_embed, vectorized_follower_dir)
        rank = torch.argsort(torch.tensor(sims['sims']), descending=True).numpy().tolist()
        counter = 0
        print(sims)
        for i, index in enumerate(rank):
            recommend_users_list.append({"user": sims['users'][index],"sims":round(sims['sims'][index], 4)})
            counter += 1
            if counter >= 10:
                break
        return jsonify(recommend_users_list)
    except len(sims)==0:
        return jsonify({"user":[],"sims":[]})

if __name__ == '__main__':
    app.run(debug=True)
