import { render, screen, fireEvent } from '@testing-library/react'
import { AddTaskInput } from '@/components/tasks/AddTaskInput'

const mockPush = jest.fn()

jest.mock('next/router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

describe('AddTaskInput', () => {
  beforeEach(() => jest.clearAllMocks())

  it('"할 일 추가..." 플레이스홀더를 렌더링한다', () => {
    render(<AddTaskInput />)
    expect(screen.getByText('할 일 추가...')).toBeInTheDocument()
  })

  it('클릭 시 /tasks/new 로 이동한다', () => {
    render(<AddTaskInput />)
    fireEvent.click(screen.getByRole('button', { name: '할 일 추가' }))
    expect(mockPush).toHaveBeenCalledWith('/tasks/new')
  })
})
