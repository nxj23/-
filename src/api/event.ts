import { mockDb } from './mock'
import type { SportsEvent } from '@/types'

export const eventApi = {
  list: () => mockDb.listEvents(),
  create: (payload: Omit<SportsEvent, 'id' | 'registeredCount'>) =>
    mockDb.createEvent(payload),
  update: (id: string, patch: Partial<SportsEvent>) =>
    mockDb.updateEvent(id, patch),
  remove: (id: string) => mockDb.deleteEvent(id),
}
