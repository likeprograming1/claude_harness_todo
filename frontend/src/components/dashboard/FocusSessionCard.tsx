import styles from './FocusSessionCard.module.css'

export function FocusSessionCard() {
  return (
    <div className={styles.card}>
      <div className={styles.iconWrap}>
        <TimerIcon />
      </div>
      <div className={styles.body}>
        <p className={styles.subtitle}>다음 세션</p>
        <p className={styles.title}>딥 워크</p>
      </div>
      <p className={styles.time}>15분 후 시작</p>
    </div>
  )
}

function TimerIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="13" r="8" stroke="white" strokeWidth="1.5" />
      <path d="M12 9v4l2.5 2.5" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M9 3h6" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M12 3v2" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}
