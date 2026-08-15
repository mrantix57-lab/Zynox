--[[
    ZYNEX MOD MENU v1.0
    A stylish Roblox mod menu with smooth animated opening.

    Features:
      - Animated menu (TweenService open/close, ease-back pop-in)
      - FPS Boost toggle (disables shadows, lowers quality, removes particles)
      - Speed toggle + Max Speed slider
      - Draggable window + keybind to open/close

    How to run: open your executor in a Roblox game, paste this script, Execute.
]]

-- ============================ SERVICES ============================
local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")
local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")

local Player = Players.LocalPlayer
local PlayerGui = Player:WaitForChild("PlayerGui")

-- ============================ CONFIG ============================
local Config = {
    Accent     = Color3.fromRGB(88, 101, 242),
    AccentDark = Color3.fromRGB(63, 73, 172),
    Background = Color3.fromRGB(20, 20, 28),
    Background2 = Color3.fromRGB(31, 31, 42),
    Text       = Color3.fromRGB(235, 235, 245),
    Muted      = Color3.fromRGB(150, 150, 165),
    OnColor    = Color3.fromRGB(70, 190, 120),
    OffColor   = Color3.fromRGB(60, 60, 75),
}

local State = {
    FpsBoost   = false,
    Speed      = false,
    MaxSpeed   = 50,
    DefaultWalkSpeed = 16,
    MenuOpen   = true,
    DragOffset = nil,
}

-- Keep original lighting so FPS boost can be restored cleanly
local SavedLighting = {}

-- ============================ HELPERS ============================
local function new(class, props)
    local obj = Instance.new(class)
    for k, v in pairs(props) do
        obj[k] = v
    end
    return obj
end

local function addCorner(parent, radius)
    local c = Instance.new("UICorner")
    c.CornerRadius = UDim.new(0, radius)
    c.Parent = parent
    return c
end

-- Smoothly tween a frame from off-screen into place
local function playOpenAnimation(frame, bg)
    if bg then
        bg.BackgroundTransparency = 1
        TweenService:Create(bg, TweenInfo.new(0.25, Enum.EasingStyle.Linear), {
            BackgroundTransparency = 0.4
        }):Play()
    end
    frame.Size = UDim2.new(0, 60, 0, 60)
    frame.Position = UDim2.new(0.5, -30, 0.5, -30)
    frame.BackgroundTransparency = 1
    frame.Parent = frame.Parent

    local open = TweenService:Create(frame, TweenInfo.new(0.55, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        Size = UDim2.new(0, 340, 0, 460),
        Position = UDim2.new(0.5, -170, 0.5, -230),
        BackgroundTransparency = 0
    })
    open:Play()
end

-- ============================ FPS BOOST ============================
local function setFpsBoost(enabled)
    if enabled then
        SavedLighting.GlobalShadows = Lighting.GlobalShadows
        SavedLighting.ShadowSoftness = Lighting.ShadowSoftness
        SavedLighting.ClockTime = Lighting.ClockTime
        SavedLighting.Ambient = Lighting.Ambient
        SavedLighting.Brightness = Lighting.Brightness

        Lighting.GlobalShadows = false
        Lighting.ShadowSoftness = 0
        Lighting.Ambient = Color3.new(1, 1, 1)
        settings().Rendering.QualityLevel = 1

        -- Strip dynamic lights
        for _, v in ipairs(Lighting:GetDescendants()) do
            if v:IsA("PointLight") or v:IsA("SpotLight") or v:IsA("SurfaceLight") then
                v.Enabled = false
            end
        end

        -- Disable sparkles / particles under workspace for extra fps
        for _, v in ipairs(workspace:GetDescendants()) do
            if v:IsA("ParticleEmitter") or v:IsA("Sparkles") or v:IsA("Fire") then
                v.Enabled = false
            end
        end
    else
        if SavedLighting.GlobalShadows ~= nil then
            Lighting.GlobalShadows = SavedLighting.GlobalShadows
            Lighting.ShadowSoftness = SavedLighting.ShadowSoftness
            Lighting.ClockTime = SavedLighting.ClockTime
            Lighting.Ambient = SavedLighting.Ambient
            Lighting.Brightness = SavedLighting.Brightness
        end
        settings().Rendering.QualityLevel = -1
        for _, v in ipairs(Lighting:GetDescendants()) do
            if v:IsA("PointLight") or v:IsA("SpotLight") or v:IsA("SurfaceLight") then
                v.Enabled = true
            end
        end
        for _, v in ipairs(workspace:GetDescendants()) do
            if v:IsA("ParticleEmitter") or v:IsA("Sparkles") or v:IsA("Fire") then
                v.Enabled = true
            end
        end
    end
end

-- ============================ SPEED ============================
local function applySpeed()
    if not State.Speed then return end
    local char = Player.Character
    local humanoid = char and char:FindFirstChildOfClass("Humanoid")
    if humanoid then
        humanoid.WalkSpeed = State.MaxSpeed
    end
end

-- Re-apply every frame so games can't reset your speed
game:GetService("RunService").Heartbeat:Connect(function()
    applySpeed()
end)

-- ============================ UI BUILDING ============================
local ScreenGui = new("ScreenGui", {
    Name = "ZynexMenu",
    ResetOnSpawn = false,
    ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
    IgnoreGuiInset = true,
    Parent = PlayerGui,
})

-- Dim background overlay
local DimBg = new("Frame", {
    Size = UDim2.fromScale(1, 1),
    BackgroundColor3 = Color3.new(0, 0, 0),
    BackgroundTransparency = 1,
    BorderSizePixel = 0,
    Parent = ScreenGui,
})

-- Main window
local Main = new("Frame", {
    Size = UDim2.new(0, 340, 0, 460),
    Position = UDim2.new(0.5, -170, 0.5, -230),
    BackgroundColor3 = Config.Background,
    BackgroundTransparency = 1,
    BorderSizePixel = 0,
    Parent = ScreenGui,
})
addCorner(Main, 14)

-- Accent top bar
local TopBar = new("Frame", {
    Size = UDim2.new(1, 0, 0, 46),
    BackgroundColor3 = Config.Background2,
    BorderSizePixel = 0,
    Parent = Main,
})
addCorner(TopBar, 14)
local CornerClip = Instance.new("UICorner")
CornerClip.CornerRadius = UDim.new(0, 14)
CornerClip.Parent = TopBar

-- Actually clip the rounded top on main: use a mask
local Mask = Instance.new("UICorner")
Mask.CornerRadius = UDim.new(0, 14)
Mask.Parent = Main

local Title = new("TextLabel", {
    Text = "ZYNEX MENU",
    Font = Enum.Font.GothamBold,
    TextSize = 20,
    TextColor3 = Config.Text,
    BackgroundTransparency = 1,
    Position = UDim2.new(0, 16, 0, 0),
    Size = UDim2.new(0, 200, 0, 46),
    TextXAlignment = Enum.TextXAlignment.Left,
    Parent = TopBar,
})

-- Toggle (open/close) button
local CloseBtn = new("TextButton", {
    Text = "−",
    Font = Enum.Font.GothamBold,
    TextSize = 24,
    TextColor3 = Config.Text,
    BackgroundColor3 = Config.Background2,
    BorderSizePixel = 0,
    Position = UDim2.new(1, -46, 0, 4),
    Size = UDim2.new(0, 38, 0, 38),
    Parent = TopBar,
})
addCorner(CloseBtn, 10)

-- ============================ DRAG ============================
local TopbarDrag = TopBar
TopbarDrag.InputBegan:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 then
        local mouse = Player:GetMouse()
        State.DragOffset = input.Position - Vector2.new(Main.AbsolutePosition.X, Main.AbsolutePosition.Y)
        local conn
        conn = input.Changed:Connect(function(prop)
            if prop == "UserInputState" and input.UserInputState == Enum.UserInputState.End then
                conn:Disconnect()
                State.DragOffset = nil
            end
        end)
    end
end)

UserInputService.InputChanged:Connect(function(input, gpe)
    if input.UserInputType == Enum.UserInputType.MouseMovement and State.DragOffset then
        local pos = UDim2.new(0, input.Position.X - State.DragOffset.X, 0, input.Position.Y - State.DragOffset.Y)
        Main.Position = pos
    end
end)

-- ============================ FEATURE ROW BUILDER ============================
local contentY = 60

local function buildToggleRow(title, subtitle, onColor)
    local row = new("Frame", {
        Size = UDim2.new(1, -24, 0, 58),
        Position = UDim2.new(0, 12, 0, contentY),
        BackgroundColor3 = Config.Background2,
        BorderSizePixel = 0,
        Parent = Main,
    })
    addCorner(row, 10)
    contentY = contentY + 66

    local name = new("TextLabel", {
        Text = title,
        Font = Enum.Font.GothamBold,
        TextSize = 16,
        TextColor3 = Config.Text,
        BackgroundTransparency = 1,
        Position = UDim2.new(0, 14, 0, 8),
        Size = UDim2.new(0, 220, 0, 22),
        TextXAlignment = Enum.TextXAlignment.Left,
        Parent = row,
    })

    if subtitle then
        new("TextLabel", {
            Text = subtitle,
            Font = Enum.Font.Gotham,
            TextSize = 12,
            TextColor3 = Config.Muted,
            BackgroundTransparency = 1,
            Position = UDim2.new(0, 14, 0, 30),
            Size = UDim2.new(0, 220, 0, 18),
            TextXAlignment = Enum.TextXAlignment.Left,
            Parent = row,
        })
    end

    -- Toggle track + knob
    local track = new("Frame", {
        BackgroundColor3 = Config.OffColor,
        BorderSizePixel = 0,
        Position = UDim2.new(1, -64, 0, 14),
        Size = UDim2.new(0, 50, 0, 28),
        Parent = row,
    })
    addCorner(track, 14)

    local knob = new("Frame", {
        BackgroundColor3 = Color3.new(1, 1, 1),
        BorderSizePixel = 0,
        Position = UDim2.new(0, 4, 0, 4),
        Size = UDim2.new(0, 20, 0, 20),
        Parent = track,
    })
    addCorner(knob, 10)

    local state = false
    local function setOn(on)
        state = on
        TweenService:Create(track, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
            BackgroundColor3 = on and onColor or Config.OffColor
        }):Play()
        TweenService:Create(knob, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
            Position = on and UDim2.new(0, 26, 0, 4) or UDim2.new(0, 4, 0, 4)
        }):Play()
    end

    local btn = new("TextButton", {
        Text = "",
        BackgroundTransparency = 1,
        Position = UDim2.new(1, -64, 0, 10),
        Size = UDim2.new(0, 50, 0, 32),
        Parent = row,
    })
    btn.MouseButton1Click:Connect(function()
        setOn(not state)
    end)

    return row, setOn, function() return state end
end

-- ============================ SLIDER BUILDER ============================
local function buildSliderRow(title, subtitle, minVal, maxVal, initial, suffix)
    local row = new("Frame", {
        Size = UDim2.new(1, -24, 0, 70),
        Position = UDim2.new(0, 12, 0, contentY),
        BackgroundColor3 = Config.Background2,
        BorderSizePixel = 0,
        Parent = Main,
    })
    addCorner(row, 10)
    contentY = contentY + 78

    local name = new("TextLabel", {
        Text = title,
        Font = Enum.Font.GothamBold,
        TextSize = 16,
        TextColor3 = Config.Text,
        BackgroundTransparency = 1,
        Position = UDim2.new(0, 14, 0, 8),
        Size = UDim2.new(0, 200, 0, 22),
        TextXAlignment = Enum.TextXAlignment.Left,
        Parent = row,
    })

    local valueLabel = new("TextLabel", {
        Text = initial .. suffix,
        Font = Enum.Font.GothamBold,
        TextSize = 16,
        TextColor3 = Config.Accent,
        BackgroundTransparency = 1,
        Position = UDim2.new(1, -70, 0, 8),
        Size = UDim2.new(0, 60, 0, 22),
        TextXAlignment = Enum.TextXAlignment.Right,
        Parent = row,
    })

    local bar = new("Frame", {
        BackgroundColor3 = Config.OffColor,
        BorderSizePixel = 0,
        Position = UDim2.new(0, 14, 0, 44),
        Size = UDim2.new(1, -28, 0, 8),
        Parent = row,
    })
    addCorner(bar, 4)

    local fill = new("Frame", {
        BackgroundColor3 = Config.Accent,
        BorderSizePixel = 0,
        Position = UDim2.new(0, 0, 0, 0),
        Size = UDim2.new(0, 0, 1, 0),
        Parent = bar,
    })
    addCorner(fill, 4)

    local knob = new("Frame", {
        BackgroundColor3 = Color3.new(1, 1, 1),
        BorderSizePixel = 0,
        Position = UDim2.new(0, -6, 0, -6),
        Size = UDim2.new(0, 20, 0, 20),
        Parent = bar,
    })
    addCorner(knob, 10)

    local value = initial
    local function setValue(v)
        value = math.clamp(math.round(v), minVal, maxVal)
        local pct = (value - minVal) / (maxVal - minVal)
        fill.Size = UDim2.new(pct, 0, 1, 0)
        knob.Position = UDim2.new(pct, -10, 0, -6)
        valueLabel.Text = value .. suffix
    end

    local function updateFromPosition(x)
        local rel = (x - bar.AbsolutePosition.X) / bar.AbsoluteSize.X
        setValue(minVal + rel * (maxVal - minVal))
    end

    bar.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            updateFromPosition(input.Position.X)
        end
    end)

    local dragConn
    bar.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            dragConn = bar.InputChanged:Connect(function(ci)
                if ci.UserInputType == Enum.UserInputType.MouseMovement then
                    updateFromPosition(ci.Position.X)
                end
            end)
            local endConn
            endConn = input.Changed:Connect(function(p)
                if p == "UserInputState" and input.UserInputState == Enum.UserInputState.End then
                    dragConn:Disconnect()
                    endConn:Disconnect()
                end
            end)
        end
    end)

    setValue(initial)
    return row, setValue, function() return value end
end

-- ============================ BUILD ROWS ============================
-- FPS BOOST
local fpsRow, fpsSetOn, fpsGet = buildToggleRow("FPS BOOST", "Disable shadows, lights & particles", Config.OnColor)
fpsSetOn(false)
fpsRow.MouseButton1Click = nil
fpsRow.Activated = nil
for _, child in ipairs(fpsRow:GetDescendants()) do
    if child:IsA("TextButton") then
        child.MouseButton1Click:Connect(function()
            State.FpsBoost = fpsGet()
            setFpsBoost(State.FpsBoost)
        end)
    end
end

-- Speed
local spdRow, spdSetOn, spdGet = buildToggleRow("SPEED", "Move faster with max speed control", Config.OnColor)
spdSetOn(false)
for _, child in ipairs(spdRow:GetDescendants()) do
    if child:IsA("TextButton") then
        child.MouseButton1Click:Connect(function()
            State.Speed = spdGet()
            if State.Speed then applySpeed() end
        end)
    end
end

-- Max Speed slider
local sliderRow, sliderSet, sliderGet = buildSliderRow("MAX SPEED", "Set your maximum movement speed", 16, 500, 50, " w/s")

-- ============================ FOOTER ============================
local Footer = new("TextLabel", {
    Text = "Zynex Mod Menu  |  RightCtrl to toggle",
    Font = Enum.Font.Gotham,
    TextSize = 12,
    TextColor3 = Config.Muted,
    BackgroundTransparency = 1,
    Position = UDim2.new(0, 0, 1, -30),
    Size = UDim2.new(1, 0, 0, 22),
    Parent = Main,
})

-- ============================ ANIMATIONS ============================
local function closeMenu()
    State.MenuOpen = false
    TweenService:Create(Main, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.In), {
        Size = UDim2.new(0, 60, 0, 60),
        Position = UDim2.new(0.5, -30, 0.5, -30),
        BackgroundTransparency = 1
    }):Play()
    TweenService:Create(DimBg, TweenInfo.new(0.35, Enum.EasingStyle.Linear), {
        BackgroundTransparency = 1
    }):Play()
    task.delay(0.35, function()
        Main.Visible = false
        DimBg.Visible = false
    end)
end

local function openMenu()
    State.MenuOpen = true
    Main.Visible = true
    DimBg.Visible = true
    DimBg.BackgroundTransparency = 1
    Main.BackgroundTransparency = 1
    Main.Size = UDim2.new(0, 60, 0, 60)
    Main.Position = UDim2.new(0.5, -30, 0.5, -30)
    TweenService:Create(DimBg, TweenInfo.new(0.25, Enum.EasingStyle.Linear), {
        BackgroundTransparency = 0.4
    }):Play()
    TweenService:Create(Main, TweenInfo.new(0.55, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
        Size = UDim2.new(0, 340, 0, 460),
        Position = UDim2.new(0.5, -170, 0.5, -230),
        BackgroundTransparency = 0
    }):Play()
end

CloseBtn.MouseButton1Click:Connect(function()
    if State.MenuOpen then closeMenu() else openMenu() end
end)

UserInputService.InputBegan:Connect(function(input, gpe)
    if gpe then return end
    if input.KeyCode == Enum.KeyCode.RightControl then
        if State.MenuOpen then closeMenu() else openMenu() end
    end
end)

-- Opening animation on load
playOpenAnimation(Main, DimBg)

-- ============================ SETTINGS SYNC ============================
-- Pull slider value into State each time it changes
local lastSpeed = State.MaxSpeed
local sliderValue = sliderGet()
task.spawn(function()
    while true do
        local sv = sliderGet()
        if sv ~= lastSpeed then
            State.MaxSpeed = sv
            lastSpeed = sv
            if State.Speed then applySpeed() end
        end
        task.wait(0.1)
    end
end)

-- Re-apply speed on respawn
Player.CharacterAdded:Connect(function()
    applySpeed()
end)

print("[Zynex] Mod Menu loaded! RightCtrl to toggle.")
