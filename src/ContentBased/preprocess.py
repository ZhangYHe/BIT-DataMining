import os
import re
import json


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
        feature_dict[user] = ''
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
            feature_dict[user] += profile_text

    print(f"[!] Invalid records in {user_dir}: {invalid_counter} / {total_counter}")
    
    return {
        "users": list(feature_dict.keys()),
        "features": list(feature_dict.values())
    }


def load_user_followers(user_dir: os.PathLike):
    user_info = load_user_info(user_dir)
    
    follower_dict = {}
    for user, info in user_info.items():
        follower_dict[user] = [follower['name'] for follower in info['followers']]
        
    return follower_dict
    