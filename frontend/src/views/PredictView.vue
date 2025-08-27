<template>
  <div class="predict-view">
    <div class="card">
      <h2>新店铺位置预测</h2>
      
      <div class="prediction-form">
        <div class="form-group">
          <label>周边人口密度 (人/平方公里):</label>
          <input type="number" v-model="formData.population" min="0" max="50000">
          <div class="slider-container">
            <input type="range" v-model="formData.population" min="0" max="50000" step="100">
          </div>
        </div>
        
        <div class="form-group">
          <label>500米内竞争对手数量:</label>
          <input type="number" v-model="formData.competitors" min="0" max="20">
          <div class="slider-container">
            <input type="range" v-model="formData.competitors" min="0" max="20">
          </div>
        </div>
        
        <div class="form-group">
          <label>交通便利指数 (0-1):</label>
          <input type="number" v-model="formData.transport" min="0" max="1" step="0.01">
          <div class="slider-container">
            <input type="range" v-model="formData.transport" min="0" max="1" step="0.01">
          </div>
        </div>
        
        <div class="form-group">
          <label>目标店铺评分:</label>
          <input type="number" v-model="formData.rating" min="1" max="5" step="0.1">
          <div class="slider-container">
            <input type="range" v-model="formData.rating" min="1" max="5" step="0.1">
          </div>
        </div>
        
        <div class="form-group">
          <label>价格水平 (1-5):</label>
          <input type="number" v-model="formData.price_level" min="1" max="5">
          <div class="slider-container">
            <input type="range" v-model="formData.price_level" min="1" max="5">
          </div>
        </div>
        
        <button class="button" @click="predict">预测位置潜力</button>
      </div>
      
      <div v-if="predictionResult" class="prediction-result">
        <h3>预测结果</h3>
        <div class="result-card" :style="{borderColor: resultColor}">
          <div class="result-header">
            <span class="cluster-indicator" :style="{backgroundColor: resultColor}"></span>
            <h4>{{ predictionResult.label }}</h4>
          </div>
          <p>{{ predictionResult.description }}</p>
          <div class="result-metrics">
            <div class="metric">
              <span class="metric-label">潜力指数</span>
              <span class="metric-value">{{ predictionResult.score }}/10</span>
            </div>
            <div class="metric">
              <span class="metric-label">建议</span>
              <span class="metric-value">{{ predictionResult.recommendation }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const formData = ref({
      population: 10000,
      competitors: 3,
      transport: 0.7,
      rating: 4.0,
      price_level: 3
    });
    
    const predictionResult = ref(null);
    
    const clusterInfo = [
      {
        label: "高潜力区域",
        description: "此区域具有极高的发展潜力，强烈推荐开设新店",
        score: 9.2,
        recommendation: "立即投资开店",
        color: "#2ecc71"
      },
      {
        label: "成熟商业区",
        description: "商业发达区域，竞争激烈但客流量大",
        score: 7.5,
        recommendation: "适合知名品牌入驻",
        color: "#3498db"
      },
      {
        label: "发展中区域",
        description: "有发展潜力但需要时间培育市场",
        score: 6.0,
        recommendation: "适合长期投资",
        color: "#f39c12"
      },
      {
        label: "低潜力区域",
        description: "目前发展条件不足，开店风险较高",
        score: 4.3,
        recommendation: "不推荐立即投资",
        color: "#e74c3c"
      },
      {
        label: "旅游热点区",
        description: "游客集中区域，租金高但客流量大",
        score: 7.8,
        recommendation: "适合特色餐饮",
        color: "#9b59b6"
      }
    ];
    
    const predict = async () => {
      try {
        const response = await axios.post('http://localhost:5000/api/predict', formData.value);
        const cluster = response.data.cluster;
        predictionResult.value = clusterInfo[cluster];
      } catch (error) {
        console.error('预测失败:', error);
        alert('预测失败，请确保后端服务已启动且模型已训练');
      }
    };
    
    return {
      formData,
      predictionResult,
      predict
    };
  },
  computed: {
    resultColor() {
      return this.predictionResult ? this.predictionResult.color : '#3498db';
    }
  }
};
</script>

<style scoped>
.prediction-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

input[type="number"] {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.slider-container {
  padding: 0 0.5rem;
}

input[type="range"] {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  outline: none;
  /* -webkit-appearance: none; */
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3498db;
  cursor: pointer;
}

.prediction-result {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.result-card {
  background: white;
  border: 2px solid;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.result-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.cluster-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: 10px;
}

.result-card h4 {
  font-size: 1.3rem;
  color: #2c3e50;
}

.result-card p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.result-metrics {
  display: flex;
  gap: 2rem;
}

.metric {
  flex: 1;
}

.metric-label {
  display: block;
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 0.3rem;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}
</style>