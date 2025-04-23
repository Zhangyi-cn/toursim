import type { Attraction } from './attraction'
import type { Guide } from './guide'
import type { Note } from './note'

// 推荐项目的基础接口
export interface RecommendationBase {
  id: number
  score: number
  reason: string
  view_count: number
  collection_count: number
  comment_count: number
  cover_image: string
}

// 景点推荐项
export interface AttractionRecommendation extends RecommendationBase, Omit<Attraction, keyof RecommendationBase> {}

// 攻略推荐项
export interface GuideRecommendation extends RecommendationBase, Omit<Guide, keyof RecommendationBase> {}

// 游记推荐项
export interface NoteRecommendation extends RecommendationBase, Omit<Note, keyof RecommendationBase> {}

// API响应类型
export interface RecommendationResponse {
  attractions: AttractionRecommendation[]
  guides: GuideRecommendation[]
  notes: NoteRecommendation[]
}

// API请求参数
export interface RecommendationParams {
  type?: 'attraction' | 'guide' | 'note'
  limit?: number
} 