interface Props {
  children: React.ReactNode
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  variant?: 'primary' | 'error' | 'warning' | 'success'
}

export function PixelButton({ children, onClick, type = 'button', disabled, variant = 'primary' }: Props) {
  return (
    <button
      className={`nes-btn is-${variant}`}
      onClick={onClick}
      type={type}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
