Option Explicit

Dim PatchShape As String
Dim ConductorName As String

Sub Main
    PatchShape = "circular"
    ConductorName = "Copper"

    Select Case LCase(PatchShape)
        Case "circular", "square", "triangular", "hexagonal", "fshaped"
        Case Else
            ReportError "Unknown patch shape: " & PatchShape
            Exit Sub
    End Select

    ResetModel
    StoreCommonParameters
    StoreShapeParameters
    SetupProject
    DefineMaterials
    BuildGroundPlane
    BuildSubstrate
    BuildPatch
    BuildFeedLine
    CreatePort
    AddMonitors
    ConfigureSolver
    SolveAndExport
End Sub

Sub StoreCommonParameters
    StoreDoubleParameter "Fc", 2.45
    StoreDoubleParameter "Fmin", 1.0
    StoreDoubleParameter "Fmax", 3.0
    StoreDoubleParameter "Eps", 4.4
    StoreDoubleParameter "Wg", 75.20
    StoreDoubleParameter "Lg", 58.76
    StoreDoubleParameter "Hs", 1.4
    StoreDoubleParameter "Ht", 0.036
    StoreDoubleParameter "Fw", 2.7
    StoreDoubleParameter "Gpf", 1.0
End Sub

Sub StoreShapeParameters
    Select Case LCase(PatchShape)
        Case "circular"
            StoreDoubleParameter "R", 17.0
            StoreParameter "Fx", "0"
            StoreParameter "Ey", "-R"
        Case "square"
            StoreDoubleParameter "S", 29.38
            StoreParameter "Fx", "0"
            StoreParameter "Ey", "-S/2"
        Case "triangular"
            StoreDoubleParameter "Tb", 37.60
            StoreDoubleParameter "Th", 29.38
            StoreParameter "Fx", "0"
            StoreParameter "Ey", "-Th/3"
        Case "hexagonal"
            StoreDoubleParameter "Ha", 17.0
            StoreParameter "Fx", "0"
            StoreParameter "Ey", "-Ha*sqr(3)/2"
        Case "fshaped"
            StoreDoubleParameter "W", 37.60
            StoreDoubleParameter "L", 29.38
            StoreDoubleParameter "Vw", 10.0
            StoreDoubleParameter "Bh", 8.0
            StoreDoubleParameter "Sh", 3.0
            StoreDoubleParameter "Mw", 25.0
            StoreParameter "Fx", "-W/2+Vw/2"
            StoreParameter "Ey", "-L/2"
        Case Else
            ReportError "Unknown shape '" & PatchShape & "'. Use circular, square, triangular, hexagonal, or fshaped."
    End Select
End Sub

Sub SetupProject
    With Units
        .Geometry "mm"
        .Frequency "GHz"
        .Time "ns"
    End With

    With Background
        .Type "Normal"
        .Epsilon "1.0"
        .Mue "1.0"
    End With

    With Boundary
        .Xmin "expanded open" : .Xmax "expanded open"
        .Ymin "expanded open" : .Ymax "expanded open"
        .Zmin "expanded open" : .Zmax "expanded open"
    End With
End Sub

Sub DefineMaterials
    With Material
        .Reset
        .Name "FR4"
        .Type "Normal"
        .Epsilon "Eps"
        .Mue "1.0"
        .TanD "0.02"
        .TanDModel "ConstTanD"
        .Colour 0.94, 0.82, 0.76
        .Create
    End With

    With Material
        .Reset
        .Name "Copper"
        .Type "Normal"
        .Mue "1.0"
        .Kappa "5.8e7"
        .Colour 0.85, 0.55, 0.35
        .Create
    End With
End Sub

Sub BuildGroundPlane
    With Brick
        .Reset
        .Name "ground" : .Component "antenna" : .Material ConductorName
        .Xrange "-Wg/2", "Wg/2"
        .Yrange "-Lg/2", "Lg/2"
        .Zrange "-Ht", "0"
        .Create
    End With
End Sub

Sub BuildSubstrate
    With Brick
        .Reset
        .Name "substrate" : .Component "antenna" : .Material "FR4"
        .Xrange "-Wg/2", "Wg/2"
        .Yrange "-Lg/2", "Lg/2"
        .Zrange "0", "Hs"
        .Create
    End With
End Sub

Sub BuildPatch
    Select Case LCase(PatchShape)
        Case "circular"   : BuildCircularPatch
        Case "square"     : BuildSquarePatch
        Case "triangular" : BuildTriangularPatch
        Case "hexagonal"  : BuildHexagonalPatch
        Case "fshaped"    : BuildFShapedPatch
    End Select
End Sub

Sub BuildCircularPatch
    With Cylinder
        .Reset
        .Name "patch" : .Component "antenna" : .Material ConductorName
        .OuterRadius "R" : .InnerRadius "0" : .Axis "z"
        .Zrange "Hs", "Hs+Ht"
        .Xcenter "0" : .Ycenter "0"
        .Segments "0"
        .Create
    End With
End Sub

Sub BuildSquarePatch
    With Brick
        .Reset
        .Name "patch" : .Component "antenna" : .Material ConductorName
        .Xrange "-S/2", "S/2"
        .Yrange "-S/2", "S/2"
        .Zrange "Hs", "Hs+Ht"
        .Create
    End With
End Sub

Sub BuildTriangularPatch
    With Extrude
        .Reset
        .Name "patch" : .Component "antenna" : .Material ConductorName
        .Mode "pointlist" : .Height "Ht"
        .Origin "0", "0", "Hs"
        .Uvector "1", "0", "0" : .Vvector "0", "1", "0"
        .Point "-Tb/2", "-Th/3"
        .LineTo "Tb/2", "-Th/3"
        .LineTo "0", "2*Th/3"
        .Create
    End With
End Sub

Sub BuildHexagonalPatch
    With Extrude
        .Reset
        .Name "patch" : .Component "antenna" : .Material ConductorName
        .Mode "pointlist" : .Height "Ht"
        .Origin "0", "0", "Hs"
        .Uvector "1", "0", "0" : .Vvector "0", "1", "0"
        .Point "Ha", "0"
        .LineTo "Ha/2", "Ha*sqr(3)/2"
        .LineTo "-Ha/2", "Ha*sqr(3)/2"
        .LineTo "-Ha", "0"
        .LineTo "-Ha/2", "-Ha*sqr(3)/2"
        .LineTo "Ha/2", "-Ha*sqr(3)/2"
        .Create
    End With
End Sub

Sub BuildFShapedPatch
    AddBar "patch",   "-W/2",      "-W/2+Vw", "-L/2",          "L/2"
    AddBar "top_bar", "-W/2",      "W/2",     "L/2-Bh",        "L/2"
    AddBar "mid_bar", "-W/2",      "-W/2+Mw", "L/2-2*Bh-Sh",   "L/2-Bh-Sh"
    Solid.Add "antenna:patch", "antenna:top_bar"
    Solid.Add "antenna:patch", "antenna:mid_bar"
End Sub

Sub AddBar (ByRef name As String, ByRef x0 As String, ByRef x1 As String, ByRef y0 As String, ByRef y1 As String)
    With Brick
        .Reset
        .Name name : .Component "antenna" : .Material ConductorName
        .Xrange x0, x1
        .Yrange y0, y1
        .Zrange "Hs", "Hs+Ht"
        .Create
    End With
End Sub

Sub BuildFeedLine
    With Brick
        .Reset
        .Name "feed" : .Component "antenna" : .Material ConductorName
        .Xrange "Fx-Fw/2", "Fx+Fw/2"
        .Yrange "-Lg/2", "Ey-Gpf"
        .Zrange "Hs", "Hs+Ht"
        .Create
    End With
End Sub

Sub CreatePort
    With Port
        .Reset
        .PortNumber "1" : .NumberOfModes "1"
        .AdjustPolarization "False" : .PolarizationAngle "0"
        .ReferencePlaneDistance "0" : .TextSize "50"
        .Coordinates "Free" : .Orientation "yneg"
        .PortOnBound "False" : .ClipPickedPortToBound "False"
        .Xrange "Fx-Fw/2-6*Hs", "Fx+Fw/2+6*Hs"
        .Yrange "-Lg/2", "-Lg/2"
        .Zrange "-Ht", "6*Hs"
        .Create
    End With
End Sub

Sub AddMonitors
    AddFieldMonitor "farfield (f=Fc)", "Farfield"
    AddFieldMonitor "e-field (f=Fc)",  "Efield"
End Sub

Sub AddFieldMonitor (ByRef name As String, ByRef fieldType As String)
    With Monitor
        .Reset
        .Name name
        .Domain "Frequency"
        .FieldType fieldType
        .MonitorValue "Fc"
        .Create
    End With
End Sub

Sub ConfigureSolver
    With MeshSettings
        .SetMeshType "Hex"
        .Set "Version", 1
        .Set "StepsPerWaveNear", "20"
        .Set "StepsPerWaveFar", "20"
        .Set "StepsPerBoxNear", "10"
        .Set "StepsPerBoxFar", "10"
    End With

    With Solver
        .FrequencyRange "Fmin", "Fmax"
        .Method "Hexahedral"
        .CalculationType "TD-S"
        .StimulationPort "All"
        .StimulationMode "All"
        .AutoImpedance "True"
        .MeshAdaption "True"
    End With
End Sub

Sub SolveAndExport
    If Not Solver.Start Then
        ReportError "Solver failed; no S-parameters to export."
        Exit Sub
    End If

    SelectTreeItem "1D Results\S-Parameters"
    With TOUCHSTONE
        .Reset
        .FileName PatchShape & "_s11"
        .Impedance 50
        .Renormalize "True"
        .FrequencyRange "Full"
        .Write
    End With
End Sub

Sub ResetModel
    On Error Resume Next
    Component.Delete "antenna"
    Port.Delete "1"
    Material.Delete "FR4"
    Material.Delete "Copper"
    Monitor.Delete "farfield (f=Fc)"
    Monitor.Delete "e-field (f=Fc)"
    On Error GoTo 0
End Sub
