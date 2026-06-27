import type {
  UserInfo,
  SportsEvent,
  Registration,
  Score,
  Notice,
} from '@/types'

export const seedUsers: UserInfo[] = [
  { id: 'T001', name: '王建国', role: 'teacher', account: 'T001', password: '123456', title: '体育教研组组长' },
  { id: 'T002', name: '李梅', role: 'teacher', account: 'T002', password: '123456', title: '赛事协调员' },
  { id: 'S001', name: '张明', role: 'student', account: 'S001', password: '123456', class: '高三(1)班', grade: '高三' },
  { id: 'S002', name: '李华', role: 'student', account: 'S002', password: '123456', class: '高三(1)班', grade: '高三' },
  { id: 'S003', name: '王芳', role: 'student', account: 'S003', password: '123456', class: '高三(2)班', grade: '高三' },
  { id: 'S004', name: '刘洋', role: 'student', account: 'S004', password: '123456', class: '高三(2)班', grade: '高三' },
  { id: 'S005', name: '陈静', role: 'student', account: 'S005', password: '123456', class: '高三(3)班', grade: '高三' },
  { id: 'S006', name: '赵磊', role: 'student', account: 'S006', password: '123456', class: '高三(3)班', grade: '高三' },
  { id: 'S007', name: '孙悦', role: 'student', account: 'S007', password: '123456', class: '高三(1)班', grade: '高三' },
  { id: 'S008', name: '周婷', role: 'student', account: 'S008', password: '123456', class: '高三(2)班', grade: '高三' },
]

export const seedEvents: SportsEvent[] = [
  { id: 'E001', name: '男子100米', category: 'track', gender: 'male', quota: 8, registeredCount: 6, venue: '主田径场', scheduledTime: '2026-06-27 09:00', record: '11.20', status: 'open', unit: '秒', group: 'A', description: '短跑冲刺项目' },
  { id: 'E002', name: '女子100米', category: 'track', gender: 'female', quota: 8, registeredCount: 5, venue: '主田径场', scheduledTime: '2026-06-27 09:30', record: '12.45', status: 'open', unit: '秒', group: 'A' },
  { id: 'E003', name: '男子跳远', category: 'field', gender: 'male', quota: 6, registeredCount: 6, venue: '跳远沙坑', scheduledTime: '2026-06-27 10:00', record: '6.45m', status: 'open', unit: '米', group: 'B' },
  { id: 'E004', name: '女子跳远', category: 'field', gender: 'female', quota: 6, registeredCount: 4, venue: '跳远沙坑', scheduledTime: '2026-06-27 10:30', record: '5.10m', status: 'open', unit: '米', group: 'B' },
  { id: 'E005', name: '男子1500米', category: 'track', gender: 'male', quota: 10, registeredCount: 7, venue: '主田径场', scheduledTime: '2026-06-27 14:00', record: '4:25.00', status: 'open', unit: '分:秒', group: 'C' },
  { id: 'E006', name: '女子800米', category: 'track', gender: 'female', quota: 10, registeredCount: 8, venue: '主田径场', scheduledTime: '2026-06-27 14:30', record: '2:30.00', status: 'open', unit: '分:秒', group: 'C' },
  { id: 'E007', name: '篮球3v3', category: 'ball', gender: 'mixed', quota: 12, registeredCount: 9, venue: '篮球馆', scheduledTime: '2026-06-27 15:00', status: 'open', unit: '分', group: 'D' },
  { id: 'E008', name: '拔河比赛', category: 'fun', gender: 'mixed', quota: 20, registeredCount: 16, venue: '中央广场', scheduledTime: '2026-06-27 16:00', status: 'open', unit: '局', group: 'E' },
  { id: 'E009', name: '男子铅球', category: 'field', gender: 'male', quota: 6, registeredCount: 5, venue: '铅球场地', scheduledTime: '2026-06-28 09:00', record: '12.30m', status: 'open', unit: '米', group: 'F' },
  { id: 'E010', name: '趣味接力', category: 'fun', gender: 'mixed', quota: 16, registeredCount: 12, venue: '主田径场', scheduledTime: '2026-06-28 10:00', status: 'open', unit: '分:秒', group: 'G' },
]

export const seedRegistrations: Registration[] = [
  { id: 'R001', studentId: 'S001', studentName: '张明', class: '高三(1)班', grade: '高三', eventId: 'E001', eventName: '男子100米', scheduledTime: '2026-06-27 09:00', venue: '主田径场', status: 'approved', createdAt: '2026-06-20 10:00' },
  { id: 'R002', studentId: 'S001', studentName: '张明', class: '高三(1)班', grade: '高三', eventId: 'E003', eventName: '男子跳远', scheduledTime: '2026-06-27 10:00', venue: '跳远沙坑', status: 'approved', createdAt: '2026-06-20 10:05' },
  { id: 'R003', studentId: 'S002', studentName: '李华', class: '高三(1)班', grade: '高三', eventId: 'E001', eventName: '男子100米', scheduledTime: '2026-06-27 09:00', venue: '主田径场', status: 'pending', createdAt: '2026-06-21 09:00' },
  { id: 'R004', studentId: 'S003', studentName: '王芳', class: '高三(2)班', grade: '高三', eventId: 'E002', eventName: '女子100米', scheduledTime: '2026-06-27 09:30', venue: '主田径场', status: 'pending', createdAt: '2026-06-21 09:30' },
  { id: 'R005', studentId: 'S004', studentName: '刘洋', class: '高三(2)班', grade: '高三', eventId: 'E003', eventName: '男子跳远', scheduledTime: '2026-06-27 10:00', venue: '跳远沙坑', status: 'approved', createdAt: '2026-06-20 11:00' },
  { id: 'R006', studentId: 'S005', studentName: '陈静', class: '高三(3)班', grade: '高三', eventId: 'E004', eventName: '女子跳远', scheduledTime: '2026-06-27 10:30', venue: '跳远沙坑', status: 'approved', createdAt: '2026-06-20 12:00' },
  { id: 'R007', studentId: 'S006', studentName: '赵磊', class: '高三(3)班', grade: '高三', eventId: 'E005', eventName: '男子1500米', scheduledTime: '2026-06-27 14:00', venue: '主田径场', status: 'pending', createdAt: '2026-06-21 14:00' },
  { id: 'R008', studentId: 'S007', studentName: '孙悦', class: '高三(1)班', grade: '高三', eventId: 'E006', eventName: '女子800米', scheduledTime: '2026-06-27 14:30', venue: '主田径场', status: 'approved', createdAt: '2026-06-20 15:00' },
  { id: 'R009', studentId: 'S008', studentName: '周婷', class: '高三(2)班', grade: '高三', eventId: 'E006', eventName: '女子800米', scheduledTime: '2026-06-27 14:30', venue: '主田径场', status: 'pending', createdAt: '2026-06-21 16:00' },
  { id: 'R010', studentId: 'S002', studentName: '李华', class: '高三(1)班', grade: '高三', eventId: 'E007', eventName: '篮球3v3', scheduledTime: '2026-06-27 15:00', venue: '篮球馆', status: 'approved', createdAt: '2026-06-20 16:00' },
]

export const seedScores: Score[] = [
  { id: 'SC001', eventId: 'E001', eventName: '男子100米', category: 'track', studentId: 'S001', studentName: '张明', class: '高三(1)班', grade: '高三', result: '11.05', rank: 1, isRecordBroken: true, medal: 'gold', unit: '秒', publishedAt: '2026-06-27 09:20' },
  { id: 'SC002', eventId: 'E001', eventName: '男子100米', category: 'track', studentId: 'S002', studentName: '李华', class: '高三(1)班', grade: '高三', result: '11.45', rank: 2, isRecordBroken: false, medal: 'silver', unit: '秒', publishedAt: '2026-06-27 09:20' },
  { id: 'SC003', eventId: 'E003', eventName: '男子跳远', category: 'field', studentId: 'S001', studentName: '张明', class: '高三(1)班', grade: '高三', result: '6.50', rank: 1, isRecordBroken: true, medal: 'gold', unit: '米', publishedAt: '2026-06-27 10:20' },
  { id: 'SC004', eventId: 'E003', eventName: '男子跳远', category: 'field', studentId: 'S004', studentName: '刘洋', class: '高三(2)班', grade: '高三', result: '6.20', rank: 2, isRecordBroken: false, medal: 'silver', unit: '米', publishedAt: '2026-06-27 10:20' },
]

export const seedNotices: Notice[] = [
  { id: 'N001', title: '2026年校园运动会开幕通知', content: '亲爱的同学们，2026年校园运动会将于6月27日正式开幕，请各班级做好赛前准备，准时到达比赛场地。预祝各位运动员取得优异成绩！', type: 'system', createdAt: '2026-06-25 09:00', read: false, level: 'info' },
  { id: 'N002', title: '男子100米比赛成绩公布', content: '恭喜张明同学以11.05秒打破校纪录！详细成绩请前往成绩查询页面查看。', type: 'system', createdAt: '2026-06-27 09:25', read: false, level: 'success' },
  { id: 'N003', title: '报名审批通过', content: '您报名的"男子跳远"项目已审批通过，请于6月27日10:00前往跳远沙坑参加比赛。', type: 'personal', target: 'S001', targetName: '张明', createdAt: '2026-06-20 10:10', read: false, level: 'success' },
  { id: 'N004', title: '赛程调整提醒', content: '因天气原因，原定6月27日14:00的男子1500米调整至15:30进行，请相关选手注意。', type: 'system', createdAt: '2026-06-26 16:00', read: true, level: 'warning' },
  { id: 'N005', title: '颁奖仪式通知', content: '今日17:00在中央广场举行颁奖仪式，请获奖选手准时参加。', type: 'system', createdAt: '2026-06-27 12:00', read: false, level: 'info' },
]
