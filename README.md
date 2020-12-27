# ink2raster
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
https://studio.youtube.com/video/4qWsX7bx_hE
