<template>
  <div class="map-view">
    <div class="card">
      <h2>餐饮店铺分布与聚类分析</h2>
      
      <div class="data-controls">
        <div class="form-group">
          <label>选择城市:</label>
          <select v-model="selectedCity">
            <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>关键词:</label>
          <input type="text" v-model="keywords" placeholder="例如: 餐厅,火锅">
        </div>
        
        <button class="button" @click="fetchData">获取数据</button>
        <button class="button" @click="refreshMap" style="margin-left: 10px">刷新地图</button>
      </div>
      
      <div v-if="loading" class="loading">
        <p>数据加载中，请稍候...</p>
      </div>
      
      <div v-else class="map-container">
        <div v-if="mapLoading" class="map-loading">
          <div class="loader"></div>
          <p>地图加载中...</p>
        </div>
        <div id="map" style="height: 500px; border-radius: 8px;"></div>
      </div>
      
      <div class="cluster-info">
        <h3>聚类说明</h3>
        <div class="cluster-item" v-for="(info, index) in clusterInfo" :key="index">
          <span class="cluster-color" :style="{backgroundColor: clusterColors[index]}"></span>
          <span class="cluster-label">{{ info.label }} ({{ info.percentage }}%)</span>
          <p>{{ info.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const clusterInfo = ref([
      {
        label: "高潜力区域",
        percentage: 25,
        description: "人口密集、竞争较少、交通便利，适合开设新店"
      },
      {
        label: "成熟商业区",
        percentage: 30,
        description: "商业发达但竞争激烈，适合知名品牌入驻"
      },
      {
        label: "发展中区域",
        percentage: 20,
        description: "人口增长中，有发展潜力但需长期投资"
      },
      {
        label: "低潜力区域",
        percentage: 15,
        description: "人口稀少或交通不便，不建议开设新店"
      },
      {
        label: "旅游热点区",
        percentage: 10,
        description: "游客集中但租金高昂，适合特色餐饮"
      }
    ]);
    
    const clusterColors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6'];
    const mapInstance = ref(null);
    const selectedCity = ref('北京市');
    const keywords = ref('餐厅,火锅');
    const loading = ref(false);
    const mapLoading = ref(false);
    const cities = ref([
      '北京市', '上海市', '广州市', '深圳市', '杭州市', 
      '南京市', '武汉市', '成都市', '重庆市', '福州市'
    ]);
    
    // 确保所有函数都在 setup 函数内部定义
    const initMap = async () => {
      mapLoading.value = true;
      
      try {
        // 确保地图容器存在
        await nextTick();
        
        // 移除旧地图实例
        if (mapInstance.value) {
          mapInstance.value.remove();
          mapInstance.value = null;
        }
        
        // 默认中心点（北京市）
        let center = [39.9042, 116.4074];
        
        // 尝试获取城市坐标
        try {
          const response = await axios.post('http://localhost:5000/api/geocode', {
            address: selectedCity.value
          });
          if (response.data && response.data.lat && response.data.lng) {
            center = [response.data.lat, response.data.lng];
          }
        } catch (error) {
          console.error('获取城市坐标失败:', error);
        }
        
        // 创建新地图实例
        mapInstance.value = L.map('map', {
          zoomSnap: 0.5, // 平滑缩放
          maxZoom: 18,
          minZoom: 10
        }).setView(center, 12);
        
        // 使用OpenStreetMap瓦片
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19
        }).addTo(mapInstance.value);
        
        // 添加比例尺
        L.control.scale({
          imperial: false,
          metric: true
        }).addTo(mapInstance.value);
        
        // 添加标记
        try {
          // 获取后端数据
          const response = await axios.get('http://localhost:5000/api/clusters');
          const restaurants = response.data;
          
          // 添加标记
          restaurants.forEach(restaurant => {
            const color = clusterColors[restaurant.cluster % clusterColors.length];
            const marker = L.circleMarker(
              [restaurant.lat, restaurant.lng],
              {
                radius: 6,
                fillColor: color,
                color: '#333',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
              }
            ).addTo(mapInstance.value);
            
            // 弹出信息
            marker.bindPopup(`
              <b>${restaurant.name}</b><br>
              地址: ${restaurant.address}<br>
              评分: ${restaurant.rating}<br>
              价格: ${'¥'.repeat(restaurant.price_level)}
            `);
          });
          
          // 添加图例
          const legend = L.control({ position: 'bottomright' });
          legend.onAdd = function() {
            const div = L.DomUtil.create('div', 'info legend');
            div.style.backgroundColor = 'white';
            div.style.padding = '10px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
            
            let html = '<h4>聚类图例</h4>';
            clusterInfo.value.forEach((info, index) => {
              html += `
                <div style="margin: 5px 0; display: flex; align-items: center;">
                  <div style="width: 12px; height: 12px; background: ${clusterColors[index]}; margin-right: 8px; border-radius: 50%;"></div>
                  ${info.label}
                </div>
              `;
            });
            div.innerHTML = html;
            return div;
          };
          legend.addTo(mapInstance.value);
          
          // 添加事件监听器防止空指针错误
          mapInstance.value.on('moveend', () => {
            // 确保地图对象有效
            if (!mapInstance.value) return;
            const center = mapInstance.value.getCenter();
            // console.log('地图中心:', center.lat, center.lng);
          });
          
          // 添加缩放结束事件监听器
          mapInstance.value.on('zoomend', () => {
            if (!mapInstance.value) return;
            const zoom = mapInstance.value.getZoom();
            // console.log('当前缩放级别:', zoom);
          });
          
        } catch (error) {
          console.error('获取数据失败:', error);
        }
        
      } catch (error) {
        console.error('地图初始化失败:', error);
      } finally {
        mapLoading.value = false;
      }
    };
    
    const fetchData = async () => {
      loading.value = true;
      try {
        await axios.post('http://localhost:5000/api/get_data', {
          city: selectedCity.value,
          keywords: keywords.value.split(',').map(k => k.trim()).filter(k => k)
        });
        
        // 等待一段时间后刷新地图
        setTimeout(() => {
          refreshMap();
          loading.value = false;
        }, 5000);
      } catch (error) {
        console.error('获取数据失败:', error);
        loading.value = false;
        alert('获取数据失败，请检查控制台查看详情');
      }
    };
    
    // 修复：确保 refreshMap 函数已定义
    const refreshMap = () => {
      initMap();
    };
    
    // 确保在组件挂载时初始化地图
    onMounted(() => {
      // 延迟初始化地图，确保DOM完全加载
      setTimeout(initMap, 100);
    });
    
    // 组件卸载时清理地图
    onBeforeUnmount(() => {
      if (mapInstance.value) {
        mapInstance.value.remove();
        mapInstance.value = null;
      }
    });
    
    return {
      clusterInfo,
      clusterColors,
      selectedCity,
      keywords,
      cities,
      loading,
      mapLoading,
      fetchData,
      refreshMap // 确保返回 refreshMap 函数
    };
  }
};
</script>

<style scoped>
.map-container {
  position: relative;
  margin-bottom: 2rem;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.cluster-info {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.cluster-item {
  margin-bottom: 1.2rem;
  padding-bottom: 1.2rem;
  border-bottom: 1px solid #eee;
}

.cluster-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.cluster-color {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: 10px;
}

.cluster-label {
  font-weight: 600;
  color: #2c3e50;
}

.cluster-item p {
  margin-top: 8px;
  margin-left: 26px;
  color: #555;
  line-height: 1.5;
}

.data-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-end;
}

.form-group {
  flex: 1;
  min-width: 200px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #2c3e50;
}

select, input[type="text"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.loading {
  text-align: center;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 20px 0;
  font-size: 1.2rem;
  color: #3498db;
}

/* 添加地图加载动画 */
.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  border-radius: 8px;
}

.map-loading p {
  margin-top: 15px;
  font-weight: 500;
  color: #3498db;
}

.loader {
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card {
    padding: 1rem;
  }
  
  .data-controls {
    flex-direction: column;
  }
  
  .form-group {
    min-width: 100%;
  }
}
</style>