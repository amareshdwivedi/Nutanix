'''
Created on Oct 8, 2014

@author: krishnamurthy_b
'''
# -*- coding: utf-8 -*-
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch, letter, cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Image, FrameBreak, Paragraph
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
import time
import string
import os

styles = getSampleStyleSheet()
def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Header
        header = Image('nutanixlogo.png', height=0.50 * inch, width=5 * cm)
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
 
        # Footer
        footer = Paragraph('Tel: 1 (855) 688-2649 | Fax: 1 (408) 916-4039 | Email: info@nutanix.com. &copy 2014 Nutanix, Inc. All Rights Reserved.', styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
 
        # Release the canvas
        canvas.restoreState()

def PDFReportGenerator(resultJson):
    #print "Hit PDFReportGenerator "
    #print "JSON STRING : ", resultJson
    
    # TimeStamp for File
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    # Template for the basic document
    pdffilename="reports"+os.path.sep+'StatusReport_' + timestamp + '.pdf'
    doc = SimpleDocTemplate(pdffilename, pagesize=letter, rightMargin=inch / 4, leftMargin=inch / 4, topMargin=inch, bottomMargin=inch / 4)
    story = []
    #Headline
    styleData = styles["Heading1"]
    styleData.alignment = TA_CENTER
    story.append(Paragraph("Health Check Report", styleData))
    
    #Create Table
    for checkers in resultJson.keys():
        datafortable = []
        if checkers == 'ncc':
            datafortable.append(["Nutanix Cluster Health Check Results"])
        elif checkers == 'vc':
            datafortable.append(["vCenter Health Check Results"])
        datafortable.append(["Check Performed", "Status", "Message"])
        # print "for checkers ",checkers, "Values :", resultJson[checkers].get('checks')
        lenght=len(resultJson[checkers].get('checks'));
        for checks in resultJson[checkers].get('checks'):
            # print "Checks : ", checks['checks']
            name, status, message = checks.get('name'), checks.get('pass:'), checks.get('message:')
            messagePara=[]
            for msg in string.split(message, ','):
                messagePara.append(Paragraph(msg, styles["Normal"]))
            datafortable.append([name, status, messagePara])
            #print name, '|', status, '|', message
        table = Table(datafortable, colWidths=[doc.width / 3.0] * 3)
        table.setStyle(TableStyle([('TEXTCOLOR', (0, 1), (2, 1), colors.white),
                                ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                ('FONTSIZE', (0, 0), (0, 0), 14),
                                ('FONTSIZE', (0, 1), (2, 1), 12),
                                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                                ('BACKGROUND', (0, 1), (2, 1), colors.black),
                                ('GRID', (1, 1), (1, 1), 0.25, colors.white),
                                ('BACKGROUND', (0, 0), (2, 0), colors.lightseagreen),
                                ('GRID', (0, 2), (3, lenght+1), 0.25, colors.black)]))
        story.append(table)
        story.append(FrameBreak())
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    print "Report Generated Successfully at ", pdffilename