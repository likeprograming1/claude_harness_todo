import { getTasks, toggleDone, createTask } from '@/lib/api/tasks'

const BASE = 'http://localhost:8000/api/v1'

const mockTask = {
  id: 'abc123',
  task_id: 'T001',
  title: '테스트 할 일',
  due_date: null,
  due_time: null,
  category_id: null,
  priority: 'medium' as const,
  is_done: false,
  notes: null,
  created_at: '2024-10-24T10:00:00',
}

function mockFetch(body: unknown, status = 200) {
  global.fetch = jest.fn().mockResolvedValue({
    ok: status < 400,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  } as Response)
}

describe('tasks API', () => {
  afterEach(() => jest.restoreAllMocks())

  describe('getTasks()', () => {
    it('파라미터 없이 /tasks를 호출한다', async () => {
      mockFetch([mockTask])
      await getTasks()
      expect(fetch).toHaveBeenCalledWith(`${BASE}/tasks`, expect.anything())
    })

    it('date 파라미터를 쿼리스트링으로 전달한다', async () => {
      mockFetch([mockTask])
      await getTasks({ date: '2024-10-24' })
      const url = (fetch as jest.Mock).mock.calls[0][0] as string
      expect(url).toContain('date=2024-10-24')
    })

    it('done=true 파라미터를 문자열로 전달한다', async () => {
      mockFetch([mockTask])
      await getTasks({ done: true })
      const url = (fetch as jest.Mock).mock.calls[0][0] as string
      expect(url).toContain('done=true')
    })

    it('Task 배열을 반환한다', async () => {
      mockFetch([mockTask])
      const result = await getTasks()
      expect(result).toEqual([mockTask])
    })
  })

  describe('toggleDone()', () => {
    it('PATCH /tasks/{id}/done 을 호출한다', async () => {
      mockFetch({ ...mockTask, is_done: true })
      await toggleDone('T001')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE}/tasks/T001/done`,
        expect.objectContaining({ method: 'PATCH' })
      )
    })

    it('업데이트된 Task를 반환한다', async () => {
      const updated = { ...mockTask, is_done: true }
      mockFetch(updated)
      const result = await toggleDone('T001')
      expect(result.is_done).toBe(true)
    })
  })

  describe('createTask()', () => {
    it('POST /tasks 를 호출하고 생성된 Task를 반환한다', async () => {
      const newTask = { ...mockTask, task_id: 'T002', title: '새 할 일' }
      mockFetch(newTask, 201)
      const result = await createTask({ title: '새 할 일' })
      expect(fetch).toHaveBeenCalledWith(
        `${BASE}/tasks`,
        expect.objectContaining({ method: 'POST' })
      )
      expect(result.title).toBe('새 할 일')
    })
  })
})
