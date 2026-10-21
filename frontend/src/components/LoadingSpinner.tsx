import clsx from 'clsx'

interface Props {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export default function LoadingSpinner({ size = 'md', className }: Props) {
  const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-16 h-16' }
  return (
    <div className={clsx('animate-spin rounded-full border-2 border-navy-700 border-t-navy-400', sizes[size], className)} />
  )
}
