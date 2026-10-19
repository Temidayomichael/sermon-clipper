-- Sermon Clipper bridge for DaVinci Resolve, Lua version (works in the free version, incl. 21.1+).
--
-- Start it from Resolve: Workspace > Scripts > Utility > sermon_clipper_bridge_lua.
-- It watches <project>/resolve/inbox for command files (*.lua), runs each one inside Resolve with
-- `resolve` available, and writes the result to resolve/outbox/<name>.json. Only that folder is read.
-- Stops after 3 hours, or when it receives a command file named stop.lua.


local ROOT = "__SERMON_CLIPPER_ROOT__/resolve" -- filled in by ./clip resolve-install
local INBOX = ROOT .. "/inbox"
local OUTBOX = ROOT .. "/outbox"
os.execute('mkdir -p "' .. INBOX .. '" "' .. OUTBOX .. '"')

if not resolve then resolve = Resolve() end

-- Minimal JSON encoder for results (tables, strings, numbers, booleans).
local function json(v)
  local t = type(v)
  if t == "nil" then return "null"
  elseif t == "boolean" or t == "number" then return tostring(v)
  elseif t == "string" then
    return '"' .. v:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\r', ''):gsub('\t', '\\t') .. '"'
  elseif t == "table" then
    local n = #v
    if n > 0 then
      local parts = {}
      for i = 1, n do parts[i] = json(v[i]) end
      return "[" .. table.concat(parts, ",") .. "]"
    end
    local parts = {}
    for k, val in pairs(v) do parts[#parts + 1] = json(tostring(k)) .. ":" .. json(val) end
    return "{" .. table.concat(parts, ",") .. "}"
  end
  return json(tostring(v))
end

local function write(path, text)
  local f = io.open(path, "w"); f:write(text); f:close()
end

local function sleep(sec)
  if bmd and bmd.wait then bmd.wait(sec) else os.execute("sleep " .. sec) end
end

write(OUTBOX .. "/_status.json", json({running = true, lang = "lua", since = os.time(), version = resolve:GetVersionString()}))
print("Sermon Clipper bridge (Lua) running. Leave this open; it stops by itself after 3 hours.")

local deadline = os.time() + 3 * 3600
while os.time() < deadline do
  local p = io.popen('ls -1 "' .. INBOX .. '" 2>/dev/null')
  local names = {}
  for name in p:lines() do
    if name:match("%.lua$") then names[#names + 1] = name end
  end
  p:close()
  table.sort(names)
  for _, name in ipairs(names) do
    local path = INBOX .. "/" .. name
    local f = io.open(path, "r"); local code = f:read("*a"); f:close()
    os.remove(path)
    if name == "stop.lua" then deadline = 0; break end
    local env = setmetatable({resolve = resolve, result = nil}, {__index = _G})
    local chunk, err = loadstring(code, name)
    local out
    if not chunk then
      out = {ok = false, error = err}
    else
      setfenv(chunk, env)
      local ok, e = pcall(chunk)
      out = ok and {ok = true, result = env.result} or {ok = false, error = tostring(e)}
    end
    write(OUTBOX .. "/" .. name:gsub("%.lua$", ".json"), json(out))
  end
  sleep(0.3)
end

write(OUTBOX .. "/_status.json", json({running = false, stopped = os.time()}))
print("Sermon Clipper bridge (Lua) stopped.")
