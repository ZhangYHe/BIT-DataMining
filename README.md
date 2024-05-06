# BIT-DataMining

## Content-Based
### Step-1: get user feature embeddings
```shell
CUDA_VISIBLE_DEVICES=x python vectorize.py \
    --embed-model /path/to/your/embed/model/ckpt \
    --raw-data-dir /path/to/followers/dir \
    --output-dir /dir/used/to/store/embeds
```

### Step-2: get recommendations for single user
```shell
CUDA_VISIBLE_DEVICES=x python content_based_matching.py \
    --user-file /single/target/user/file \
    --vectorized-follower-dir /dir/used/to/store/embeds \
    --num-recommend x
```

### Output Format:
```plain text
[!] target user: JacksonHinkle
Preference ranking:
1. 专业戳轮胎熊律师: 0.9536
2. 番茄殿下: 0.9522
3. 伊能靜: 0.9503
4. 一个专员: 0.9502
5. 并不软的软喵子: 0.9476
6. 咕咕咕_乐: 0.9465
7. CyberZhiqi: 0.9449
8. 铁手叫兽: 0.9433
9. 商建刚: 0.9414
10. 三联生活周刊: 0.9409
```