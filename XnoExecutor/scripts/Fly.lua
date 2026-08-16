-- Xno Fly (Smooth)
local UIS = game:GetService("UserInputService")
local player = game.Players.LocalPlayer

local fly = false
local speed = 50

local function getChar()
    return player.Character or player.CharacterAdded:Wait()
end

UIS.InputBegan:Connect(function(input, gP)
    if gP then return end
    if input.KeyCode == Enum.KeyCode.F then
        fly = not fly
        if fly then
            spawn(function()
                local char = getChar()
                local root = char:WaitForChild("HumanoidRootPart")
                local humanoid = char:WaitForChild("Humanoid")
                local bodyGyro = Instance.new("BodyGyro")
                local bodyVel = Instance.new("BodyVelocity")
                bodyGyro.MaxTorque = Vector3.new(9e5, 9e5, 9e5)
                bodyVel.MaxForce = Vector3.new(9e9, 9e9, 9e9)
                bodyGyro.Parent = root
                bodyVel.Parent = root
                while fly and root and root.Parent do
                    bodyGyro.CFrame = root.CFrame
                    local move = Vector3.new(
                        (UIS:IsKeyDown(Enum.KeyCode.D) and 1 or 0) - (UIS:IsKeyDown(Enum.KeyCode.A) and 1 or 0),
                        0,
                        (UIS:IsKeyDown(Enum.KeyCode.S) and 1 or 0) - (UIS:IsKeyDown(Enum.KeyCode.W) and 1 or 0)
                    )
                    if UIS:IsKeyDown(Enum.KeyCode.Space) then move = move + Vector3.new(0, 1, 0) end
                    if UIS:IsKeyDown(Enum.KeyCode.LeftShift) then move = move - Vector3.new(0, 1, 0) end
                    bodyVel.Velocity = root.CFrame:VectorToWorldSpace(move) * speed
                    wait()
                end
                bodyGyro:Destroy()
                bodyVel:Destroy()
            end)
        end
    end
end)
print("[Xno] Fly enabled - press F to toggle, WASD/Space/Shift to move")
