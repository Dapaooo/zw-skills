/**
 * 共享调色板预设
 * 内容处理时根据 content_type 选择对应色调
 */
const PALETTES = {
  '思辨/哲学': { bg: '#FAF8F4', accent: '#7C6853', text: '#1D1D1F', textMid: '#6E6E73', textDim: '#ACACB0', rule: '#E5E5EA' },
  '技术/工程': { bg: '#F4F7FB', accent: '#3D5A80', text: '#1D1D1F', textMid: '#6E6E73', textDim: '#ACACB0', rule: '#E5E5EA' },
  '文学/叙事': { bg: '#FBF8F5', accent: '#6B4E3D', text: '#1D1D1F', textMid: '#6E6E73', textDim: '#ACACB0', rule: '#E5E5EA' },
  '科学/研究': { bg: '#F4FAF6', accent: '#2D6A4F', text: '#1D1D1F', textMid: '#6E6E73', textDim: '#ACACB0', rule: '#E5E5EA' },
  '商业/管理': { bg: '#FAF8F4', accent: '#8B5A2B', text: '#1D1D1F', textMid: '#6E6E73', textDim: '#ACACB0', rule: '#E5E5EA' },
  '默认':     { bg: '#FAF8F4', accent: '#7C6853', text: '#1D1D1F', textMid: '#6E6E73', textDim: '#ACACB0', rule: '#E5E5EA' },
};

function getPalette(content) {
  const type = content.content_type || '默认';
  const preset = PALETTES[type] || PALETTES['默认'];
  // 如果 JSON 里显式指定了 palette，合并覆盖
  if (content.palette) {
    return { ...preset, ...content.palette };
  }
  return preset;
}

module.exports = { PALETTES, getPalette };
