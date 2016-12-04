"""Generate a sequence alignment dot plot"""

from ch11_plot import Plot

class DotPlot(Plot):

# Overridden class field values

    sans_faces = ('Helvetica Narrow', 'Futura',
                  'Helvetica', 'Arial', 'sans-serif')
    PlotName = 'Dot Plot'
    x_tic_width = y_tic_width = 3


# Class fields for this class

    title_font_size = 12

    top_title_margin = round(title_font_size / 2)
    name_height = 22                # x 2 if 2 names
    axis_width = 3                  # if axis option is specified

    # These are the defaults for showing the plot without axes;
    # if options.axes is true, they will be reset in setup_parameters
    left_title_margin = 10
    x_label_height = y_label_width = 4

    # so I can take snapshots without the lower-right corner dragger
    ipad_right = 12
    #keep track of non - matches
    realMatches = 0

    def __init__(self, seq1, seq2, seqname1 = '', seqname2='',
                 window=1, threshold=1, with_axes=False, dot_size=1,
                 # super parameters:
                 window_title=None,
                 scale=1.0, ps_filename=None, ps_scale = 1.0):
        self.seq1 = seq1
        self.seq2 = seq2
        self.seqname1 = seqname1
        self.seqname2 = seqname2
        self.window = window
        self.threshold = threshold
        self.with_axes = with_axes
        self.dot_size = dot_size
        self.window_title = window_title
        # calling super init last because it calls some methods
        # that need the fields
        super().__init__(window_title, scale, ps_filename, ps_scale)

    def setup_fonts(self):
        super().setup_fonts()
        self.add_font('title', self.findfont(self.sans_faces,
                                             self.title_font_size))

    def setup_data(self):
        self.points = self.compute_points()
        self.max_x = max(self.points, key=lambda pt: pt[0])[0]
        self.max_y = max(self.points, key=lambda pt: pt[1])[1]

    def compute_points(self):
        pts = []
        for y in range(1 + len(self.seq2) - self.window):
            for x in range(1 + len(self.seq1) - self.window):
                if self.seq2[y] != "-":
                    if self.test_point(self.seq1, x, self.seq2, y):
                            pts.append((x, y))
                            self.realMatches = self.realMatches + 1
        for y in range(1 + len(self.seq2) - self.window):
            for x in range(1 + len(self.seq1) - self.window):
                if self.seq2[y] == "-":
                        if self.test_point(self.seq1, x, self.seq2, y):
                                pts.append((x, y))
        return pts

    def test_point(self, seq1, x, seq2, y):
        cnt = 0
        for n in range(self.window):
            if seq1[x+n] == seq2[y+n]:
                cnt += 1
        return cnt >= self.threshold

    def setup_parameters(self):
        super().setup_parameters()

        if not self.with_axes:
            self.x_axis_width = self.y_axis_width = 0
        else:
            self.x_axis_width = self.axis_width
            self.y_axis_width = self.axis_width
            self.x_label_height = self.x_tic_length + 5
            self.y_label_width = self.y_tic_length + 5
            self.left_title_margin = \
                self.left_title_margin + self.y_label_width

    def get_plot_dimensions(self):
        return  (round((self.max_x + self.window) * self.scale),
                 round((self.max_y + self.window) * self.scale) +
                 self.y_tic_width,
                 self.y_label_width,
                 self.ipad_right,
                 5 + self.name_height *
                 (bool(self.seqname1) + bool(self.seqname2)),
                 self.x_label_height)

    def draw(self):
        super().draw()
        self.draw_titles()

    def draw_titles(self):
        if self.seqname1 and self.seqname2:
            self.draw_title('x = ' + self.seqname1,
                            self.top_title_margin)
            self.draw_title('y = ' + self.seqname2,
                            self.top_title_margin +
                            self.title_font_size + 6)

        elif self.seqname1 or self.seqname2:
            self.draw_title(self.seqname1 or self.seqname2,
                            self.top_title_margin)

    def draw_title(self, title, ypos):
        self.draw_text_unscaled(self.left_title_margin,
                                ypos, title, 'title', 'nw')

    def draw_x_axis_labels(self):
        adjust = 0#round((self.x_tic_width)/2)
        for x in range(100, self.plot_width+1, 100):
            self.draw_line(x - adjust,
                           -self.x_axis_width,
                           x - adjust,
                           -(self.x_axis_width + self.x_tic_length),
                           self.x_tic_width)

    def draw_y_axis_labels(self):
        adjust = round((self.y_tic_width - 1)/2)
        for y in range(100, self.plot_height+1, 100):
            self.draw_line(-self.y_axis_width,
                           y + adjust,
                           -(self.y_axis_width + self.y_tic_length),
                           y + adjust,
                           self.y_tic_width)

    def draw_plot(self):
        pointsDrawn = 0
        for pt in self.points:
           if pointsDrawn <= self.realMatches:
                self.draw_oval(
                    pt[0],
                    self.plot_height - self.window - pt[1],
                    pt[0] + self.dot_size - 1,
                    self.plot_height - self.window - pt[1] - self.dot_size - 1)
                pointsDrawn = pointsDrawn + 1
           else:
                self.draw_oval2(
                     pt[0],
                     self.plot_height - self.window - pt[1],
                     pt[0] + self.dot_size - 1,
                     self.plot_height - self.window - pt[1] - self.dot_size - 1)
