-- Xno Noclip
local player = game.Players.LocalPlayer

local function applyNoclip(char)
    if not char then return end
    local humanoid = char:FindFirstChildOfClass("Humanoid")
    if not humanoid then return end
    if not char:FindFirstChild("Noclip") then
        local tool = Instance.new("Script")
        tool.Name = "Noclip"
        tool.Parent = char
        tool.Source = [[
local char = script.Parent
local humanoid = char:FindFirstChildOfClass("Humanoid")
if not humanoid then return end
for _, part in pairs(char:GetChildren()) do
    if part:IsA("BasePart") then part.CanCollide = false end
end
humanoid:GetPropertyChangedSignal("Jump"):Connect(function()
    for _, part in pairs(char:GetChildren()) do
        if part:IsA("BasePart") then part.CanCollide = false end
    end
end)
]]
    end
end

applyNoclip(player.Character)
player.CharacterAdded:Connect(applyNoclip)
print("[Xno] Noclip enabled")
