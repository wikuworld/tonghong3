/** Animasi kartu “kirim file” dari tombol Tambah ke baris tabel baru. */

function prefersReducedMotion() {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function sendToRowAnimation({ fromEl, toEl, label = '' }) {
  return new Promise((resolve) => {
    if (!toEl) {
      resolve()
      return
    }

    const finish = () => {
      toEl.classList.add('draft-line-just-added')
      window.setTimeout(() => toEl.classList.remove('draft-line-just-added'), 1200)
      resolve()
    }

    if (prefersReducedMotion() || !fromEl) {
      finish()
      return
    }

    if (typeof toEl.scrollIntoView === 'function') {
      toEl.scrollIntoView({ block: 'nearest', inline: 'nearest' })
    }

    const from = fromEl.getBoundingClientRect()
    const to = toEl.getBoundingClientRect()
    const ghost = document.createElement('div')
    ghost.className = 'so-send-ghost'
    ghost.setAttribute('aria-hidden', 'true')
    const icon = document.createElement('span')
    icon.className = 'so-send-ghost__icon'
    const text = document.createElement('span')
    text.className = 'so-send-ghost__label'
    text.textContent = label || 'SO'
    ghost.append(icon, text)
    document.body.appendChild(ghost)

    const startX = from.left + from.width / 2 - 80
    const startY = from.top + from.height / 2 - 18
    const endX = to.left + 16
    const endY = to.top + to.height / 2 - 18
    const midX = (startX + endX) / 2
    const midY = Math.min(startY, endY) - 56

    ghost.style.transform = `translate(${startX}px, ${startY}px)`

    const anim = ghost.animate(
      [
        { transform: `translate(${startX}px, ${startY}px) scale(1) rotate(0deg)`, opacity: 1, offset: 0 },
        { transform: `translate(${midX}px, ${midY}px) scale(0.92) rotate(-10deg)`, opacity: 0.95, offset: 0.45 },
        { transform: `translate(${endX}px, ${endY}px) scale(0.32) rotate(8deg)`, opacity: 0.12, offset: 1 },
      ],
      { duration: 460, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
    )

    anim.onfinish = () => {
      ghost.remove()
      finish()
    }
  })
}
