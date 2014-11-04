'''
Created on Oct 22, 2014

@author: krishnamurthy_b
'''
# -*- coding: utf-8 -*-

from reportlab.lib import colors

from reportlab.lib.pagesizes import inch, cm, landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, StyleSheet1, ParagraphStyle
from reportlab.platypus import  LongTable, TableStyle, Image, Paragraph, Spacer, Table
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.enums import  TA_CENTER
import copy
import time
import os

# import json
# fp = open("results.json", 'r')
# resultJson = json.load(fp)

# registering the font colors for each message type
PSstyle1 = ParagraphStyle
styles = getSampleStyleSheet()
stylesheet = StyleSheet1()
NormalMsgStyle = styles['Normal']
HeadingMsgStyle = styles['Heading1']
stylesheet.add(PSstyle1(name='Footer',
                            parent=NormalMsgStyle,
                            fontName='Times-Roman'))
FooterMsgStyle = copy.deepcopy(stylesheet['Footer'])
FooterMsgStyle.alignment = TA_CENTER
stylesheet.add(PSstyle1(name='Cover',
                            parent=HeadingMsgStyle,
                            fontName='Times-Roman', fontSize=25))
CoverMsgStyle = copy.deepcopy(stylesheet['Cover'])
CoverMsgStyle.alignment = TA_CENTER
stylesheet.add(PSstyle1(name='Normal',
                            parent=NormalMsgStyle,
                            fontName='Times-Roman'))
NormalMessageStyle = copy.deepcopy(stylesheet['Normal'])
stylesheet.add(PSstyle1(name='Fail',
                            parent=NormalMsgStyle,
                            textColor=colors.red,
                            fontName='Times-Roman'))
FailMsgStyle = copy.deepcopy(stylesheet['Fail'])
stylesheet.add(PSstyle1(name='Pass',
                            parent=NormalMsgStyle,
                      textColor=colors.forestgreen,
                      fontName='Times-Roman'))
SuccessMsgStyle = copy.deepcopy(stylesheet['Pass'])
stylesheet.add(PSstyle1(name='Error',
                            parent=NormalMsgStyle,
                      textColor=colors.darkkhaki,
                      fontName='Times-Roman'))
ErrorMsgStyle = copy.deepcopy(stylesheet['Error'])
stylesheet.add(PSstyle1(name='Warning',
                            parent=NormalMsgStyle,
                      textColor=colors.purple,
                      fontName='Times-Roman'))
WarningMsgStyle = copy.deepcopy(stylesheet['Warning'])

# Function for returning the font color based on the message
def getFontColor(status):
    
    if ((status == 'Fail') or (status == 'FAIL')):
        return FailMsgStyle
    elif ((status == 'Pass') or (status == 'PASS')) or ((status == 'Done') or (status == 'DONE')):
        return SuccessMsgStyle
    elif ((status == 'Warn') or (status == 'WARN')):
        return WarningMsgStyle
    elif ((status == 'err') or (status == 'Err')):
        return ErrorMsgStyle
    else:
        return NormalMessageStyle
# Function to add Header and footer to all pages except first page
def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Header
        png_path=os.path.dirname(__file__)+os.path.sep+'resources'+os.path.sep+'images'+os.path.sep+'nutanixlogo.png'
        header = Image(png_path, height=0.50 * inch, width=5 * cm)
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
        
 
        # Footer
        
        footer = Paragraph('Tel: 1 (855) 688-2649 | Fax: 1 (408) 916-4039 | Email: info@nutanix.com. &copy 2014 Nutanix, Inc. All Rights Reserved.', FooterMsgStyle)
        w, h = footer.wrap(doc.width, doc.bottomMargin) 
        footer.drawOn(canvas, doc.leftMargin, h) 
        # Release the canvas
        canvas.restoreState()
        
        
# Function to generate report for VC        
def vc_report(story, checks_list):
    count = 0
    for checks in checks_list:
            count += 1
            story.append(Spacer(1, 0.01 * inch))
            checks_data = [[str(count) + ". Check: " + checks.get('Name'), "   Status: " + checks.get('Status'), "   Severity: " + str(checks.get('Severity'))]]
            checks_para_table = Table(checks_data, hAlign='LEFT')
            checks_para_table.setStyle(TableStyle([('ALIGN', (0, 0), (2, 0), 'LEFT'),
                                                   ('FONTSIZE', (0, 0), (2, 0), 10.50)]))
            checks_property_data = [['Properties Tested', 'Status']]
            property_lenght = len(checks.get('Properties'))
            
            for properties in checks.get('Properties'):
               
                if properties is not None:
                    
                    msg = '<br/>(Exp'.join(properties.get('Message').split('(Exp'))
                    status = properties.get('Status')
                    if status == 'FAIL':
                        checks_property_data.append([Paragraph(msg, NormalMessageStyle), Paragraph('Fail', getFontColor(status))])
                    elif status == 'PASS':
                        checks_property_data.append([Paragraph(msg, NormalMessageStyle), Paragraph('Pass', getFontColor(status))])
                    else:
                        checks_property_data.append([Paragraph(msg, NormalMessageStyle), Paragraph(status, getFontColor(status))])
                  
                    
                    
            checks_property_table = LongTable(checks_property_data, colWidths=[6 * inch, 0.75 * inch])
            checks_property_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), colors.fidlightblue),
                                                       ('ALIGN', (0, 0), (1, property_lenght), 'LEFT'),
                                        ('INNERGRID', (0, 0), (2, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (1, property_lenght), 0.25, colors.black),
                                        ('TEXTFONT', (0, 0), (1, 0), 'Times-Roman'),
                                        ('FONTSIZE', (0, 0), (1, 0), 10)]))
            
           
            story.append(checks_para_table)
            story.append(Spacer(1, 0.05 * inch))
            story.append(checks_property_table)
            story.append(Spacer(1, 0.3 * inch))
            

# Function to generate report for NCC
def ncc_report(story, checks_list):
    property_lenght = len(checks_list)
    checks_property_data = [['Properties Tested', 'Status']]
    for checks in checks_list:
    
            status = checks.get('Status')
            msg = checks.get('Name')
            checks_property_data.append([Paragraph(msg, NormalMessageStyle), Paragraph(status, getFontColor(status))])
          
            
                   
    checks_property_table = LongTable(checks_property_data, colWidths=[6 * inch, 0.75 * inch])
    # style sheet for table
    checks_property_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), colors.fidlightblue),
                                                       ('ALIGN', (0, 0), (1, property_lenght), 'LEFT'),
                                        ('INNERGRID', (0, 0), (2, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (1, property_lenght), 0.25, colors.black),
                                        ('TEXTFONT', (0, 0), (1, 0), 'Times-Roman'),
                                        ('FONTSIZE', (0, 0), (1, 0), 10)]))
            
           
            # story.append(checks_para_table)
    story.append(Spacer(1, 0.05 * inch))
    story.append(checks_property_table)
    story.append(Spacer(1, 0.3 * inch))


    
def PDFReportGenerator(resultJson):   
    # Adding timestamp to the report name  
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    # path for generating the report
    pdffilename = os.path.abspath(os.path.dirname(__file__))+os.path.sep+"reports" + os.path.sep + 'Healthcheck-' + timestamp + '.pdf'
    doc = SimpleDocTemplate(pdffilename, pagesizes=letter, format=landscape, rightMargin=inch / 4, leftMargin=inch / 10, topMargin=inch, bottomMargin=inch / 4)
    story = []
    date = time.strftime("%B %d, %Y")
    png_path=os.path.abspath(os.path.dirname(__file__))+os.path.sep+'resources'+os.path.sep+'images'+os.path.sep+'hcr.png'
    headingdata = [["   ", "   ", "  ", "  ", Image(png_path, height=0.37 * inch, width=12 * cm)],
                    [ "    ", "    ", "   ", "   ", "  " , date]]
    headingtable = Table(headingdata)
    headingtable.setStyle(TableStyle([('ALIGN', (0, 1), (4, 1), 'RIGHT'),
                                      ('TEXTFONT', (0, 1), (4, 1), 'Times-Roman'),
                                      ('FONTSIZE', (0, 1), (4, 1), 12)]))
    story.append(headingtable)

    
    for checkers in resultJson.keys():
        checkers_table_data = []
        # Adding heading to the document based on the checkers
        if checkers == 'ncc':
            checkers_table_data = [["Nutanix Cluster Health Check Results"]]
            checkers_table_data.append([Paragraph("CVM IP:" + resultJson[checkers].get('ip'), NormalMessageStyle)])
            checkers_table_data.append([Paragraph("Username:" + resultJson[checkers].get('user'), NormalMessageStyle)])
        elif checkers == 'vc':
            checkers_table_data = [["vCenter Health Check Results"]]
            checkers_table_data.append([Paragraph("vCenter Server IP:" + resultJson[checkers].get('ip'), NormalMessageStyle)])
            checkers_table_data.append([Paragraph("Username:" + resultJson[checkers].get('user'), NormalMessageStyle)])
        
        checkers_table = LongTable(checkers_table_data)
        # style sheet for table
        checkers_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTRE'),
                                            ('TEXTFONT', (0, 0), (0, 2), 'Times-Bold'),
                                            ('FONTSIZE', (0, 0), (0, 0), 14),
                                            ('BACKGROUND', (0, 0), (0, 0), colors.fidlightblue)]))
        story.append(checkers_table)
        story.append(Spacer(1, 0.03 * inch))
        # calling the function based on the checkers
        if resultJson[checkers].get('checks') is None:
            exit()
        if checkers == 'vc':
            vc_report(story, resultJson[checkers].get('checks'))
        if checkers == 'ncc':
            ncc_report(story, resultJson[checkers].get('checks'))
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    
    print "\nReports generated successfully at " + os.path.abspath(os.path.dirname(__file__))+os.path.sep+"reports"
    #print "Success"            
#PDFReportGenerator(resultJson)
