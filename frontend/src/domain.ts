export type Status = 'OPEN' | 'CLOSED' | 'LIMITED' | 'UNKNOWN'
export interface Restaurant {
  id: string; name: string; location: string; platform: string | null;
  order_url: string | null; info_url: string; dine_in: boolean | null;
  takeaway: boolean | null; status: Status; last_checked: string | null;
  reason: string; category: string; icon: string; tone: string;
  name_en: string; name_zh: string; name_zh_origin: string; location_zh: string;
  dine_in_available: boolean | null; takeaway_available: boolean | null;
  services_source: string; services_source_url: string | null;
  online_payment: boolean | null; mobile_only: boolean; session_minutes: number | null;
  ordering_notes_source_url: string | null;
  check_delayed?: boolean;
}
export const statusLabels: Record<Status, string> = {
  OPEN: 'Available for order', CLOSED: 'Not accepting orders', LIMITED: 'Limited availability', UNKNOWN: 'Order status unknown',
}
export function isOrderable(r: Restaurant): boolean {
  return r.status === 'OPEN' || r.status === 'LIMITED'
}
export function effectiveRestaurant(r: Restaurant, now = Date.now()): Restaurant {
  if (!r.last_checked || !Number.isFinite(Date.parse(r.last_checked)) || now - Date.parse(r.last_checked) > 180_000) {
    return { ...r, status: 'UNKNOWN', dine_in_available: null, takeaway_available: null, reason: 'Awaiting a fresh automatic availability check.', check_delayed: false }
  }
  return r
}
export function formatTime(value: string | null) {
  return value ? new Intl.DateTimeFormat('en-HK', {hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Asia/Hong_Kong'}).format(new Date(value)) : 'Not checked'
}
