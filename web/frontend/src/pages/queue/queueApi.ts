import { api } from '../../api/client'

export interface QueueEnterResult {
  queueToken: string
  position: number
  estimatedWaitSeconds: number
}

export interface QueueStatusResult {
  status: string
  position: number
  estimatedWaitSeconds: number
  entryTicket: string | null
}

export const queueApi = {
  enter: (performanceId: number, scheduleId: number) =>
    api.post<QueueEnterResult>('/queue/enter', { performanceId, scheduleId }),
  status: (queueToken: string) => api.get<QueueStatusResult>(`/queue/${queueToken}/status`),
}
