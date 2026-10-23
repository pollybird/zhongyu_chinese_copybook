import test from 'node:test'
import assert from 'node:assert/strict'

import { calculatePages, buildPages } from '../src/renderer/src/engine/copybook.js'
import { DEFAULT_SETTINGS } from '../src/renderer/src/engine/zyzcb-format.js'

/** 从 buildPages 结果中提取所有字符（排除换行产生的空行） */
function charsOf(pages) {
  return pages.flatMap((rows) => rows.flatMap((row) => row.cells.map((c) => c.char)))
}

test('calculatePages 至少返回 1 页', () => {
  assert.equal(calculatePages('', '米字格', '描红'), 1)
  assert.ok(calculatePages('a'.repeat(1000), '米字格', '描红') >= 1)
})

test('排版既不多字也不漏字（米字格 / 描红）', () => {
  const text = '床前明月光\n疑是地上霜\n\n举头望明月'
  const pages = buildPages({ ...DEFAULT_SETTINGS, text, grid_type: '米字格', mode: '描红' })
  assert.ok(pages.length >= 1)
  const expected = text.replace(/\n/g, '')
  assert.equal(charsOf(pages).join(''), expected)
})

test('排版既不多字也不漏字（作文纸 / 抄写）', () => {
  const text = Array.from({ length: 60 }, (_, i) => `字${i}`).join('\n')
  const pages = buildPages({ ...DEFAULT_SETTINGS, text, grid_type: '作文纸', mode: '抄写' })
  assert.ok(pages.length >= 1)
  const expected = text.replace(/\n/g, '')
  assert.equal(charsOf(pages).join(''), expected)
})

test('空白文案也能得到至少一页', () => {
  const pages = buildPages({ ...DEFAULT_SETTINGS, text: '   \n\n  ' })
  assert.equal(pages.length, 1)
})

test('每种格子类型都能正常排版', () => {
  const text = '测试内容测试内容'
  for (const gridType of ['米字格', '田字格', '回宫格', '作文纸']) {
    const pages = buildPages({ ...DEFAULT_SETTINGS, text, grid_type: gridType, mode: '描红' })
    assert.ok(pages.length >= 1, `${gridType} 排版失败`)
    assert.equal(charsOf(pages).join(''), text, `${gridType} 字符丢失`)
  }
})
