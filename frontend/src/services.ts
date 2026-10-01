import type { Restaurant } from './domain'
export async function fetchRestaurants(signal?: AbortSignal): Promise<Restaurant[]> {
  const response = await fetch('/api/restaurants', {signal, cache:'no-store'})
  if (!response.ok) throw new Error('Availability could not be refreshed.')
  const value = await response.json()
  if (!Array.isArray(value) || value.some(r => !r.id || !r.name || !['OPEN','CLOSED','LIMITED','UNKNOWN'].includes(r.status) || !r.reason || (r.last_checked !== null && !Number.isFinite(Date.parse(r.last_checked))))) throw new Error('Invalid availability response.')
  return value
}
export function readFavorites(): string[] {
  try {const value = JSON.parse(localStorage.getItem('food-now-favorites') || '[]'); return Array.isArray(value) ? value.filter(x => typeof x === 'string') : []} catch { return [] }
}
export function saveFavorites(ids: string[]) {
  try { localStorage.setItem('food-now-favorites', JSON.stringify(ids)); return true } catch { return false }
}
