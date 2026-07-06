import { render, screen } from '@testing-library/react'
import { BottomNav } from '@/components/layout/BottomNav'

const mockPush = jest.fn()

jest.mock('next/router', () => ({
  useRouter: () => ({ pathname: '/', push: mockPush }),
}))

jest.mock('next/link', () => {
  const Link = ({ href, children, className, ...rest }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
    <a href={href} className={className} {...rest}>{children}</a>
  )
  Link.displayName = 'Link'
  return Link
})

describe('BottomNav', () => {
  it('4개의 탭을 렌더링한다', () => {
    render(<BottomNav />)
    expect(screen.getByText('할 일')).toBeInTheDocument()
    expect(screen.getByText('통계')).toBeInTheDocument()
    expect(screen.getByText('캘린더')).toBeInTheDocument()
    expect(screen.getByText('설정')).toBeInTheDocument()
  })

  it('현재 경로(/)에서 "할 일" 탭이 active 상태다', () => {
    render(<BottomNav />)
    const taskLink = screen.getByRole('link', { name: /할 일/ })
    expect(taskLink).toHaveAttribute('aria-current', 'page')
  })

  it('"통계" 탭은 active 상태가 아니다', () => {
    render(<BottomNav />)
    const statsLink = screen.getByRole('link', { name: /통계/ })
    expect(statsLink).not.toHaveAttribute('aria-current', 'page')
  })

  it('미구현 탭(캘린더/설정)은 aria-disabled 처리된다', () => {
    render(<BottomNav />)
    const disabled = screen.getAllByRole('generic').filter(
      (el) => el.getAttribute('aria-disabled') === 'true'
    )
    expect(disabled.length).toBe(2)
  })
})
