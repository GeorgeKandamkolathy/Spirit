from enum import auto
import os

from fpdf import FPDF
from datetime import date
import itertools


class PDF(FPDF):
    """
    Subclass of FPDF to define some of the standard sections of the reports.
    """

    def __init__(self, title: str='', title_font: str='Times',
            left_margin: float=10, right_margin: float=10,
            top_margin: float=10):
        """Sets some important metavariables.
        
        Args:
            title: The title to set for the report in the header.
            title_font: The font family for the title.
            left_margin: The margin from the left in mm.
            right_margin: The margin from the top in mm.
            top_margin: The margin from the top in mm.
        """

        super().__init__()

        # Set args as class attributes for the other functions of this class
        self.title = title
        self.title_font = title_font

        # Set margins for this pdf
        self.set_margins(left=left_margin, top=top_margin, 
                right=right_margin)


    def header(self, ln_break: int=20):
        """Defines the header for the pdf."""

        # Logo in top left corner
        self.image('data_science/dataclean/src/resources/images/orefoxlogo.png', y=15, w=45)

        # Display title
        self.set_font(self.title_font, 'B', size=20)
        self.cell(0, 10, self.title, align='R')

        # Set a line break after the header
        self.ln(ln_break)

    
    def footer(self):
        """Defines the footer for the pdf."""

        # 15mm from bottom
        self.set_y(-15)

        self.set_font(self.title_font, 'I')

        # Display a page count
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class ReportMaker:
    """Handles process of generating reports."""

    def __init__(self, temp_filepath: str='test/reports/temporary/',
            image_width: float=160, make_temp_dir: bool=True):

        if make_temp_dir:
            try:
                os.makedirs(temp_filepath)
            except FileExistsError:
                # If directory already exists, don't do anything
                pass

        self.temp_filepath = temp_filepath
        self.image_width = image_width

    def make_title(self, pdf, title: str, fontsize=14):
        """Function to make a title for a page."""
        pdf.set_font(pdf.title_font, 'B', size=fontsize)
        pdf.cell(0, 10, title, align='L')
        pdf.ln(10)
        pdf.set_font('Merriweather', '', 12)

    def get_x_value_image_centre(self, image_width: float):
        """Finds centre for an image. Useful for centering images.
        
        Takes an image's width and finds the horizontal coordinate for the
        top left by taking the middle of the document and taking half of the
        width from that number.

        Args:
            image_width: The width of the image in inches (matplotlib default).
        """

        # A4 pages are 210mm wide, with 10mm margins on either side
        midpoint = 95 # 190/2

        # Convert image width to mm and divide by two
        distance_from_midpoint = image_width/2

        return 10 + midpoint - distance_from_midpoint


    def title_page(self, pdf, title: str, tag_name: str):
        """Displays a title page for the given report.

        Args:
            pdf: The pdf to display in.
            title: The title of the report.
            body_info_filepath: The filepath for the body of the title page.
        """
        pdf.add_page()

        pdf.image('data_science/dataclean/src/resources/images/default.jpg', x=10 , y=45, w=75, h=175)

        pdf.ln(22)

        pdf.set_font(pdf.title_font, 'B', size=25) 
        pdf.set_x(90)
        pdf.multi_cell(40, h=10, txt=title, align='L')
        pdf.ln(10)
        pdf.set_font('Merriweather', '', 12)

        pdf.set_x(90)
        pdf.cell(30, h=5, txt="Date prepared: " + str(date.today()))
        pdf.ln(10)
        pdf.set_x(90)
        pdf.cell(30, h=5, txt="Tag: " + tag_name)

    def comment_summary(self, pdf):
        pdf.add_page()

        pdf.set_font(pdf.title_font, 'B', size=15) 
        pdf.set_text_color(0, 112, 192)
        pdf.cell(30, txt="Summary of Executed Methods:") 
        pdf.ln(10)
        pdf.set_font('Merriweather', '', 12)
        pdf.set_text_color(0, 0, 0)
        page = 3

        pdf.set_x(15)
        link = pdf.add_link()
        pdf.set_link(link=link, page=page)
        pdf.cell(30, txt="\u2022 Analyser Statistics........................................................................................................................." + str(page), link=link)
        pdf.ln(10)
        page += 1

    def comments(self, pdf, comments):
        """Helper function to display analyser.stats in report.
        
        Args:
            pdf: The pdf to display the stats in.
            analyser: The analyser to get the stats from.
        """
        pdf.add_page()

        pdf.set_font('Merriweather', '', size=14)
        pdf.set_text_color(0, 112, 192)
        pdf.ln(5)
        pdf.cell(30, txt="Summary of Analyser Stats:") 
        pdf.ln(10)
        pdf.set_font('Merriweather', '', 12)
        pdf.set_text_color(0, 0, 0)

        for number, comment in enumerate(comments):
            # Feature count
            pdf.set_font('Merriweather', '', size=14)
            pdf.cell(0, h=10, txt="Comment " + str(number) + ":", ln=1)
            pdf.set_font('Merriweather', '', size=12)
            pdf.multi_cell(0, h=10, txt=comment["comment"])
    
    def make_comment_report(self, comments, filepath: str, tag_name: str,
            display_text: bool=True):
        """Makes a report based on analysis done.
        
        Args:
            analyser: The analyser to generate a report on.
            filepath: The output filepath for the pdf report.
        """

        pdf = PDF(title='Comment Report')
        pdf.alias_nb_pages()
        pdf.add_font('Merriweather', fname='data_science/dataclean/src/resources/fonts/Merriweather-Regular.ttf', uni=True)
        pdf.set_font('Merriweather', '', 12)

        # Title page
        self.title_page(pdf=pdf, title='Comment Report', tag_name=tag_name)

        self.comment_summary(pdf=pdf)
        
        self.comments(pdf=pdf, comments=comments)

        pdf.output(filepath, 'F')

        # Clear temp dir
        #files = glob.glob(self.temp_filepath + '/*')
        #for f in files:
            #os.remove(f)



