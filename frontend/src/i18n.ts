import type { Restaurant, Status } from './domain'
import en from './locales/en.json'
import zh from './locales/zh-Hant.json'
import hans from './locales/zh-Hans.json'
import traditionalReasons from './locales/reasons.zh-Hant.json'
import simplifiedReasons from './locales/reasons.zh-Hans.json'
import simplifiedDisplay from './locales/display.zh-Hans.json'

export type Language = 'zh-Hant' | 'zh-Hans' | 'en'
type Key = keyof typeof en
const dictionaries:Record<Language,Record<Key,string>>={en,'zh-Hant':zh,'zh-Hans':hans}
export function translator(language:Language) {return (key:Key) => dictionaries[language][key]}
export function readLanguage():Language {
  try {const saved=localStorage.getItem('eats-now-language'); if(saved==='en'||saved==='zh-Hant'||saved==='zh-Hans')return saved} catch { /* Defaults still work without storage. */ }
  return 'en'
}
export function saveLanguage(language:Language) {
  try {localStorage.setItem('eats-now-language',language)} catch { /* Switching still works for this visit. */ }
}
export const statusText: Record<Language,Record<Status,string>> = {
  en:{OPEN:'Available for order',CLOSED:'Not accepting orders',LIMITED:'Limited availability',UNKNOWN:'Order status unconfirmed'},
  'zh-Hant':{OPEN:'現在可以落單',CLOSED:'目前暫停接單',LIMITED:'部分點餐可用',UNKNOWN:'點餐狀態尚未確認'},
  'zh-Hans':{OPEN:'现在可以下单',CLOSED:'目前暂停接单',LIMITED:'部分点餐可用',UNKNOWN:'点餐状态尚未确认'},
}
export function chineseText(value:string,l:Language):string {
  return l==='zh-Hans'?(simplifiedDisplay as Record<string,string>)[value]||value:value
}
export function restaurantName(r:Restaurant,l:Language) {return l==='en'?r.name_en:chineseText(r.name_zh,l)}
export function restaurantLocation(r:Restaurant,l:Language) {return l==='en'?r.location:chineseText(r.location_zh,l)}
export function restaurantSearchText(r:Restaurant) {
  return [r.name,r.name_en,r.name_zh,r.location,r.location_zh,chineseText(r.name_zh,'zh-Hans'),chineseText(r.location_zh,'zh-Hans')].join(' ').toLowerCase()
}
export function categoryText(category:string,l:Language) {
  const labels:Record<string,[string,string]>={Canteen:['飯堂','食堂'],Restaurant:['餐廳','餐厅'],'Café':['咖啡店','咖啡店'],Kiosk:['小食亭','小食亭']}
  return l==='en'?category:labels[category]?.[l==='zh-Hans'?1:0]||category
}
export function reasonText(r:Restaurant,l:Language):string {
  if(l==='en')return r.reason
  const category=r.reason.match(/^Ordering confirmed in the current “(.+)” menu, with a purchasable food or drink\.$/)
  // Menu titles come from the merchant. Keep the quoted original rather than inventing a translation.
  if(category)return l==='zh-Hans'?`当前「${category[1]}」菜单已确认有可购买的食品或饮品。`:`目前「${category[1]}」餐牌已確認有可購買的食品或飲品。`
  const brand=r.reason.match(/^Ordering confirmed for (.+); both brands are not confirmed fully available\.$/)
  if(brand)return l==='zh-Hans'?`${brand[1].replace('Tai Tai','台台')} 已确认可下单；尚未确认两个品牌全部可用。`:`${brand[1].replace('Tai Tai','台台')} 已確認可落單；尚未確認兩個品牌全部可用。`
  const reasons:Record<string,string>=l==='zh-Hans'?simplifiedReasons:traditionalReasons
  return reasons[r.reason]||(l==='zh-Hans'?'官方系统尚未提供可确认的点餐状态。':'官方系統尚未提供可確認的點餐狀態。')
}

