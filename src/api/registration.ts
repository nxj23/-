import { mockDb } from './mock'
import type { Registration } from '@/types'

export const registrationApi = {
  list: () => mockDb.listRegistrations(),
  create: (payload: Omit<Registration, 'id' | 'createdAt' | 'status'>) =>
    mockDb.createRegistration(payload),
  updateStatus: (id: string, status: 'approved' | 'rejected') =>
    mockDb.updateRegistrationStatus(id, status),
  remove: (id: string) => mockDb.deleteRegistration(id),
}
