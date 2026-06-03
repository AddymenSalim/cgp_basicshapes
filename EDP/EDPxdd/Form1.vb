Public Class frmTrafficSystem
    ' Timer for controlling traffic light cycles
    Private tmrTrafficControl As New Timer()

    ' Traffic light state variables
    Private currentPhase As Integer = 0
    Private phaseTimer As Integer = 0
    Private Const PHASE_DURATION As Integer = 30 ' 3 seconds at 100ms intervals
    Private Const YELLOW_DURATION As Integer = 10 ' 1 second for yellow light
    Private Const PEDESTRIAN_DURATION As Integer = 20 ' 2 seconds for pedestrian crossing
    Private isSimulationRunning As Boolean = False

    ' Pedestrian request flags
    Private pedestrianRequests(3) As Boolean ' 0=North, 1=South, 2=East, 3=West
    Private pedestrianActive(3) As Boolean
    Private pedestrianTimer(3) As Integer

    ' Traffic light arrays - all intersections for each direction
    ' Structure: trafficLights(direction, intersection, light) 
    ' direction: 0=North, 1=South, 2=East, 3=West
    ' intersection: 0-3 for each numbered intersection
    ' light: 0=Green, 1=Yellow, 2=Red
    Private trafficLights(3, 3, 2) As Panel

    ' Control buttons
    Private btnStart As New Button()
    Private btnStop As New Button()
    Private btnReset As New Button()

    Private Sub frmTrafficSystem_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        ' Initialize all traffic light panel references
        InitializeTrafficLights()

        ' Initialize pedestrian arrays
        For i = 0 To 3
            pedestrianRequests(i) = False
            pedestrianActive(i) = False
            pedestrianTimer(i) = 0
        Next

        ' Configure timer
        tmrTrafficControl.Interval = 100 ' 100ms intervals
        AddHandler tmrTrafficControl.Tick, AddressOf TimerTick

        ' Initialize control buttons
        InitializeControlButtons()

        ' Set initial traffic light state
        AllTrafficLightsOff()
    End Sub

    Private Sub InitializeTrafficLights()
        ' North Intersections (N1, N2, N3, N4)
        trafficLights(0, 0, 0) = pnlN1Green
        trafficLights(0, 0, 1) = pnlN1Yellow
        trafficLights(0, 0, 2) = pnlN1Red

        trafficLights(0, 1, 0) = pnlN2Green
        trafficLights(0, 1, 1) = pnlN2Yellow
        trafficLights(0, 1, 2) = pnlN2Red

        trafficLights(0, 2, 0) = pnlN3Green
        trafficLights(0, 2, 1) = pnlN3Yellow
        trafficLights(0, 2, 2) = pnlN3Red

        trafficLights(0, 3, 0) = pnlN4Green
        trafficLights(0, 3, 1) = pnlN4Yellow
        trafficLights(0, 3, 2) = pnlN4Red

        ' South Intersections (S1, S2, S3, S4)
        trafficLights(1, 0, 0) = pnlS1Green
        trafficLights(1, 0, 1) = pnlS1Yellow
        trafficLights(1, 0, 2) = pnlS1Red

        trafficLights(1, 1, 0) = pnlS2Green
        trafficLights(1, 1, 1) = pnlS2Yellow
        trafficLights(1, 1, 2) = pnlS2Red

        trafficLights(1, 2, 0) = pnlS3Green
        trafficLights(1, 2, 1) = pnlS3Yellow
        trafficLights(1, 2, 2) = pnlS3Red

        trafficLights(1, 3, 0) = pnlS4Green
        trafficLights(1, 3, 1) = pnlS4Yellow
        trafficLights(1, 3, 2) = pnlS4Red

        ' East Intersections (E1, E2, E3, E4)
        trafficLights(2, 0, 0) = pnlE1Green
        trafficLights(2, 0, 1) = pnlE1Yellow
        trafficLights(2, 0, 2) = pnlE1Red

        trafficLights(2, 1, 0) = pnlE2Green
        trafficLights(2, 1, 1) = pnlE2Yellow
        trafficLights(2, 1, 2) = pnlE2Red

        trafficLights(2, 2, 0) = pnlE3Green
        trafficLights(2, 2, 1) = pnlE3Yellow
        trafficLights(2, 2, 2) = pnlE3Red

        trafficLights(2, 3, 0) = pnlE4Green
        trafficLights(2, 3, 1) = pnlE4Yellow
        trafficLights(2, 3, 2) = pnlE4Red

        ' West Intersections (W1, W2, W3, W4)
        trafficLights(3, 0, 0) = pnlW1Green
        trafficLights(3, 0, 1) = pnlW1Yellow
        trafficLights(3, 0, 2) = pnlW1Red

        trafficLights(3, 1, 0) = pnlW2Green
        trafficLights(3, 1, 1) = pnlW2Yellow
        trafficLights(3, 1, 2) = pnlW2Red

        trafficLights(3, 2, 0) = pnlW3Green
        trafficLights(3, 2, 1) = pnlW3Yellow
        trafficLights(3, 2, 2) = pnlW3Red

        trafficLights(3, 3, 0) = pnlW4Green
        trafficLights(3, 3, 1) = pnlW4Yellow
        trafficLights(3, 3, 2) = pnlW4Red
    End Sub

    Private Sub InitializeControlButtons()
        ' Calculate center position for buttons (below title)
        Dim buttonWidth As Integer = 110
        Dim spacing As Integer = 15
        Dim totalWidth As Integer = (buttonWidth * 3) + (spacing * 2)
        Dim startX As Integer = ((Me.ClientSize.Width - totalWidth) \ 2) - 40

        ' START Button
        btnStart.Text = "▶ START"
        btnStart.Font = New Font("Segoe UI", 11, FontStyle.Bold)
        btnStart.Size = New Size(buttonWidth, 45)
        btnStart.Location = New Point(startX, 67)
        btnStart.BackColor = Color.LimeGreen
        btnStart.ForeColor = Color.White
        btnStart.Cursor = Cursors.Hand
        AddHandler btnStart.Click, AddressOf btnStart_Click
        Me.Controls.Add(btnStart)

        ' STOP Button
        btnStop.Text = "⏸ STOP"
        btnStop.Font = New Font("Segoe UI", 11, FontStyle.Bold)
        btnStop.Size = New Size(buttonWidth, 45)
        btnStop.Location = New Point(startX + buttonWidth + spacing, 67)
        btnStop.BackColor = Color.OrangeRed
        btnStop.ForeColor = Color.White
        btnStop.Enabled = False
        btnStop.Cursor = Cursors.Hand
        AddHandler btnStop.Click, AddressOf btnStop_Click
        Me.Controls.Add(btnStop)

        ' RESET Button
        btnReset.Text = "↻ RESET"
        btnReset.Font = New Font("Segoe UI", 11, FontStyle.Bold)
        btnReset.Size = New Size(buttonWidth, 45)
        btnReset.Location = New Point(startX + (buttonWidth + spacing) * 2, 67)
        btnReset.BackColor = Color.RoyalBlue
        btnReset.ForeColor = Color.White
        btnReset.Cursor = Cursors.Hand
        AddHandler btnReset.Click, AddressOf btnReset_Click
        Me.Controls.Add(btnReset)
    End Sub

    Private Sub TimerTick(sender As Object, e As EventArgs)
        If Not isSimulationRunning Then Return

        phaseTimer += 1

        ' Update pedestrian timers
        For i = 0 To 3
            If pedestrianActive(i) Then
                pedestrianTimer(i) -= 1
                If pedestrianTimer(i) <= 0 Then
                    pedestrianActive(i) = False
                End If
            End If
        Next

        ' Check if phase should advance
        If phaseTimer >= PHASE_DURATION Then
            phaseTimer = 0
            currentPhase = (currentPhase + 1) Mod 4
        End If

        UpdateTrafficLights()
    End Sub

    Private Sub UpdateTrafficLights()
        ' Turn off all lights first
        For d = 0 To 3
            For i = 0 To 3
                For l = 0 To 2
                    trafficLights(d, i, l).BackColor = Color.DarkGray
                Next
            Next
        Next

        ' Determine which directions get green/yellow/red based on phase
        ' Phase 0: North and South get GREEN, East and West get RED
        ' Phase 1: North and South get YELLOW, East and West get RED
        ' Phase 2: East and West get GREEN, North and South get RED
        ' Phase 3: East and West get YELLOW, North and South get RED

        Select Case currentPhase
            Case 0
                ' North: GREEN, South: GREEN, East: RED, West: RED
                SetDirectionLight(0, Color.Green) ' North Green
                SetDirectionLight(1, Color.Green) ' South Green
                SetDirectionLight(2, Color.Red)   ' East Red
                SetDirectionLight(3, Color.Red)   ' West Red

            Case 1
                ' North: YELLOW, South: YELLOW, East: RED, West: RED
                SetDirectionLight(0, Color.Yellow) ' North Yellow
                SetDirectionLight(1, Color.Yellow) ' South Yellow
                SetDirectionLight(2, Color.Red)    ' East Red
                SetDirectionLight(3, Color.Red)    ' West Red

            Case 2
                ' East: GREEN, West: GREEN, North: RED, South: RED
                SetDirectionLight(2, Color.Green) ' East Green
                SetDirectionLight(3, Color.Green) ' West Green
                SetDirectionLight(0, Color.Red)   ' North Red
                SetDirectionLight(1, Color.Red)   ' South Red

            Case 3
                ' East: YELLOW, West: YELLOW, North: RED, South: RED
                SetDirectionLight(2, Color.Yellow) ' East Yellow
                SetDirectionLight(3, Color.Yellow) ' West Yellow
                SetDirectionLight(0, Color.Red)    ' North Red
                SetDirectionLight(1, Color.Red)    ' South Red
        End Select
    End Sub

    Private Sub SetDirectionLight(directionIndex As Integer, lightColor As Color)
        ' Set the appropriate light for all intersections in a direction
        Dim lightIndex As Integer = 2 ' Default to Red

        Select Case lightColor
            Case Color.Green
                lightIndex = 0
            Case Color.Yellow
                lightIndex = 1
            Case Color.Red
                lightIndex = 2
        End Select

        ' Apply to all 4 intersections in this direction
        For intersection = 0 To 3
            trafficLights(directionIndex, intersection, lightIndex).BackColor = lightColor
        Next
    End Sub

    Private Sub AllTrafficLightsOff()
        ' Turn off all lights
        For d = 0 To 3
            For i = 0 To 3
                For l = 0 To 2
                    trafficLights(d, i, l).BackColor = Color.DarkGray
                Next
            Next
        Next
    End Sub

    ' Pedestrian button event handlers - All North directions
    Private Sub btnN1Pedestrian_Click(sender As Object, e As EventArgs) Handles btnN1Pedestrian.Click
        HandlePedestrianRequest(0)
    End Sub

    Private Sub btnN2Pedestrian_Click(sender As Object, e As EventArgs) Handles btnN2Pedestrian.Click
        HandlePedestrianRequest(0)
    End Sub

    Private Sub btnN3Pedestrian_Click(sender As Object, e As EventArgs) Handles btnN3Pedestrian.Click
        HandlePedestrianRequest(0)
    End Sub

    Private Sub btnN4Pedestrian_Click(sender As Object, e As EventArgs) Handles btnN4Pedestrian.Click
        HandlePedestrianRequest(0)
    End Sub

    ' Pedestrian button event handlers - All South directions
    Private Sub btnS1Pedestrian_Click(sender As Object, e As EventArgs) Handles btnS1Pedestrian.Click
        HandlePedestrianRequest(1)
    End Sub

    Private Sub btnS2Pedestrian_Click(sender As Object, e As EventArgs) Handles btnS2Pedestrian.Click
        HandlePedestrianRequest(1)
    End Sub

    Private Sub btnS3Pedestrian_Click(sender As Object, e As EventArgs) Handles btnS3Pedestrian.Click
        HandlePedestrianRequest(1)
    End Sub

    Private Sub btnS4Pedestrian_Click(sender As Object, e As EventArgs) Handles btnS4Pedestrian.Click
        HandlePedestrianRequest(1)
    End Sub

    ' Pedestrian button event handlers - All East directions
    Private Sub btnE1Pedestrian_Click(sender As Object, e As EventArgs) Handles btnE1Pedestrian.Click
        HandlePedestrianRequest(2)
    End Sub

    Private Sub btnE2Pedestrian_Click(sender As Object, e As EventArgs) Handles btnE2Pedestrian.Click
        HandlePedestrianRequest(2)
    End Sub

    Private Sub btnE3Pedestrian_Click(sender As Object, e As EventArgs) Handles btnE3Pedestrian.Click
        HandlePedestrianRequest(2)
    End Sub

    Private Sub btnE4Pedestrian_Click(sender As Object, e As EventArgs) Handles btnE4Pedestrian.Click
        HandlePedestrianRequest(2)
    End Sub

    ' Pedestrian button event handlers - All West directions
    Private Sub btnW1Pedestrian_Click(sender As Object, e As EventArgs) Handles btnW1Pedestrian.Click
        HandlePedestrianRequest(3)
    End Sub

    Private Sub btnW2Pedestrian_Click(sender As Object, e As EventArgs) Handles btnW2Pedestrian.Click
        HandlePedestrianRequest(3)
    End Sub

    Private Sub btnW3Pedestrian_Click(sender As Object, e As EventArgs) Handles btnW3Pedestrian.Click
        HandlePedestrianRequest(3)
    End Sub

    Private Sub btnW4Pedestrian_Click(sender As Object, e As EventArgs) Handles btnW4Pedestrian.Click
        HandlePedestrianRequest(3)
    End Sub

    Private Sub HandlePedestrianRequest(direction As Integer)
        ' Set pedestrian request and activate crossing
        If Not pedestrianActive(direction) Then
            pedestrianRequests(direction) = True
            pedestrianActive(direction) = True
            pedestrianTimer(direction) = PEDESTRIAN_DURATION
        End If
    End Sub

    Private Sub lblTitle_Click(sender As Object, e As EventArgs) Handles lblTitle.Click
        ' Title label - no action needed
    End Sub

    ' Control Button Event Handlers
    Private Sub btnStart_Click(sender As Object, e As EventArgs)
        If Not isSimulationRunning Then
            isSimulationRunning = True
            tmrTrafficControl.Start()
            btnStart.Enabled = False
            btnStop.Enabled = True
            UpdateTrafficLights()
        End If
    End Sub

    Private Sub btnStop_Click(sender As Object, e As EventArgs)
        If isSimulationRunning Then
            isSimulationRunning = False
            tmrTrafficControl.Stop()
            btnStart.Enabled = True
            btnStop.Enabled = False
        End If
    End Sub

    Private Sub btnReset_Click(sender As Object, e As EventArgs)
        ' Stop the simulation
        isSimulationRunning = False
        tmrTrafficControl.Stop()

        ' Reset all variables
        currentPhase = 0
        phaseTimer = 0

        ' Reset pedestrian arrays
        For i = 0 To 3
            pedestrianRequests(i) = False
            pedestrianActive(i) = False
            pedestrianTimer(i) = 0
        Next

        ' Turn off all lights
        AllTrafficLightsOff()

        ' Reset button states
        btnStart.Enabled = True
        btnStop.Enabled = False
    End Sub
End Class
