import type { LeaderboardEntry } from '../lib/apiBackend'

interface Props {
  entry: LeaderboardEntry
}

const RANK_ICONS: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' }

export function ScoreRow({ entry }: Props) {
  const icon = RANK_ICONS[entry.rank] ?? `#${entry.rank}`
  return (
    <tr>
      <td>{icon}</td>
      <td>{entry.username}</td>
      <td style={{ textAlign: 'right' }}>{entry.score.toLocaleString()}</td>
      <td className="nes-text is-disabled" style={{ fontSize: '0.8rem' }}>
        {new Date(entry.achieved_at).toLocaleDateString()}
      </td>
    </tr>
  )
}
