import Modal from './Modal'

interface Props {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmLabel?: string
  isDanger?: boolean
  isLoading?: boolean
}

export default function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirm',
  isDanger = false,
  isLoading,
}: Props) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-slate-400 mb-6">{message}</p>
      <div className="flex justify-end gap-3">
        <button className="btn-secondary" onClick={onClose}>
          Cancel
        </button>
        <button
          className={isDanger ? 'btn-danger' : 'btn-primary'}
          onClick={onConfirm}
          disabled={isLoading}
        >
          {isLoading ? 'Processing...' : confirmLabel}
        </button>
      </div>
    </Modal>
  )
}
