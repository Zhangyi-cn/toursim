import dayjs from 'dayjs'

export function formatDate(date: string | Date, format = 'YYYY-MM-DD HH:mm:ss'): string {
  return dayjs(date).format(format)
}

export function formatDateRange(start: string | Date, end: string | Date): string {
  return `${formatDate(start, 'YYYY-MM-DD')} 至 ${formatDate(end, 'YYYY-MM-DD')}`
}

export function isDateBefore(date: string | Date, compareDate: string | Date = new Date()): boolean {
  return dayjs(date).isBefore(compareDate)
}

export function isDateAfter(date: string | Date, compareDate: string | Date = new Date()): boolean {
  return dayjs(date).isAfter(compareDate)
}

export function addDays(date: string | Date, days: number): Date {
  return dayjs(date).add(days, 'day').toDate()
}

export function subtractDays(date: string | Date, days: number): Date {
  return dayjs(date).subtract(days, 'day').toDate()
}

export function getStartOfDay(date: string | Date = new Date()): Date {
  return dayjs(date).startOf('day').toDate()
}

export function getEndOfDay(date: string | Date = new Date()): Date {
  return dayjs(date).endOf('day').toDate()
}

export function getStartOfMonth(date: string | Date = new Date()): Date {
  return dayjs(date).startOf('month').toDate()
}

export function getEndOfMonth(date: string | Date = new Date()): Date {
  return dayjs(date).endOf('month').toDate()
}

export function getDaysBetween(start: string | Date, end: string | Date): number {
  return dayjs(end).diff(start, 'day')
}

export function formatRelativeTime(date: string | Date): string {
  const now = dayjs()
  const target = dayjs(date)
  const diffMinutes = now.diff(target, 'minute')
  
  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  
  const diffHours = now.diff(target, 'hour')
  if (diffHours < 24) return `${diffHours}小时前`
  
  const diffDays = now.diff(target, 'day')
  if (diffDays < 30) return `${diffDays}天前`
  
  const diffMonths = now.diff(target, 'month')
  if (diffMonths < 12) return `${diffMonths}个月前`
  
  return formatDate(date, 'YYYY-MM-DD')
} 