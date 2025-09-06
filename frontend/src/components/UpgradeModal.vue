<template>
  <transition name="modal" @after-leave="$emit('after-close')">
    <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
      <div class="activation-modal">
        <!-- 头部 -->
        <div class="modal-header">
          <div class="header-content">
            <div class="icon-wrapper">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="header-text">
            <h3>激活码兑换</h3>
            <p class="header-subtitle">输入激活码，解锁专属服务</p>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 4L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- 主体内容 - 横向布局 -->
      <div class="modal-body">
        <div class="horizontal-layout">
          <!-- 左侧：二维码展示区域 -->
          <div class="qr-section">

            
            <div class="qr-container">
              <div class="qr-wrapper">
                <div class="qr-placeholder">
                  <div class="qr-pattern">
                    <div class="qr-dot" v-for="i in 64" :key="i" :style="getRandomStyle(i)"></div>
                  </div>
                  <div class="qr-logo">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="qr-info">
              <h3>{{random_code}}</h3>
              <p>扫描上方二维码，访问官方网站获取专属激活码</p>
              <div class="qr-steps">
                <div class="step-item">
                  <div class="step-number">1</div>
                  <span>扫描二维码</span>
                </div>
                <div class="step-arrow">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 2L10 6L6 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="step-item">
                  <div class="step-number">2</div>
                  <span>获取激活码</span>
                </div>
                <div class="step-arrow">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 2L10 6L6 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="step-item">
                  <div class="step-number">3</div>
                  <span>输入激活码</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧：激活码输入区域 -->
          <div class="activation-section">
            <div class="activation-form">
              <div class="activation-header">
                <h4>输入激活码</h4>
                <p>已有激活码？输入后立即享受专属服务</p>
              </div>
              <div class="activation-input">
                <input 
                  type="text" 
                  v-model="activationCode"
                  placeholder="请输入激活码"
                  class="activation-field"
                  maxlength="6"
                  @input="formatActivationCode"
                  @keyup.enter="handleActivation"
                />
                <button class="activation-btn" @click="handleActivation" :disabled="!activationCode || activationCode.length < 5 || activationCode.length > 6">
                  <span>立即兑换</span>
                </button>
              </div>
              <div class="activation-features">
                <div class="feature-item">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Z" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M8 11V8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M8 5H8.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  <span>稳定·安全·放心</span>
                </div>
                <div class="feature-item">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Z" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M10.5 8H5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  <span>24小时技术支持</span>
                </div>
                <div class="feature-item">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 15A7 7 0 1 0 8 1a7 7 0 0 0 0 14Z" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M10.5 5.5L5.5 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M10.5 10.5L5.5 5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                  <span>银行级加密保障</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部安全提示 -->
      <div class="modal-footer">
        <div class="security-notice">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>所有信息均经过加密处理，保障您的账户安全</span>
        </div>
      </div>
    </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { defineProps } from 'vue';
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  accountLevel: {
    type: String,
    default: 'free'
  }
});

import { defineEmits } from 'vue';
const emit = defineEmits(['close', 'confirm', 'activation', 'after-close']);

// 状态管理
const activationCode = ref('');
const randomNum = ref('');

// 生成6位随机数
const generateRandomCode = () => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

// 计算属性：显示的随机码
const random_code = computed(() => {
  if (!randomNum.value) {
// 由于计算属性不应有副作用，因此不在这里修改 randomNum.value
// 可依赖 onMounted 钩子在组件挂载时初始化 randomNum.value
return generateRandomCode();
  }
  return randomNum.value;
});

// 组件挂载时生成随机码
onMounted(() => {
  if (!randomNum.value) {
    randomNum.value = generateRandomCode();
  }
});

// 方法
const handleActivation = async () => {
  console.log('收到点击')
  if (activationCode.value.trim() && (activationCode.value.length >= 5 && activationCode.value.length <= 6)) {
    // 将5-6位的激活码填充为16位
    let paddedCode = activationCode.value.trim().toUpperCase();
    paddedCode = paddedCode.padStart(16, '0');
    
    try {
      const response = await fetch('/api/verify-activation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          randomCode: randomNum.value,
          activationCode: paddedCode
        })
});
      
      const result = await response.json();
      
      if (result.success) {
        // 激活成功，通知父组件
        emit('activation', {
          success: true,
          version: result.version,
          expiryDate: result.expiryDate
        });
        activationCode.value = '';
      } else {
        // 激活失败，显示错误信息
        ElMessage.error(result.error || '激活码验证失败，请检查激活码是否正确');
      }
    } catch (error) {
      console.error('激活码验证请求失败:', error);
      ElMessage.error('激活码验证请求失败，请稍后重试');
    }
  } else {
    ElMessage.error('激活码长度不正确，请输入5-6位激活码');
  }
};

const formatActivationCode = (event) => {
  let value = event.target.value.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  activationCode.value = value;
};

const getRandomStyle = (index) => {
  const colors = ['#3b82f6', '#1d4ed8', '#60a5fa', '#93c5fd'];
  const color = colors[Math.floor(Math.random() * colors.length)];
  const size = Math.random() * 4 + 2;
  const opacity = Math.random() * 0.5 + 0.3;
  
  return {
    backgroundColor: color,
    width: `${size}px`,
    height: `${size}px`,
    opacity: opacity,
    animationDelay: `${index * 0.1}s`
  };
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(12px);
  animation: fadeIn 0.4s ease;
}

.activation-modal {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 24px;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.5s ease;
}

.modal-header {
  padding: 32px 32px 24px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 24px 24px 0 0;
}

.header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  animation: pulse 2s infinite;
}

.header-text h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.header-subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f3f4f6;
  border: none;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #374151;
  transform: scale(1.05);
}

.modal-body {
  padding: 24px;
}

/* 横向布局 */
.horizontal-layout {
  display: flex;
  gap: 32px;
  align-items: stretch;
}

/* 左侧二维码区域 */
.qr-section {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.qr-container {
  margin-bottom: 20px;
}

.qr-wrapper {
  display: inline-block;
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.qr-wrapper:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.qr-placeholder {
  width: 160px;
  height: 160px;
  position: relative;
  background: linear-gradient(45deg, #f8fafc 25%, #ffffff 25%, #ffffff 50%, #f8fafc 50%, #f8fafc 75%, #ffffff 75%, #ffffff);
  background-size: 20px 20px;
  border-radius: 10px;
  overflow: hidden;
}

.qr-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  grid-template-rows: repeat(8, 1fr);
  gap: 2px;
  padding: 10px;
}

.qr-dot {
  border-radius: 2px;
  animation: qrPulse 3s infinite;
}

.qr-logo {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  color: #3b82f6;
}

.qr-info h4 {
  margin: 0 0 6px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.qr-info p {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.qr-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.step-number {
  width: 18px;
  height: 18px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
}

.step-item span {
  font-size: 10px;
  color: #374151;
  font-weight: 500;
}

.step-arrow {
  color: #9ca3af;
  animation: bounce 2s infinite;
}



/* 右侧激活码区域 */
.activation-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.activation-form {
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.activation-header {
  text-align: center;
  margin-bottom: 20px;
}

.activation-header h4 {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.activation-header p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.activation-input {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.activation-field {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #1f2937;
  background: white;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

.activation-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.activation-field::placeholder {
  color: #9ca3af;
  text-transform: none;
  letter-spacing: normal;
}

.activation-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  min-width: 80px;
}

.activation-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

.activation-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.activation-features {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  font-size: 12px;
  color: #374151;
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: #f1f5f9;
  border-color: #3b82f6;
}

.feature-item svg {
  color: #3b82f6;
  flex-shrink: 0;
}

/* 底部安全提示 */
.modal-footer {
  padding: 20px 32px 24px;
  border-radius: 0 0 24px 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-top: 1px solid #f3f4f6;
}

.security-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #6b7280;
  font-size: 12px;
}

.security-notice svg {
  color: #10b981;
  flex-shrink: 0;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.4s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .activation-modal,
.modal-leave-active .activation-modal {
  transition: all 0.4s ease;
}

.modal-enter-from .activation-modal,
.modal-leave-to .activation-modal {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slideDown {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes qrPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(3px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .activation-modal {
    margin: 20px;
    width: calc(100% - 40px);
    max-height: 80vh;
    border-radius: 20px;
  }
  
  .modal-header {
    padding: 24px 24px 20px;
    border-radius: 20px 20px 0 0;
  }
  
  .header-content {
    gap: 12px;
  }
  
  .icon-wrapper {
    width: 40px;
    height: 40px;
  }
  
  .header-text h3 {
    font-size: 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  /* 横向布局改为垂直布局 */
  .horizontal-layout {
    flex-direction: column;
    gap: 24px;
  }
  

  
  .qr-placeholder {
    width: 160px;
    height: 160px;
  }
  
  .qr-steps {
    flex-direction: column;
    gap: 12px;
  }
  
  .step-arrow {
    transform: rotate(90deg);
  }
  
  .activation-form {
    padding: 20px;
  }
  
  .activation-input {
    flex-direction: column;
  }
  
  .activation-btn {
    justify-content: center;
  }
  
  .modal-footer {
    padding: 16px 24px 20px;
    border-radius: 0 0 20px 20px;
  }
}

@media (max-width: 480px) {
  .activation-modal {
    margin: 12px;
    width: calc(100% - 24px);
  }
  
  .modal-header {
    padding: 20px 20px 16px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .activation-features {
    gap: 8px;
  }
  
  .feature-item {
    font-size: 12px;
    padding: 6px 10px;
  }
  
  .modal-footer {
    padding: 12px 20px 16px;
  }
}
</style>