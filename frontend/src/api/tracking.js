import http from './http'

const QUEUE = []
let timer = null
const FLUSH_INTERVAL = 30000

function startTimer() {
  if (timer) return
  timer = setInterval(flush, FLUSH_INTERVAL)
}

function flush() {
  if (QUEUE.length === 0) return
  const batch = QUEUE.splice(0)
  const token = localStorage.getItem('token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}

  if (navigator.sendBeacon) {
    const blob = new Blob(
      [JSON.stringify({ events: batch })],
      { type: 'application/json' },
    )
    navigator.sendBeacon('/api/v1/tracking/batch', blob)
  } else {
    http.post('/tracking/batch', { events: batch }).catch(() => {})
  }
}

export function trackEvent(event) {
  QUEUE.push({ ...event, _ts: Date.now() })
  startTimer()
}

export function trackClick(targetType, targetId, pagePath) {
  trackEvent({
    event_type: 'click',
    target_type: targetType,
    target_id: String(targetId || ''),
    page_path: pagePath || window.location.pathname,
  })
}

export function trackPageView(pagePath) {
  trackEvent({
    event_type: 'page_view',
    target_type: 'page',
    page_path: pagePath || window.location.pathname,
  })
}

export function trackPageLeave(pagePath, durationMs) {
  trackEvent({
    event_type: 'page_leave',
    target_type: 'page',
    page_path: pagePath,
    duration_ms: durationMs,
  })
}

if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', flush)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') flush()
  })
}
