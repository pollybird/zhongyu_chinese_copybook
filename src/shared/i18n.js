/**
 * 国际化（中 / 英）
 *
 * 语言检测：主进程 app.getLocale()，zh* 用中文，其余一律英文兜底。
 * 主进程与渲染进程共用本模块（electron-vite 分别打包，纯数据/函数无副作用）。
 *
 * 注意：grid_type / mode / page_format / page_position 的中文值
 * （'米字格'、'描红'、'不显示'……）是 .zyzcb 工程文件的枚举令牌，不可翻译，
 * 界面 option 只翻译显示文本；title / fields 属于用户文档内容，默认值随语言走
 * （见 defaultDoc）。
 */

export function isZhLocale(locale) {
  return /^zh([-_]|$)/i.test(String(locale || ''))
}

const messages = {
  zh: {
    appName: '钟毓汉字字帖生成器',

    menu: {
      file: '文件',
      edit: '编辑',
      help: '帮助',
      new: '新建',
      open: '打开',
      save: '保存',
      saveAs: '另存为',
      print: '打印',
      printPreview: '打印预览',
      exportPdf: '导出PDF',
      close: '关闭',
      cut: '剪切',
      copy: '复制',
      paste: '粘贴',
      selectAll: '全选',
      helpItem: '帮助',
      agreement: '用户协议',
      website: '官网',
      about: '关于'
    },

    dlg: {
      openTitle: '加载工程',
      saveTitle: '保存工程',
      pdfTitle: '导出PDF',
      projectFilter: '字帖工程文件',
      pdfFilter: 'PDF文件',
      defaultPdfName: '汉字字帖'
    },

    preview: {
      title: '打印预览',
      print: '打印',
      zoomOut: '缩小',
      zoomIn: '放大',
      fitWidth: '适应页宽',
      page: '第 {current} / {total} 页'
    },

    sel: {
      title: '截图识别',
      hint: '拖拽框选要识别的文字区域，Enter / 双击确认，Esc 取消'
    },

    print: { title: 'PDF 导出' },

    ui: {
      untitled: '未命名',
      newTabTip: '新建工程 (Ctrl+N)',
      inputContent: '输入内容',
      textPlaceholder: '请输入要生成字帖的汉字...',
      ocrBtn: '截图识别',
      ocrBtnTip: '截取屏幕区域并识别其中的文字',
      ocrLangTip: 'OCR 识别语言',
      ocrLangEng: '英文',
      ocrLangChi: '中文简体',
      ocrLangBoth: '英文+中文',
      settings: '调整设置',
      fontName: '字体:',
      fontSize: '字体大小:',
      offsetX: 'X轴偏移:',
      offsetY: 'Y轴偏移:',
      gridType: '线格类型',
      gridMi: '米字格',
      gridTian: '田字格',
      gridHui: '回宫格',
      gridZuowen: '作文纸',
      mode: '生成模式',
      modeTrace: '描红',
      modeCopy: '抄写',
      modeTraceCopy: '描红+抄写',
      modeCopybook: '纯字帖',
      titleSettings: '标题设置',
      titleLabel: '字帖标题:',
      customHeader: '自定义头部',
      pageSettings: '页码设置',
      pageFormat: '页码格式:',
      pageFormatNone: '不显示',
      pageFormatNum: '第1页',
      pageFormatCnNum: '第一页',
      pageFormatNumTotal: '第1页 共x页',
      pageFormatCnNumTotal: '第一页 共X页',
      pagePosition: '页码位置:',
      pagePosBottomCenter: '底部居中',
      pagePosBottomLeft: '底部靠左',
      pagePosBottomRight: '底部靠右',
      preview: '预览效果',
      prevTip: '上一页 (PageUp)',
      nextTip: '下一页 (PageDown)',
      pageOf: '第 {current} 页 / 共 {total} 页',
      pageEmpty: '第 0 页 / 共 0 页',
      exportPdf: '导出PDF',
      closeTab: '关闭标签'
    },

    btn: {
      ok: '确定',
      cancel: '取消',
      save: '保存',
      discard: '不保存'
    },

    msg: {
      saveQuestionTitle: '保存提示',
      saveQuestion: '当前工程未保存，是否保存？',
      loadFailTitle: '加载失败',
      loadFail: '加载工程文件失败: {detail}',
      saveFailTitle: '保存失败',
      saveFail: '保存工程文件失败: {detail}',
      exportOkTitle: '导出成功',
      exportOk: 'PDF文件导出成功！',
      exportFailTitle: '导出失败',
      exportFail: '导出PDF失败: {detail}',
      printFailTitle: '打印失败',
      printIncomplete: '打印未完成: {detail}',
      printUnknown: '未知错误',
      previewFailTitle: '打开预览失败',
      ocrSelecting: '请拖拽框选要识别的文字区域（Esc 取消）',
      ocrRecognizing: '正在识别文字...',
      ocrEmptyTitle: '识别结果',
      ocrEmpty: '未识别到文字，请重试或调整识别区域。',
      ocrDone: '识别完成，已填入 {n} 个字符',
      ocrFailTitle: '识别失败',
      ocrFail: 'OCR识别失败: {detail}',
      helpTitle: '帮助',
      agreementTitle: '用户协议',
      aboutTitle: '关于'
    },

    err: {
      renderTimeout: '页面渲染超时',
      captureFailed: '无法获取屏幕画面',
      invalidImage: '无效的图像数据'
    },

    help: `汉字字帖生成器帮助

1. 在左侧文本框中输入要生成字帖的汉字内容
2. 设置字体、字体大小、位置偏移等参数
3. 选择线格类型（米字格、田字格、回宫格、作文纸）
4. 选择生成模式（描红、抄写、描红+抄写、纯字帖）
5. 设置标题和自定义头部字段
6. 设置页码格式和位置
7. 点击保存工程可以保存当前设置
8. 点击加载工程可以加载之前保存的设置
9. 点击导出PDF可以将字帖导出为PDF文件

快捷键：
  Ctrl+N        新建工程
  Ctrl+O        打开工程
  Ctrl+S        保存工程
  Ctrl+Shift+S  另存为
  Ctrl+P        打印
  Ctrl+F        导出PDF
  PageUp/PageDown 预览翻页`,

    about: `钟毓汉字字帖生成器（Electron 版）

版本：2.0.1
作者：泰州姜堰钟毓信息技术有限公司
官网：https://www.tzzhy.cn/
功能：生成汉字字帖，支持多种格子类型和生成模式`
  },

  en: {
    appName: 'Zhongyu Chinese Copybook Generator',

    menu: {
      file: 'File',
      edit: 'Edit',
      help: 'Help',
      new: 'New',
      open: 'Open',
      save: 'Save',
      saveAs: 'Save As',
      print: 'Print',
      printPreview: 'Print Preview',
      exportPdf: 'Export PDF',
      close: 'Close',
      cut: 'Cut',
      copy: 'Copy',
      paste: 'Paste',
      selectAll: 'Select All',
      helpItem: 'Help',
      agreement: 'User Agreement',
      website: 'Website',
      about: 'About'
    },

    dlg: {
      openTitle: 'Open Project',
      saveTitle: 'Save Project',
      pdfTitle: 'Export PDF',
      projectFilter: 'Copybook Project',
      pdfFilter: 'PDF File',
      defaultPdfName: 'Chinese Copybook'
    },

    preview: {
      title: 'Print Preview',
      print: 'Print',
      zoomOut: 'Zoom out',
      zoomIn: 'Zoom in',
      fitWidth: 'Fit width',
      page: 'Page {current} of {total}'
    },

    sel: {
      title: 'Screen OCR',
      hint: 'Drag to select the text area. Enter / double-click to confirm, Esc to cancel'
    },

    print: { title: 'Export PDF' },

    ui: {
      untitled: 'Untitled',
      newTabTip: 'New project (Ctrl+N)',
      inputContent: 'Input Content',
      textPlaceholder: 'Enter the Chinese text to generate a copybook...',
      ocrBtn: 'Screen OCR',
      ocrBtnTip: 'Capture a screen area and recognize text in it',
      ocrLangTip: 'OCR language',
      ocrLangEng: 'English',
      ocrLangChi: 'Simplified Chinese',
      ocrLangBoth: 'English + Chinese',
      settings: 'Settings',
      fontName: 'Font:',
      fontSize: 'Font size:',
      offsetX: 'X offset:',
      offsetY: 'Y offset:',
      gridType: 'Grid Type',
      gridMi: 'Mi-character Grid',
      gridTian: 'Tian-character Grid',
      gridHui: 'Hui-character Grid',
      gridZuowen: 'Composition Paper',
      mode: 'Mode',
      modeTrace: 'Trace',
      modeCopy: 'Copy',
      modeTraceCopy: 'Trace + Copy',
      modeCopybook: 'Copybook Only',
      titleSettings: 'Title Settings',
      titleLabel: 'Copybook title:',
      customHeader: 'Custom Header Fields',
      pageSettings: 'Page Number Settings',
      pageFormat: 'Page number format:',
      pageFormatNone: 'None',
      pageFormatNum: 'Page 1',
      pageFormatCnNum: 'Page One',
      pageFormatNumTotal: 'Page 1 of X',
      pageFormatCnNumTotal: 'Page One of X',
      pagePosition: 'Page number position:',
      pagePosBottomCenter: 'Bottom center',
      pagePosBottomLeft: 'Bottom left',
      pagePosBottomRight: 'Bottom right',
      preview: 'Preview',
      prevTip: 'Previous page (PageUp)',
      nextTip: 'Next page (PageDown)',
      pageOf: 'Page {current} of {total}',
      pageEmpty: 'Page 0 of 0',
      exportPdf: 'Export PDF',
      closeTab: 'Close tab'
    },

    btn: {
      ok: 'OK',
      cancel: 'Cancel',
      save: 'Save',
      discard: "Don't Save"
    },

    msg: {
      saveQuestionTitle: 'Save',
      saveQuestion: 'The current project is unsaved. Save changes?',
      loadFailTitle: 'Load Failed',
      loadFail: 'Failed to load project file: {detail}',
      saveFailTitle: 'Save Failed',
      saveFail: 'Failed to save project file: {detail}',
      exportOkTitle: 'Export Complete',
      exportOk: 'The PDF file was exported successfully.',
      exportFailTitle: 'Export Failed',
      exportFail: 'Failed to export PDF: {detail}',
      printFailTitle: 'Print Failed',
      printIncomplete: 'Printing did not complete: {detail}',
      printUnknown: 'Unknown error',
      previewFailTitle: 'Preview Failed',
      ocrSelecting: 'Drag to select the text area (Esc to cancel)',
      ocrRecognizing: 'Recognizing text...',
      ocrEmptyTitle: 'Recognition Result',
      ocrEmpty: 'No text recognized. Please try again or adjust the selected area.',
      ocrDone: 'Recognition complete. {n} characters inserted',
      ocrFailTitle: 'Recognition Failed',
      ocrFail: 'OCR failed: {detail}',
      helpTitle: 'Help',
      agreementTitle: 'User Agreement',
      aboutTitle: 'About'
    },

    err: {
      renderTimeout: 'Page render timed out',
      captureFailed: 'Failed to capture the screen',
      invalidImage: 'Invalid image data'
    },

    help: `Chinese Copybook Generator Help

1. Enter the Chinese text for the copybook in the text box on the left
2. Adjust font, font size and position offsets
3. Choose a grid type (Mi-character, Tian-character, Hui-character, Composition Paper)
4. Choose a generation mode (Trace, Copy, Trace + Copy, Copybook Only)
5. Set the title and custom header fields
6. Set the page number format and position
7. Use Save to store the current project
8. Use Open to load a previously saved project
9. Use Export PDF to save the copybook as a PDF file

Shortcuts:
  Ctrl+N          New project
  Ctrl+O          Open project
  Ctrl+S          Save project
  Ctrl+Shift+S    Save As
  Ctrl+P          Print
  Ctrl+F          Export PDF
  PageUp/PageDown Preview paging`,

    about: `Zhongyu Chinese Copybook Generator (Electron Edition)

Version: 2.0.1
Author: Taizhou Jiangyan Zhongyu Information Technology Co., Ltd.
Website: https://www.tzzhy.cn/
Features: Generate Chinese copybooks with multiple grid types and modes`
  }
}

/**
 * 新工程的文档默认内容（用户可见、会被画到字帖上，随语言走）
 * 注意：grid_type / mode / page_format / page_position 不在这里，始终使用
 * zyzcb-format.js 中的中文枚举（工程文件令牌）
 */
const defaultDoc = {
  zh: { title: '汉字字帖', fields: ['班级', '姓名', '学号'] },
  en: { title: 'Chinese Copybook', fields: ['Class', 'Name', 'No.'] }
}

function lookup(lang, key) {
  const table = messages[lang] || messages.en
  const val = key.split('.').reduce((obj, k) => (obj == null ? undefined : obj[k]), table)
  if (val !== undefined) return val
  // 兜底：英文 → key 本身，避免界面出现 undefined
  return (messages.en && lookupRaw(messages.en, key)) ?? key
}

function lookupRaw(table, key) {
  return key.split('.').reduce((obj, k) => (obj == null ? undefined : obj[k]), table)
}

/**
 * 创建翻译函数：const t = createT(app.getLocale()); t('ui.mode') / t('msg.ocrDone', { n: 3 })
 */
export function createT(locale) {
  const lang = isZhLocale(locale) ? 'zh' : 'en'
  return (key, vars) => {
    let str = lookup(lang, key)
    if (vars) {
      str = str.replace(/\{(\w+)\}/g, (m, name) =>
        vars[name] !== undefined ? String(vars[name]) : m
      )
    }
    return str
  }
}

export function getLang(locale) {
  return isZhLocale(locale) ? 'zh' : 'en'
}

export function getDefaultDoc(locale) {
  const lang = isZhLocale(locale) ? 'zh' : 'en'
  return { ...defaultDoc[lang], fields: [...defaultDoc[lang].fields] }
}
