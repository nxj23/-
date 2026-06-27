import { mockDb } from './mock'
import type { Notice } from '@/types'

export const noticeApi = {
  list: () => mockDb.listNotices(),
  create: (payload: Omit<Notice, 'id' | 'createdAt' | 'read'>) =>
    mockDb.createNotice(payload),
  remove: (id: string) => mockDb.deleteNotice(id),
  markRead: (id: string) => mockDb.markNoticeRead(id),
  markAllRead: (target?: string) => mockDb.markAllRead(target),
}
