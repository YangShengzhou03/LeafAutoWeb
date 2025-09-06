<template>
  <nav class="navigation">
    <div class="nav-brand">
      <img src="@/assets/images/logo.svg" alt="LeafAuto" class="logo" />
      <span class="app-name">LeafAuto Web</span>
    </div>
    
    <ul class="nav-menu">
      <li class="nav-item">
        <router-link to="/" class="nav-link" exact-active-class="active">
          <i class="icon-home"></i>
          <span>首页</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link to="/auto-info" class="nav-link" active-class="active">
          <i class="icon-message"></i>
          <span>消息自动化</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link to="/ai-takeover" class="nav-link" active-class="active">
          <i class="icon-ai"></i>
          <span>AI接管</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link to="/other-box" class="nav-link" active-class="active">
          <i class="icon-box"></i>
          <span>其他功能</span>
        </router-link>
      </li>
    </ul>
    
    <div class="nav-user">
      <div class="user-info">
        <img src="@/assets/images/user-avatar.svg" alt="用户" class="user-avatar" />
        <span class="user-name">管理员</span>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AppNavigation',
  data() {
    return {
      isCollapsed: false
    }
  }
}
</script>

<style scoped>
.navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  width: 32px;
  height: 32px;
}

.app-name {
  font-size: 1.25rem;
  font-weight: 600;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 2rem;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-user {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.user-name {
  font-weight: 500;
}

/* 图标样式 */
.icon-home::before { content: "🏠"; }
.icon-message::before { content: "💬"; }
.icon-ai::before { content: "🤖"; }
.icon-box::before { content: "📦"; }

/* 响应式设计 */
@media (max-width: 768px) {
  .navigation {
    padding: 0 1rem;
  }
  
  .nav-menu {
    gap: 1rem;
  }
  
  .app-name {
    display: none;
  }
  
  .user-name {
    display: none;
  }
}
</style>