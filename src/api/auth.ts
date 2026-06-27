import { mockDb } from './mock'
import type { UserInfo } from '@/types'

export const authApi = {
  login: (account: string, password: string) => mockDb.login(account, password),
  logout: () => mockDb.logout(),
  currentUser: (): UserInfo | null => mockDb.currentUser(),
  getUsers: () => mockDb.getUsers(),
}
