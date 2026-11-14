-- Registry-driven server-rendered HTML; data never becomes a shell command.
function Div(element)
  local view = nil
  if element.classes:includes('updates-home') then view = 'latest' end
  if element.classes:includes('updates-history') then view = 'history' end
  if view then
    return pandoc.RawBlock('html', pandoc.pipe('python3', {'scripts/updates.py', 'render', '--view', view}, ''))
  end
end
