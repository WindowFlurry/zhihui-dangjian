import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import PersonalHome from '../views/PersonalHome.vue'
import KnowledgeBaseHome from '../views/KnowledgeBaseHome.vue'
import KnowledgeBaseDetail from '../views/KnowledgeBaseDetail.vue'
import PreLogin from '../views/PreLogin.vue'
import ResetPassword from '../views/ResetPassword.vue'
import EditProfile from '../views/EditProfile.vue'
import AccountSettings from '../views/AccountSettings.vue'

// 双击打开（file://）时用 hash 路由，普通开发/部署仍用 history 路由
const isFileProtocol = typeof window !== 'undefined' && window.location.protocol === 'file:'

const router = createRouter({
  history: isFileProtocol ? createWebHashHistory() : createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'prelogin',
      component: PreLogin
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPassword
    },
    {
      path: '/home',
      name: 'home-page',
      component: Home,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/personal-home',
      name: 'personal-home',
      component: PersonalHome,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/knowledge-base-home',
      name: 'knowledge-base-home',
      component: KnowledgeBaseHome,
      meta: {
        requiresAuth: true
      }
    },
    // 404路由处理未匹配的路径，如'/my/order'
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: Home,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/edit-profile',
      name: 'edit-profile',
      component: EditProfile,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/account-settings',
      name: 'account-settings',
      component: AccountSettings,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/knowledge-base-detail/:id',
      name: 'knowledge-base-detail',
      component: KnowledgeBaseDetail,
      meta: {
        requiresAuth: true
      }
    }
  ]
})

// 全局路由守卫 不懂不懂
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    // 临时禁用登录验证，用于测试优化后的界面
    // const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
    // if (isLoggedIn) {
    //   next()
    // } else {
    //   next('/login')
    // }
    // 直接允许访问所有页面
    next()
  } else {
    next()
  }
})

export default router