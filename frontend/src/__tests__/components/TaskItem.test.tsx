import { render, screen, fireEvent } from '@testing-library/react'
import { TaskItem } from '@/components/tasks/TaskItem'

describe('TaskItem', () => {
  const baseProps = {
    id: 'T001',
    title: '디자인 검토',
    is_done: false,
    onToggle: jest.fn(),
  }

  beforeEach(() => jest.clearAllMocks())

  it('제목을 렌더링한다', () => {
    render(<TaskItem {...baseProps} />)
    expect(screen.getByText('디자인 검토')).toBeInTheDocument()
  })

  it('미완료 상태: 체크박스가 비어있다', () => {
    render(<TaskItem {...baseProps} is_done={false} />)
    const btn = screen.getByRole('button', { name: '완료' })
    expect(btn).toHaveAttribute('aria-pressed', 'false')
  })

  it('완료 상태: 체크 아이콘이 보이고 aria-pressed가 true다', () => {
    render(<TaskItem {...baseProps} is_done={true} />)
    const btn = screen.getByRole('button', { name: '완료 취소' })
    expect(btn).toHaveAttribute('aria-pressed', 'true')
  })

  it('체크박스 클릭 시 onToggle이 id와 함께 호출된다', () => {
    const onToggle = jest.fn()
    render(<TaskItem {...baseProps} onToggle={onToggle} />)
    fireEvent.click(screen.getByRole('button', { name: '완료' }))
    expect(onToggle).toHaveBeenCalledTimes(1)
    expect(onToggle).toHaveBeenCalledWith('T001')
  })

  it('category가 있으면 뱃지를 렌더링한다', () => {
    render(
      <TaskItem
        {...baseProps}
        category={{ id: 'cat_work', name: '업무', color: '#4A6FFF' }}
      />
    )
    expect(screen.getByText('업무')).toBeInTheDocument()
  })

  it('category가 없으면 뱃지를 렌더링하지 않는다', () => {
    render(<TaskItem {...baseProps} />)
    expect(screen.queryByText('업무')).not.toBeInTheDocument()
  })
})
