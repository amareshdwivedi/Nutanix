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
from report_generator_helper import get_vc_check_actual_output_format 
import copy
import time
import os
import csv


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
        png_path=os.path.dirname(__file__)+os.path.sep+'static'+os.path.sep+'images'+os.path.sep+'nutanixlogo.png'
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
def vc_report(story, checks_list,vCenterIP):
    count = 0
    for checks in checks_list:
            count += 1
            categoryList=""
            story.append(Spacer(1, 0.01 * inch))
            categoryListLen = len(checks.get('Category'))
            for category in checks.get('Category'):
                categoryList += category
                if(categoryListLen > 1):
                    categoryList += ","
                    categoryListLen = categoryListLen - 1
                else : 
                    continue   
            checks_data = [[str(count) + ". Check: " + checks.get('Name'), "  Category: "+ categoryList]]
            checks_para_table = Table(checks_data, hAlign='LEFT')
            checks_para_table.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                                   ('FONTSIZE', (0, 0), (1, 0), 10.50)]))
            checks_property_data = [['Entity Tested','Datacenter Name','Cluster Name','Expected Result','Check Status','Severity']]
            property_lenght = len(checks.get('Properties'))
            expected_result = checks.get('Expected_Result')
            for properties in checks.get('Properties'):
               
                if properties is not None:
                    entity_tested_name = properties.get('Entity')
                    datacenter_name = properties.get('Datacenter')
                    cluster_name = properties.get('Cluster')
                    #msg = '<br/>(Exp'.join(properties.get('Message').split('(Exp'))
                    xprop_msg, xprop_actual, xprop_exp = properties.get('Message').split("=")
                    if xprop_msg == "":
                            xprop_msg = check['name']
                    xprop_actual = xprop_actual.split(' (')[0] or xprop_actual.split(' ')[0] or "None"

                    actual_result, is_prop_include , severity =get_vc_check_actual_output_format(checks.get('Name'),
                                                                                                 xprop_actual,
                                                                                                 properties.get('Entity'),
                                                                                                 properties.get('Datacenter'),
                                                                                                 properties.get('Cluster'),
                                                                                                 properties.get('Host'),
                                                                                                 properties.get('Status'),
                                                                                                 xprop_exp.strip(')'),
                                                                                                 vCenterIP)
                    
                    if is_prop_include == False:
                        property_lenght-=1
                        continue
                    
                    checks_property_data.append([Paragraph(entity_tested_name, NormalMessageStyle),
                                                 Paragraph(datacenter_name, NormalMessageStyle),
                                                 Paragraph(cluster_name, NormalMessageStyle),
                                                 Paragraph(expected_result, NormalMessageStyle),
                                                 Paragraph(actual_result, NormalMessageStyle),
                                                 Paragraph(severity, NormalMessageStyle)])

                                     
            checks_property_table = LongTable(checks_property_data, colWidths=[1 * inch,1.2*inch,1*inch,1.15*inch,3*inch, 0.75 * inch])
            checks_property_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (5, 0), colors.fidlightblue),
                                                       ('ALIGN', (0, 0), (5, property_lenght), 'LEFT'),
                                        ('INNERGRID', (0, 0), (5, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                        ('BOX', (0, 0), (1, property_lenght), 0.25, colors.black),
                                        ('TEXTFONT', (0, 0), (5, 0), 'Times-Roman'),
                                        ('FONTSIZE', (0, 0), (5, 0), 10)]))
            
           
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


    
def PDFReportGenerator(resultJson,curdir=None):   
    # Adding timestamp to the report name  
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    # path for generating the report
    if curdir is None:
        pdffilename = os.getcwd() + os.path.sep +"reports" + os.path.sep+ 'Healthcheck-' + timestamp + '.pdf'
    else:
        pdffilename =  curdir + os.path.sep +"reports" + os.path.sep+ 'Healthcheck-' + timestamp + '.pdf'   

    doc = SimpleDocTemplate(pdffilename, pagesizes=letter, format=landscape, rightMargin=inch / 8, leftMargin=inch / 12, topMargin=inch, bottomMargin=inch / 4)
    story = []
    date = time.strftime("%B %d, %Y")
    png_path=os.path.abspath(os.path.dirname(__file__))+os.path.sep+'static'+os.path.sep+'images'+os.path.sep+'hcr.png'
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
            checkers_table_data = [["Nutanix Cluster"+ " ["+resultJson[checkers].get('ip')+"] "+" Health Check Results"]]
            checkers_table_data.append([Paragraph("Username:" + resultJson[checkers].get('user'), NormalMessageStyle)])
        elif checkers == 'vc':
            checkers_table_data = [["vCenter"+ " ["+resultJson[checkers].get('ip')+"] "+" Health Check Results"]]
            checkers_table_data.append([Paragraph("Username:" + resultJson[checkers].get('user'), NormalMessageStyle)])
        
        checkers_table = LongTable(checkers_table_data)
        # style sheet for table
        checkers_table.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTRE'),
                                            ('TEXTFONT', (0, 0), (0, 1), 'Times-Bold'),
                                            ('FONTSIZE', (0, 0), (0, 0), 14),
                                            ('BACKGROUND', (0, 0), (0, 0), colors.fidlightblue)]))
        story.append(checkers_table)
        story.append(Spacer(1, 0.03 * inch))
        # calling the function based on the checkers
        if resultJson[checkers].get('checks') is None:
            exit()
        if checkers == 'vc':
            vc_report(story, resultJson[checkers].get('checks'),resultJson[checkers].get('ip'))
        if checkers == 'ncc':
            ncc_report(story, resultJson[checkers].get('checks'))
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    
    if curdir is None:
        print "\nReports generated successfully at :: " + os.getcwd() + os.path.sep +"reports"
    else:
        print "\nReports generated successfully at :: " + curdir + os.path.sep +"reports"  




def CSVReportGenerator(resultJson,curdir=None): 
       
    timestamp = time.strftime("%Y%m%d-%H%M%S")  
    if curdir is None:
        csvfilename = os.getcwd() + os.path.sep +"reports" + os.path.sep+ 'Healthcheck-' + timestamp + '.csv'
    else:
        csvfilename =  curdir + os.path.sep +"reports" + os.path.sep+ 'Healthcheck-' + timestamp + '.csv'      
        
    rows = []
    details = []
    details.append(["Nutanix Cluster Health Check Results"])
    rows.append(["Category", "Health Check Variable","Entity Tested","Datacenter Name","Cluster Name","Expected Result","Check Status","Check Category", "Severity"])
    for xchecker,allChecks in resultJson.iteritems():
        details.append(["IP",allChecks['ip']])
        details.append(["Category",allChecks['Name']])
        details.append(["User Name",allChecks['user']])
        details.append(["Timestamp",str(time.strftime("%B %d, %Y %H:%M:%S"))])
        details.append(["Overall Check Status",allChecks['Status']])
            
        try:
            for xcheck in allChecks['checks']:
                if isinstance(xcheck['Properties'], list):
                    #rows.append([xchecker, xcheck['Name'],"Overall Status",xcheck['Status'], xcheck['Severity']])
                    for prop in xcheck['Properties']:
                        xprop_msg, xprop_actual, xprop_exp = prop['Message'].split("=")
                        if xprop_msg == "":
                            xprop_msg = check['name']
                        xprop_actual = xprop_actual.split(' (')[0] or xprop_actual.split(' ')[0] or "None"

                        actual_result, is_prop_include , severity =get_vc_check_actual_output_format(xcheck['Name'],
                                                                                                 xprop_actual,
                                                                                                 prop['Entity'],
                                                                                                 prop['Datacenter'],
                                                                                                 prop['Cluster'],
                                                                                                 prop['Host'],
                                                                                                 prop['Status'],
                                                                                                 xprop_exp.strip(')'),
                                                                                                 allChecks['ip'])
                        if is_prop_include == False:
                           continue
                       
                        rows.append([xchecker, xcheck['Name'],prop['Entity'],prop['Datacenter'],prop['Cluster'],xcheck['Expected_Result'],actual_result,xcheck['Category'], severity])
                else:
                    rows.append([xchecker, xcheck['Name'],None,None,None,None,xcheck['Status'],None,None])
        except KeyError:
                #It means- No checks were executed for this checker. 
            continue
        
    if len(rows) > 1:
        details.append([None])
        file_name = csvfilename
        csv_file = open(file_name ,'wb')
        csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(details)
        csv_writer.writerows(rows)
        csv_file.close()
             