import { ActivityStatus } from '@/types/activity'

export const ACTIVITY_STATUS_MAP: Record<ActivityStatus, string> = {
  not_started: '未开始',
  in_progress: '进行中',
  ended: '已结束'
}

export const ACTIVITY_STATUS_CLASS: Record<ActivityStatus, string> = {
  not_started: 'upcoming',
  in_progress: 'ongoing',
  ended: 'ended'
} 