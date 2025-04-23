import { createRouter, createWebHistory, RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/home'
      },
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/home/index.vue'),
        meta: {
          title: '首页'
        }
      },
      {
        path: 'attractions',
        name: 'Attractions',
        component: () => import('../views/attractions/index.vue'),
        meta: {
          title: '景点'
        }
      },
      {
        path: 'attractions/:id',
        name: 'AttractionDetail',
        component: () => import('../views/attractions/detail.vue'),
        meta: {
          title: '景点详情'
        }
      },
      {
        path: 'travel-guides',
        name: 'TravelGuides',
        component: () => import('../views/travel-guides/index.vue'),
        meta: {
          title: '旅游攻略'
        }
      },
      {
        path: 'travel-guides/create',
        name: 'CreateGuide',
        component: () => import('@/views/travel-guides/edit.vue'),
        meta: {
          title: '创建攻略',
          requiresAuth: true
        }
      },
      {
        path: 'travel-guides/edit/:id',
        name: 'EditGuide',
        component: () => import('@/views/travel-guides/edit.vue'),
        meta: {
          title: '编辑攻略',
          requiresAuth: true
        }
      },
      {
        path: 'travel-guides/:id',
        name: 'TravelGuideDetail',
        component: () => import('../views/travel-guides/detail.vue'),
        meta: {
          title: '攻略详情'
        }
      },
      {
        path: 'activities',
        name: 'Activities',
        component: () => import('../views/activities/index.vue'),
        meta: {
          title: '活动'
        }
      },
      {
        path: 'activity/:id',
        name: 'ActivityDetail',
        component: () => import('../views/activities/detail.vue'),
        meta: {
          title: '活动详情'
        }
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('../views/notes/index.vue'),
        meta: {
          title: '游记'
        }
      },
      {
        path: 'notes/write',
        name: 'WriteNote',
        component: () => import('../views/notes/write.vue'),
        meta: {
          title: '写游记',
          requireAuth: true
        }
      },
      {
        path: 'notes/edit/:id',
        name: 'EditNote',
        component: () => import('../views/notes/write.vue'),
        meta: {
          title: '编辑游记',
          requireAuth: true
        }
      },
      {
        path: 'note/:id',
        name: 'NoteDetail',
        component: () => import('../views/notes/detail.vue'),
        meta: {
          title: '游记详情'
        }
      },
      {
        path: 'user/settings',
        name: 'UserSettings',
        component: () => import('../views/user/settings.vue'),
        meta: { 
          title: '个人设置',
          requireAuth: true
        }
      },
      {
        path: 'user/collections',
        name: 'UserCollections',
        component: () => import('../views/user/collections.vue'),
        meta: { 
          title: '我的收藏',
          requireAuth: true
        }
      },
      {
        path: 'user/guides',
        name: 'UserGuides',
        component: () => import('../views/user/guides.vue'),
        meta: { 
          title: '我的攻略',
          requireAuth: true
        }
      },
      {
        path: 'user/orders',
        name: 'UserOrders',
        component: () => import('../views/order/index.vue'),
        meta: { 
          title: '我的订单',
          requireAuth: true
        }
      },
      {
        path: 'user/notes',
        name: 'UserNotes',
        component: () => import('../views/user/notes.vue'),
        meta: { 
          title: '我的游记',
          requireAuth: true
        }
      },
      {
        path: 'user/:id',
        name: 'UserDetail',
        component: () => import('../views/user/index.vue'),
        meta: {
          title: '用户主页'
        }
      }
    ]
  },
  {
    path: '/auth',
    component: () => import('../layout/BlankLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('../views/auth/login.vue'),
        meta: {
          title: '登录'
        }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('../views/auth/register.vue'),
        meta: {
          title: '注册'
        }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/error/404.vue'),
    meta: {
      title: '404'
    }
  }
]

// 扩展 RouteMeta 接口
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requireAuth?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to: RouteLocationNormalized, from: RouteLocationNormalized, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫
router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 旅游平台` : '旅游平台'
  
  // 需要登录的页面验证
  if (to.meta.requireAuth) {
    const token = localStorage.getItem('token')
    if (token) {
      next()
    } else {
      next({
        path: '/auth/login',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    next()
  }
})

export default router 