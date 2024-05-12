import os
import json
from tqdm import tqdm
import torch
import argparse
import shutil
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from preprocess import load_user_feature_text


def average_pool(
    last_hidden_states: Tensor,
    attention_mask: Tensor
) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--embed-model', type=str, default='thenlper/gte-large-zh')
    parser.add_argument('--raw-data-dir', type=str, required=True)
    parser.add_argument('--output-dir', type=str, required=True)
    parser.add_argument('--chunk-size', type=int, default=50)
    parser.add_argument('--force-revectorize', action='store_true')
    args = parser.parse_args()
    
    # do cleaning
    if args.force_revectorize and os.path.isdir(args.output_dir):
        shutil.rmtree(args.output_dir)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        
    # load all user feature text
    user_features = load_user_feature_text(args.raw_data_dir)
    
    # load indices of vectorized user feature
    embed_index_file = os.path.join(args.output_dir, 'index.json')
    if os.path.exists(embed_index_file):
        with open(embed_index_file, 'r+', encoding='utf-8') as f:
            embed_index = json.load(f)
    else:
        embed_index = {}
        
    # collect user features to be vectorized
    user_features_to_be_vectorized = {
        "users": [],
        "features": []
    }
    if args.force_revectorize:
        user_features_to_be_vectorized = user_features
    else:
        for user, feature in zip(user_features['users'], user_features['features']):
            if user not in embed_index:
                user_features_to_be_vectorized['users'].append(user)
                user_features_to_be_vectorized['features'].append(feature)
    
    # handle incomplete last chunk
    first_chunk_incomplete = False
    first_chunk_size = args.chunk_size
    if not args.force_revectorize:
        first_chunk_id = max([chunk_index for _, chunk_index in embed_index.items()]) if len(embed_index) != 0 else 0
        first_chunk_info_file = os.path.join(args.output_dir, f"chunk_info_{first_chunk_id:>04d}.json")
        if os.path.exists(first_chunk_info_file):
            with open(first_chunk_info_file, 'r+', encoding='utf-8') as f:
                first_chunk_info = json.load(f)
            
            if len(first_chunk_info['users']) < args.chunk_size:
                first_chunk_size -= len(first_chunk_info['users'])
                first_chunk_incomplete = True
                
                chunk_file = os.path.join(args.output_dir, f"chunk_{first_chunk_id:>04d}.bin")
                first_chunk_embed = torch.load(chunk_file)
            else:
                first_chunk_id += 1
    else:
        first_chunk_id = 0
    
    # split input data into chunks
    batch_data = [{
        "id": first_chunk_id,
        "users": user_features_to_be_vectorized['users'][:first_chunk_size],
        "features": user_features_to_be_vectorized['features'][:first_chunk_size]
    }]
    for i in range(first_chunk_size, len(user_features_to_be_vectorized['users']), args.chunk_size):
        batch_data.append({
            "id": batch_data[-1]['id'] + 1,
            "users": user_features_to_be_vectorized['users'][i: i + args.chunk_size],
            "features": user_features_to_be_vectorized['features'][i: i + args.chunk_size]
        })
    
    # load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.embed_model)
    model = AutoModel.from_pretrained(args.embed_model).cuda()
    
    # inference
    for i, batch in tqdm(enumerate(batch_data), total=len(batch_data)):
        input_texts = batch['features']

        # Tokenize the input texts
        batch_dict = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')
        for key, value in batch_dict.items():
            if isinstance(value, torch.Tensor):
                batch_dict[key] = value.cuda()

        outputs = model(**batch_dict)
        embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

        # (Optionally) normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        chunk_info_file = os.path.join(args.output_dir, f"chunk_info_{batch['id']:>04d}.json")
        chunk_file = os.path.join(args.output_dir, f"chunk_{batch['id']:>04d}.bin")
        if i == 0 and first_chunk_incomplete:
            batch = {
                "id": batch['id'],
                "users": first_chunk_info['users'] + batch['users'],
                "features": first_chunk_info['features'] + batch['features']
            }
            prev_embeddings = torch.load(chunk_file)
            embeddings = torch.cat([prev_embeddings, embeddings], dim=0)
        
        with open(chunk_info_file, 'w+', encoding='utf-8') as f:
            json.dump(obj=batch, fp=f, indent=4, ensure_ascii=False)
        torch.save(obj=embeddings.detach(), f=chunk_file)
        
        with open(embed_index_file, 'w+', encoding='utf-8') as f:
            for user in batch['users']:
                embed_index[user] = batch['id']
            json.dump(obj=embed_index, fp=f, indent=4, ensure_ascii=False)
            
        del outputs, embeddings
