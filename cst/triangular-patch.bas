Option Explicit

Sub Main
    SetupParameters
    SetupProject
    DefineMaterials
    BuildGroundPlane
    BuildSubstrate
    BuildTriangularPatch
    BuildFeedLine
    CreatePort
    AddMonitors
    ConfigureSolver
End Sub

' Antenna dimensions
Sub SetupParameters
    StoreDoubleParameter "Tb", 37.60
    StoreDoubleParameter "Th", 29.38
    StoreDoubleParameter "Wg", 75.20
    StoreDoubleParameter "Lg", 58.76
    StoreDoubleParameter "Hs", 1.4
    StoreDoubleParameter "Ht", 0.036
    StoreDoubleParameter "Fw", 2.7
    StoreDoubleParameter "Gpf", 1.0
End Sub

' Units and frequency
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
        .Xmin "expanded open"
        .Xmax "expanded open"
        .Ymin "expanded open"
        .Ymax "expanded open"
        .Zmin "expanded open"
        .Zmax "expanded open"
    End With
End Sub

' FR-4 material
Sub DefineMaterials
    With Material
        .Reset
        .Name "FR4"
        .Type "Normal"
        .Epsilon "4.4"
        .Mue "1"
        .TanD "0.02"
        .Colour 0.94, 0.82, 0.76
        .Create
    End With
End Sub

' PEC ground
Sub BuildGroundPlane
    With Brick
        .Reset
        .Name "ground"
        .Component "antenna"
        .Material "PEC"
        .Xrange "-Wg/2", "Wg/2"
        .Yrange "-Lg/2", "Lg/2"
        .Zrange "-Ht", "0"
        .Create
    End With
End Sub

' FR-4 substrate
Sub BuildSubstrate
    With Brick
        .Reset
        .Name "substrate"
        .Component "antenna"
        .Material "FR4"
        .Xrange "-Wg/2", "Wg/2"
        .Yrange "-Lg/2", "Lg/2"
        .Zrange "0", "Hs"
        .Create
    End With
End Sub

' Isosceles triangle patch
Sub BuildTriangularPatch
    With Extrude
        .Reset
        .Name "patch"
        .Component "antenna"
        .Material "PEC"
        .Mode "pointlist"
        .Height "Ht"
        .Origin "0", "0", "Hs"
        .Uvector "1", "0", "0"
        .Vvector "0", "1", "0"
        .Point "-Tb/2", "-Th/3"
        .LineTo "Tb/2", "-Th/3"
        .LineTo "0", "2*Th/3"
        .Create
    End With
End Sub

' 50-ohm feed
Sub BuildFeedLine
    With Brick
        .Reset
        .Name "feed"
        .Component "antenna"
        .Material "PEC"
        .Xrange "-Fw/2", "Fw/2"
        .Yrange "-Lg/2", "-Th/3-Gpf"
        .Zrange "Hs", "Hs+Ht"
        .Create
    End With
End Sub

' Waveguide port
Sub CreatePort
    With Port
        .Reset
        .PortNumber "1"
        .NumberOfModes "1"
        .AdjustPolarization "False"
        .PolarizationAngle "0"
        .ReferencePlaneDistance "0"
        .TextSize "50"
        .Coordinates "Free"
        .Orientation "yneg"
        .PortOnBound "False"
        .ClipPickedPortToBound "False"
        .Xrange "-Fw/2-6*Hs", "Fw/2+6*Hs"
        .Yrange "-Lg/2", "-Lg/2"
        .Zrange "-Ht", "6*Hs"
        .Create
    End With
End Sub

' Field monitors
Sub AddMonitors
    With Monitor
        .Reset
        .Name "farfield (f=2.45)"
        .Domain "Frequency"
        .FieldType "Farfield"
        .MonitorValue "2.45"
        .Create
    End With

    With Monitor
        .Reset
        .Name "e-field (f=2.45)"
        .Domain "Frequency"
        .FieldType "Efield"
        .MonitorValue "2.45"
        .Create
    End With
End Sub

' Time-domain solver
Sub ConfigureSolver
    With MeshSettings
        .SetMeshType "Hex"
        .Set "Version", 1
    End With

    With Solver
        .FrequencyRange "1", "3"
        .Method "Hexahedral"
        .CalculationType "TD-S"
        .StimulationPort "All"
        .StimulationMode "All"
    End With
End Sub
