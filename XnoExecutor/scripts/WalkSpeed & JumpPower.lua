-- Xno WalkSpeed & JumpPower
local player = game.Players.LocalPlayer
local char = player.Character or player.CharacterAdded:Wait()
local humanoid = char:WaitForChild("Humanoid")

humanoid.WalkSpeed = 100
humanoid.JumpPower = 100

print("[Xno] WalkSpeed set to 100, JumpPower set to 100")
