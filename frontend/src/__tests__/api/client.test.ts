import { get, post, ApiError } from '@/lib/api/client'

const BASE = 'http://localhost:8000/api/v1'

function mockFetch(status: number, body: unknown) {
  global.fetch = jest.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  } as Response)
}

describe('API client', () => {
  afterEach(() => jest.restoreAllMocks())

  describe('get()', () => {
    it('올바른 URL로 GET 요청을 보낸다', async () => {
      mockFetch(200, [])
      await get('/tasks')
      expect(fetch).toHaveBeenCalledWith(
        `${BASE}/tasks`,
        expect.objectContaining({ headers: { 'Content-Type': 'application/json' } })
      )
    })

    it('쿼리 파라미터를 URL에 추가한다', async () => {
      mockFetch(200, [])
      await get('/tasks', { date: '2024-10-24' })
      expect(fetch).toHaveBeenCalledWith(
        `${BASE}/tasks?date=2024-10-24`,
        expect.anything()
      )
    })

    it('응답 JSON을 반환한다', async () => {
      const data = [{ id: '1', title: '테스트' }]
      mockFetch(200, data)
      const result = await get('/tasks')
      expect(result).toEqual(data)
    })
  })

  describe('post()', () => {
    it('POST 메서드와 JSON body로 요청한다', async () => {
      const payload = { title: '새 할 일' }
      mockFetch(201, { id: '2', ...payload })
      await post('/tasks', payload)
      expect(fetch).toHaveBeenCalledWith(
        `${BASE}/tasks`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(payload),
        })
      )
    })
  })

  describe('ApiError', () => {
    it('4xx 응답에서 ApiError를 던진다', async () => {
      mockFetch(404, { detail: 'Not found' })
      await expect(get('/tasks/invalid')).rejects.toBeInstanceOf(ApiError)
    })

    it('ApiError에 status 코드가 포함된다', async () => {
      mockFetch(422, { detail: 'Validation error' })
      try {
        await get('/tasks/invalid')
      } catch (e) {
        expect((e as ApiError).status).toBe(422)
      }
    })

    it('5xx 응답에서도 ApiError를 던진다', async () => {
      mockFetch(500, { detail: 'Server error' })
      await expect(get('/health')).rejects.toBeInstanceOf(ApiError)
    })
  })
})
