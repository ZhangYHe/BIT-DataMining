<template>
  <div class="container">
    <div v-for="(post, index) in posts" :key="index" class="post-container">
      <div class="post">
        <div class="user-info">
          <span class="name">{{ post.user }}</span>
        </div>
        <div class="content">{{ post.content }}</div>
        <div class="actions">
          <button @click="toggleLike(index)" :class="{ 'like-button': true, 'liked': post.liked }">
            {{ post.liked ? '取消点赞' : '点赞' }}
          </button>
        </div>
      </div>
    </div>
    <button class="refresh-button" @click="refresh">刷新</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      posts: [],
      likedUsers: []
    };
  },
  mounted() {
    this.refresh();
  },
  methods: {
    async sendLikedUsers() {
      try {
        const response = await fetch('http://localhost:5000/api/save_liked_users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ followers: this.likedUsers })
        });

        if (!response.ok) {
          throw new Error('Failed to save liked users');
        }
        console.log('Liked users saved successfully');
      } catch (error) {
        console.error('Error saving liked users:', error.message);
      }
    },
    async refresh() {
      try {
        const response = await fetch('http://localhost:5000/api/recommend_users');
        if (!response.ok) {
          throw new Error('Failed to fetch random posts');
        }
        const data = await response.json();
        this.posts = data.map(post => ({
          user: post.user,
          content: post.post,
          liked: false
        }));
        // 数据加载完成后发送点赞用户信息
        this.sendLikedUsers();
      } catch (error) {
        console.error('Error fetching random posts:', error.message);
      }
    },
    toggleLike(index) {
      const post = this.posts[index];
      post.liked = !post.liked;
      if (post.liked) {
        this.likedUsers.push({ name: post.user });
      } else {
        const userIndex = this.likedUsers.findIndex(user => user.name === post.user);
        if (userIndex !== -1) {
          this.likedUsers.splice(userIndex, 1);
        }
      }
    }
  }
};
</script>

<style>
.container {
  width: 60%;
  margin: 0 auto;
  padding: 20px;
}

.post-container {
  margin-bottom: 20px;
}

.post {
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 10px;
}

.user-info {
  margin-bottom: 5px;
}

.name {
  font-size: 18px;
  font-weight: bold;
}

.content {
  margin-bottom: 10px;
}

.actions {
  text-align: right;
}

.like-button {
  background-color: #007bff;
  color: #fff;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

.like-button.liked {
  background-color: #ff6347;
}

.refresh-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}
</style>
