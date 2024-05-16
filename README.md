# BIT-DataMining

## project
本项目的系统所在
### step-1:在web中开启前端
### step-2:在server中开启后端

## src
两个推荐算法：协同过滤算法和使用gte做embedding的基于内容推荐算法
### Collaborative-Filtering

- 协同过滤：`CollaborativeFiltering.py`
- 可视化: `visualize.py`

#### Output Format:
```plain text
[!] target user: Hutchinsons好轻松一家
Preference ranking:
1. 荒蛋制造局 : -0.353553
2. 赖跃森超写实油画 : -0.471405
3. 兔三格格 : -0.512989
4. 地理研究舍 : -0.516398
5. 日本大使金杉宪治 : -0.516398
6. 有趣de歪果仁 : -0.516398
7. JackyQ_Talking : -0.651920
8. 魏建军 : -0.745356
9. 毕福剑 : -0.772328
10. 寻鸭 : N/A
```

### Content-Based
#### Step-1: get user feature embeddings
```shell
CUDA_VISIBLE_DEVICES=x python vectorize.py \
    --embed-model /path/to/your/embed/model/ckpt \
    --raw-data-dir /path/to/followers/dir \
    --output-dir /dir/used/to/store/embeds
```

#### Step-2: get recommendations for single user
```shell
CUDA_VISIBLE_DEVICES=x python content_based_matching.py \
    --user-file /single/target/user/file \
    --vectorized-follower-dir /dir/used/to/store/embeds \
    --num-recommend x
```

#### Output Format:
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
