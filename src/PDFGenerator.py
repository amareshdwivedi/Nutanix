'''
Created on Oct 8, 2014

@author: krishnamurthy_b
'''
# -*- coding: utf-8 -*-
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import inch, cm, landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, StyleSheet1,ParagraphStyle
from reportlab.platypus import  LongTable, TableStyle, Image, Paragraph,Spacer,Table
from reportlab.platypus.doctemplate import SimpleDocTemplate
import time
import string
import os
import copy


stylesheet = StyleSheet1()
PSred = ParagraphStyle
PSgreen = ParagraphStyle
styles = getSampleStyleSheet()
def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        # Header
        header = Image('nutanixlogo.png', height=0.50 * inch, width=5 * cm)
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
 
        # Footer
      
        footer = Paragraph('Tel: 1 (855) 688-2649 | Fax: 1 (408) 916-4039 | Email: info@nutanix.com. &copy 2014 Nutanix, Inc. All Rights Reserved.', styles["Normal"])
        w, h = footer.wrap(doc.width, doc.bottomMargin) 
        footer.drawOn(canvas, doc.leftMargin, h) 
        # Release the canvas
        canvas.restoreState()
        
        
def vc_report(story,checks_list):
    NormalMsgStyle = styles['Normal']
    stylesheet.add(PSred(name='Fail',
                        parent=NormalMsgStyle,
                  textColor=Color(255, 0, 0)))
    ErrorMsgStyle = copy.deepcopy(stylesheet['Fail'])
    stylesheet.add(PSgreen(name='Pass',
                        parent=NormalMsgStyle,
                  textColor=Color(0, 255, 0)))
    SuccessMsgStyle = copy.deepcopy(stylesheet['Pass'])
    for checks in checks_list:
#             print '\t' + checks.get('Name')
#             print '\t' + checks.get('Status')
#             print '\t' + str(checks.get('Severity'))
            checks_data=[]
            checks_data.append([Paragraph("Name : " + checks.get('Name'), styles['Normal']), 
                                Paragraph("Status : " + checks.get('Status'), styles['Normal']),
                                Paragraph("Severity : " + str(checks.get('Severity')),styles["Normal"])])

            checks_para_table = Table([checks_data])
            checks_property_data = [['Property Tested', 'Status']]
            property_lenght = len(checks.get('Properties'))
            
            for properties in checks.get('Properties'):
                # print '\t\t' + properties.get('Status') + '\t\t' + str(properties.get('Message'))
                if properties is not None:
                    
                    msg= '<br/>(Exp'.join(properties.get('Message').split('(Exp'))
                    status=properties.get('Status')
                    if status == 'FAIL':
                        checks_property_data.append([Paragraph(msg, styles['Normal']), Paragraph(status, ErrorMsgStyle)])
                    else:
                        checks_property_data.append([Paragraph(msg, styles['Normal']), Paragraph(status, SuccessMsgStyle)])
                    
            checks_property_table = LongTable(checks_property_data, colWidths=[6 * inch, 0.75 * inch])
            checks_property_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), colors.lightsteelblue),
                                                       ('ALIGN', (0, 0), (1, property_lenght), 'LEFT'),
                                        ('INNERGRID', (0, 0), (2, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (1, property_lenght), 0.25, colors.black),
                                        ('TEXTFONT', (0, 0), (1, property_lenght), 'Gotham'),
                                        ('FONTSIZE', (0, 0), (1, 0), 11),
                                        ('FONTSIZE', (0, 1), (1, property_lenght), 10)]))
            
           
            story.append(checks_para_table)
            story.append(Spacer(1,0.05*inch))
            story.append(checks_property_table)
            story.append(Spacer(1,0.3*inch))
            


def ncc_report(story,checks_list):
    NormalMsgStyle = styles['Normal']
    stylesheet.add(PSred(name='Failed',
                        parent=NormalMsgStyle,
                  textColor=Color(221, 223, 30)))
    ErrorMsgStyle = copy.deepcopy(stylesheet['Failed'])
    
    stylesheet.add(PSgreen(name='Passed',
                        parent=NormalMsgStyle,
                  textColor=Color(0,255, 0)))
    SuccessMsgStyle = copy.deepcopy(stylesheet['Passed'])
    property_lenght=len(checks_list)
    checks_property_data = [['Property Tested', 'Status']]
    for checks in checks_list:
#             print '\t' + checks.get('Name')
#             print '\t' + checks.get('Status')
#             print '\t' + str(checks.get('Severity'))
            status = checks.get('Status')
            msg=checks.get('Name')
            #checks_property_data.append([Paragraph(msg, styles['Normal']), Paragraph(status, NormalMsgStyle)])
            if status == 'Fail':
                checks_property_data.append([Paragraph(msg, styles['Normal']), Paragraph(status, ErrorMsgStyle)])
            else:
                checks_property_data.append([Paragraph(msg, styles['Normal']), Paragraph(status, SuccessMsgStyle)])         
    checks_property_table = LongTable(checks_property_data, colWidths=[6 * inch, 0.75 * inch])
    checks_property_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), colors.lightsteelblue),
                                                       ('ALIGN', (0, 0), (1, property_lenght), 'LEFT'),
                                        ('INNERGRID', (0, 0), (2, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (1, property_lenght), 0.25, colors.black),
                                        ('TEXTFONT', (0, 0), (1, property_lenght), 'Gotham'),
                                        ('FONTSIZE', (0, 0), (1, 0), 11),
                                        ('FONTSIZE', (0, 1), (1, property_lenght), 10)]))
            
           
            #story.append(checks_para_table)
    story.append(Spacer(1,0.05*inch))
    story.append(checks_property_table)
    story.append(Spacer(1,0.3*inch))

            
 
def PDFReportGenerator(resultJson):     
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pdffilename = "reports"+os.path.sep+'StatusReport_' + timestamp + '.pdf'
    doc = SimpleDocTemplate(pdffilename, pagesizes=letter, format=landscape, rightMargin=inch / 4, leftMargin=inch / 4, topMargin=inch, bottomMargin=inch / 4)
    story = []
    
    
    for checkers in resultJson.keys():
        checkers_table_data = []
        if checkers == 'ncc':
            checkers_table_data.append(["Nutanix Cluster Health Check Results"])
        elif checkers == 'vc':
            checkers_table_data.append(["vCenter Health Check Results"])
        
        if resultJson[checkers].get('checks') is None:
            exit()
        checks_lenght = len(resultJson[checkers].get('checks'));
        checkers_table = LongTable(checkers_table_data, 500 * inch)
        checkers_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTRE'),
                                            ('TEXTFONT', (0, 0), (0, 0), 'Gotham-Bold'),
                                            ('FONTSIZE', (0, 0), (0, 0), 14),
                                            ('BACKGROUND', (0, 0), (0, 0), colors.fidlightblue)]))
        story.append(checkers_table)
        # print lenght
        if checkers == 'vc':
            vc_report(story,resultJson[checkers].get('checks'))
        if checkers == 'ncc':
            ncc_report(story,resultJson[checkers].get('checks'))
           
            # checkers_table_data.append([checks_property_table])
    
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)