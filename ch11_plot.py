#!/usr/bin/env python3
### The Plot class used in Chapter 11's Tkinter examples

"""Superclass for Tk-based plotting classes"""

import sys
import os
import re

try:
    from pyutil3 import descr
except:
    pass

import tkinter
from tkinter.font import Font

import sys

class SubclassResponsibility(Exception):
    pass

class Plot:

    """Abstract framework class for tkinter plots.

    __init__ arguments and default values:
        windowtitle = None         title for the window
        scale = 1.0                scale of the plot
        ps_filename = None         if provided, Postscript file will
                                   be generated
        ps_scale = 1.0             scale of the Postscript output
                                   relative to the scale of the plot

All methods except one are implemented: subclasses can override or
add methods and class fields as desired. The unimplemented method is
get_plot_dimensions(), which must return the values describing the
geometry of the plot relative to its canvas:

    (width, height, leftspace, rightspace, topspace, bottomspace)

"Space" means distance from the corresponding edge of the canvas to
the actual plot. The reason for the spaces is both for aesthetics and
to allow the canvas to draw text and other graphic objects in areas
outside of the plot itself.

The x, y origin will be at
        (leftspace+x_axis_width, bottomspace+x_axis_width)
relative to the edges left and bottom edges of the canvas.  Points
with y > 0 are above the x-axis, y < 0 above. This is the opposite of
tkinter's use of y=0 as top.  That is to say, methods draw using the
natural coordinate system rather than "inverting" the y values.

This class provides several canvas drawing methods that are somewhat
more convenient to use than the equivalent tkinter.Canvas methods.
The following adjust the points according to the value of scale:

    def draw_line(self, x1, y1, x2, y2, width=1, fill='black'):
    def draw_oval(self, x1, y1, x2, y2, width=1, fill='black'):
    def draw_rectangle(self, x, y, w, h, fill='black'):
    def draw_text(self, x, y, text, font, anchor='center', fill='black'):

The following do not adjust the points for scale.
    def draw_line_unscaled(self, x1, y1, x2, y2, width=1, fill='black'):
    def draw_text_unscaled(self, x1, y1, text, font, anchor, fill='black'):

This class adds a single component to the window: a canvas.
If other components are desired -- Labels, Frames, etc. --
the subclass should override create_widgets(). All that this class's
implementation of create_widgets does is call create_canvas, so there
isn't really any need to call super().create_widgets() in the
subclass's definition of create_widgets.

"""

    PlotName = 'Plot'

## override these in subclasses as desired

    # unscaled space around the canvas
    canvas_pad_x = canvas_pad_y = canvas_border = 0
    x_axis_width = y_axis_width = 2
    x_axis_font_size = y_axis_font_size = 12
    x_tic_length = y_tic_length = 12
    x_tic_width = y_tic_width = 1
    canvas_background = 'white'

    serif_faces = ('Palatino', 'Georgia', 'Times')
    sans_faces = ('Futura', 'Gill Sans', 'Verdana', 'Helvetica', 'Arial')
    mono_faces = ('Liberation Mono Regular',
                  'Lucida Sans Typerwriter',
                  'DejaVu Sans Mono',
                  'Bitstream Sans Mono',
                  'Courier')

    Instances = []
    PlotNumber = 0


## Utility Class Methods

    @classmethod
    def file_name_only(self, path):
        return os.path.splitext(os.path.split(path)[1])[0]

    @classmethod
    def NextPlotNumber(self):
        self.PlotNumber += 1
        return str(self.PlotNumber)

    @classmethod
    def closeall(self):
        for inst in self.Instances:
            inst.close()

## Utility Instance Methods

    def findfont(self, faces, sz=11, boldflg=False, italicflg=False):
        for face in faces:
            font = Font(root=self.root,
                        family=face,
                        size=sz,
                        weight = 'bold' if boldflg else 'normal',
                        slant = 'italic' if italicflg else 'roman')
            if face == font.actual('family'):
                return font

# Access
    def get_root(self):
        return self.root

    def add_font(self, name, font):
        self.fonts[name] = font

    def get_font(self, name):
        return self.fonts.get(name, None)

## Fundamental methods

    def __init__(self, windowtitle=None,
                 scale=1.0, ps_filename=None, ps_scale = 1.0):
        self.Instances.append(self)
        self.fonts = {}
        self.window_title = (windowtitle or
                             self.PlotName + ' ' + self.NextPlotNumber())
        self.root = tkinter.Tk()
        self.root.title(self.window_title)

        self.scale = scale
        self.ps_filename = ps_filename
        self.ps_scale = ps_scale

        self.setup()

    def __str__(self):
        return self.window_title

## Layout Framework

    def setup(self):
        self.setup_fonts()
        self.setup_data()
        self.setup_parameters()
        (self.plot_width, self.plot_height,
         self.plot_left_margin, self.plot_right_margin,
         self.plot_top_margin, self.plot_bottom_margin) = \
            self.get_plot_dimensions()
        self.determine_layout()

    def setup_fonts(self):
        self.add_font('x', self.findfont(self.sans_faces,
                                         self.x_axis_font_size,
                                           True))
        self.add_font('y', self.findfont(self.sans_faces,
                                         self.y_axis_font_size,
                                         True))
    def setup_data(self):
        pass

    def setup_parameters(self):
        pass

    def get_plot_dimensions(self):
        """Return a tuple of six values describing the placement and
        dimensions of the plot within the canvas:
        (width, height, left, right, top, bottom)"""
        raise SubclassResponsibility(
            "Subclass must implement get_plot_dimensions")

    def determine_layout(self):
        self.origin_x = self.plot_left_margin + self.y_axis_width
        self.origin_y = self.plot_top_margin + self.plot_height
        self.canvas_width = (self.plot_left_margin +
                             self.y_axis_width +
                             self.plot_width +
                             self.plot_right_margin)
        self.canvas_height = (self.plot_top_margin +
                              self.plot_height +
                              self.x_axis_width +
                              self.plot_bottom_margin)

## Drawing Framework

    def execute(self):
        self.create_widgets()
        self.draw()
        if self.ps_filename:
            self.write_postscript()
        return self

    def close(self):
        if self in self.Instances:
            self.Instances.remove(self)
        if self.root:
            self.root.destroy()

    def create_widgets(self):
        self.create_canvas()

    def create_canvas(self):
        self.canvas = tkinter.Canvas(self.root,
                                     width=self.canvas_width,
                                     height=self.canvas_height,
                                     bd=self.canvas_border,
                                     bg=self.canvas_background)
        self.canvas.pack(side='top',
                         padx=self.canvas_pad_x,
                         pady=self.canvas_pad_y)

    def draw(self):
        self.draw_axes()
        self.draw_plot()

    def draw_axes(self):
        xadjust = round(self.x_axis_width / 2)
        yadjust = round(self.y_axis_width  / 2)
        if self.x_axis_width:
            self.draw_line(-xadjust, -yadjust,
                           self.plot_width - xadjust, -yadjust,
                           self.x_axis_width)
            self.draw_x_axis_labels()
        if self.y_axis_width:
            self.draw_line(-xadjust, -yadjust,
                           -xadjust, self.plot_height - yadjust,
                           self.y_axis_width)
            self.draw_y_axis_labels()
        self.draw_x_tics()
        self.draw_y_tics()

    def draw_x_tics(self):
        pass

    def draw_y_tics(self):
        pass

    def draw_x_axis_labels(self):
        pass

    def draw_y_axis_labels(self):
        pass

    def draw_plot(self):
        raise SubclassResponsibility(
            "Subclass must implement draw_plot")

    def write_postscript(self):
        self.canvas.postscript(
            file=self.ps_filename,
            width=self.canvas_width,
            height=self.canvas_height,
            pagewidth=self.ps_scale*self.canvas_width,
            colormode='gray')
        print('wrote', self.ps_filename, file=sys.stderr)


## Drawing functions
## y=0 at canvas x-axis, not top

    def draw_line(self, x1, y1, x2, y2, width=1, fill='black'):
        """Draw line on canvas relative to canvas origin and scale"""
        self.canvas.create_line(self.origin_x + round(x1*self.scale),
                                self.origin_y - round(y1*self.scale),
                                self.origin_x + round(x2*self.scale),
                                self.origin_y - round(y2*self.scale),
                                width=round(width*self.scale),
                                fill=fill,
                                capstyle='projecting',
                                )

    def draw_line_unscaled(self, x1, y1, x2, y2, width=1, fill='black'):
        """Draw line on canvas in unscaled coordinates, unscaled"""
        self.canvas.create_line(self.origin_x + x1,
                                self.origin_y - y1,
                                self.origin_x + x2,
                                self.origin_y - y2,
                                width=width,
                                fill=fill,
                                )

    def draw_oval(self, x1, y1, x2, y2, width=1, fill='black'):
        """Draw oval on canvas relative to canvas origin and scale"""
        self.canvas.create_oval(self.origin_x + round(x1*self.scale),
                                self.origin_y - round(y1*self.scale),
                                self.origin_x + round(x2*self.scale),
                                self.origin_y - round(y2*self.scale),
                                width=round(width*self.scale),
                                fill=fill,
                                )
    def draw_oval2(self, x1, y1, x2, y2, width=1, fill='red'):
        """Draw oval on canvas relative to canvas origin and scale"""
        self.canvas.create_oval(self.origin_x + round(x1*self.scale),
                                self.origin_y - round(y1*self.scale),
                                self.origin_x + round(x2*self.scale),
                                self.origin_y - round(y2*self.scale),
                                width=round(width*self.scale),
                                fill=fill,
                                outline=fill,
                                )

    def draw_rectangle(self, x, y, w, h, fill='black'):
        """Draw rectangle on canvas relative to canvas origin and scale"""
        x = self.origin_x + x*self.scale
        y = self.origin_y - y*self.scale
        self.canvas.create_rectangle(x, y, x+w, y-h, fill=fill)

    def draw_text(self, x, y, txt, fontname,
                  anchor='center', fill='black'):
        """Draw text on canvas relative to canvas origin and scale"""
        self.canvas.create_text(
                self.origin_x + round(x*self.scale),
                self.origin_y - round(y*self.scale),
                text=txt,
                font=self.get_font(fontname),
                anchor=anchor,
                fill=fill,
                )

    def draw_text_unscaled(self, x1, y1, txt, fontname,
                           anchor, fill='black'):
        self.canvas.create_text(x1, y1, text=txt,
                                font=self.get_font(fontname),
                                anchor=anchor, fill=fill,
                                )


    def describe_font(self, name):
        font = self.get_font(name)
        print(font.actual('family'),
              font.actual('size'),
              font.actual('weight'),
              font.actual('slant')
              )

    def describe_fonts(self):
        for k in sorted(self.fonts.keys()):
            print('{:12}'.format(k), end='\t')
            self.describe_font(k)

    def show(self):
        descr(self)

if __name__ == '__main__':
    # check that all the Framework pieces are here and connected appropriately

    class EmptyPlot(Plot):
        canvas_pad_x = 20
        canvas_pad_y = 5
        canvas_background = 'gray90'
        def __init__(self):
            super().__init__(ps_filename='temp/EmptyPlot.ps', ps_scale=0.6)

        def get_plot_dimensions(self):
            return 150, 150, 20, 20, 10, 10
        def draw_plot(self):
            self.draw_line(0, 0, 100, 100)

    try:
        plot = None
        plot = EmptyPlot()
        plot.execute()
        input('Press Return to close ')
    finally:
        if plot:
            plot.close()


"""
Hierarchy of method calls:
Key:
    x subclass would normally NOT implement (framework definition)
    ! subclass MUST OVERRIDE
    * subclass MUST EXTEND
    + subclass MAY EXTEND
    / subclass MAY EXTEND or OVERRIDE
2    - subclass MAY OVERRIDE (empty methods for convenience and clarity)

Utility Methods:

x   NextPlotNumber
x   closeall
x   findfont

Access
x   get_root
x   add_font
x   get_font
/   __str__


Layout Framework
*   __init__    tracks instance, creates Tk root, stores parameters
x       setup
+           setup_fonts
-           setup_data
-           setup_parameters
!           get_plot_dimensions
x           determine_layout   canvas width & height, origin x,y

Drawing Framework
x   execute
/       create_widgets
x           create_canvas
x       draw
x       draw_axes
-           draw_x_tics
-           draw_y_tics
-           draw_x_axis_labels
-           draw_y_axis_labels
!       draw_plot
x   close

Drawing Functions
x   draw_line
x   draw_line_unscaled
x   draw_oval
x   draw_rectangle
x   draw_text
x   draw_text_unscaled

"""
