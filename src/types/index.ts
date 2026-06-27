export type Role = 'teacher' | 'student'

export interface UserInfo {
  id: string
  name: string
  role: Role
  account: string
  password: string
  avatar?: string
  class?: string
  grade?: string
  title?: string
}

export type EventCategory = 'track' | 'field' | 'ball' | 'fun'
export type Gender = 'male' | 'female' | 'mixed'
export type EventStatus = 'open' | 'closed' | 'finished'

export interface SportsEvent {
  id: string
  name: string
  category: EventCategory
  gender: Gender
  quota: number
  registeredCount: number
  venue: string
  scheduledTime: string
  record?: string
  status: EventStatus
  unit: string
  description?: string
  group?: string
}

export type RegistrationStatus = 'pending' | 'approved' | 'rejected'

export interface Registration {
  id: string
  studentId: string
  studentName: string
  class: string
  grade: string
  eventId: string
  eventName: string
  scheduledTime: string
  venue: string
  status: RegistrationStatus
  createdAt: string
  conflict?: string
}

export type Medal = 'gold' | 'silver' | 'bronze'

export interface Score {
  id: string
  eventId: string
  eventName: string
  category: EventCategory
  studentId: string
  studentName: string
  class: string
  grade: string
  result: string
  rank: number
  isRecordBroken: boolean
  medal?: Medal
  unit: string
  publishedAt?: string
}

export type NoticeType = 'system' | 'personal'

export interface Notice {
  id: string
  title: string
  content: string
  type: NoticeType
  target?: string
  targetName?: string
  createdAt: string
  read: boolean
  level: 'info' | 'success' | 'warning' | 'danger'
}

export interface ClassScore {
  class: string
  grade: string
  gold: number
  silver: number
  bronze: number
  total: number
}

export interface MedalStat {
  studentId: string
  studentName: string
  class: string
  gold: number
  silver: number
  bronze: number
  total: number
}

export interface DashboardStats {
  pendingApprovals: number
  pendingScores: number
  todayEvents: number
  noticeCount: number
}
