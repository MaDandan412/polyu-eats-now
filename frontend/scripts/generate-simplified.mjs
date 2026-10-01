import fs from 'node:fs'
import * as OpenCC from 'opencc-js'
const locales = new URL('../src/locales/', import.meta.url)
const read = name => JSON.parse(fs.readFileSync(new URL(name, locales), 'utf8'))
const write = (name,data) => fs.writeFileSync(new URL(name, locales), JSON.stringify(data,null,2)+'\n')
const convert = OpenCC.Converter({from:'hk',to:'cn'})
const strings = data => Object.fromEntries(Object.entries(data).map(([key,value])=>[key,convert(value)]))
const en=read('en.json'), zh=read('zh-Hant.json'), overrides=read('zh-Hans.overrides.json')
if(JSON.stringify(Object.keys(en).sort())!==JSON.stringify(Object.keys(zh).sort()))throw new Error('English / Traditional Chinese keys differ')
for(const key of Object.keys(overrides))if(!(key in zh))throw new Error('Unknown Simplified Chinese override: '+key)
write('zh-Hans.json',{...Object.fromEntries(Object.entries(strings(zh)).map(([key,value])=>[key,value.replaceAll('落单','下单').replaceAll('心水','喜欢的').replaceAll('餐牌','菜单')])),...overrides})
write('reasons.zh-Hans.json',Object.fromEntries(Object.entries(strings(read('reasons.zh-Hant.json'))).map(([key,value])=>[key,value.replaceAll('落单','下单').replaceAll('餐牌','菜单').replaceAll('连线','联网')])))
const catalogue=JSON.parse(fs.readFileSync(new URL('../../data/restaurants.json',import.meta.url),'utf8'))
const display={}
for(const r of catalogue)for(const key of ['name_zh','location_zh'])display[r[key]]=convert(r[key])
write('display.zh-Hans.json',display)
console.log('Generated Simplified Chinese UI, check reasons and '+catalogue.length+' official outlet names.')
