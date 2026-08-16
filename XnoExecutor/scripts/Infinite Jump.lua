-- Xno Infinite Jump
local UIS = game:GetService("UserInputService")
local player = game.Players.LocalPlayer
local char = player.Character or player.CharacterAdded:Wait()
local humanoid = char:WaitForChild("Humanoid")

local jumping = false

UIS.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    if input.KeyCode == Enum.KeyCode.Space then
        jumping = true
        while jumping and humanoid and humanoid.Parent do
            humanoid:ChangeState(Enum.HumanoidStateType.Jumping)
            wait(0.08)
        end
    end
end)

UIS.InputEnded:Connect(function(input, gameProcessed)
    if input.KeyCode == Enum.KeyCode.Space then
        jumping = false
    end
end)

print("[Xno] Infinite Jump enabled - hold Space")
