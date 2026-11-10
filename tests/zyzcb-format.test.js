import test from 'node:test'
import assert from 'node:assert/strict'

import {
  DEFAULT_SETTINGS,
  normalizeSettings,
  serializeProject,
  parseProject
} from '../src/renderer/src/engine/zyzcb-format.js'

test('serializeProject → parseProject 往返保持设置', () => {
  const settings = {
    ...DEFAULT_SETTINGS,
    text: '床前明月光\n疑是地上霜 \\ 反斜杠',
    font_name: '宋体',
    font_size: 28,
    offset_x: -5,
    offset_y: 3,
    grid_type: '田字格',
    mode: '抄写',
    title: '测试字帖',
    fields: ['班级', '姓名'],
    page_format: '第1页 共x页',
    page_position: '底部靠右'
  }
  const bytes = serializeProject(settings)
  assert.ok(bytes instanceof Uint8Array)
  assert.deepEqual(parseProject(bytes), settings)
})

test('缺失或非法字段回落到默认值', () => {
  const parsed = normalizeSettings({ grid_type: '未知格子', font_size: '28' })
  assert.equal(parsed.grid_type, DEFAULT_SETTINGS.grid_type)
  assert.equal(parsed.font_size, DEFAULT_SETTINGS.font_size)
  assert.equal(parsed.mode, DEFAULT_SETTINGS.mode)
  assert.deepEqual(parsed.fields, DEFAULT_SETTINGS.fields)
})

test('JSON 格式工程文件可解析', () => {
  const json = new TextEncoder().encode(JSON.stringify({ text: '汉字内容', title: 'JSON 标题' }))
  const parsed = parseProject(json)
  assert.equal(parsed.text, '汉字内容')
  assert.equal(parsed.title, 'JSON 标题')
  assert.equal(parsed.grid_type, DEFAULT_SETTINGS.grid_type)
})
