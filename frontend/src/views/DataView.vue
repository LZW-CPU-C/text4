<template>
  <div class="data-view">
    <div class="card">
      <h2>数据管理</h2>
      
      <div class="data-info">
        <p>当前数据来源：高德地图API</p>
        <p>数据更新时间：{{ lastUpdate }}</p>
        <p>数据条目数：{{ dataCount }}</p>
      </div>
      
      <div class="actions">
        <button class="button" @click="refreshData">刷新数据</button>
        <button class="button" @click="exportData" style="margin-left: 10px">导出数据</button>
      </div>
      
      <div class="data-table">
        <table>
          <thead>
            <tr>
              <th>名称</th>
              <th>地址</th>
              <th>评分</th>
              <th>价格水平</th>
              <th>聚类</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in sampleData" :key="index">
              <td>{{ item.name }}</td>
              <td>{{ item.address }}</td>
              <td>{{ item.rating }}</td>
              <td>{{ '¥'.repeat(item.price_level) }}</td>
              <td>
                <span class="cluster-tag" :style="{backgroundColor: clusterColors[item.cluster]}">
                  {{ clusterLabels[item.cluster] }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const lastUpdate = ref(new Date().toLocaleString());
    const dataCount = ref(0);
    const clusterLabels = [
      "高潜力区域", "成熟商业区", "发展中区域", "低潜力区域", "旅游热点区"
    ];
    const clusterColors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6'];
    
    // 模拟数据
    const sampleData = ref([
      { name: "海底捞火锅", address: "朝阳区建国路87号", rating: 4.8, price_level: 3, cluster: 0 },
      { name: "星巴克咖啡", address: "海淀区中关村大街1号", rating: 4.5, price_level: 2, cluster: 1 },
      { name: "外婆家", address: "西城区西单北大街131号", rating: 4.3, price_level: 2, cluster: 2 },
      { name: "全聚德烤鸭", address: "东城区王府井大街88号", rating: 4.6, price_level: 4, cluster: 3 },
      { name: "麦当劳", address: "丰台区南三环西路16号", rating: 4.0, price_level: 1, cluster: 4 },
    ]);
    
    dataCount.value = sampleData.value.length;
    
    const refreshData = async () => {
      try {
        await axios.post('http://localhost:5000/api/get_data', {
          city: '北京市',
          keywords: ['餐厅']
        });
        lastUpdate.value = new Date().toLocaleString();
        alert('数据已刷新，请返回地图查看');
      } catch (error) {
        console.error('刷新数据失败:', error);
        alert('刷新数据失败，请检查控制台');
      }
    };
    
    const exportData = () => {
      alert('数据导出功能将在后续版本实现');
    };
    
    return {
      lastUpdate,
      dataCount,
      sampleData,
      clusterLabels,
      clusterColors,
      refreshData,
      exportData
    };
  }
};
</script>

<style scoped>
.data-view {
  max-width: 1200px;
  margin: 0 auto;
}

.data-info {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.data-info p {
  margin: 0.5rem 0;
  font-size: 1.1rem;
}

.actions {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.data-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

th {
  background-color: #3498db;
  color: white;
  font-weight: 600;
}

tbody tr:hover {
  background-color: #f5f7fa;
}

.cluster-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  color: white;
  font-size: 0.85rem;
  font-weight: 500;
}
</style>