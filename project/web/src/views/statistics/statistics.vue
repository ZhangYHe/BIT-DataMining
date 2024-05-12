<template>
  <div class="st-container">
    <div class="charts-container">
      <div class="bar-chart" ref="barChart"></div>
      <div class="pie-chart" ref="pieChart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  data() {
    return {
      likedUsers: [],
      similarityScores: []
    };
  },
  mounted() {
    this.fetchLikedUsers();
    this.fetchSimilarityScores();
  },
  methods: {
    async fetchLikedUsers() {
      try {
        const response = await fetch('http://localhost:5000/api/liked_users');
        if (!response.ok) {
          throw new Error('Failed to fetch liked users');
        }
        const data = await response.json();
        this.likedUsers = data.followers.map(user => user.name);
        this.renderPieChart();
      } catch (error) {
        console.error('Error fetching liked users:', error.message);
      }
    },
    async fetchSimilarityScores() {
      try {
        const response = await fetch('http://localhost:5000/api/similarity_scores');
        if (!response.ok) {
          throw new Error('Failed to fetch similarity scores');
        }
        const data = await response.json();
        // Reverse the array to ensure higher scores are displayed on top
        this.similarityScores = data.reverse();
        this.renderBarChart();
      } catch (error) {
        console.error('Error fetching similarity scores:', error.message);
      }
    },
    renderPieChart() {
      const userCount = {};
      this.likedUsers.forEach(user => {
        userCount[user] = (userCount[user] || 0) + 1;
      });
      const pieChart = echarts.init(this.$refs.pieChart);
      const option = {
        title: {
          text: '用户点赞博主的饼图',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'middle',
          data: Object.keys(userCount)
        },
        series: [
          {
            name: 'Liked Users',
            type: 'pie',
            radius: '50%',
            center: ['40%', '50%'],
            data: Object.keys(userCount).map(user => ({
              name: user,
              value: userCount[user]
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      pieChart.setOption(option);
    },
    renderBarChart() {
      const barChart = echarts.init(this.$refs.barChart);
      const option = {
        title: {
          text: '用户偏好的博主及偏好分数',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '15%',
          right: '15%'
        },
        xAxis: {
          type: 'value',
          boundaryGap: [0, 0.01]
        },
        yAxis: {
          type: 'category',
          data: this.similarityScores.map(item => item.user)
        },
        series: [
          {
            name: 'Similarity Scores',
            type: 'bar',
            data: this.similarityScores.map(item => item.sims)
          }
        ]
      };
      barChart.setOption(option);
    },
    refresh() {
      this.fetchLikedUsers();
      this.fetchSimilarityScores();
    }
  }
};
</script>

<style>
.st-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.charts-container {
  display: flex;
  width: 100%;
  justify-content: space-around;
}

.pie-chart,
.bar-chart {
  width: 45%;
  height: 400px;
}

</style>
