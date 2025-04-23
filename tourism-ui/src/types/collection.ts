// 收藏目标类型
export type CollectionTargetType = 'attraction' | 'guide' | 'note'

// 收藏目标信息
export interface CollectionTarget {
  id: number
  title: string
  cover: string
  type: CollectionTargetType
}

// 收藏记录
export interface Collection {
  id: number
  user_id: number
  target_type: CollectionTargetType
  target_id: number
  created_at: string
  target: CollectionTarget
}

// 分页信息
export interface CollectionPagination {
  total: number
  pages: number
  page: number
  per_page: number
}

// 收藏列表响应
export interface CollectionResponse {
  code: number
  msg: string
  data: {
    items: Collection[]
    total: number
    pages: number
    page: number
    per_page: number
  }
} 