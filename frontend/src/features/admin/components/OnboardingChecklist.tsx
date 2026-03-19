import { CheckCircle, ChevronRight, Circle, X } from 'lucide-react'
import { useAuthStore } from '../../auth/stores/authStore'
import { useCompleteOnboarding, useOnboarding } from '../hooks/useOnboarding'
import type { ChecklistItem, OnboardingStatus } from '../api/onboarding'

interface OnboardingChecklistProps {
  status: OnboardingStatus
  onDismiss: () => void
  isPending: boolean
}

function ChecklistItemRow({ item }: { item: ChecklistItem }) {
  return (
    <button
      onClick={() => {
        window.location.href = item.route
      }}
      className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left
                 hover:bg-[var(--bg-elevated)] transition-colors"
    >
      {item.completed ? (
        <CheckCircle className="h-5 w-5 shrink-0 text-green-500" />
      ) : (
        <Circle className="h-5 w-5 shrink-0 text-[var(--text-muted)]" />
      )}
      <span
        className={[
          'flex-1 text-sm',
          item.completed
            ? 'text-[var(--text-muted)] line-through'
            : 'text-[var(--text-primary)]',
        ].join(' ')}
      >
        {item.label}
      </span>
      {!item.completed && (
        <ChevronRight className="h-4 w-4 text-[var(--text-muted)]" />
      )}
    </button>
  )
}

export function OnboardingChecklist({
  status,
  onDismiss,
  isPending,
}: OnboardingChecklistProps) {
  const doneCount = status.items.filter((i) => i.completed).length
  const total = status.items.length

  return (
    <div className="rounded-xl border border-[var(--sphotel-border)] bg-[var(--bg-surface)] p-6">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h2 className="text-base font-semibold text-[var(--text-primary)]">
            Welcome! Let&apos;s get you set up
          </h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            {doneCount} of {total} steps complete
          </p>
        </div>
        <button
          onClick={onDismiss}
          disabled={isPending}
          className="rounded p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]
                     hover:bg-[var(--bg-elevated)] disabled:opacity-50 transition-colors"
          aria-label="Dismiss checklist"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="divide-y divide-[var(--sphotel-border)]">
        {status.items.map((item) => (
          <ChecklistItemRow key={item.key} item={item} />
        ))}
      </div>

      <div className="mt-4 border-t border-[var(--sphotel-border)] pt-4">
        <button
          onClick={onDismiss}
          disabled={isPending}
          className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]
                     disabled:opacity-50 transition-colors"
        >
          {isPending ? 'Saving\u2026' : 'Dismiss checklist'}
        </button>
      </div>
    </div>
  )
}

export function OnboardingBanner() {
  const role = useAuthStore((s) => s.currentUser?.role)
  const { data: status } = useOnboarding()
  const { mutate: completeOnboarding, isPending } = useCompleteOnboarding()

  if (role !== 'admin' || !status || status.completed) return null

  return (
    <div className="p-6">
      <OnboardingChecklist
        status={status}
        onDismiss={() => completeOnboarding()}
        isPending={isPending}
      />
    </div>
  )
}
