import styles from './ProgressTracker.module.css';

const STEP_ICONS = {
  upload:   { done: '☁️', running: '⬆️', error: '❌', skipped: '⏭️', pending: '○' },
  extract:  { done: '📄', running: '🔍', error: '❌', skipped: '⏭️', pending: '○' },
  analyze:  { done: '🤖', running: '⚡', error: '❌', skipped: '⏭️', pending: '○' },
  generate: { done: '📝', running: '⚙️', error: '❌', skipped: '⏭️', pending: '○' },
  drive:    { done: '✅', running: '🔄', error: '❌', skipped: '⏭️', pending: '○' },
};

function StepItem({ step, index }) {
  const icon = STEP_ICONS[step.id]?.[step.status] ?? '○';
  const isActive = step.status === 'running';

  return (
    <div
      className={`${styles.step} ${styles[step.status]}`}
      style={{ animationDelay: `${index * 0.08}s` }}
    >
      <div className={styles.stepLeft}>
        <div className={`${styles.stepDot} ${isActive ? styles.pulsing : ''}`}>
          {isActive ? <span className="spinner" /> : <span className={styles.dotIcon}>{icon}</span>}
        </div>
        {index < 4 && <div className={`${styles.line} ${step.status === 'done' ? styles.lineDone : ''}`} />}
      </div>

      <div className={styles.stepBody}>
        <p className={styles.stepLabel}>{step.label}</p>
        {step.message && (
          <p className={styles.stepMessage}>{step.message}</p>
        )}
      </div>

      <div className={styles.stepStatus}>
        <span className={`${styles.statusBadge} ${styles['badge_' + step.status]}`}>
          {step.status}
        </span>
      </div>
    </div>
  );
}

export default function ProgressTracker({ steps, error }) {
  const doneCount = steps.filter(s => s.status === 'done' || s.status === 'skipped').length;
  const pct = Math.round((doneCount / steps.length) * 100);

  return (
    <div className={`${styles.container} glass animate-fade-up`}>
      <div className={styles.header}>
        <div>
          <h3>Processing Pipeline</h3>
          <p className={styles.subtitle}>AI-powered analysis in progress…</p>
        </div>
        <div className={styles.pctBadge}>{pct}%</div>
      </div>

      <div className={styles.progressBar}>
        <div className={styles.progressFill} style={{ width: `${pct}%` }} />
      </div>

      <div className={styles.steps}>
        {steps.map((step, i) => (
          <StepItem key={step.id} step={step} index={i} />
        ))}
      </div>

      {error && (
        <div className={styles.errorBox}>
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}
