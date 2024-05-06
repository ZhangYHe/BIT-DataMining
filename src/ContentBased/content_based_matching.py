import os
import json
import torch
import argparse
import torch.nn.functional as F


def get_user_preference_embedding(followers, vector_dir: os.PathLike):
    preference_embedding = None
    
    index_file = os.path.join(vector_dir, 'index.json')
    with open(index_file, 'r+', encoding='utf-8') as f:
        user_index = json.load(f)
    
    chunk_ids = []
    for follower in followers:
        if follower in user_index and user_index[follower] not in chunk_ids:
            chunk_ids.append(user_index[follower])
    
    for chunk_id in chunk_ids:
        chunk_info_file = os.path.join(vector_dir, f"chunk_info_{chunk_id:>04d}.json")
        with open(chunk_info_file, 'r+', encoding='utf-8') as f:
            chunk_info = json.load(f)
            
        chunk_file = os.path.join(vector_dir, f"chunk_{chunk_id:>04d}.bin")
        chunk_embed = torch.load(chunk_file)

        for follower in followers:
            if follower in chunk_info['users']:
                follower_index = chunk_info['users'].index(follower)
            follower_embed = chunk_embed[follower_index]
            if preference_embedding is not None:
                preference_embedding += follower_embed
            else:
                preference_embedding = follower_embed
    preference_embedding = F.normalize(preference_embedding.unsqueeze(0), p=2, dim=1)
    return preference_embedding


def cosine_similarity_matching(preference_embed, vector_dir: os.PathLike):
    index_file = os.path.join(vector_dir, 'index.json')
    with open(index_file, 'r+', encoding='utf-8') as f:
        user_index = json.load(f)
        
    user_sim = {"users": [], "sims": []}
    num_chunks = max([chunk_index for _, chunk_index in user_index.items()]) + 1
    
    for chunk_id in range(num_chunks):
        chunk_info_file = os.path.join(vector_dir, f"chunk_info_{chunk_id:>04d}.json")
        with open(chunk_info_file, 'r+', encoding='utf-8') as f:
            chunk_info = json.load(f)
            
        chunk_file = os.path.join(vector_dir, f"chunk_{chunk_id:>04d}.bin")
        chunk_embed = torch.load(chunk_file)
        
        cosine_sim = preference_embed @ chunk_embed.T
        cosine_sim = cosine_sim.squeeze().cpu().numpy().tolist()

        user_sim['users'].extend(chunk_info['users'])
        user_sim['sims'].extend(cosine_sim)
        del chunk_embed
        
    return user_sim


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--user-file', type=str, required=True)
    parser.add_argument('--vectorized-follower-dir', type=str, required=True)
    parser.add_argument('--num-recommend', type=int, default=10)
    args = parser.parse_args()
    
    with open(args.user_file, 'r+', encoding='utf-8') as f:
        info = json.load(f)
        followers = [follower['name'] for follower in info['followers']]
        
    pref_embed = get_user_preference_embedding(followers, args.vectorized_follower_dir)
    sims = cosine_similarity_matching(pref_embed, args.vectorized_follower_dir)

    print(f"[!] target user: {info['profile']['screen_name']}")
    print(f"Preference ranking:")
    rank = torch.argsort(torch.tensor(sims['sims']), descending=True).numpy().tolist()
    counter = 0
    for i, index in enumerate(rank):
        if sims['users'][index] in followers:
            continue
        print(f"{counter + 1}. {sims['users'][index]}: {round(sims['sims'][index], 4)}")
        counter += 1
        if counter >= args.num_recommend:
            break
