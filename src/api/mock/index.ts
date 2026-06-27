import type {
  UserInfo,
  SportsEvent,
  Registration,
  Score,
  Notice,
  ClassScore,
  MedalStat,
} from '@/types'
import { storage } from '@/utils/storage'
import {
  seedUsers,
  seedEvents,
  seedRegistrations,
  seedScores,
  seedNotices,
} from './seed'

const KEYS = {
  users: 'users',
  events: 'events',
  registrations: 'registrations',
  scores: 'scores',
  notices: 'notices',
  currentUser: 'currentUser',
} as const

function ensureSeed(): void {
  if (!storage.has(KEYS.users)) storage.set(KEYS.users, seedUsers)
  if (!storage.has(KEYS.events)) storage.set(KEYS.events, seedEvents)
  if (!storage.has(KEYS.registrations)) storage.set(KEYS.registrations, seedRegistrations)
  if (!storage.has(KEYS.scores)) storage.set(KEYS.scores, seedScores)
  if (!storage.has(KEYS.notices)) storage.set(KEYS.notices, seedNotices)
}

ensureSeed()

function delay<T>(value: T, ms = 120): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

function genId(prefix: string): string {
  return prefix + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
}

export const mockDb = {
  // ---- auth ----
  login(account: string, password: string): Promise<UserInfo | null> {
    const users = storage.get<UserInfo[]>(KEYS.users, [])
    const user = users.find(
      (u) => u.account === account && u.password === password,
    )
    if (user) {
      const { password: _pw, ...safe } = user
      storage.set(KEYS.currentUser, safe)
      return delay(safe as UserInfo)
    }
    return delay(null)
  },
  logout(): Promise<void> {
    storage.remove(KEYS.currentUser)
    return delay(undefined)
  },
  currentUser(): UserInfo | null {
    return storage.get<UserInfo | null>(KEYS.currentUser, null)
  },
  getUsers(): Promise<UserInfo[]> {
    return delay(storage.get<UserInfo[]>(KEYS.users, []))
  },

  // ---- events ----
  listEvents(): Promise<SportsEvent[]> {
    return delay(storage.get<SportsEvent[]>(KEYS.events, []))
  },
  createEvent(payload: Omit<SportsEvent, 'id' | 'registeredCount'>): Promise<SportsEvent> {
    const events = storage.get<SportsEvent[]>(KEYS.events, [])
    const event: SportsEvent = { ...payload, id: genId('E'), registeredCount: 0 }
    events.push(event)
    storage.set(KEYS.events, events)
    return delay(event)
  },
  updateEvent(id: string, patch: Partial<SportsEvent>): Promise<SportsEvent | null> {
    const events = storage.get<SportsEvent[]>(KEYS.events, [])
    const idx = events.findIndex((e) => e.id === id)
    if (idx === -1) return delay(null)
    events[idx] = { ...events[idx], ...patch }
    storage.set(KEYS.events, events)
    return delay(events[idx])
  },
  deleteEvent(id: string): Promise<boolean> {
    const events = storage.get<SportsEvent[]>(KEYS.events, [])
    const next = events.filter((e) => e.id !== id)
    storage.set(KEYS.events, next)
    return delay(next.length !== events.length)
  },

  // ---- registrations ----
  listRegistrations(): Promise<Registration[]> {
    return delay(storage.get<Registration[]>(KEYS.registrations, []))
  },
  createRegistration(payload: Omit<Registration, 'id' | 'createdAt' | 'status'>): Promise<{ ok: boolean; registration?: Registration; conflict?: string }> {
    const regs = storage.get<Registration[]>(KEYS.registrations, [])
    const events = storage.get<SportsEvent[]>(KEYS.events, [])

    const event = events.find((e) => e.id === payload.eventId)
    if (!event) return delay({ ok: false, conflict: '项目不存在' })

    if (event.quota <= event.registeredCount) {
      return delay({ ok: false, conflict: '名额已满' })
    }

    const conflict = regs.find(
      (r) =>
        r.studentId === payload.studentId &&
        r.eventId === payload.eventId &&
        r.status !== 'rejected',
    )
    if (conflict) {
      return delay({ ok: false, conflict: '已报名该项目' })
    }

    const timeConflict = regs.find(
      (r) =>
        r.studentId === payload.studentId &&
        r.scheduledTime === payload.scheduledTime &&
        r.status === 'approved',
    )
    if (timeConflict) {
      return delay({ ok: false, conflict: `与已批准项目「${timeConflict.eventName}」时间冲突` })
    }

    const registration: Registration = {
      ...payload,
      id: genId('R'),
      status: 'pending',
      createdAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
    }
    regs.push(registration)
    storage.set(KEYS.registrations, regs)

    event.registeredCount += 1
    storage.set(KEYS.events, events)

    return delay({ ok: true, registration })
  },
  updateRegistrationStatus(id: string, status: 'approved' | 'rejected'): Promise<Registration | null> {
    const regs = storage.get<Registration[]>(KEYS.registrations, [])
    const idx = regs.findIndex((r) => r.id === id)
    if (idx === -1) return delay(null)
    regs[idx].status = status
    storage.set(KEYS.registrations, regs)

    if (status === 'rejected') {
      const events = storage.get<SportsEvent[]>(KEYS.events, [])
      const ev = events.find((e) => e.id === regs[idx].eventId)
      if (ev && ev.registeredCount > 0) {
        ev.registeredCount -= 1
        storage.set(KEYS.events, events)
      }
    }

    if (status === 'approved') {
      const events = storage.get<SportsEvent[]>(KEYS.events, [])
      const ev = events.find((e) => e.id === regs[idx].eventId)
      const user = storage.get<UserInfo[]>(KEYS.users, []).find((u) => u.id === regs[idx].studentId)
      if (ev && user) {
        const notices = storage.get<Notice[]>(KEYS.notices, [])
        notices.unshift({
          id: genId('N'),
          title: '报名审批通过',
          content: `您报名的「${regs[idx].eventName}」项目已审批通过，请于 ${regs[idx].scheduledTime} 前往 ${regs[idx].venue} 参加比赛。`,
          type: 'personal',
          target: user.id,
          targetName: user.name,
          createdAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
          read: false,
          level: 'success',
        })
        storage.set(KEYS.notices, notices)
      }
    }
    return delay(regs[idx])
  },
  deleteRegistration(id: string): Promise<boolean> {
    const regs = storage.get<Registration[]>(KEYS.registrations, [])
    const target = regs.find((r) => r.id === id)
    const next = regs.filter((r) => r.id !== id)
    storage.set(KEYS.registrations, next)
    if (target && target.status !== 'rejected') {
      const events = storage.get<SportsEvent[]>(KEYS.events, [])
      const ev = events.find((e) => e.id === target.eventId)
      if (ev && ev.registeredCount > 0) {
        ev.registeredCount -= 1
        storage.set(KEYS.events, events)
      }
    }
    return delay(next.length !== regs.length)
  },

  // ---- scores ----
  listScores(): Promise<Score[]> {
    return delay(storage.get<Score[]>(KEYS.scores, []))
  },
  saveScores(payload: Score[]): Promise<Score[]> {
    const scores = storage.get<Score[]>(KEYS.scores, [])
    const eventIds = new Set(payload.map((p) => p.eventId))
    const remaining = scores.filter((s) => !eventIds.has(s.eventId))
    const merged = [...payload, ...remaining]
    storage.set(KEYS.scores, merged)

    const events = storage.get<SportsEvent[]>(KEYS.events, [])
    eventIds.forEach((eid) => {
      const ev = events.find((e) => e.id === eid)
      if (ev) ev.status = 'finished'
    })
    storage.set(KEYS.events, events)
    return delay(payload)
  },
  classScoreBoard(): Promise<ClassScore[]> {
    const scores = storage.get<Score[]>(KEYS.scores, [])
    const map = new Map<string, ClassScore>()
    scores.forEach((s) => {
      if (!s.medal) return
      const key = `${s.grade}|${s.class}`
      if (!map.has(key)) {
        map.set(key, { class: s.class, grade: s.grade, gold: 0, silver: 0, bronze: 0, total: 0 })
      }
      const entry = map.get(key)!
      if (s.medal === 'gold') entry.gold += 1
      if (s.medal === 'silver') entry.silver += 1
      if (s.medal === 'bronze') entry.bronze += 1
      entry.total = entry.gold * 3 + entry.silver * 2 + entry.bronze * 1
    })
    return delay(Array.from(map.values()).sort((a, b) => b.total - a.total))
  },
  medalBoard(): Promise<MedalStat[]> {
    const scores = storage.get<Score[]>(KEYS.scores, [])
    const map = new Map<string, MedalStat>()
    scores.forEach((s) => {
      if (!s.medal) return
      if (!map.has(s.studentId)) {
        map.set(s.studentId, {
          studentId: s.studentId,
          studentName: s.studentName,
          class: s.class,
          gold: 0, silver: 0, bronze: 0, total: 0,
        })
      }
      const entry = map.get(s.studentId)!
      if (s.medal === 'gold') entry.gold += 1
      if (s.medal === 'silver') entry.silver += 1
      if (s.medal === 'bronze') entry.bronze += 1
      entry.total = entry.gold + entry.silver + entry.bronze
    })
    return delay(Array.from(map.values()).sort((a, b) => {
      if (b.gold !== a.gold) return b.gold - a.gold
      if (b.silver !== a.silver) return b.silver - a.silver
      return b.bronze - a.bronze
    }))
  },

  // ---- notices ----
  listNotices(): Promise<Notice[]> {
    return delay(storage.get<Notice[]>(KEYS.notices, []))
  },
  createNotice(payload: Omit<Notice, 'id' | 'createdAt' | 'read'>): Promise<Notice> {
    const notices = storage.get<Notice[]>(KEYS.notices, [])
    const notice: Notice = {
      ...payload,
      id: genId('N'),
      createdAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
      read: false,
    }
    notices.unshift(notice)
    storage.set(KEYS.notices, notices)
    return delay(notice)
  },
  deleteNotice(id: string): Promise<boolean> {
    const notices = storage.get<Notice[]>(KEYS.notices, [])
    const next = notices.filter((n) => n.id !== id)
    storage.set(KEYS.notices, next)
    return delay(next.length !== notices.length)
  },
  markNoticeRead(id: string): Promise<void> {
    const notices = storage.get<Notice[]>(KEYS.notices, [])
    const idx = notices.findIndex((n) => n.id === id)
    if (idx !== -1) {
      notices[idx].read = true
      storage.set(KEYS.notices, notices)
    }
    return delay(undefined)
  },
  markAllRead(target?: string): Promise<void> {
    const notices = storage.get<Notice[]>(KEYS.notices, [])
    notices.forEach((n) => {
      if (n.type === 'system') n.read = true
      else if (target && n.target === target) n.read = true
    })
    storage.set(KEYS.notices, notices)
    return delay(undefined)
  },

  resetAll(): void {
    Object.values(KEYS).forEach((k) => storage.remove(k))
    ensureSeed()
  },
}
