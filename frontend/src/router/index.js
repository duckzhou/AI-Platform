import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/chat',
    children: [
      {
        path: '/chat',
        name: 'Chat',
        component: () => import('@/views/Chat.vue'),
        meta: { title: 'AI对话', icon: 'ChatDotRound' }
      },
      {
        path: '/create',
        name: 'Create',
        component: () => import('@/views/Create.vue'),
        meta: { title: 'AI创作', icon: 'Magic' }
      },
      {
        path: '/tasks',
        name: 'Tasks',
        component: () => import('@/views/Tasks.vue'),
        meta: { title: '任务管理', icon: 'List' }
      },
      {
        path: '/materials',
        name: 'Materials',
        component: () => import('@/views/Materials.vue'),
        meta: { title: '素材管理', icon: 'Picture' }
      },
      {
        path: '/quota',
        name: 'Quota',
        component: () => import('@/views/Quota.vue'),
        meta: { title: '额度中心', icon: 'Coin' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', icon: 'User' }
      },
      {
        path: '/about',
        name: 'About',
        component: () => import('@/views/About.vue'),
        meta: { title: '关于我们', icon: 'InfoFilled' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (!to.meta.public && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
