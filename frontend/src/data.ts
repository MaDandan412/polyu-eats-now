import catalogue from '../../data/restaurants.json'
import sources from '../../data/sources.json'
import type { Restaurant, Status } from './domain'
const officialDirectory = 'https://www.polyu.edu.hk/cfso/campus-environment-and-facilities/catering-facilities/catering-outlets/'
export const initialRestaurants: Restaurant[] = catalogue.map(r => {
  const source = sources[r.id as keyof typeof sources]
  return { ...r, platform: source.platform, order_url: source.order_url, info_url: source.info_url || officialDirectory,
    ...source.reported_services, services_source: source.services_source, services_source_url: source.services_source_url,
    online_payment: source.online_payment, mobile_only: source.mobile_only, session_minutes: source.session_minutes,
    ordering_notes_source_url: 'ordering_notes_source_url' in source ? source.ordering_notes_source_url : null,
    dine_in_available: null, takeaway_available: null, status: 'UNKNOWN', last_checked: null, reason: 'Waiting for official ordering evidence.' }
})
// Entirely synthetic presentation fixtures. Never used as an API fallback.
export function demoRestaurants(): Restaurant[] {
  const states: Status[] = ['OPEN','OPEN','CLOSED','OPEN','OPEN','LIMITED','UNKNOWN','OPEN','OPEN','OPEN','CLOSED','LIMITED','OPEN','UNKNOWN','CLOSED','UNKNOWN']
  return initialRestaurants.map((r, i) => ({...r, status: states[i], last_checked: new Date().toISOString(), reason: 'Sample status for the demo. This is not a live availability check.'}))
}
