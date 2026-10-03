import './styles.css'
import { drawPageToCanvas, calculatePages } from './engine/copybook.js'
import {
  DEFAULT_SETTINGS,
  normalizeSettings,
  serializeProject,
  parseProject
} from './engine/zyzcb-format.js'
import { showAlert, showQuestion, showPrompt, showTextPage, setModalI18n } from './modals.js'
import { createT, getLang, getDefaultDoc } from '../../shared/i18n.js'
import agreementZh from './assets/agreement.txt?raw'
import agreementEn from './assets/agreement.en.txt?raw'

// 界面语言：启动时从主进程取系统 locale（zh* 中文，其余英文兜底）
let lang = 'zh'
let t = (key) => key

// ---------------- DOM ----------------
const $ = (id) => document.getElementById(id)
const els = {
  tabs: $('tabs'),
  newTab: $('btn-new-tab'),
  text: $('inp-text'),
  fontName: $('inp-font-name'),
  fontSize: $('inp-font-size'),
  offsetX: $('inp-offset-x'),
  offsetY: $('inp-offset-y'),
  gridType: $('inp-grid-type'),
  mode: $('inp-mode'),
  title: $('inp-title'),
  field0: $('inp-field-0'),
  field1: $('inp-field-1'),
  field2: $('inp-field-2'),
  pageFormat: $('inp-page-format'),
  pagePosition: $('inp-page-position'),
  ocr: $('btn-ocr'),
  ocrLang: $('ocr-lang'),
  ocrStatus: $('ocr-status'),
  prev: $('btn-prev'),
  next: $('btn-next'),
  pageLabel: $('page-label'),
  exportPdf: $('btn-export'),
  canvas: $('preview-canvas')
}

// ---------------- 标签页状态 ----------------
let tabs = []
let activeTab = null
let tabSeq = 0
let syncing = false
let previewQueued = false

// 新工程默认值：grid_type/mode/page_format/page_position 始终为文件格式中文枚举；
// title/fields 是打印在纸上的文档内容，随界面语言给默认值
function cloneDefaults() {
  const s = structuredClone(DEFAULT_SETTINGS)
  return { ...s, ...getDefaultDoc(lang) }
}

function createTab(state = null) {
  const tab = {
    id: ++tabSeq,
    state: state || cloneDefaults(),
    currentPage: 0,
    filePath: null,
    modified: false
  }
  tabs.push(tab)
  return tab
}

function basename(p) {
  return p.split(/[\\/]/).pop()
}

function untitledName() {
  let name = t('ui.untitled')
  let counter = 1
  while (tabs.some((tab) => tabDisplayName(tab) === name)) {
    name = `${t('ui.untitled')}${counter++}`
  }
  return name
}

function tabDisplayName(tab) {
  const name = tab.filePath ? basename(tab.filePath) : untitledNameFor(tab)
  return tab.modified ? name + '*' : name
}

// 未保存标签的固定名称（创建时确定，与原版递增逻辑一致）
function untitledNameFor(tab) {
  return tab.untitled || t('ui.untitled')
}

// ---------------- 标签栏渲染 ----------------
function renderTabs() {
  els.tabs.innerHTML = ''
  for (const tab of tabs) {
    const tabEl = document.createElement('div')
    tabEl.className = 'tab' + (tab === activeTab ? ' active' : '')

    const label = document.createElement('span')
    label.className = 'tab-label'
    label.textContent = tabDisplayName(tab)
    tabEl.appendChild(label)

    const close = document.createElement('button')
    close.className = 'tab-close'
    close.textContent = '×'
    close.title = t('ui.closeTab')
    close.onclick = (e) => {
      e.stopPropagation()
      closeTab(tab)
    }
    tabEl.appendChild(close)

    tabEl.onclick = () => activateTab(tab)
    els.tabs.appendChild(tabEl)
  }
  syncWindowTitle()
}

function activateTab(tab) {
  if (tab === activeTab) return
  activeTab = tab
  fillForm(tab.state)
  renderTabs()
  schedulePreview()
}

async function closeTab(tab) {
  if (tab.modified) {
    const answer = await showQuestion(t('msg.saveQuestionTitle'), t('msg.saveQuestion'))
    if (answer === 'cancel') return
    if (answer === 'save') {
      if (!(await saveTab(tab))) return
    }
  }
  const idx = tabs.indexOf(tab)
  tabs.splice(idx, 1)
  if (activeTab === tab) {
    activeTab = tabs[Math.min(idx, tabs.length - 1)] || null
    if (activeTab) {
      fillForm(activeTab.state)
    }
  }
  renderTabs()
  schedulePreview()
}

function syncWindowTitle() {
  if (!activeTab) {
    window.api.setTitle(t('appName'))
    return
  }
  window.api.setTitle(`${t('appName')} - ${tabDisplayName(activeTab)}`)
}

// ---------------- 字体加载 ----------------
async function loadFonts() {
  const select = els.fontName
  select.innerHTML = ''

  // 获取系统所有已安装字体
  let fontFamilies = []
  if ('queryLocalFonts' in window) {
    try {
      const fonts = await window.queryLocalFonts()
      fontFamilies = [...new Set(fonts.map((f) => f.family))].sort()
    } catch (err) {
      console.warn('queryLocalFonts failed:', err)
    }
  }

  // 如果 queryLocalFonts 不可用，回退到常见中文字体列表
  if (fontFamilies.length === 0) {
    fontFamilies = [
      '楷体', 'KaiTi', '宋体', 'SimSun', '黑体', 'SimHei',
      '微软雅黑', 'Microsoft YaHei', '等线', 'DengXian',
      '方正硬笔楷书简体', '方正楷体简体', '方正宋体简体',
      '仿宋', 'FangSong', '隶书', 'LiSu', '幼圆', 'YouYuan',
      '华文楷体', 'STKaiti', '华文宋体', 'STSong', '华文黑体', 'STHeiti'
    ]
  }

  for (const font of fontFamilies) {
    const option = document.createElement('option')
    option.value = font
    option.textContent = font
    select.appendChild(option)
  }

  // 默认选择：优先楷体类
  const preferred = ['楷体', 'KaiTi', '方正硬笔楷书简体', '华文楷体', 'STKaiti']
  for (const p of preferred) {
    if (fontFamilies.includes(p)) {
      select.value = p
      return
    }
  }
  if (fontFamilies.length > 0) select.value = fontFamilies[0]
}

// ---------------- 表单同步 ----------------
function fillForm(s) {
  syncing = true
  els.text.value = s.text
  els.fontName.value = s.font_name
  els.fontSize.value = s.font_size
  els.offsetX.value = s.offset_x
  els.offsetY.value = s.offset_y
  els.gridType.value = s.grid_type
  els.mode.value = s.mode
  els.title.value = s.title
  els.field0.value = s.fields[0] || ''
  els.field1.value = s.fields[1] || ''
  els.field2.value = s.fields[2] || ''
  els.pageFormat.value = s.page_format
  els.pagePosition.value = s.page_position
  syncing = false
}

function clampInt(input, min, max) {
  let v = parseInt(input.value, 10)
  if (!Number.isFinite(v)) v = min
  v = Math.min(max, Math.max(min, v))
  input.value = v
  return v
}

function bindInputs() {
  els.text.addEventListener('input', () => {
    activeTab.state.text = els.text.value
    markModified()
  })

  els.fontName.addEventListener('change', () => {
    activeTab.state.font_name = els.fontName.value
    markModified()
  })

  const bindNumber = (input, key, min, max) => {
    input.addEventListener('input', () => {
      if (syncing) return
      activeTab.state[key] = clampInt(input, min, max)
      markModified()
    })
  }
  bindNumber(els.fontSize, 'font_size', 10, 100)
  bindNumber(els.offsetX, 'offset_x', -50, 50)
  bindNumber(els.offsetY, 'offset_y', -50, 50)

  els.gridType.addEventListener('change', () => {
    activeTab.state.grid_type = els.gridType.value
    // 作文纸自动调整字体大小
    if (els.gridType.value === '作文纸') {
      els.fontSize.value = 20
      activeTab.state.font_size = 20
    } else if (activeTab.state.font_size === 20) {
      els.fontSize.value = 32
      activeTab.state.font_size = 32
    }
    markModified()
  })

  els.mode.addEventListener('change', () => {
    activeTab.state.mode = els.mode.value
    markModified()
  })

  els.title.addEventListener('input', () => {
    activeTab.state.title = els.title.value
    markModified()
  })

  const bindField = (input, index) => {
    input.addEventListener('input', () => {
      activeTab.state.fields[index] = input.value
      markModified()
    })
  }
  bindField(els.field0, 0)
  bindField(els.field1, 1)
  bindField(els.field2, 2)

  els.pageFormat.addEventListener('change', () => {
    activeTab.state.page_format = els.pageFormat.value
    markModified()
  })

  els.pagePosition.addEventListener('change', () => {
    activeTab.state.page_position = els.pagePosition.value
    markModified()
  })
}

function markModified() {
  if (syncing || !activeTab) return
  activeTab.modified = true
  renderTabs()
  schedulePreview()
}

// ---------------- 预览 ----------------
function dpr() {
  return Math.min(window.devicePixelRatio || 1, 2)
}

function renderPreview() {
  previewQueued = false
  if (!activeTab) {
    const ctx = els.canvas.getContext('2d')
    els.canvas.width = 595
    els.canvas.height = 842
    ctx.clearRect(0, 0, 595, 842)
    els.pageLabel.textContent = t('ui.pageEmpty')
    els.prev.disabled = true
    els.next.disabled = true
    return
  }
  const { totalPages } = drawPageToCanvas(
    els.canvas,
    activeTab.state,
    activeTab.currentPage,
    dpr()
  )
  if (activeTab.currentPage > totalPages - 1) {
    activeTab.currentPage = totalPages - 1
    drawPageToCanvas(els.canvas, activeTab.state, activeTab.currentPage, dpr())
  }
  els.pageLabel.textContent = t('ui.pageOf', {
    current: activeTab.currentPage + 1,
    total: totalPages
  })
  els.prev.disabled = activeTab.currentPage <= 0
  els.next.disabled = activeTab.currentPage >= totalPages - 1
}

function schedulePreview() {
  if (previewQueued) return
  previewQueued = true
  requestAnimationFrame(renderPreview)
}

function prevPage() {
  if (activeTab && activeTab.currentPage > 0) {
    activeTab.currentPage--
    renderPreview()
  }
}

function nextPage() {
  const totalPages = calculatePages(
    activeTab.state.text,
    activeTab.state.grid_type,
    activeTab.state.mode
  )
  if (activeTab.currentPage < totalPages - 1) {
    activeTab.currentPage++
    renderPreview()
  }
}

// ---------------- 工程文件 ----------------
async function newProject() {
  const tab = createTab()
  tab.untitled = untitledName()
  activeTab = tab
  fillForm(tab.state)
  renderTabs()
  schedulePreview()
}

async function openProject() {
  const filePath = await window.api.openProjectDialog()
  if (filePath) await loadFromPath(filePath)
}

async function loadFromPath(filePath) {
  try {
    const bytes = await window.api.readFile(filePath)
    const state = parseProject(bytes)

    // 与原版一致：若当前仅有一个空白标签，则在其中打开
    let target
    if (
      tabs.length === 1 &&
      !tabs[0].filePath &&
      !tabs[0].modified
    ) {
      target = tabs[0]
    } else {
      target = createTab()
    }
    target.state = state
    target.filePath = filePath
    target.modified = false
    target.currentPage = 0
    activeTab = target
    fillForm(state)
    renderTabs()
    schedulePreview()
  } catch (err) {
    await showAlert(t('msg.loadFailTitle'), t('msg.loadFail', { detail: err.message || err }))
  }
}

async function saveTab(tab, saveAs = false) {
  let filePath = saveAs ? null : tab.filePath
  if (!filePath) {
    filePath = await window.api.saveProjectDialog(tab.filePath || undefined)
    if (!filePath) return false
  }
  try {
    await window.api.writeFile(filePath, serializeProject(tab.state))
    tab.filePath = filePath
    tab.modified = false
    if (tab === activeTab) renderTabs()
    else syncWindowTitle()
    return true
  } catch (err) {
    await showAlert(t('msg.saveFailTitle'), t('msg.saveFail', { detail: err.message || err }))
    return false
  }
}

async function exportPdf() {
  const tab = activeTab
  if (!tab) return
  let defaultName = ''
  if (tab.filePath) {
    const base = basename(tab.filePath)
    defaultName = base.replace(/\.zyzcb$/i, '')
  }
  const filePath = await window.api.savePdfDialog(defaultName || undefined)
  if (!filePath) return
  try {
    await document.fonts.ready
    await window.api.exportPdf(filePath, tab.state)
    await showAlert(t('msg.exportOkTitle'), t('msg.exportOk'))
  } catch (err) {
    await showAlert(t('msg.exportFailTitle'), t('msg.exportFail', { detail: err.message || err }))
  }
}

// 直接打印 / 打印预览（无需先导出 PDF，与导出共用同一渲染管线）
async function printJob(preview) {
  const tab = activeTab
  if (!tab) return
  try {
    await document.fonts.ready
    if (preview) {
      await window.api.printJob(tab.state, 'preview')
      return
    }
    const { ok, reason } = await window.api.printJob(tab.state, 'direct')
    if (!ok && !/cancel/i.test(reason)) {
      await showAlert(t('msg.printFailTitle'), t('msg.printIncomplete', { detail: reason || t('msg.printUnknown') }))
    }
  } catch (err) {
    await showAlert(preview ? t('msg.previewFailTitle') : t('msg.printFailTitle'), `${err.message || err}`)
  }
}

// ---------------- 关闭确认 ----------------
async function canCloseAll() {
  const modified = tabs.filter((tab) => tab.modified)
  for (let i = modified.length - 1; i >= 0; i--) {
    const tab = modified[i]
    const answer = await showQuestion(t('msg.saveQuestionTitle'), t('msg.saveQuestion'))
    if (answer === 'cancel') return false
    if (answer === 'save') {
      if (!(await saveTab(tab))) return false
    }
  }
  return true
}

// ---------------- 菜单与快捷键 ----------------
function bindMenu() {
  window.api.onMenuAction((id) => {
    switch (id) {
      case 'new':
        newProject()
        break
      case 'open':
        openProject()
        break
      case 'save':
        if (activeTab) saveTab(activeTab)
        break
      case 'saveAs':
        if (activeTab) saveTab(activeTab, true)
        break
      case 'exportPdf':
        exportPdf()
        break
      case 'print':
        printJob(false)
        break
      case 'printPreview':
        printJob(true)
        break
      case 'help':
        showTextPage(t('msg.helpTitle'), t('help'))
        break
      case 'agreement':
        showTextPage(t('msg.agreementTitle'), lang === 'zh' ? agreementZh : agreementEn, true)
        break
      case 'about':
        showTextPage(t('msg.aboutTitle'), t('about'))
        break
    }
  })

  window.api.onOpenFile((filePath) => loadFromPath(filePath))

  document.addEventListener('keydown', (e) => {
    if (e.key === 'PageUp') {
      e.preventDefault()
      prevPage()
    } else if (e.key === 'PageDown') {
      e.preventDefault()
      nextPage()
    }
  })
}

// ---------------- 截图 OCR ----------------
function bindOcr() {
  els.ocr.onclick = () => {
    els.ocr.disabled = true
    els.ocrStatus.hidden = false
    els.ocrStatus.textContent = t('msg.ocrSelecting')
    window.api.startOcrCapture()
  }

  window.api.onOcrCaptured(async (dataUrl) => {
    els.ocr.disabled = false
    if (!dataUrl) {
      els.ocrStatus.hidden = true
      return
    }
    els.ocrStatus.textContent = t('msg.ocrRecognizing')
    try {
      const text = await window.api.ocrRecognize(dataUrl, els.ocrLang.value)
      const clean = (text || '').replace(/\n{3,}/g, '\n\n').replace(/[ \t]+\n/g, '\n').trim()
      if (!clean) {
        els.ocrStatus.hidden = true
        await showAlert(t('msg.ocrEmptyTitle'), t('msg.ocrEmpty'))
        return
      }
      els.text.focus()
      els.text.select()
      document.execCommand('insertText', false, clean)
      els.ocrStatus.textContent = t('msg.ocrDone', { n: clean.length })
      setTimeout(() => {
        els.ocrStatus.hidden = true
      }, 2500)
    } catch (err) {
      els.ocrStatus.hidden = true
      await showAlert(t('msg.ocrFailTitle'), t('msg.ocrFail', { detail: err.message || err }))
    }
  })
}

// ---------------- 静态文案应用 ----------------
function applyStaticI18n() {
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en'
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.dataset.i18n)
  })
  document.querySelectorAll('[data-i18n-title]').forEach((el) => {
    el.title = t(el.dataset.i18nTitle)
  })
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder)
  })
}

// ---------------- 启动 ----------------
async function init() {
  // 先确定界面语言（zh* 中文，其余英文兜底）
  const locale = await window.api.getLocale()
  lang = getLang(locale)
  t = createT(locale)
  setModalI18n(t)
  applyStaticI18n()

  bindInputs()
  bindOcr()
  els.newTab.onclick = () => newProject()
  els.prev.onclick = prevPage
  els.next.onclick = nextPage
  els.exportPdf.onclick = exportPdf
  bindMenu()

  await loadFonts()

  const firstName = untitledName()
  const first = createTab()
  first.untitled = firstName
  activeTab = first
  fillForm(first.state)
  renderTabs()
  renderPreview()

  const initialFiles = await window.api.getInitialFiles()
  if (initialFiles && initialFiles.length > 0) {
    loadFromPath(initialFiles[0])
  }
}

window.__appHooks = {
  canClose: canCloseAll
}

init()
