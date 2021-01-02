# inkscape raster2gcode
Extension for Inkscape to convert an 8-Bit BW picture to gcode for laser plotter.
Plotter used is a 15Watt grbl 1.1 laser.

Copy all files into the Inkscape extension folder. Under Ubuntu for example ~/.config/inkscape/extensions

Tested with 15W China Laser, grbl 1.1, arduino nano
1) Create 8-Bit BW PNG picture file
2) Import into Inkscape
3) Extension -> Inkraster2Gcode
4) Set params
5) Create PNG preview and gcode file

Needs: png.py

Operation;
The orig PNG file is transformed by inkscape to wanted size and then
read back by png.py into workking matrix.
Matrix X-row is laser scan- and burnline
The gcode file uses a general speed set and varies the burn intensity
by {S} param. This is needed because when using M4 and M5 the movement
is shattering due the acceleration and deceleration from burn px to burn px.

Example video:
https://m.youtube.com/watch?v=4qWsX7bx_hE

Laser settings i used:
$0 = 10    (Step pulse time, microseconds)
$1 = 25    (Step idle delay, milliseconds)
$2 = 0    (Step pulse invert, mask)
$3 = 0    (Step direction invert, mask)
$4 = 0    (Invert step enable pin, boolean)
$5 = 0    (Invert limit pins, boolean)
$6 = 0    (Invert probe pin, boolean)
$10 = 1    (Status report options, mask)
$11 = 0.010    (Junction deviation, millimeters)
$12 = 0.002    (Arc tolerance, millimeters)
$13 = 0    (Report in inches, boolean)
$20 = 0    (Soft limits enable, boolean)
$21 = 0    (Hard limits enable, boolean)
$22 = 0    (Homing cycle enable, boolean)
$23 = 0    (Homing direction invert, mask)
$24 = 25.000    (Homing locate feed rate, mm/min)
$25 = 500.000    (Homing search seek rate, mm/min)
$26 = 250    (Homing switch debounce delay, milliseconds)
$27 = 1.000    (Homing switch pull-off distance, millimeters)
$30 = 1000    (Maximum spindle speed, RPM)
$31 = 0    (Minimum spindle speed, RPM)
$32 = 1    (Laser-mode enable, boolean)
$100 = 80.000    (X-axis travel resolution, step/mm)
$101 = 80.000    (Y-axis travel resolution, step/mm)
$102 = 250.000    (Z-axis travel resolution, step/mm)
$110 = 2000.000    (X-axis maximum rate, mm/min)
$111 = 2000.000    (Y-axis maximum rate, mm/min)
$112 = 500.000    (Z-axis maximum rate, mm/min)
$120 = 200.000    (X-axis acceleration, mm/sec^2)
$121 = 200.000    (Y-axis acceleration, mm/sec^2)
$122 = 10.000    (Z-axis acceleration, mm/sec^2)
$130 = 390.000    (X-axis maximum travel, millimeters)
$131 = 300.000    (Y-axis maximum travel, millimeters)
$132 = 200.000    (Z-axis maximum travel, millimeters)
