import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd
import numpy as np

def parse_recommendations(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
    users = data.split('[!] target user:')
    results = {}
    for user in users[1:]:  
        lines = user.strip().split('\n')
        username = lines[0].strip()
        scores = {}
        for line in lines[2:]:  
            if ':' in line:
                item, score = line.split(':')
                item = item.strip().split('.')[1].strip()
                score = score.strip()
                scores[item] = None if score == 'N/A' else float(score)
        results[username] = scores
    return results

def visualize_recommendations(recommendation_data):
    
    font_path = "/Users/zhangyunhe/Downloads/SourceHanSansCN-VF.ttf"  
    prop = matplotlib.font_manager.FontProperties(fname=font_path)
    
    for user, scores in recommendation_data.items():
        items = list(scores.keys())
        values = [scores[item] if scores[item] is not None else -1 for item in items]  
        plt.figure(figsize=(10, 5))
        plt.bar(items, values, color='blue')
        plt.xlabel('Recommended Items', fontproperties=prop)
        plt.ylabel('Similarity Score', fontproperties=prop)
        plt.title(f'Recommendation Scores for {user}', fontproperties=prop)
        plt.xticks(rotation=45, ha='right', fontproperties=prop)
        plt.tight_layout()
        
        
        plt.savefig(f'./img/{user}.png', bbox_inches='tight')
        plt.close()

def parse_recommendations_to_df(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
    users = data.split('[!] target user:')
    results = {}
    for user in users[1:]:
        lines = user.strip().split('\n')
        username = lines[0].strip()
        scores = {}
        for line in lines[2:]:
            if ':' in line:
                item, score = line.split(':')
                item = item.strip().split('.')[1].strip()
                score = score.strip()
                scores[item] = float(-1.00) if score == 'N/A' else float(score)
        results[username] = scores
    return pd.DataFrame(results)

def plot_heatmap(df):
    
    font_path = "/Users/zhangyunhe/Downloads/SourceHanSansCN-VF.ttf"  
    prop = matplotlib.font_manager.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = prop.get_name()  

    # 绘制热度图
    plt.figure(figsize=(12, 10))
    sns.heatmap(df.T, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
    plt.title('Similarity Score Distribution Across All Users', fontproperties=prop)
    plt.xlabel('Recommended Items', fontproperties=prop)
    plt.ylabel('Users', fontproperties=prop)
    plt.xticks(fontproperties=prop, rotation=45)
    plt.yticks(fontproperties=prop, rotation=0)
    plt.tight_layout()

    plt.savefig(f'./img/heatmap.png')
    plt.close()



if __name__ == "__main__":
    
    filename = '/Users/zhangyunhe/Files/homework/数据挖掘/BIT-DataMining/src/CollaborativeFiltering/recommendations.txt'
    # recommendation_data = parse_recommendations(filename)
    # visualize_recommendations(recommendation_data)

    df = parse_recommendations_to_df(filename)
    # 填充缺失值
    df.fillna(-1.00, inplace=True)
    plot_heatmap(df)