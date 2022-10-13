from openpyxl.styles import Alignment, Border, Side, Font


red_font = Font(color='00FF0000', bold=True)
date_alignment = Alignment(horizontal='center', vertical='center', wrapText=True)
center_cell = Alignment(horizontal='center', vertical='center', wrapText=False)


thin_border = Border(left=Side(style='thin'),
                     right=Side(style='thin'),
                     top=Side(style='thin'),
                     bottom=Side(style='thin'))
left_double_border = Border(left=Side(style='double'),
                            right=Side(style='thin'),
                            top=Side(style='thin'),
                            bottom=Side(style='thin'))
right_double_border = Border(left=Side(style='thin'),
                             right=Side(style='double'),
                             top=Side(style='thin'),
                             bottom=Side(style='thin'))
left_right_double_border = Border(left=Side(style='double'),
                                  right=Side(style='double'),
                                  top=Side(style='thin'),
                                  bottom=Side(style='thin'))
all_double_border = Border(left=Side(style='double'),
                           right=Side(style='double'),
                           top=Side(style='double'),
                           bottom=Side(style='double'))
top_double_border = Border(left=Side(style='thin'),
                           right=Side(style='thin'),
                           top=Side(style='double'),
                           bottom=Side(style='thin'))
top_left_double_border = Border(left=Side(style='double'),
                                right=Side(style='thin'),
                                top=Side(style='double'),
                                bottom=Side(style='thin'))
left_only_double_border = Border(left=Side(style='double'))
top_only_double_border = Border(top=Side(style='double'))
