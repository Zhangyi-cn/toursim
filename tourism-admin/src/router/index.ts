import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录',
      hidden: true
    }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/content/notes',
    children: [
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: {
          title: '个人资料',
          hidden: true
        }
      }
    ]
  },
  {
    path: '/attractions',
    component: Layout,
    redirect: '/attractions/list',
    meta: {
      title: '景点管理',
      icon: 'Location'
    },
    children: [
      {
        path: 'list',
        name: 'AttractionList',
        component: () => import('@/views/attractions/list.vue'),
        meta: {
          title: '景点列表'
        }
      },
      {
        path: 'categories',
        name: 'AttractionCategories',
        component: () => import('@/views/attractions/categories.vue'),
        meta: {
          title: '分类管理'
        }
      }
    ]
  },
  {
    path: '/tickets',
    component: Layout,
    redirect: '/tickets/list',
    meta: {
      title: '门票管理',
      icon: 'Ticket'
    },
    children: [
      {
        path: 'list',
        name: 'TicketList',
        component: () => import('@/views/tickets/list.vue'),
        meta: {
          title: '门票列表'
        }
      }
    ]
  },
  {
    path: '/guides',
    component: Layout,
    redirect: '/guides/list',
    meta: {
      title: '攻略管理',
      icon: 'Notebook'
    },
    children: [
      {
        path: 'list',
        name: 'GuideList',
        component: () => import('@/views/guides/list.vue'),
        meta: {
          title: '攻略列表'
        }
      },
      {
        path: 'categories',
        name: 'GuideCategories',
        component: () => import('@/views/guides/categories.vue'),
        meta: {
          title: '分类管理'
        }
      }
    ]
  },
  {
    path: '/orders',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Orders',
        component: () => import('@/views/orders/index.vue'),
        meta: {
          title: '订单管理',
          icon: 'List'
        }
      }
    ]
  },
  {
    path: '/content',
    component: Layout,
    redirect: '/content/notes',
    meta: {
      title: '内容管理',
      icon: 'Document'
    },
    children: [
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('@/views/content/notes.vue'),
        meta: {
          title: '游记管理'
        }
      },
      {
        path: 'comments',
        name: 'Comments',
        component: () => import('@/views/content/comments.vue'),
        meta: {
          title: '评论管理'
        }
      },
      {
        path: 'banners',
        name: 'Banners',
        component: () => import('@/views/content/banners.vue'),
        meta: {
          title: '轮播图管理'
        }
      }
    ]
  },
  {
    path: '/users',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Users',
        component: () => import('@/views/users/index.vue'),
        meta: {
          title: '用户管理',
          icon: 'User'
        }
      }
    ]
  },
  {
    path: '/password',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Password',
        component: () => import('@/views/profile/index.vue'),
        meta: {
          title: '修改密码',
          hidden: true
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '旅游管理系统'}`
  
  // 获取 token
  const token = localStorage.getItem('token')
  
  // 如果访问登录页且已登录，跳转到首页
  if (to.path === '/login' && token) {
    next('/')
    return
  }
  
  // 如果访问其他页面且未登录，跳转到登录页
  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }
  
  next()
})

export default router 