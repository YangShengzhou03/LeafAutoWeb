<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="top-section">
        <div class="user-info">
          <div class="avatar">{{avatarChar}}</div>
          <span class="unlogin">{{nickname}}</span>
        </div>
        <nav class="menu">
          <ul>
            <li class="menu-item" :class="{ active: currentRoute === '/' }">
              <router-link to="/">首页</router-link>
            </li>
            <li class="menu-item" :class="{ active: currentRoute === '/auto_info' }">
              <router-link to="/auto_info">自动信息</router-link>
            </li>
            <li class="menu-item" :class="{ active: currentRoute === '/ai_takeover' }">
              <router-link to="/ai_takeover">AI 运营</router-link>
            </li>
            <li class="menu-item" :class="{ active: currentRoute === '/other_box' }">
              <router-link to="/other_box">数据导出</router-link>
            </li>
          </ul>
        </nav>
      </div>
      <div class="sidebar-footer">
        <div class="dev-info">已发信息 {{ quotaInfo.used_today }} / {{ quotaInfo.is_unlimited ? '∞' : quotaInfo.daily_limit }}</div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: quotaInfo.is_unlimited ? '100%' : (quotaInfo.used_today / quotaInfo.daily_limit) * 100 + '%' }"></div>
        </div>
        <button class="upgrade-btn" @click="handleUpgrade">{{ upgradeButtonText }}</button>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>

    <!-- 升级模态框 -->
    <UpgradeModal 
      :show="showUpgradeModal" 
      :account-level="quotaInfo.account_level"
      @close="showUpgradeModal = false"
      @confirm="handlePayment"
      @activation="handleActivation"
    />
  </div>
</template>

<script setup>
import { useRoute, onBeforeRouteUpdate } from 'vue-router';
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import UpgradeModal from '@/components/UpgradeModal.vue';

const nickname = ref("未登录");
const avatarChar = ref("未");
const route = useRoute();
const currentRoute = ref(route.path);
const wxStatusInterval = ref(null);
const quotaInfo = ref({
  used_today: 0,
  daily_limit: 100,
  remaining: 100,
  account_level: 'free',
  is_unlimited: false
});
const quotaInterval = ref(null);
const showUpgradeModal = ref(false);

// 计算升级按钮文本
const upgradeButtonText = computed(() => {
  const level = quotaInfo.value.account_level;
  if (level === 'free') return '升级基础版';
  if (level === 'basic') return '升级企业版';
  return '获取帮助';
});

// 处理升级按钮点击
const handleUpgrade = () => {
  const level = quotaInfo.value.account_level;
  if (level === 'free' || level === 'basic') {
    showUpgradeModal.value = true;
  } else {
    // 企业版用户点击时打开帮助链接
    window.open('https://qm.qq.com/q/EYFzhIHdhC', '_blank');
  }
};



// 处理支付
const handlePayment = () => {
  // 这里可以添加实际的支付逻辑
  ElMessage.warning('支付功能即将上线，请稍后再试');
  showUpgradeModal.value = false;
};

// 处理激活
const handleActivation = (result) => {
  if (result.success) {
    // 根据激活的版本显示不同的成功消息
    const versionText = result.version === 'enterprise' ? '企业版' : '基础版';
    ElMessage.success(`${versionText}激活成功`);
    
    // 刷新页面以更新用户状态
    setTimeout(() => {
      window.location.reload();
    }, 1500);
  }
  showUpgradeModal.value = false;
};

// 检查微信登录状态
const checkWeChatStatus = async () => {
  const maxRetries = 3;
  const retryDelay = 1000; // 1秒重试延迟
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch('http://localhost:5000/api/wechat-status');
      
      
      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`);
      }
      
      const result = await response.json();


      
      if (result.success && result.online) {
        // 显示真实的微信用户名，如果获取不到则显示"微信在线"
        nickname.value = result.username || '微信在线';
        avatarChar.value = result.username ? result.username.charAt(0) : '微';
        return; // 成功获取状态，退出函数
      } else {
        nickname.value = result.online ? (result.username || '微信在线') : '未登录';
        avatarChar.value = result.online ? (result.username ? result.username.charAt(0) : '微') : '未';
        return; // API返回失败状态，退出函数
      }
    } catch (error) {
      console.error(`检查微信状态失败 (尝试 ${attempt}/${maxRetries}):`, error);
      
      if (attempt === maxRetries) {
        // 最后一次尝试失败
        nickname.value = '连接异常';
        avatarChar.value = '异';
      } else {
        // 等待后重试
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
      }
    }
  }
};

// 检查消息配额状态
const checkMessageQuota = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/message-quota');
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`);
    }
    
    const result = await response.json();
    if (result.success) {
      quotaInfo.value = result.quota;
    }
  } catch (error) {
    console.error('获取消息配额失败:', error);
  }
};

onMounted(() => {
  // 立即检查一次状态
  checkWeChatStatus();
  checkMessageQuota();
  
  // 每5分钟检查一次微信状态
  wxStatusInterval.value = setInterval(checkWeChatStatus, 300000);
  // 每10秒检查一次消息配额，实现实时响应式更新
  quotaInterval.value = setInterval(checkMessageQuota, 10000);
});

onUnmounted(() => {
  if (wxStatusInterval.value) {
    clearInterval(wxStatusInterval.value);
  }
  if (quotaInterval.value) {
    clearInterval(quotaInterval.value);
  }
});

onBeforeRouteUpdate((to) => {
  currentRoute.value = to.path;
});
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  background: white;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
  padding: 8px 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 100vh;
  position: sticky;
  top: 0;
  left: 0;
  z-index: 10;
  transition: all 0.3s ease;
  border-right: 1px solid #f0f0f0;
  border-radius: 0 12px 12px 0;
}

.top-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
  padding-top: 16px;
  padding-bottom: 16px;
  border-bottom: none;
  width: 100%;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #4361ee;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 8px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(67, 97, 238, 0.15);
}

.avatar:hover {
  transform: scale(1.05) rotate(5deg);
  box-shadow: 0 6px 16px rgba(67, 97, 238, 0.25);
  background-color: #3a56d4;
}

.avatar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(147, 51, 234, 0.05), rgba(192, 132, 252, 0.05));
}

.unlogin {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.menu {
  width: 100%;
  padding: 0 1rem;
}

.menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
}

.menu-item {
  margin-bottom: 0.5rem;
  border-radius: 8px;
  transition: var(--transition);
  width: 100%;
  text-align: center;
  position: relative;
  cursor: pointer;
}

.menu-item a {
  color: var(--text-primary);
  text-decoration: none;
  display: block;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  transition: var(--transition);
  font-size: 16px;
  width: 100%;
  height: 100%;
}

.menu-item:hover {
  background-color: rgba(67, 97, 238, 0.08);
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(67, 97, 238, 0.1);
}

.menu-item.active {
  background-color: rgba(67, 97, 238, 0.12);
  box-shadow: 0 2px 8px rgba(67, 97, 238, 0.15);
}

.menu-item.active a {
  color: var(--primary-color);
  font-weight: 600;
}

.menu-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: var(--primary-color);
  border-radius: 0 4px 4px 0;
}

.sidebar-footer {
  width: 100%;
  padding: 1rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 9px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}

.dev-info {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 0rem;
  line-height: 1.4;
}

.upgrade-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: var(--transition);
  width: 100%;
  max-width: 160px;
  box-shadow: 0 2px 8px rgba(67, 97, 238, 0.25);
}

.upgrade-btn:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(67, 97, 238, 0.3);
  }



.progress-bar {
  width: 100%;
  height: 6px;
  background-color: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4361ee, #3a56d4);
  border-radius: 3px;
  transition: width 0.3s ease;
  box-shadow: 0 1px 3px rgba(67, 97, 238, 0.3);
}

.main-content {
  flex: 1;
  padding: 12px;
  box-sizing: border-box;
  overflow-y: auto;
  background-color: #fafafa;
  min-height: 100vh;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 180px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 160px;
  }

  .menu-item a {
    font-size: 14px;
  }
}
</style>
