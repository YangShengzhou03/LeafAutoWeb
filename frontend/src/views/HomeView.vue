<template>
  <div class="home-container">

    <!-- 当不是企业版时显示定价方案 -->
    <section v-if="!isEnterpriseVersion" class="pricing">
      <div class="section-header">
        <h2>选择适合您企业的方案</h2>
        <p>灵活的定价策略，满足不同规模企业的需求</p>
      </div>
      <div class="pricing-cards">
        <template v-for="plan in homeData.pricingPlans" :key="plan.id">
          <div :class="['pricing-card', { 'popular': plan.isPopular }]">
            <div v-if="plan.isPopular" class="popular-tag">最受欢迎</div>
            <div class="card-header">
              <h3>{{ plan.name }}</h3>
              <div class="price">
                <span class="amount">{{ typeof plan.price === 'number' ? '¥' + plan.price : plan.price }}</span>
                <span class="period">{{ plan.period }}</span>
              </div>
            </div>
            <div class="card-features">
              <div class="feature" v-for="feature in plan.features" :key="feature">
                <i class="el-icon-check"></i>
                <span>{{ feature }}</span>
              </div>
            </div>
            <button :class="['select-plan', { 'popular-btn': plan.isPopular }]" @click="handleSelectPlan(plan)">
              {{ plan.isPopular ? '选择方案' : (plan.id === 3 ? '联系我们' : '选择方案') }}
            </button>
          </div>
        </template>
      </div>
    </section>

    <!-- 当是企业版时显示宣传轮播图 -->
    <section v-else class="promotion-carousel">
      <div class="carousel-container">
        <div class="carousel-wrapper" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
          <div class="carousel-slide" v-for="(slide, index) in promotionSlides" :key="index">
            <div class="slide-content">
              <div class="slide-image">
                <img :src="slide.image" :alt="slide.title">
              </div>
              <div class="slide-info">
                <h3>{{ slide.title }}</h3>
                <p>{{ slide.description }}</p>
              </div>
            </div>
          </div>
        </div>
        <button class="carousel-control prev" @click="prevSlide">❮</button>
        <button class="carousel-control next" @click="nextSlide">❯</button>
      </div>
      <div class="carousel-indicators">
        <span 
          v-for="(slide, index) in promotionSlides" 
          :key="index" 
          :class="['indicator', { active: currentSlide === index }]"
          @click="goToSlide(index)"
        ></span>
      </div>
    </section>


    <section class="key-metrics">
      <div class="metrics-container">
        <div class="metric-card" v-for="metric in homeData.keyMetrics" :key="metric.id">
          <div class="metric-value counter" :data-target="metric.value">{{ metric.value }}</div>
          <div class="metric-label">{{ metric.label }}</div>
        </div>
      </div>
    </section>


    <section class="dashboard">
      <div class="section-header">
        <h2>系统概览</h2>
        <p>实时监控您的自动化状态和效果</p>
      </div>
      <div class="dashboard-cards">
        <div class="dashboard-card" v-for="item in homeData.dashboardData" :key="item.id">
          <div class="card-title">
            <h3>{{ item.title }}</h3>
            <span v-if="item.trend" :class="item.trend === 'up' ? 'trend-up' : 'trend-down'">
              {{ item.trend === 'up' ? '↑' : '↓' }} {{ item.trendValue }}%
            </span>
          </div>
          <div :class="['card-value', { 'status-normal': item.status === 'normal', 'status-abnormal': item.status === 'abnormal' }]">
            {{ item.value }}{{ item.id !== 4 ? '%' : '' }}
          </div>
          <div class="card-footer">
            <span>{{ item.footer }}</span>
          </div>
        </div>
      </div>
    </section>


    <section class="testimonials">
      <div class="section-header">
        <h2>客户评价</h2>
        <p>听听我们的客户怎么说</p>
      </div>
      <div class="testimonial-cards">
        <div class="testimonial-card" v-for="testimonial in homeData.testimonials" :key="testimonial.id">
          <div class="quote">"{{ testimonial.quote }}"</div>
          <div class="customer-info">
            <img :src="require('@/assets/images/user-avatar.svg')" alt="客户头像"
              class="w-12 h-12 rounded-full object-cover mr-4 bg-gray-100" />
            <div class="customer-details">
              <div class="name">{{ testimonial.customerName }}</div>
              <div class="company">{{ testimonial.customerCompany }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
  
  <UpgradeModal 
    :show="showUpgradeModal" 
    @close="showUpgradeModal = false"
    @activation="handleActivation"
  />
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import UpgradeModal from '@/components/UpgradeModal.vue';
import { ElMessage } from 'element-plus'

const animationActive = ref(false);
const showUpgradeModal = ref(false);
// 添加版本状态变量
const isEnterpriseVersion = ref(false);
// 添加轮播图相关变量
const currentSlide = ref(0);
const promotionSlides = ref([
  {
    title: '产品核心功能',
    description: '我们的自动化工具能够帮您处理日常工作中的重复性任务，从数据收集到分析再到执行，一站式解决您的需求。不需要复杂的设置，简单几步就能让系统开始为您工作，让您有更多时间专注于更重要的事情。',
    image: require('@/assets/images/product-features.svg')
  },
  {
    title: 'AI技术创新',
    description: '我们不只是简单地自动化，而是通过智能学习不断优化工作流程。系统会根据您的使用习惯和反馈，自动调整执行策略，越用越聪明。这种自适应技术让我们的工具在同类产品中脱颖而出。',
    image: require('@/assets/images/ai-innovation.svg')
  },
  {
    title: '成功战绩',
    description: '目前已有超过5000家企业选择我们的服务，每月处理的任务量突破100万次。客户反馈显示，使用我们的工具后，工作效率平均提升了85%，满意度高达98%。这些数字背后是我们对产品质量的坚持和对客户需求的深入理解。',
    image: require('@/assets/images/achievements.svg')
  },
  {
    title: '为什么选择我们',
    description: '我们的团队由行业专家组成，不仅懂技术，更了解您的业务痛点。我们提供量身定制的解决方案，而不是千篇一律的产品。数据安全是我们的底线，所有信息都经过加密处理。最重要的是，我们始终在进步，不断根据用户反馈优化产品。',
    image: require('@/assets/images/why-choose-us.svg')
  },
  {
    title: '获取帮助与支持',
    description: '遇到问题？别担心，我们提供多种支持渠道。从详细的使用文档到直观的视频教程，从7×24小时在线客服到活跃的用户社区，总有一种方式适合您。我们的目标是不让任何一个问题成为您使用我们产品的障碍。',
    image: require('@/assets/images/get-support.svg')
  }
]);

// 轮播图控制函数
const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % promotionSlides.value.length;
};

const prevSlide = () => {
  currentSlide.value = (currentSlide.value - 1 + promotionSlides.value.length) % promotionSlides.value.length;
};

const goToSlide = (index) => {
  currentSlide.value = index;
};

// 自动轮播
let autoSlideInterval;
const startAutoSlide = () => {
  autoSlideInterval = setInterval(() => {
    nextSlide();
  }, 5000);
};

const stopAutoSlide = () => {
  clearInterval(autoSlideInterval);
};

// 检查当前版本状态
const checkVersionStatus = async () => {
  try {
    // 从message_quota.json获取版本状态
    const response = await fetch('http://localhost:5000/api/message-quota');
    const result = await response.json();
    // 判断account_level是否为enterprise
    if (result.success) {
      isEnterpriseVersion.value = result.quota.account_level === 'enterprise';
    } else {
      isEnterpriseVersion.value = false;
    }
  } catch (error) {
    console.error('获取版本状态失败:', error);
    // 默认设置为非企业版
    isEnterpriseVersion.value = false;
  }
};

const homeData = ref({
  pricingPlans: [
    { id: 1, name: '基础版', price: '--', period: '/月', features: ['--', '--', '--'], isPopular: false },
    { id: 2, name: '企业版', price: '--', period: '/月', features: ['--', '--', '--'], isPopular: true },
    { id: 3, name: '定制版', price: '--', period: '联系我们', features: ['--', '--', '--'], isPopular: false }
  ],
  keyMetrics: [
    { id: 1, value: '--', label: '活跃企业客户' },
    { id: 2, value: '--', label: '自动化任务' },
    { id: 3, value: '--', label: '系统稳定性' },
    { id: 4, value: '--', label: '消息发送量' }
  ],
  dashboardData: [
    { id: 1, title: '自动化任务完成率', value: '--', status: 'null', footer: '--' },
    { id: 2, title: '消息送达率', value: '--', status: 'null', footer: '--' },
    { id: 3, title: 'AI辅助功能使用率', value: '--', status: 'null', footer: '--' },
    { id: 4, title: '系统状态', value: '正在连接', status: 'normal', footer: '--' }
  ],
  testimonials: [
    { id: 1, quote: '--', customerName: '--', customerCompany: '--' },
    { id: 2, quote: '--', customerName: '--', customerCompany: '--' },
    { id: 3, quote: '--', customerName: '--', customerCompany: '--' }
  ]
});

// 从后端获取数据
const fetchHomeData = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/home-data');
    const data = await response.json();
    
    // 更新现有数据结构，保持框架可见
    if (data.pricingPlans) {
      homeData.value.pricingPlans = data.pricingPlans;
    }
    if (data.keyMetrics) {
      homeData.value.keyMetrics = data.keyMetrics;
    }
    if (data.dashboardData) {
      homeData.value.dashboardData = data.dashboardData;
    }
    if (data.testimonials) {
      homeData.value.testimonials = data.testimonials;
    }

    // 数据加载完成后触发动画
    if (!animationActive.value) {
      triggerAnimations();
    }
  } catch (error) {
    console.error('获取首页数据失败:', error);
    // 保持现有的占位符数据不变，框架始终可见
  }
};

// 触发动画的函数
const triggerAnimations = () => {
  animationActive.value = true;
  const counters = document.querySelectorAll('.counter');
  if (counters.length) {
    counters.forEach(counter => {
      counter.style.opacity = '0';
      counter.style.transform = 'translateY(20px)';
      counter.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

      setTimeout(() => {
        counter.style.opacity = '1';
        counter.style.transform = 'translateY(0)';

        const targetValue = counter.dataset.target;
        // 只对数字值进行计数动画，占位符（--）保持不变
        if (targetValue && targetValue !== '--' && !isNaN(parseFloat(targetValue))) {
          const target = parseFloat(targetValue);
          const duration = 2500;
          const frameDuration = 1000 / 60;
          const totalFrames = Math.round(duration / frameDuration);
          let frame = 0;

          const easeOutQuad = (t) => t * (2 - t);

          const updateCounter = () => {
            frame++;
            const progress = easeOutQuad(frame / totalFrames);
            const current = Math.round(target * progress);

            counter.innerText = current.toLocaleString();

            if (frame < totalFrames) {
              requestAnimationFrame(updateCounter);
            } else {
              counter.innerText = target.toLocaleString();
            }
          };

          updateCounter();
        }
      }, Math.random() * 300);
    });
  }

  setTimeout(() => {
    document.querySelectorAll('.pricing-card, .dashboard-card, .testimonial-card, .metric-card, .carousel-slide').forEach((el, index) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';

      setTimeout(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      }, index * 100 + Math.random() * 100);
    });
  }, 100);
};

// 处理选择方案按钮点击
const handleSelectPlan = (plan) => {
  if (plan.id === 3) {
    // 定制版方案，显示联系我们提示
    ElMessage.info('联系客服获取定制版报价')
  } else {
    // 基础版和企业版，显示升级对话框
    showUpgradeModal.value = true;
  }
};

// 处理激活码提交
const handleActivation = (activationCode) => {
  console.log('提交激活码:', activationCode);
  // 这里可以添加激活码验证逻辑
  ElMessage.success('提交激活码成功，等待验证结果')
  showUpgradeModal.value = false;
};

onMounted(() => {
  // 检查版本状态
  checkVersionStatus();
  
  // 立即触发框架动画，不等待数据加载
  triggerAnimations();
  
  // 异步获取数据
  fetchHomeData();
  
  // 如果是企业版，启动自动轮播
  if (isEnterpriseVersion.value) {
    startAutoSlide();
  }
});

// 组件卸载时清除自动轮播
onUnmounted(() => {
  stopAutoSlide();
});
</script>

<style>
:root {
  --primary-color: #1e40af;
  --secondary-color: #3b82f6;
  --accent-color: #2563eb;
  --light-color: #f8fafc;
  --dark-color: #1e293b;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --success-color: #10b981;
  --success-rgb: 16, 185, 129;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --danger-rgb: 239, 68, 68;
  --border-color: #e2e8f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.home-container {
  background-color: var(--light-color);
  min-height: 100vh;
  overflow-x: hidden;
}


.key-metrics {
  background-color: var(--primary-color);
  color: white;
  padding: 3rem 5%;
}

.metrics-container {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 2rem;
}

.metric-card {
  flex: 1;
  min-width: 150px;
  text-align: center;
  padding: 1.5rem;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  backdrop-filter: blur(5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.metric-card:hover {
  transform: translateY(-5px);
  background-color: rgba(255, 255, 255, 0.15);
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.metric-label {
  font-size: 0.9rem;
  opacity: 0.9;
}


.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.section-header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
  max-width: 700px;
  margin: 0 auto;
}


.pricing {
  padding: 2rem 2%;
  background-color: white;
}

.pricing-cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2rem;
}

.pricing-card {
  flex: 1;
  min-width: 280px;
  max-width: 350px;
  background-color: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 2rem;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.03);
}

.pricing-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 15px 30px rgba(30, 64, 175, 0.1);
  border-color: var(--primary-color);
}

.pricing-card.popular:hover {
  transform: translateY(-15px) scale(1.03);
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.pricing-card.popular {
  border-color: var(--primary-color);
  transform: translateY(-10px);
  box-shadow: 0 10px 30px rgba(30, 64, 175, 0.1);
}

.popular-tag {
  position: absolute;
  top: 0;
  right: 0;
  background-color: var(--primary-color);
  color: white;
  padding: 0.25rem 1.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  transform: rotate(45deg) translate(35%, -100%);
  transform-origin: top right;
}

.card-header {
  margin-bottom: 2rem;
}

.card-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.price {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.amount {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
}

.period {
  color: var(--text-secondary);
}

.card-features {
  margin-bottom: 2rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.feature i {
  color: var(--success-color);
}

.feature span {
  color: var(--text-secondary);
}

.select-plan {
  width: 100%;
  padding: 0.75rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: white;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.select-plan:hover {
  background-color: rgba(30, 64, 175, 0.05);
}

.select-plan.popular-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
}

.select-plan.popular-btn:hover {
  background-color: #1e3a8a;
}


.dashboard {
  padding: 5rem 5%;
  background-color: #f1f5f9;
}

.dashboard-cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.dashboard-card {
  flex: 1;
  min-width: 250px;
  max-width: 300px;
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.07);
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.trend-up {
  color: var(--danger-color);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.trend-down {
  color: var(--success-color);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.card-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.status-normal {
  color: var(--success-color);
  background-color: rgba(var(--success-rgb), 0.15);
  border-radius: 12px;
  padding: 4px 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.status-abnormal {
  color: var(--danger-color);
  background-color: rgba(var(--danger-rgb), 0.15);
  border-radius: 12px;
  padding: 4px 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.card-footer {
  font-size: 0.85rem;
  color: var(--text-secondary);
}


.testimonials {
  padding: 5rem 5%;
  background-color: white;
}

.testimonial-cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2rem;
  position: relative;
}


.testimonial-controls {
  display: none;
}

@media (max-width: 768px) {
  .testimonial-cards {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding: 1rem 0;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .testimonial-cards::-webkit-scrollbar {
    display: none;
  }

  .testimonial-card {
    flex: 0 0 90%;
    margin: 0 0.5rem;
    scroll-snap-align: center;
  }

  .testimonial-controls {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
  }

  .testimonial-control {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: var(--border-color);
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .testimonial-control.active {
    background-color: var(--primary-color);
    transform: scale(1.2);
  }
}

.testimonial-card {
  flex: 1;
  min-width: 300px;
  max-width: 400px;
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.testimonial-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.07);
}

.quote {
  font-size: 1.1rem;
  color: var(--text-primary);
  margin-bottom: 2rem;
  line-height: 1.6;
  position: relative;
  padding-left: 1.5rem;
}

.quote::before {
  content: '"';
  position: absolute;
  top: 0;
  left: 0;
  font-size: 3rem;
  color: var(--primary-color);
  opacity: 0.2;
  line-height: 1;
}

.customer-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.customer-info img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.customer-details {
  display: flex;
  flex-direction: column;
}

.name {
  font-weight: 600;
  color: var(--text-primary);
}

.company {
  font-size: 0.85rem;
  color: var(--text-secondary);
}


@media (max-width: 768px) {
  .metrics-container {
    flex-direction: column;
    align-items: center;
  }

  .metric-card {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 576px) {

  .pricing-card,
  .dashboard-card,
  .testimonial-card {
    max-width: 100%;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .section-header p {
    font-size: 1rem;
  }
}

/* 轮播图样式 */
.promotion-carousel {
  padding: 2rem 2%;
  background-color: white;
}

.carousel-container {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.carousel-wrapper {
  display: flex;
  transition: transform 0.5s ease-in-out;
}

.carousel-slide {
  min-width: 100%;
  background-color: #f8fafc;
}

.slide-content {
  display: flex;
  align-items: center;
  padding: 2rem;
  height: 400px;
}

.slide-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.slide-image img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

.slide-info {
  flex: 1;
  padding: 1rem 2rem;
}

.slide-info h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.slide-info p {
  font-size: 1.1rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.carousel-control {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(255, 255, 255, 0.7);
  color: var(--primary-color);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
  z-index: 10;
}

.carousel-control:hover {
  background-color: var(--primary-color);
  color: white;
}

.carousel-control.prev {
  left: 10px;
}

.carousel-control.next {
  right: 10px;
}

.carousel-indicators {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  gap: 0.5rem;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: var(--border-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background-color: var(--primary-color);
  transform: scale(1.2);
}

@media (max-width: 768px) {
  .slide-content {
    flex-direction: column;
    height: auto;
    padding: 1.5rem;
  }
  
  .slide-info {
    padding: 1rem 0;
    text-align: center;
  }
  
  .slide-info h3 {
    font-size: 1.5rem;
  }
  
  .slide-info p {
    font-size: 1rem;
  }
}

@media (max-width: 576px) {
  .carousel-control {
    width: 30px;
    height: 30px;
    font-size: 14px;
  }
  
  .indicator {
    width: 10px;
    height: 10px;
  }
}

@media (max-width: 768px) {
  .metrics-container {
    flex-direction: column;
    align-items: center;
  }

  .metric-card {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 576px) {

  .pricing-card,
  .dashboard-card,
  .testimonial-card {
    max-width: 100%;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .section-header p {
    font-size: 1rem;
  }
}
</style>