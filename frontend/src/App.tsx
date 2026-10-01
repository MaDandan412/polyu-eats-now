import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ArrowUpRight, Check, Clock3, Coffee, CreditCard, Heart, Info, Leaf, MapPin, RefreshCw, Search, ShoppingBag, Smartphone, Utensils, UtensilsCrossed, WifiOff, X } from 'lucide-react'
import { demoRestaurants, initialRestaurants } from './data'
import { effectiveRestaurant, formatTime, isOrderable } from './domain'
import type { Restaurant, Status } from './domain'
import { categoryText, readLanguage, saveLanguage, reasonText, restaurantName, restaurantLocation, restaurantSearchText, statusText, translator } from './i18n'
import type { Language } from './i18n'
import { fetchRestaurants, readFavorites, saveFavorites } from './services'
import { OrderLaunch } from './OrderLaunch'

type Tab = 'food' | 'favorites' | 'info'
type Filter = 'ALL' | 'AVAILABLE' | 'APP_ONLY' | Exclude<Status,'OPEN'>
const filters:Filter[] = ['AVAILABLE','ALL','LIMITED','CLOSED','UNKNOWN','APP_ONLY']
const tabs = [{id:'food' as Tab,Icon:UtensilsCrossed},{id:'favorites' as Tab,Icon:Heart},{id:'info' as Tab,Icon:Info}]

function Service({label,value,Icon,language}: {label:string;value:boolean|null;Icon:typeof Utensils;language:Language}) {
  if(value===null)return null
  const t=translator(language)
  return <span className={`service ${value?'yes':'no'}`}><Icon size={14}/>{label}<small>{value?<><Check size={12}/><span>{t('supported')}</span></>:t('unsupported')}</small></span>
}
function Card({r,favorite,toggle,demo,language,launch}: {r:Restaurant;favorite:boolean;toggle:()=>void;demo:boolean;language:Language;launch:(r:Restaurant)=>void}) {
  const t=translator(language), name=restaurantName(r,language)
  return <article className="restaurant-card">
    <div className="card-top"><div className={`food-icon ${r.tone}`} aria-hidden="true">{r.icon}</div><span className="category">{categoryText(r.category,language)}</span><button className={`favorite-button ${favorite?'is-favorite':''}`} aria-label={`${t(favorite?'removeFavorite':'addFavorite')} · ${name}`} aria-pressed={favorite} onClick={toggle}><Heart size={19} fill={favorite?'currentColor':'none'}/></button></div>
    <h3>{name}</h3><p className="location"><MapPin size={13}/>{restaurantLocation(r,language)}</p>
    <div className={`status ${r.status.toLowerCase()}`}><span className="status-dot"/>{r.platform==='Mobile App'?t('appOrderingStatus'):statusText[language][r.status]}</div>
    <div className="services" title={t('serviceFacts')}><Service Icon={Utensils} label={t('onlineDine')} value={r.dine_in} language={language}/><Service Icon={ShoppingBag} label={t('onlineTake')} value={r.takeaway} language={language}/></div>
    <p className="services-source">{r.services_source.startsWith('official-')?<a href={r.services_source_url||r.info_url} target="_blank" rel="noopener noreferrer">{t(r.services_source==='official-ordering-page'?'orderingFacts':'officialFacts')}<ArrowUpRight size={10}/></a>:r.dine_in!==null||r.takeaway!==null?t('suppliedFacts'):t('noServices')}</p>
    {(r.online_payment===true||r.mobile_only||r.session_minutes)&&<div className="ordering-features">{r.online_payment===true&&<span title={t('paymentNote')}><CreditCard size={12}/>{t('payment')}</span>}{r.mobile_only&&<span><Smartphone size={12}/>{t('mobileOnly')}</span>}{r.session_minutes&&<span title={t('sessionNote')}><Clock3 size={12}/>{t('session')}</span>}</div>}
    <p className="reason">{reasonText(r,language)}{r.check_delayed&&r.status!=='UNKNOWN'&&<><br/><span>{t('checkDelayed')}</span></>}</p>
    <div className="card-footer"><span><Clock3 size={12}/>{t(demo?'sample':r.last_checked?'checked':'notChecked')}{r.last_checked?` ${formatTime(r.last_checked)}`:''}</span>{!demo&&r.order_url?(r.mobile_only?<button className={`order-button ${isOrderable(r)?'primary':''}`} onClick={()=>launch(r)}>{t(isOrderable(r)?'order':'officialPage')}<Smartphone size={15}/></button>:<a className={`order-button ${isOrderable(r)?'primary':''}`} href={r.order_url} target="_blank" rel="noopener noreferrer">{t(isOrderable(r)?'order':'officialPage')}<ArrowUpRight size={15}/></a>):demo?<button className="order-button" disabled>{t('demoOnly')}</button>:<a className="order-button" href={r.info_url} target="_blank" rel="noopener noreferrer">{t('outletInfo')}<ArrowUpRight size={15}/></a>}</div>
  </article>
}

export default function App() {
  const [language,setLanguage]=useState<Language>(readLanguage)
  const t=translator(language)
  const [tab,setTab]=useState<Tab>('food')
  const [demo,setDemo]=useState(new URLSearchParams(location.search).get('demo')==='1')
  const [restaurants,setRestaurants]=useState<Restaurant[]>(initialRestaurants)
  const [favorites,setFavorites]=useState(readFavorites)
  const [filter,setFilter]=useState<Filter>('AVAILABLE')
  const [query,setQuery]=useState('')
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState<'apiError'|'favoriteError'|''>('')
  const [now,setNow]=useState(Date.now())
  const [online,setOnline]=useState(navigator.onLine)
  const [sample,setSample]=useState(demoRestaurants)
  const [launch,setLaunch]=useState<Restaurant|null>(null)
  const controller=useRef<AbortController|null>(null)
  useEffect(()=>{
    document.documentElement.lang=language
    document.title=language==='zh-Hant'?'PolyU Eats Now · 香港理工大學即時點餐':language==='zh-Hans'?'PolyU Eats Now · 香港理工大学即时点餐':'PolyU Eats Now · Hong Kong PolyU Food Ordering'
  },[language])
  const refresh=useCallback(async()=>{
    if(demo){setSample(demoRestaurants());return}
    controller.current?.abort(); const request=new AbortController();controller.current=request
    const timeout=window.setTimeout(()=>request.abort(),15_000)
    setLoading(true);setError('')
    try {const result=await fetchRestaurants(request.signal);if(controller.current===request){setRestaurants(result);setNow(Date.now())}}
    catch {if(controller.current===request){setNow(Date.now());setError('apiError')}}
    finally {clearTimeout(timeout);if(controller.current===request)setLoading(false)}
  },[demo])
  useEffect(()=>{void refresh();const timer=setInterval(()=>{void refresh()},15_000);return()=>{clearInterval(timer);controller.current?.abort()}},[refresh])
  useEffect(()=>{const tick=setInterval(()=>setNow(Date.now()),15_000);const update=()=>setOnline(navigator.onLine);window.addEventListener('online',update);window.addEventListener('offline',update);return()=>{clearInterval(tick);window.removeEventListener('online',update);window.removeEventListener('offline',update)}},[])
  const rows=useMemo(()=>(demo?sample:restaurants).map(r=>demo?r:online?effectiveRestaurant(r,now):{...r,status:'UNKNOWN' as Status,dine_in_available:null,takeaway_available:null,reason:'You are offline. Check again when connected.'}),[demo,sample,restaurants,now,online])
  const counts=useMemo(()=>({ALL:rows.length,APP_ONLY:rows.filter(r=>r.platform==='Mobile App').length,AVAILABLE:rows.filter(isOrderable).length,...Object.fromEntries((['OPEN','LIMITED','CLOSED','UNKNOWN'] as Status[]).map(status=>[status,rows.filter(r=>r.status===status&&(status!=='UNKNOWN'||r.platform!=='Mobile App')).length]))}) as Record<Filter,number>,[rows])
  const appOnly=rows.filter(r=>r.platform==='Mobile App').length, webTotal=rows.length-appOnly
  const confirmed=rows.filter(r=>r.platform!=='Mobile App'&&r.status!=='UNKNOWN').length
  const visible=rows.filter(r=>(tab!=='favorites'||favorites.includes(r.id))&&(filter==='ALL'||(filter==='AVAILABLE'?isOrderable(r):filter==='APP_ONLY'?r.platform==='Mobile App':r.status===filter&&(filter!=='UNKNOWN'||r.platform!=='Mobile App')))&&restaurantSearchText(r).includes(query.trim().toLowerCase())).sort((a,b)=>({OPEN:0,LIMITED:1,UNKNOWN:2,CLOSED:3}[a.status]-{OPEN:0,LIMITED:1,UNKNOWN:2,CLOSED:3}[b.status]))
  const lastChecked=rows.map(r=>r.last_checked).filter((s):s is string=>Boolean(s)).sort().at(-1)||null
  function toggleFavorite(id:string){const next=favorites.includes(id)?favorites.filter(x=>x!==id):[...favorites,id];setFavorites(next);if(!saveFavorites(next))setError('favoriteError')}
  function changeMode(){setDemo(!demo);setFilter('AVAILABLE');setError('');controller.current?.abort();const url=new URL(location.href);url.searchParams.delete('demo');history.replaceState(null,'',url)}
  function selectTab(id:Tab){setTab(id);setQuery('');setFilter(id==='food'?'AVAILABLE':'ALL');window.scrollTo({top:0,behavior:'instant'})}
  function changeLanguage(next:Language){saveLanguage(next);setLanguage(next)}
  return <div className="app">
    <header className="topbar"><div className="topbar-inner"><a className="brand" href="/" aria-label={t('home')}><img className="university-emblem" src="/polyu-logo.png" width="45" height="45" alt={t('logo')}/><span>PolyU <b>Eats Now</b><small>{t('tagline')}</small></span></a><nav className="desktop-nav" aria-label={t('mainNav')}>{tabs.map(({id,Icon})=><button key={id} className={tab===id?'active':''} onClick={()=>selectTab(id)}><Icon size={17}/>{t(id)}</button>)}</nav><div className="language-picker" role="group" aria-label={t('languagePicker')}>{([{id:'zh-Hans',label:'简',name:'简体中文'},{id:'en',label:'EN',name:'English'},{id:'zh-Hant',label:'繁',name:'繁體中文'}] as const).map(option=><button key={option.id} className={language===option.id?'selected':''} aria-label={option.name} aria-pressed={language===option.id} onClick={()=>changeLanguage(option.id)}>{option.label}</button>)}</div></div></header>
    <main className="main">
      <div className="page-heading"><div><p className="eyebrow"><span/>{t('eyebrow')}</p><h1>{tab==='favorites'?t('favoritesTitle'):tab==='info'?t('infoTitle'):<>{t('hungry')} <span>{t('fix')}</span></>}</h1><p className="subtitle">{t(tab==='favorites'?'favoritesSubtitle':tab==='info'?'infoSubtitle':'foodSubtitle')}</p></div><button className="mode-switch" onClick={changeMode}><span className={demo?'demo-dot':'live-dot'}/>{t(demo?'demo':'live')}</button></div>
      {demo&&<div className="notice demo-notice"><Info size={16}/><span>{t('demoNotice')}</span><button onClick={changeMode}>{t('viewLive')}<ArrowUpRight size={14}/></button></div>}
      {!online&&<div className="notice"><WifiOff size={16}/>{t('offline')}</div>}
      {error&&<div role="alert" className="notice error-notice"><Info size={16}/>{t(error)}{error==='apiError'&&<button onClick={()=>void refresh()}>{t('retry')}</button>}</div>}
      {tab==='info'?<section className="info-content"><div className="info-intro"><span className="info-art"><UtensilsCrossed size={42}/></span><h2>{t('know')}</h2><p>{t('intro')}</p></div><div className="info-grid"><article><h3>{t('statuses')}</h3>{(['OPEN','LIMITED','CLOSED','UNKNOWN'] as const).map(status=><div className="legend-row" key={status}><span className={`status ${status.toLowerCase()}`}><span className="status-dot"/>{statusText[language][status]}</span><p>{t(`${status}Info`)}</p></div>)}<p>{t('mealInfo')}</p></article><article><h3>{t('sourceTitle')}</h3><p>{t('sourceIntro')}</p><p>{t('factsInfo')}</p><p>{t('notesInfo')}</p><p>{t('languageInfo')}</p><p>{t('privacy')}</p><a className="info-link" href="https://www.polyu.edu.hk/cfso/campus-environment-and-facilities/catering-facilities/catering-outlets/" target="_blank" rel="noopener noreferrer">{t('directory')}<ArrowUpRight size={15}/></a><img className="university-wordmark" src="/polyu-wordmark.png" width="250" height="48" alt={t('logo')}/><div className="small-note">{t('independent')} · v0.1<br/>{t('nonOfficial')}</div></article><article className="phrasebook"><h3>{t('glossaryTitle')}</h3><p>{t('glossaryIntro')}</p><dl>{(['omit','onion','ice','lessIce'] as const).map(term=><div key={term}><dt>{t(`${term}Term`)}</dt><dd>{t(`${term}Meaning`)}</dd></div>)}</dl><p>{t('glossaryFuture')}</p></article></div></section>:<>
      <section className="availability-banner" aria-label={t('AVAILABLE')}><div className="availability-main"><span className="availability-icon"><UtensilsCrossed size={25}/></span><div><h2><span className="green-dot"/>{!demo&&!lastChecked&&!error?t('initialChecking'):<>{counts.AVAILABLE} {t(demo?'demoOrderable':'confirmedOrderable')}</>}</h2><p>{t(!demo&&!lastChecked&&!error?'initialCheckingHint':counts.AVAILABLE?'choose':'noConfirmed')}</p></div></div><div className="updated"><span><Clock3 size={14}/>{t(demo?'sample':lastChecked?'updated':'waiting')}{lastChecked?` ${formatTime(lastChecked)}`:''}</span><button aria-label={t('refresh')} disabled={loading} onClick={()=>void refresh()}><RefreshCw size={17} className={loading?'spinning':''}/></button></div></section>
      {!demo&&<section className="coverage-note"><div><strong>{confirmed} / {webTotal} {t('coverage')}</strong><p>{webTotal-confirmed} {t('unconfirmed')} · {appOnly} {t('appOnly')}</p></div><span>{t('background')}</span></section>}
      <section className="restaurant-section" aria-label={t('allCampus')}><div className="section-title"><div><h2>{t(tab==='favorites'?'favorites':filter==='AVAILABLE'?'orderNow':'allCampus')}<span>{tab==='favorites'?favorites.length:filter==='AVAILABLE'?counts.AVAILABLE:rows.length}</span></h2><p>{t(tab==='favorites'?'favoritesHint':filter==='AVAILABLE'?'orderHint':'allHint')}</p></div><label className="search"><Search size={17}/><input aria-label={t('search')} placeholder={t('search')} value={query} onChange={e=>setQuery(e.target.value)}/>{query&&<button aria-label={t('clearSearch')} onClick={()=>setQuery('')}><X size={14}/></button>}</label></div><div className="filter-row" role="group" aria-label={t('statusFilter')}>{filters.map(f=><button key={f} onClick={()=>setFilter(f)} aria-pressed={filter===f} className={filter===f?'selected':''}>{f==='AVAILABLE'&&<span className="green-dot"/>}{t(f)}<span className="filter-count">{counts[f]}</span></button>)}</div>
      <div className="restaurant-grid">{visible.map(r=><Card key={r.id} r={r} language={language} launch={setLaunch} demo={demo} favorite={favorites.includes(r.id)} toggle={()=>toggleFavorite(r.id)}/>)}</div>
      {!visible.length&&<div className="empty-state">{tab==='favorites'?<Heart size={36}/>:<Coffee size={36}/>}<h3>{t(tab==='favorites'&&!favorites.length?'emptyFavorite':'empty')}</h3><p>{t(tab==='favorites'&&!favorites.length?'saveHint':filter==='AVAILABLE'?'checkingHint':'filterHint')}</p><button onClick={()=>{setFilter('ALL');setQuery('');if(tab==='favorites'&&!favorites.length)setTab('food')}}>{t(tab==='favorites'&&!favorites.length?'explore':filter==='AVAILABLE'?'viewAll':'clearFilters')}</button></div>}
      </section><div className="source-note"><Leaf size={17}/><p>{t('source')}<span>{t(demo?'sampleSource':'unresolved')}</span></p></div></>}
      <footer className="page-footer"><span>{t('footer')}</span><span>{t('independent')} · v0.1</span></footer>
    </main><nav className="bottom-nav" aria-label={t('mobileNav')}>{tabs.map(({id,Icon})=><button key={id} className={tab===id?'active':''} onClick={()=>selectTab(id)}><Icon size={21}/><span>{t(id)}</span></button>)}</nav>
    {launch&&<OrderLaunch restaurant={launch} language={language} close={()=>setLaunch(null)}/>}
  </div>
}
