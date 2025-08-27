import { createRouter, createWebHistory } from 'vue-router'
import MapView from './views/MapView.vue'
import PredictView from './views/PredictView.vue'
import DataView from './views/DataView.vue'

const routes = [
  {
    path: '/',
    name: 'Map',
    component: MapView
  },
  {
    path: '/predict',
    name: 'Predict',
    component: PredictView
  },
  {
    path: '/data',
    name: 'Data',
    component: DataView
  },
  // 添加 404 处理
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL), // 使用环境变量中的基础路径
  routes
})

export default router