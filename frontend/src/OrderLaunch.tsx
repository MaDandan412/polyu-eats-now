import { useEffect, useRef, useState } from 'react'
import { ArrowUpRight, Copy, Smartphone, X } from 'lucide-react'
import type { Restaurant } from './domain'
import { restaurantName, translator } from './i18n'
import type { Language } from './i18n'

export function OrderLaunch({restaurant,language,close}:{restaurant:Restaurant;language:Language;close:()=>void}) {
  const t=translator(language), dialog=useRef<HTMLDialogElement>(null)
  const [copyState,setCopyState]=useState<'copy'|'copied'|'copyError'>('copy')
  const input=useRef<HTMLInputElement>(null)
  const phone=/iPhone|Android.*Mobile|Windows Phone/i.test(navigator.userAgent)
  useEffect(()=>{const el=dialog.current;el?.showModal();return()=>el?.close()},[])
  async function copy() {
    try {await navigator.clipboard.writeText(restaurant.order_url!);setCopyState('copied')}
    catch {input.current?.focus();input.current?.select();setCopyState('copyError')}
  }
  return <dialog ref={dialog} className="order-dialog" onCancel={close} onClick={e=>{if(e.target===dialog.current)close()}} aria-labelledby="launch-title">
    <button className="dialog-close" aria-label={t('close')} onClick={close}><X size={20}/></button>
    <span className="dialog-icon"><Smartphone size={27}/></span><h2 id="launch-title">{t('launchTitle')}</h2><h3>{restaurantName(restaurant,language)}</h3>
    <p>{t('launchIntro')}</p>
    {!phone&&<img className="order-qr" src="/block-y-order-qr.png" width="230" height="230" alt={t('qrAlt')}/>}
    <div className="session-note"><p>{t('sessionNote')}</p>{restaurant.online_payment===true&&<p>{t('paymentNote')}</p>}</div>
    {phone&&<a className="launch-primary" href={restaurant.order_url!} target="_blank" rel="noopener noreferrer" onClick={close}>{t('order')}<ArrowUpRight size={17}/></a>}
    <button className="copy-button" onClick={()=>void copy()}><Copy size={15}/>{t(copyState)}</button>
    <input ref={input} className="official-url" aria-label={t('officialPage')} value={restaurant.order_url!} readOnly onFocus={e=>e.currentTarget.select()}/>
  </dialog>
}
