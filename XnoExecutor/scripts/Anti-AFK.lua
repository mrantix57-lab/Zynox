-- Xno Anti-AFK
local VU = game:GetService("VirtualUser")
game.Players.LocalPlayer.Idled:Connect(function()
    VU:Button2Down(Vector2.new(0, 0), workspace.CurrentCamera.CFrame)
    wait(1)
    VU:Button2Up(Vector2.new(0, 0), workspace.CurrentCamera.CFrame)
end)
print("[Xno] Anti-AFK enabled")
