from shiny import *
import numpy as np
import pandas as pd
import random
from datetime import date
from ipydatagrid import DataGrid, TextRenderer, Expr
from shinywidgets import *
import plotly.express as px
import plotly.graph_objects as go
from math import floor
import os
import textwrap
from shiny.types import ImgData
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import faicons as fa
from base64 import b64encode
import requests
import json
pd.options.mode.copy_on_write = True

# Global Variable for use as status indicators
ICONS = {
  'Goal not': fa.icon_svg('circle-minus', 'solid', fill='Tomato'),
  'Goal will': fa.icon_svg('circle-exclamation', 'solid', fill='Khaki'),
  'cc': fa.icon_svg('circle-check', 'solid', fill='darkseagreen'),
  'ai':fa.icon_svg('wand-magic-sparkles', 'solid', fill='linear-gradient(to right, lightsteelblue , royalblue)')
}



'''
UNIVERSAL SPACING TOOLS
'''

# Blank card for spacing
dummy = ui.card(style='border: 0px; box-shadow: none;')

# Blank card for spacing - grey background
dummy_grey = ui.card(style='border: 0px; box-shadow: none;background-color: rgba(245, 245, 245, 1)')

# Large spacer using a blank image
dummy_spacer = ui.card(ui.output_image("spacer"), style='border: 0px; box-shadow: none')

# Large block of  spacers for visibility later on
white_grey_spacer = ui.layout_columns(
  dummy,dummy,dummy, dummy_grey, dummy_grey,
  col_widths=[12,12,12,12,12]
)

# Large block of  spacers for visibility later on
grey_white_spacer = ui.layout_columns(
  dummy_grey,dummy_grey,dummy_grey, dummy, dummy,
  col_widths=[12,12,12,12,12]
)

# Large block of  spacers for visibility later on
grey_spacer = ui.layout_columns(
  dummy_grey,dummy_grey,dummy_grey, dummy_grey, dummy_grey,
  col_widths=[12,12,12,12,12]
)

white_spacer = ui.layout_columns(
  dummy,dummy,dummy,dummy,dummy,
  col_widths = [12,12,12,12,12]
)

border_spacer0 = ui.card(
  ui.panel_well('', ' ', style='background-color: rgba(228, 237, 255, 255); border: solid rgba(228, 237, 255, 255)'),
  style='border: 0px; box-shadow: none;'
)

border_spacer1 = ui.card(
  ui.panel_well('', ' ', style='background-color: rgba(228, 237, 255, 255); border: solid rgba(228, 237, 255, 255)'),
  style='border: 0px; box-shadow: none;'
)

border_spacer2 = ui.card(
  ui.panel_well('', ' ', style='background-color: rgba(228, 237, 255, 255); border: solid rgba(228, 237, 255, 255);'),
  style='border: 0px; box-shadow: none;'
)

border_spacer3 = ui.card(
  ui.panel_well('', ' ', style='background-color: rgba(228, 237, 255, 255); border: solid rgba(228, 237, 255, 255)'),
  style='border: 0px; box-shadow: none;'
)

'''
WELCOME ELEMENTS + LAYOUT
'''
# Welcome message
welcome_msg = ui.card(
  ui.output_text('welcome_msg'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 300%;text-align:center;border: 0px; box-shadow: none"
)

# Message about data privacy
privacy_msg = ui.card(
  ui.output_text('privacy_msg'),
  style="color:rgba(65,65,65,255);;font-size: 150%;text-align:center;border: 0px; box-shadow: none"
)

# Mockup-graphic of visualizations
mockup = ui.card(
  ui.output_image('mockup', inline=True),
  style="align:center;border: 0px; box-shadow: none; float:right"
)

# layout block for welcome page + privacy statement
welcome_privacy = ui.layout_columns(
    dummy,

    dummy,
    ui.layout_columns(
      dummy,
      ui.output_image('logo', inline=True),
      col_widths=[1,11]),

    dummy, dummy, dummy,
    welcome_msg,
    dummy, dummy, dummy,

    dummy,
    ui.layout_columns(
      dummy,
      mockup,
      col_widths=[3,9]),
    dummy,

    dummy, dummy, dummy,
    
    dummy, privacy_msg, dummy,
    col_widths=[12,
                4,8,
                12,12,12,
                12,
                12,12,12,
                1,10,1,
                12,12,12,
                3,6,3]
)

'''
GOAL SETTING ELEMENTS + LAYOUT
'''

# Spacing between sections
top_gap1 = ui.card(
  ui.output_text('top_gap1'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 200%;text-align:center;border: 0px; box-shadow: none; background-color: rgba(245, 245, 245, 1)"
)

# Goal section title text
goal_msg = ui.card(
  ui.output_text('goal_msg'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 200%;text-align:center;border: 0px; box-shadow: none; background-color: rgba(245, 245, 245, 1)"
)

# Panel containing all the goal setting inputs
## - Target Group
## - Target Scope
## - Target Percentage
## - Time to Reach DEI Goal

#random start for the target group selector, outside of server because it is not using a user input
def ranodm_start():
  choices = ['Women','Non-Binary','Black','Hispanic','Asian','Native American',
            'Native Hawaiian or Pacific Islander','Two or more Races', 'Disabled']
  start_choice = random.choice(choices)
  return str(start_choice)

goal_setting_panel = ui.card(
  ui.input_checkbox_group('target_group', "What are your diversity segment(s) of focus?",
                          choices = {'Women':'Women','Non-Binary': 'Non-Binary','Black':'Black',
                                     'Hispanic':'Hispanic','Asian':'Asian','Native American':'Native American',
                                     'Native Hawaiian or Pacific Islander': 'Native Hawaiian or Pacific Islander','Two or more Races':'Two or more Races',
                                     'Disabled':'Disabled',
                                     }, selected= ranodm_start(), width='100%'),
  ui.input_select('industry', 'What industry sector is your company in?', {'Prefer not to say':'Prefer not to say',
                                                                           'Construction': 'Construction',
                                                                           'Finance':'Finance',
                                                                           'Government':'Government',
                                                                           'Information':'Information',
                                                                           'Leisure and Hospitality':'Leisure and Hospitality',
                                                                           'Manufactuaring':'Manufacturing',
                                                                           'Mining and Logging':'Mining and Logging',
                                                                           'Professional and Business Services':'Professional and Business Services',
                                                                           'Trade, Transportation, and Utilities':'Trade, Transportation, and Utilities'}, width='100%'),
  ui.input_select('target_scope', "At what level will the change take place?", {'Company-wide': 'Company-wide', 'Leadership':'Leadership', 'Department':'Department'},width='100%'),
  ui.input_slider("target_percent",ui.output_text('goal_name_rep_goal'), 0, 100, 15, post = "%",width='100%'),
  ui.input_numeric("time_to_goal", "How many years to achieve this goal?", 3, min=1, step=1, max=10, width='100%'),
  style='border: 0px; box-shadow: none; background-color: rgba(245, 245, 245, 1)'
  )

# Navigation panel
jump_panel = ui.card(
                      ui.input_action_link('set_goal', 'Set Goals', style="font-size:125%;text-align:center;font-weight:bold;color:rgba(65,65,65,255);background-color: rgba(174, 202, 255, 255); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#goal_msg';"),
                      ui.input_action_link('data_input', 'Add Data', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#data_input_msg';"),
                      style='border: 0px; box-shadow: none; background-color: rgba(245, 245, 245, 1)'
                    )

# Spacing for bottom of goal section
bot_gap1 = ui.card(
  ui.output_text('bot_gap1'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 200%;text-align:center;border: 0px; box-shadow: none; background-color: rgba(245, 245, 245, 1)"
)

# Layout for goal setting
goal_setting = ui.layout_columns(
  top_gap1,
  dummy_grey,
  ui.layout_columns(
    goal_msg,
    dummy_grey,
    goal_setting_panel,
    dummy_grey,
    col_widths=[12, 2,8,2],
    style='background-color: rgba(245, 245, 245, 1)'),
  dummy_grey,
  ui.layout_columns(
    jump_panel,
    dummy_grey,
    col_widths=[10,2],
    style='background-color: rgba(245, 245, 245, 1)'
  ),
  bot_gap1,
  col_widths=[12, 3,6,1,2,12],
  style='background-color: rgba(245, 245, 245, 1)'
)

'''
ADD DATA ELEMENTS + LAYOUT
'''

# Title for data input section
data_input_msg = ui.card(
  ui.output_text('data_input_msg'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 200%;text-align:center;border: 0px; box-shadow: none"
)

# Instructions for data input
data_input_instructions = ui.card(
  ui.output_text('data_input_instructions'),
  style="color:rgba(65,65,65,255);;font-size: 150%;text-align:center;border: 0px; box-shadow: none"
)

# Button for users to add another years worth of data
add_inputs = ui.card(
  ui.input_action_button("add_inputs", "Add More Data", width='100%', style='background-color: rgba(158,214,189,255); border: 2px solid rgba(158,214,189,255)'),
  style='border: 0px; box-shadow: none'
)

# Button for users to remove a years worth of data
remove_inputs = ui.card(
  ui.panel_conditional("(input.add_inputs - input.remove_inputs) >= 1",
  ui.input_action_button("remove_inputs", "Remove Oldest Data", width='100%', style='background-color: rgba(235,121,113,255); border: 2px solid rgba(235,121,113,255)')),
  style='border: 0px; box-shadow: none'
)

# Base panel for inputing data. If only one year of data, then it will appear as a singular panel. If multiple years, then it will appear as an accordion
data_input = ui.card(

  # Panel if only one year of data
  ui.panel_conditional("(input.add_inputs - input.remove_inputs) < 1",
                    ui.panel_title(title=f"Last Year's Data  ({date.today().year - 1})"),
                    ui.input_numeric("total_employees", "How many employees do you have?", 100, min=1, step=1,width='100%'),        
                    ui.input_slider("current_percent", ui.output_text('goal_name_now_rep'), 0, 100, 10, post = "%",width='100%'),
                    ui.input_numeric("new_hires", "How many new hires did you make last year?", 20, min=0, step=1,width='100%'),

                    # Specific input if scope is leadership
                    ui.panel_conditional("input.target_scope == 'Leadership'", 
                                          ui.input_numeric('promotions', "How many promotions did you have last year?", 5, min=0, step=1,width='100%')),

                    # Specific input if scope is department
                    ui.panel_conditional("input.target_scope == 'Department'", 
                                          ui.input_numeric('transfers', "How many transfers did you have last year?", 5, min=0, step=1,width='100%')),

                    # Conditional checkbox to use numbers instead of percentages
                    ui.input_checkbox('use_numbers', 'Use Numbers Instead of Percents', False),

                    # If percentages, use the following inputs
                    ui.panel_conditional('input.use_numbers == false', 
                                          ui.input_slider("target_hire_percent", ui.output_text('hire_rep_p'), 0, 100, 20, post = "%",width='100%'),
                                          ui.panel_conditional("input.use_numbers == false && input.target_scope == 'Leadership'",
                                                              ui.input_slider('target_promotion_percent', ui.output_text('ts_promotion_p'), 0, 100, 20, post = "%",width='100%'),),
                                          ui.panel_conditional("input.use_numbers == false && input.target_scope == 'Department'",
                                                              ui.input_slider('target_transfer_percent', ui.output_text('ts_transfer_p'), 0, 100, 20, post = "%",width='100%'),),
                                          ui.input_slider("target_attrition_rate", ui.output_text('tg_attrition_r'), 0, 100, 5, post = "%",width='100%'),
                                          ui.input_slider("non_target_attrition_rate", ui.output_text("non_tg_attrition_r"), 0, 100, 5, post = "%",width='100%')),

                    # If numbers, use the following inputs
                    ui.panel_conditional('input.use_numbers',
                                          ui.input_numeric('target_hire_number',ui.output_text('hire_rep_num'), 5, min=0, step=1,width='100%'),
                                          ui.panel_conditional("input.use_numbers && input.target_scope == 'Leadership'",
                                                              ui.input_numeric('target_promotion_number', ui.output_text('ts_promotion_num'), 0, min=0, step=1,width='100%'),),
                                          ui.panel_conditional("input.use_numbers && input.target_scope == 'Department'",
                                                              ui.input_numeric('target_transfer_number', ui.output_text('ts_transfer_num'), 0, min=0, step=1,width='100%'),),
                                          ui.input_numeric('target_left_number', ui.output_text('tg_attrition_num'), 2, min=0, step=1,width='100%'),
                                          ui.input_numeric('non_target_left_number', ui.output_text('non_tg_attrition_num'), 3, min=0, step=1,width='100%')),
                    style='border-style: solid;border-width: 1px; padding: 15px; border-color: rgba(226,226,226,255)'),

  # Change the panel to an accordion if more than one years worth of data is present
  ui.panel_conditional("(input.add_inputs - input.remove_inputs) >= 1", 
                        ui.panel_title(title='Historical Data'),

                        ui.accordion(ui.accordion_panel(f"Data for {date.today().year - 1}", ui.output_ui('render_initial_panel')), id="acc", multiple = True)),
  style='border: 0px; box-shadow: none'
)

# Navigation panel
jump_panel2 = ui.card(
                      ui.input_action_link('set_goal2', 'Set Goals', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#goal_msg';"),
                      ui.input_action_link('data_input2', 'Add Data', style="font-size:125%;text-align:center;font-weight:bold;color:rgba(65,65,65,255);background-color: rgba(174, 202, 255, 255); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#data_input_msg';"),
                      ui.input_action_link('overview2', 'Results', style="font-size: 125%;text-align: center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot_msg';"),
                      style='border: 0px; box-shadow: none'
                    )

# Layout for the data input/removal section
data_input_portion = ui.layout_columns(
  dummy,
  ui.layout_columns(
    data_input_msg,
    data_input_instructions,
    ui.layout_columns(
      dummy,
      add_inputs,
      remove_inputs,
      dummy,
      col_widths=[1,5,5,1]
    ),
    dummy,
    data_input,
    dummy,
    col_widths=[12, 12,12,1,10,1]
  ),
  dummy,
  ui.layout_columns(
    jump_panel2,
    dummy,
    col_widths=[10,2]
  ),
  col_widths=[3,6,1,2]
)

'''
PLOT ELEMENTS + LAYOUT
'''

# Title text for plot
plot_msg = ui.card(
  ui.output_text('plot_msg'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 250%;text-align:center;border: 0px; box-shadow: none"
)

# Description of plot
plot_desc = ui.card(
  ui.output_ui('plot_desc'),
  style="color:rgba(65,65,65,255);font-size: 125%;text-align:left;border: 0px; box-shadow: none"
)



# Goal status message
goal_status = ui.card(
  ui.value_box(
    '', ui.output_ui('goal_status'), showcase=ui.output_ui('goal_status_icon'),
    style='text-align:left;color:rgba(65,65,65,255);background-color: rgba(247, 247, 247, 1); border-radius: 15px;border-color: rgba(242, 242, 242, 1)'
  ),
  style='border: 0px; box-shadow: none;'
)

# Dynamic input for target percentage
plot_tp2 = ui.card(
  ui.input_slider("target_percent2", ui.output_text('goal_name_rep_goal2'), value=0, min=0, max=100, post = "%"),
  style='border: 0px; box-shadow: none'
)

# Dynamic input for time to goal
plot_ttg2 = ui.card(
  ui.input_numeric("time_to_goal2", "How many years to achieve this goal?", value=3, min=1, max=10, step=1),
  style='border: 0px; box-shadow: none'
)

# Dynamic input for plot type
plot_pt = ui.card(
  ui.input_select('plot_type', "Type of Plot", {'Projection Only':'Projection Only', 'Plot Historical Data':'Plot Historical Data', 
                                                'Overlay Historical Data':'Overlay Historical Data'}),
  style='border: 0px; box-shadow: none'
)

# Navigation panel for visualization
links1 = ui.card(
  ui.input_action_link('plot1', 'Projection', style="font-size:125%;text-align:center;font-weight:bold;color:rgba(65,65,65,255);background-color: rgba(174, 202, 255, 255); border: 1px solid rgba(174, 202, 255, 255);border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot1';"),
  ui.input_action_link('table1', 'Edit Values', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot2';"),
  ui.input_action_link('recommendations1', 'Recommendations', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot3';"),
  ui.input_action_link('faq1', 'FAQ', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot4';"),
  style='border: 0px; box-shadow: none'
)

# Panel containing the visualization of projection + Benchmark button
plot = ui.card(
  output_widget('px_plot', fill=True, fillable=True),
  style='border: 0px; box-shadow: none;text-align:center',
  full_screen=True
  )

benchmark = ui.card(
  ui.input_checkbox('benchmark_checkbox', 'Compare with BLS Data!'),
  ui.panel_conditional('input.benchmark_checkbox', ui.output_text('attrition_benchmark_message')),
  style='border: 0px; box-shadow: none;font-weight:bold',
)

# UI Layout for the plot section
plot_block = ui.layout_columns(
  ui.layout_columns(
    dummy,
    ui.layout_columns(
      plot_msg,
      dummy,
      goal_status,
      dummy,
      ui.layout_columns(
        dummy,
        plot_desc,
        dummy,
        col_widths=[4,5,3]
      ),
      col_widths=[12,1, 10,1,12]
    ),
    ui.layout_columns(
      links1,
      dummy,
      col_widths=[10,2]
    ),
    col_widths=[2,8,2]
  ),
  dummy,
  benchmark,
  dummy,
  dummy,
  plot,
  dummy,
  col_widths=[12,2,8,2,2,8,2])

'''
TABLE ELEMENTS + LAYOUT
'''

# Title text for table section
table_msg = ui.card(
  ui.output_text('table_msg'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 200%;text-align:center;border: 0px; box-shadow: none;"
)

# Overview of table section
table_desc = ui.card(
  ui.output_text('table_desc'),
  style="color:rgba(65,65,65,255);font-size: 150%;text-align:center;border: 0px; box-shadow: none"
)

# Navigation panel for visualization
links2 = ui.card(
  ui.input_action_link('plot2', 'Projection', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot1';"),
  ui.input_action_link('table2', 'Edit Values', style="font-size: 125%;text-align:center;font-weight:bold; color:rgba(65,65,65,255);background-color: rgba(174, 202, 255, 255); border: 1px solid rgba(174, 202, 255, 255);border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot2';"),
  ui.input_action_link('recommendations2', 'Recommendations', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot3';"),
  ui.input_action_link('faq2', 'FAQ', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot4';"),
  style='border: 0px; box-shadow: none;'
)

# Panel containing the data table for projection and download button
table = ui.card(
  #output table widget
  output_widget("tbl_widget",fill=True, fillable=True),
  style='border: 0px; box-shadow: none;float: right',
  full_screen=True
  )

table_button = ui.card(
  ui.download_button('downloadData', 'Download Table', width='100%', style='background-color: rgba(174, 202, 255, 255); border: 2px solid rgba(174, 202, 255, 255); font-weight:bold'),
  style='border: 0px; box-shadow:none;'
)

# Layout for the table section
table_block = ui.layout_columns(
  ui.layout_columns(
    dummy,
    ui.layout_columns(
      table_msg,
      table_desc,
      col_widths=[12,12]
    ),
    ui.layout_columns(
      links2,
      dummy,
      col_widths=[10,2]
    ),
    col_widths=[2,8,2]
  ),
  dummy,
  ui.layout_columns(
    dummy,
    plot_tp2,
    plot_ttg2,
    plot_pt,
    dummy,
    col_widths=[2,3,3,3,1]
  ),
  dummy,
  dummy,table,dummy,
  dummy,table_button,dummy,
  col_widths=[12,12,12,12,
              1,10,1,
              4,4,4],
)

'''
LLM ELEMENTS + LAYOUT
'''

# Title text for LLM section
llm_msg = ui.card(
  ui.output_text('llm_msg'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 200%;text-align:center;border: 0px; box-shadow: none"
)

# Descriptive text for LLM Section
llm_desc = ui.card(
  ui.output_text('llm_desc'),
  style="color:rgba(65,65,65,255);font-size: 150%;text-align:center;border: 0px; box-shadow: none"
)

llm_ai = ui.card(
  ui.value_box('', ui.output_ui('llm_ai'), showcase=ICONS['ai'],style="color: dodgerblue;text-align:left;border: 0px; box-shadow: none;"),
  style="font-size:25%;border: 0px; box-shadow: none"

)

# Navigation panel for visualization
links3 = ui.card(
  ui.input_action_link('plot3', 'Projection', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot1';"),
  ui.input_action_link('table3', 'Edit Values', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot2';"),
  ui.input_action_link('recommendations3', 'Recommendations', style="font-size: 125%;text-align:center;font-weight:bold; color:rgba(65,65,65,255);background-color: rgba(174, 202, 255, 255); border: 1px solid rgba(174, 202, 255, 255);border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot3';"),
  ui.input_action_link('faq3', 'FAQ', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot4';"),
  style='border: 0px; box-shadow: none'
)

# Selection box for type of LLM desired
llm_options = ui.card(
  ui.input_select('llm_option', "Choose your type of recommendation", {'Use the information provided to make recommendations that are focused on dealing with attrition rates':'Prioritize employee attrition.', 
                                                                       'Use the information provided to make recommendations that are focused on dealing with time frame':'Prioritize my time frame.',
                                                                       'Use the information provided to make recommendations that are focused on dealing with the target groups': 'Prioritize insights for target group.',
                                                                       'General Recommendations':'Give me a general recommendation.',}),
  style="color:rgba(65,65,65,255);text-align:center;border: 0px; box-shadow: none"
)

# Generate LLM button
llm_gen = ui.card(
  ui.input_action_button('llm_gen', "Get my recommendations!",style='background-color: rgba(174, 202, 255, 255); border: 2px solid rgba(174, 202, 255, 255); font-weight:bold'),
  style="color:rgba(65,65,65,255);text-align:center;border: 0px; box-shadow: none"
)

# Generate LLM button
llm_regen = ui.card(
  ui.input_action_button('llm_regen', "Get new recommendations!",style='background-color: rgba(174, 202, 255, 255); border: 2px solid rgba(174, 202, 255, 255); font-weight:bold'),
  style="color:rgba(65,65,65,255);text-align:center;border: 0px; box-shadow: none"
)

# LLM Call for DEI Improvement Tips + Download Button for Report
llm = ui.card(
  ui.output_ui('llm_response_with_load',  fill=True, fillable=True),
  style='border: 0px; box-shadow: none',
  full_screen=True
  )

# layout for generate llm section - type selection and generate button disappear in lieu of LLM once pressed
llm_gen_output = ui.card(
  ui.panel_conditional('input.llm_gen - input.llm_regen != 0',
                       ui.layout_columns(
                         dummy,
                         ui.layout_columns(
                           dummy,
                           ui.layout_columns(
                             dummy,
                             llm_options,
                             col_widths=[1,11]
                           ),
                           col_widths=[2,10]
                         ),
                         dummy,
                         col_widths=[4,4,4]
                        ),
                       ui.layout_columns(
                         dummy,
                         ui.layout_columns(
                           dummy,
                           llm_gen,
                           dummy,
                           col_widths=[2,8,2]
                         ),
                         dummy,
                         col_widths=[4,4,4]
                       )
                      ),
  ui.panel_conditional('input.llm_gen - input.llm_regen == 0',
                       ui.layout_columns(
                         dummy,
                         llm_regen,
                         dummy,
                         col_widths=[4,4,4]
                       ),
                       ui.layout_columns(
                         dummy,
                         llm,
                         dummy,
                         col_widths=[2,8,2]
                       )
                       ),
  style='border: 0px; box-shadow: none'
)

# Layout for LLM Section
llm_block = ui.layout_columns(
  ui.layout_columns(
    dummy,
    ui.layout_columns(
      llm_msg,
      llm_desc,
      dummy,
      llm_ai,
      col_widths=[12,12,2,10]
    ),
    ui.layout_columns(
      links3,
      dummy,
      col_widths=[10,2]
    ),
    col_widths=[2,8,2]
  ),
  llm_gen_output,
  col_widths=[12,12]
)

'''
FAQ ELEMENTS + LAYOUT
'''

# Title text for FAQ
faq_msg = ui.card(
  ui.output_text('faq_msg'),
  style="color:rgba(65,65,65,255);font-weight:bold;font-size: 200%;text-align:center;border: 0px; box-shadow: none"
)

# Overview text for FAQ
faq_desc = ui.card(
  ui.output_text('faq_desc'),
  style="color:rgba(65,65,65,255);font-size: 150%;text-align:center;border: 0px; box-shadow: none"
)

# Navigation panel for visualization
links4 = ui.card(
  ui.input_action_link('plot4', 'Projection', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot1';"),
  ui.input_action_link('table4', 'Edit Values', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot2';"),
  ui.input_action_link('recommendations4', 'Recommendations', style="font-size: 125%;text-align:center;color:rgba(65,65,65,255);background-color: rgba(210, 210, 210, 0.8); border-radius: 5px;text-decoration-line: none;", onclick ="location.href='#plot3';"),
  ui.input_action_link('faq4', 'FAQ', style="font-size: 125%;text-align:center;font-weight:bold; color:rgba(65,65,65,255);background-color: rgba(174, 202, 255, 255); border: 1px solid rgba(174, 202, 255, 255);border-radius: 5px;text-decoration-line: none;",onclick ="location.href='#plot4';"),
  style='border: 0px; box-shadow: none;'
)

# Markdown Text for the about us section
about_us = """
### Bochen Lu

![Bochen Image](https://media.licdn.com/dms/image/C5603AQFjt2KGnckE2g/profile-displayphoto-shrink_200_200/0/1571964239563?e=1718841600&v=beta&t=AR9p4pwhq_8jo7CRCh4AgUmU1FdqvAM6KFg0gXwSP_o)
Product Manager

### Andy Wong

![Andy Image](https://media.licdn.com/dms/image/D4D03AQGLwmQ2nUGoLg/profile-displayphoto-shrink_200_200/0/1663793162002?e=1720656000&v=beta&t=-S3-kLu0CeccEjC74vJ3N5eKGbDER6uXDRF7Rg4vTog)
UX Designer & Data Scientist

### Marquis Bullock 

![Marquis Image](https://media.licdn.com/dms/image/C5603AQEHApSEVNsxnA/profile-displayphoto-shrink_200_200/0/1624683372098?e=1718841600&v=beta&t=Uzx0HK1IeCQKzOG9PiZEMH4i6aYqpyh0cYcBA-h1cQo)
Developer & Writer

### Christopher Olson

![Chris Image](https://media.licdn.com/dms/image/C4E03AQHxHhZrZUgQ7w/profile-displayphoto-shrink_200_200/0/1556406865080?e=1718841600&v=beta&t=9-FHErygPKW8B7nr527eWSpcqePoRV3388ugZM9n_Hc)
BI Engineer & Data Scientist
"""

# Accordion for the FAQ Section
faq_accordion = ui.accordion(ui.accordion_panel(ui.markdown("**How do I use the DEI Calculator?**"),
                                                ui.markdown(
                                                  """
                                                  The calculator is a tool to help calculate and visualize the representation of a specified target demographic given your historical DEI data!
                                                  If you're on this page, this means that all of your data has been input, and it's time to analyze and plan! We've provided a
                                                  visualization of what we predict to be your DEI goal trajectory, a table of projected values, and some recommendations given your DEI goal!
                                                  """
                                                  )
                                                ),
                             ui.accordion_panel(ui.markdown("**How exactly do the inputs adjust my visualization?**"),
                                                ui.markdown(
                                                  """
                                                    - **Representation Goal**: This sets the percentage representation of a specific target group that you wish to set as your goal! 
                                                    Changing the value will change the dotted yellow line on the plot. Basically, if your projection line (green) crosses the dotted yellow line,
                                                    that means you've reached the representation goal you set!
                                                    - **How many years to achieve this goal?**: This sets how many years you want to have to achieve your DEI goal. As you add more years (up to 10), 
                                                    our calculator will add more projection points onto the visualization!
                                                    - **Type of Plot**: This changes the type of visualization plot that will be output! There are three options:
                                                      - *Projection Only*: Plot only the points that the calculator is projecting for you (only future points)
                                                      - *Plot Historical Data*: Plot both historical data and projection points (user-input past points + future points) in a sequential order
                                                      - *Overlay Historical Data*: Plot both historical data and projection points (user-input past points + future points), but treat the historical data
                                                      as a separate line sharing the same x-axis as the projection.
                                                  """
                                                  )
                                                ),
                             ui.accordion_panel(ui.markdown("**How do I interpret my visualization?**"),
                                                ui.markdown(
                                                  """
                                                  To interpret the visualization, first lets do a quick run-down of all elements on the graph!
                                                  - **Points**: Points represent the total representation of the interest target group as a percentage of total employees
                                                    - *Projection Points (Green)*: These represent points that the calculator has projected based on input historical data.
                                                    - *Historical Points (Red)*: These indicate the representation percentages from the past given the data you have entered.
                                                  - **Labels**: Labels help convey what our visualization is trying to convey.
                                                    - *Year*: The year is represented on the X-Axis.
                                                    - *Representation (%)*: The percentage representation of the target group is represented on the Y-Axis.
                                                  - **Goal Status**: The area above the visualization serves as an 'at-a-glance' indicator of whether or not the set DEI goal was met. 
                                                    - *Content*: The message states whether or not the goal has been met, and the year the goal was met if applicable. If the goal is not met 
                                                    in 10 years, then it will simply state the goal won't be met in a 10 year span.
                                                  - **Yellow Shading + Dotted Line**: This serves as an indicator of the DEI goal set.
                                                    - *Dotted Line*: This line serves as an indicator of what the representation goal set is. 
                                                    - *Yellow Shading*: The shading starts at the point with the largest representation %, and fills in upwards towards the representation goal. It
                                                    serves as an indication of how far away from the goal you are given historical trends. If you are projected to meet your goal, the yellow shading 
                                                    will not appear.
                                                  """
                                                  )
                                                ),        
                             ui.accordion_panel(ui.markdown("**What does each table column represent?**"),
                                                ui.markdown(
                                                  """
                                                  Each column is on a per year basis. All numbers reflect only one year.
                                                    - **Total Employees**: Total amount of employees in your Organization
                                                    - **Number of ___ Employees**: Amount of employees that belong to the target DEI group in your Organization
                                                    - **New Hires**: Total Amount of new hires in your Organization
                                                    - **New Hires who are ___**: Amount of new hires that belong to the target DEI group in your Organization
                                                    - **___ Employee Separations**: Amount of separations in your organization where the separated employee belongs to the target DEI group
                                                    - **Non-___ Employee Separations**: Amount of separations in your organization where the separated employee does not belong to the target DEI group
                                                    - **# Promoted**: Total amount of employees promoted in your organization
                                                    - **# ___ Promoted**: Total amount of employees that belong to the target DEI group promoted in your organization
                                                    - **# Transfers**: Total amount of employees transfered in your organization
                                                    - **# ___ Transfers**: Total amount of employees that belong to the target DEI group transfered in your organization
                                                  """
                                                  )
                                                ),          
                             ui.accordion_panel(ui.markdown("**I want to test another DEI goal. How do I do that?**"),
                                                ui.markdown(
                                                  """
                                                    If you wish to test another DEI goal with a different target group and new respective data, please refresh the page since you'll 
                                                    have to input new target group specific data. Otherwise, adjusting the inputs above will dynamically change your projection automatically!
                                                  """
                                                  )
                                                ),     
                             ui.accordion_panel(ui.markdown("**How can I use the calculator to its fullest potential?**"),
                                                ui.markdown(
                                                  """
                                                  The beauty of the calculator is that its versatile! What 'fullest potential' means depends on the intentions and purpose of using the 
                                                  calculator in the first place. To help, here are some common uses of the calculator:
                                                  - *Pitch Graphic*: Having the visualization as part of a slide deck could help illustrate how well/poorly DEI goals are going! To easily export our 
                                                  visualization as an image, click the *camera* icon in the top right toolbar that appears when you hover over the graphic!
                                                  - *Theoretical Scenario Planning*: Edit the data table by double clicking it, and check out how the projection will change if certain metrics change like 
                                                  the amount of new hires!
                                                  - *Baseline Planning*: Our integrated-LLM can help provide great advice on how to improve your specific DEI goal! Using its advice as a general foundation
                                                   for a more specific plan will help ensure that your DEI plan is thorough and well-thought out!
                                                  """
                                                  )
                                                ),
                            ui.accordion_panel(ui.markdown("**How accurate is the projection?**"),
                                                ui.markdown(
                                                  """
                                                  Our projection is meant to give a sense of the direction your organization is heading with DEI. 
                                                  In order to make an accurate forecast, a lot more data would need to be provide than what the calculator asks for!
                                                  Your organization's DEI efforts will likely not be as smooth as the projection shows and hopefully new initiatives crafted after 
                                                  using our calculator will put you on an upward trajectory!
                                                  """
                                                  )
                                                ),   
                             ui.accordion_panel(ui.markdown("**What should I do if I encounter an error or bug?**"),
                                                ui.markdown(
                                                  """
                                                  Please report to **Included.ai** with a detailed description of the problem.
                                                  """
                                                  )
                                                ),
                             ui.accordion_panel(ui.markdown('**Who made this calculator?**'),
                                                ui.markdown(about_us)),
                             id='faq_accordion'
                            )

# Layout for FAQ Section
faq_block = ui.layout_columns(
  ui.layout_columns(
    dummy,
    ui.layout_columns(
      faq_msg,
      faq_desc,
      col_widths=[12,12]
    ),
    ui.layout_columns(
      links4,
      dummy,
      col_widths=[10,2]
    ),
    col_widths=[2,8,2]
  ),
  faq_accordion,
  col_widths=[12,12],
)

def horizontal_striping(cell):
  return 'rgba(255, 255, 255, 255)' if cell.row %2 == 0 else 'rgba(245,245,245,1)'

app_ui = ui.page_fluid(
  # Format appearance of card headers
  ui.tags.style(".card-header { color:white; background:rgba(199,217,251,255) !important; }"),
  # Set title of card to Included DEI Calculator
  
  ui.layout_columns(
    welcome_privacy,
    white_grey_spacer,
    goal_setting,
    grey_white_spacer,
    data_input_portion,
    white_spacer,
    border_spacer0,
    plot_block,
    border_spacer1,
    table_block,
    border_spacer2,
    llm_block,
    border_spacer3,
    faq_block,

    col_widths = [12,

                  12,
                  
                  12,

                  12,


                  12,

                  12,

                  12,
                  12,
                  12,
                  12,
                  12,
                  12,
                  12,
                  12,
                  12,
                  12,
                  12,
                  ],
    
  ),
  title='Included DEI Calculator',
)


def server(input: Inputs, output: Outputs, session: Session):
    
    # Format text for various target groups
    def format_group(groups, plot_or_table = False):
      if plot_or_table == False:
        return ', '.join(["Female" if g == "Women" else g for g in groups])
      elif plot_or_table == True:
        if len(groups) == 1 and groups[0] == 'Hawaiian or Pacific Islander':
          return 'NHPI'
        #if greater than 24 characters, return target group
        elif len(', '.join(["Female" if g == "Women" else g for g in groups])) > 24:
          return 'Target Group'
        else:
          return ', '.join(["Female" if g == "Women" else g for g in groups])
    
    @render.text
    def plot_msg():
      return 'Based on your inputs...'
    
    @render.ui
    def plot_desc():
      return ui.markdown(
      """
      For employees who are **%s**  
      On a **%s** level  
      With **%i** years to achieve **%i**%% representation
      """ %(str(input.target_group()).replace("(", "").replace(")",'').replace("'",''), input.target_scope(), int(input.time_to_goal2()),int(input.target_percent2())))

    @render.text
    def table_msg():
      return 'Projection Adjustment'

    @render.text
    def table_desc():
      return 'Alter your goals and check how your projection changes. Double click to edit table cells.'

    @render.text
    def llm_msg():
      return 'How can I improve DEI?'
    
    @render.text
    def llm_desc():
      return 'Based on your circumstances, we\'ve created some personalized recommendations for change.'
    
    @render.text
    def faq_msg():
      return 'FAQ'
    
    @render.text
    def faq_desc():
      return 'Learn more about how to make the most of our calculator'
    
    @render.text
    def initiate_instructions():
      return 'We\'ve been calculating your DEI projection behind the scenes, and it\'s time to explore'
    
    @render.text
    def initiate_msg():
      return 'Let\'s get planning'

    # Render image from directory: Privacy Message
    @render.image
    def image_msg():
      dir = Path(__file__).resolve().parent
      img: ImgData = {"src": str(dir / "image2.png"), "width": "1000px"}
      return img
    
    @render.text
    def welcome_msg():
      return 'Let\'s create a more equitable workplace together.'
    
    @render.text
    def privacy_msg():
      return 'Our calculator is completely anonymous, and stores absolutely none of your data. Scenario plan with no worries.'
    
    @render.text
    def data_input_instructions():
      return "If you wish to add data prior to 2023, click 'Add More Data'"
    
    @render.text
    def visualization_msg():
      return "Welcome to your visualization!"
    
    @render.ui
    def visualization_instructions2():
      msg = ui.markdown("""
                      **Visualization of Goals**: A projection estimating your DEI goal progress.\n
                      **Points of Impact Table**: A table containing all of the projected values generated from our algorithm.\n
                      **How can you improve DEI?**: Our advice to help you reach your goal.\n
                      **FAQ**: Additional help navigating our claculator.
                      """
                      ),
      return msg
    
    @render.text
    def visualization_instructions1():
      return 'Scroll below to find:'
    
    @render.text
    def bot_gap():
      return "   "
    
    @render.text
    def bot_gap2():
      return "   "
    
    @render.text
    def bot_gap3():
      return "   "    
    
    @render.text
    def top_gap1():
      return "   "
    
    @render.text
    def top_gap2():
      return "   "
    
    @render.text
    def goal_msg():
      return 'What are your DEI goals?'
    
    @render.text
    def data_input_msg():
      return "Let\'s get to know your organization"    
    
    # Render image from directory: Privacy Message
    @render.image
    def logo():
      dir = Path(__file__).resolve().parent
      img: ImgData = {"src": str(dir / "CapstoneLogo.png"), 'width': '400px'}
      return img
    
    # Render image from directory: Privacy Message
    @render.image
    def mockup():
      dir = Path(__file__).resolve().parent
      img: ImgData = {"src": str(dir / "mockup.png"), 'width':'725px'}
      return img

    # Functions to return formatted text of relevant inquiries
    @render.text
    def goal_name_rep_goal():
      return f'What is your representation goal for {format_group(input.target_group())} employees?'
    
    @render.text
    def goal_name_rep_goal2():
      return f'What is your representation goal for {format_group(input.target_group())} employees?'

    @render.text
    def goal_name_now_rep():
      return f'What is the current representation of {format_group(input.target_group())} employees?'
    
    @render.text
    def hire_rep_p():
      return f'What percentage of your new hires last year were {format_group(input.target_group())}?'
    
    @render.text
    def hire_rep_num():
      return f'How many of your new hires last year were {format_group(input.target_group())}?'
    
    @render.text
    def tg_attrition_r():
      #conditional to fix the grammar
      if format_group(input.target_group()) == 'Women':
        group = 'Female'
      else: 
        group = format_group(input.target_group())
      
      return "What was the attrition rate for " + group + ' Employees last year?'
    
    @render.text
    def non_tg_attrition_r():
      #conditional to fix the grammar
      if format_group(input.target_group()) == 'Women':
        group = 'Female'
      else: 
        group = format_group(input.target_group())
      
      return "What was the attrition rate for Non-" + group + ' Employees last year?'
    
    @render.text
    def tg_attrition_num():
      #conditional to fix the grammar
      if format_group(input.target_group()) == 'Women':
        group = 'Female'
      else: 
        group = format_group(input.target_group())
      return "How many " + group + " employees left last year?"
    
    @render.text
    def non_tg_attrition_num():
      #conditional to fix the grammar
      if format_group(input.target_group()) == 'Women':
        group = 'Female'
      else: 
        group = format_group(input.target_group())
      return "How many of Non-" + group + " employees left last year?"
    
    @render.text
    def ts_transfer_p():
      return f'What percentage of transfers were {format_group(input.target_group())}?'
    
    @render.text
    def ts_transfer_num():
      return f"How many transfers were {format_group(input.target_group())}?"
    
    @render.text
    def ts_promotion_p():
      #conditional to fix the grammar
      if format_group(input.target_group()) == 'Women':
        group = 'Female'
      else: 
        group = format_group(input.target_group())
      
      return "What percent of promotions that went to " + group + " employees?"
    
    @render.text
    def ts_promotion_num():
      #conditional to fix the grammar
      if format_group(input.target_group()) == 'Women':
        group = 'Female'
      else: 
        group = format_group(input.target_group())
      
      return "How many promotions went to " + group + " employees?"
    
    
    #function to create labels for the initial and the inserted accordion panels
    def generate_label(group, label):
      #case/switch statemtne to determine what label to generate
        if label == "noets":
          return f'What is the current representation of {format_group(input.target_group())} employees?'
        elif label == "nohts":
          return f'How many of your new hires last year were {format_group(input.target_group())}?'
        elif label == "nosts":
          if group == 'Women':
            group = 'Female'
          else: 
            group = group
          return "How many " + group + " employees left last year?"
        elif label == "promsts":
          if group == 'Women':
            group = 'Female'
          else: 
            group = group
          return "How many promotions went to " + group + " employees?"
        elif label == "transfersts":
          return f"How many transfers were {format_group(input.target_group())}?"

    @render.ui
    def render_initial_panel():
    #function necessary to render initial UI in the accordion dynamically    
    #offset necessary to create a zero index
        i = str(0)
  
        if input.use_numbers() == False:
          hires_ts = round(input.new_hires() * (input.target_hire_percent()/100))
          seperations_nts = round((input.total_employees() - round(input.total_employees() * (input.current_percent()/100))) * (input.non_target_attrition_rate()/100))
          seperations_ts = round(round(input.total_employees() * (input.current_percent()/100)) * (input.target_attrition_rate()/100))
        else:
          hires_ts = input.target_hire_number()
          seperations_nts = input.non_target_left_number()
          seperations_ts = input.target_left_number()

        common_UI_inputs =   [ui.input_numeric(id= "noe" + i, width='100%', label = "How many employees do you have?", value = input.total_employees(), min=0, step=1),
                         ui.input_numeric(id = "noets" + i, label = generate_label(format_group(input.target_group()), "noets"), value = floor((input.current_percent()/100)*input.total_employees()), min=0, step=1,width='100%'),
                         ui.input_numeric(id = "noh" + i, label = "How many new hires did you make last year?", value = input.new_hires(), min=0, step=1,width='100%'),
                         ui.input_numeric(id = "nohts" + i, label = generate_label(format_group(input.target_group()), "nohts"), value = hires_ts, min=0, step=1,width='100%'),
                         ui.input_numeric(id = "nos" + i, label = "How many employees left last year? ", value =  (seperations_nts + seperations_ts), min=0, step=1,width='100%'),
                         ui.input_numeric(id = "nosts" + i, label = generate_label(format_group(input.target_group()), "nosts"), value = seperations_ts, min=0, step=1,width='100%')]
        
        #add extra inputs depending on the target scope
        if input.target_scope() == 'Leadership':
          if input.use_numbers() == False:
            promotions_ts = floor(input.promotions() * (input.target_promotion_percent()/100))
          else:
            promotions_ts = input.target_promotion_number()
          common_UI_inputs.insert(3, ui.input_numeric('proms' + i, "How many promotions did you have last year?", value = input.promotions(), min=0, step=1,width='100%'))
          common_UI_inputs.insert(4, ui.input_numeric('promsts' + i, generate_label(format_group(input.target_group()), "promsts"), value = promotions_ts, min=0, step=1,width='100%'))
        elif input.target_scope() == 'Department':
          if input.use_numbers() == False:
            transfers_ts = floor(input.transfers() * (input.target_transfer_percent()/100))
          else:
            transfers_ts = input.target_transfer_number()
          common_UI_inputs.insert(3, ui.input_numeric('transfers' + i, "How many transfers did you have last year?", value = input.transfers(), min=0, step=1,width='100%'))
          common_UI_inputs.insert(4, ui.input_numeric('transfersts' + i, generate_label(format_group(input.target_group()), "transfersts"), value = transfers_ts, min=0, step=1,width='100%'))
        
        return common_UI_inputs
    
    
    def generate_inputs(i, update_target_segment = False):
      #function to render additional accordion UI dynamically
      #taking the absolute prevents an error and represents the number of variables to be accounted for
      i = str(abs(i))
      
      if i == str(0) and update_target_segment == False:
        noe_value = input.total_employees()
        noets_value = floor((input.current_percent()/100)*input.total_employees())
        noh_value = input.new_hires()
        if input.use_numbers() == False:
          hires_ts = round(input.new_hires() * (input.target_hire_percent()/100))
          seperations_nts = round((input.total_employees() - round(input.total_employees() * (input.current_percent()/100))) * (input.non_target_attrition_rate()/100))
          seperations_ts = round(round(input.total_employees() * (input.current_percent()/100)) * (input.target_attrition_rate()/100))
        else:
          hires_ts = input.target_hire_number()
          seperations_nts = input.non_target_left_number()
          seperations_ts = input.target_left_number()
      #if an existing ui element is not being updated
      elif update_target_segment == False:
        noe_value = 0
        noets_value = 0
        noh_value = 0
        hires_ts = 0
        seperations_nts = 0
        seperations_ts = 0
      #if an existing ui element is being updated
      elif update_target_segment == True: 
        noe_value = input[f"noe{i}"]()
        noets_value = 0
        noh_value = input[f"noh{i}"]()
        hires_ts = 0
        seperations_nts = 0
        seperations_ts = 0

      common_inputs =   [ui.input_numeric(id= "noe" + i, label = " How many employees do you have? ", value = noe_value, min=0, step=1,width='100%'),
                         ui.input_numeric(id = "noets" + i, label = generate_label(format_group(input.target_group()), "noets"), value = noets_value, min=0, step=1,width='100%'),
                         ui.input_numeric(id = "noh" + i, label = " How many new hires did you make last year? ", value = noh_value, min=0, step=1,width='100%'),
                         ui.input_numeric(id = "nohts" + i, label = generate_label(format_group(input.target_group()), "nohts"), value = hires_ts, min=0, step=1,width='100%'),
                         ui.input_numeric(id = "nos" + i, label = " How many employees left last year? ", value =  (seperations_nts + seperations_ts), min=0, step=1,width='100%'),
                         ui.input_numeric(id = "nosts" + i, label = generate_label(format_group(input.target_group()), "nosts"), value = seperations_ts, min=0, step=1,width='100%')]
        
        #add extra inputs depending on the target scope
      if input.target_scope() == 'Leadership' and i == 0:
          promotions_value = input.promotions()
          if input.use_numbers() == False:
            promotions_ts = floor(input.promotions() * (input.target_promotion_percent()/100))
          else:
            promotions_ts = input.target_promotion_number()
      else: 
        promotions_value = 0
        promotions_ts = 0
      
      if input.target_scope() == 'Department' and i == 0:
        transfers_value = input.transfers()
        if input.use_numbers() == False:
          transfers_ts = floor(input.transfers() * (input.target_transfer_percent()/100))
        else:
          transfers_ts = input.target_transfer_number()
      else: 
        transfers_value = 0
        transfers_ts = 0

      if input.target_scope() == 'Leadership':
        common_inputs.insert(3, ui.input_numeric('proms' + i, "Number of Promotions", value = promotions_value, min=0, step=1,width='100%'))
        common_inputs.insert(5, ui.input_numeric('promsts' + i, generate_label(format_group(input.target_group()), "promsts"), value = promotions_ts, min=0, step=1,width='100%'))
      elif input.target_scope() == 'Department':
        common_inputs.insert(3, ui.input_numeric('transfers' + i, "Number of Transfers", value = transfers_value, min=0, step=1,width='100%'))
        common_inputs.insert(5, ui.input_numeric('transfersts' + i, generate_label(format_group(input.target_group()), "transfersts"), value = transfers_ts, min=0, step=1,width='100%'))
      
      return common_inputs
    
    def make_panel(i) -> ui.AccordionPanel:
      #numeric offset needed to generate the prior years in the correct order
      return ui.accordion_panel(f"Data for {date.today().year - (i+1)}", generate_inputs(i))
    
    @reactive.Effect
    @reactive.event(input.add_inputs)
    def _():
        #keeps track of the year being generated, allows user to at and remove years as they want
        ui.insert_accordion_panel("acc", make_panel((input.add_inputs()- input.remove_inputs())))

    @reactive.Effect
    @reactive.event(input.remove_inputs)
    def _():

        # Remove panel, +2 needed to remove the most recently added years due to other ofsets in the code
        ui.remove_accordion_panel("acc", f"Data for {(date.today().year - ((input.add_inputs()+2) - input.remove_inputs()))}")
 
      #function needed to update additional UI if a setting changes
    @reactive.Effect
    @reactive.event( input.target_group, input.target_scope, ignore_none=True)
    def _():
      #update the labels, preserve the general inputs when the target segment is changed and reset everthing to zero, changing the target scope also resets to zero
      #iterate through each panel and regenerate their inputs when the target group or scope changes
      #zip needed to iterate throught two ranges and -1 and +1 needed because range is not incluse of the last value
      for year, i in zip(range(date.today().year -1, ((date.today().year - ((input.add_inputs()+2) - input.remove_inputs()))) -1, -1), range(0, (input.add_inputs()- input.remove_inputs())+1)):
        ui.update_accordion_panel("acc", f"Data for {year}", generate_inputs(i, update_target_segment = True))
    
    #function to organize the inputs into a dataframe for future calculations
    @reactive.calc
    def inputs_to_df():
    
      #list to collect data from each condition/year           
      multi_year_data = []
      
      #single year case or multiyear case.
      year_case_conditions = input.add_inputs() - input.remove_inputs()
      
      if year_case_conditions <= 0:
        data_row = {
          'year': date.today().year - 1,
          'total_employees': input.total_employees(),
          'target_seg_rep': floor((input.current_percent()/100)*input.total_employees()),
          'new_hires': input.new_hires(),
          'target_seg_attrition': floor(floor(input.total_employees() * (input.current_percent()/100)) * (input.target_attrition_rate()/100)),
          'non_target_seg_attrition':floor((input.total_employees() - floor(input.total_employees() * (input.current_percent()/100))) * (input.non_target_attrition_rate()/100)),
          'new_hires_target_seg_rep':input.new_hires() * (input.target_hire_percent()/100) 
          }
            #conditionals for target scope
        
        if input.use_numbers() == True:
          data_row.update({
          'target_seg_attrition': input.target_left_number(),
          'non_target_seg_attrition':input.non_target_left_number(),
          'new_hires_target_seg_rep': input.target_hire_number(),
          })
        
        #if floor forces attrition to zero, change it to 1
        if data_row['non_target_seg_attrition'] == 0:
          data_row['non_target_seg_attrition'] = 1
        if data_row['target_seg_attrition'] == 0:
          data_row['target_seg_attrition'] = 1

        if input.target_scope() == "Leadership":
          data_row['promotions'] = input.promotions()
          data_row['promotions_target_seg_rep'] = int((input.target_promotion_percent()/100) * input.promotions())
          if input.use_numbers() == True:
            data_row.update({'promotions_target_seg_rep': input.target_promotion_number()}),
          
        if input.target_scope() == "Department":
          data_row['transfers_target_seg_rep'] = int((input.target_transfer_percent()/100) * input.transfers())
          data_row['transfers'] = input.transfers()
          if input.use_numbers() == True:
            data_row.update({'transfers_target_seg_rep': input.target_transfer_number()}),
            
        multi_year_data.append(data_row)     

        
      else:
        #for addtional years of data. 
        for i in range(0, year_case_conditions + 1):
          data_row = {
            'year' : date.today().year - (i + 1),
            'total_employees': int(input[f"noe{i}"]()),
            'target_seg_rep' : int(input[f"noets{i}"]()),
            'new_hires' : int(input[f"noh{i}"]()),
            'new_hires_target_seg_rep' : int(input[f"nohts{i}"]()),
            'target_seg_attrition' : int(input[f"nosts{i}"]()),
            'non_target_seg_attrition': (int(input[f"nos{i}"]()) - int(input[f"nosts{i}"]())),
          }
            
          if input.target_scope() == "Leadership":
            data_row['promotions'] = int(input[f"proms{i}"]())
            data_row["promotions_target_seg_rep"] = int(input[f"promsts{i}"]())
               
          elif input.target_scope() == "Department":
            data_row['transfers'] = int(input[f"transfers{i}"]())
            data_row['transfers_target_seg_rep'] = int(input[f"transfersts{i}"]())
        
          multi_year_data.append(data_row)
  
      #Create the DF
      df = pd.DataFrame(data = multi_year_data)
      #df = df_pre[(df.iloc[:, 1:] != 0).any(axis=1)]
      df.set_index('year', inplace=True)
      
      #filter rows where all DEI inputs are not zero. 
      return df
     

    #function for projection
    @reactive.Calc
    def project():
      
      #read in the inputs from the inputs_to_df function
      df = inputs_to_df()
      df.rename(columns = {'Total Employees':'total_employees', 
                      f'Number of {format_group(input.target_group(), plot_or_table = True)} Employees':'target_seg_rep', 
                      'New Hires':'new_hires', 
                      f'New Hires who are {format_group(input.target_group(), plot_or_table = True)}':'new_hires_target_seg_rep', 
                      f'{format_group(input.target_group(), plot_or_table = True)} Employee Seperations':'target_seg_attrition', 
                      f'Non-{format_group(input.target_group(), plot_or_table = True)} Employee Seperations':'non_target_seg_attrition', 
                      f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)':'target_seg_rep_p'}, inplace = True)
                      
      #logic for a projection, linear assumptions, for multi-year inputs take average (assume normal distribution)
      #net change in target segment (all using numbers)
      if input.target_scope() == 'Company-wide': 
        ts_net_change = df['new_hires_target_seg_rep'] - df["target_seg_attrition"]
        ts_hires = df['new_hires_target_seg_rep']
        ts_attrition = df["target_seg_attrition"]
        #take averages and round for multi year inputs
        if len(ts_net_change) > 1:
          ts_hires = ts_hires.mean().round()
          ts_attrition = ts_attrition.mean().round()
          ts_net_change =  ts_hires - ts_attrition 
      
      elif input.target_scope() == 'Leadership':
        ts_net_change = (df['new_hires_target_seg_rep'] + df['promotions_target_seg_rep']) - df["target_seg_attrition"]
        ts_hires = df['new_hires_target_seg_rep']
        ts_promotions = df['promotions_target_seg_rep']
        ts_attrition = df["target_seg_attrition"]
        #take averages and round for multi year inputs
        if len(ts_net_change) > 1:
          ts_hires = ts_hires.mean().round()
          ts_promotions = ts_promotions.mean().round()
          ts_attrition = ts_attrition.mean().round()
          ts_net_change = (ts_hires + ts_promotions) - ts_attrition
      
      elif input.target_scope() == 'Department':
        ts_net_change = (df['new_hires_target_seg_rep'] + df['transfers_target_seg_rep']) - df["target_seg_attrition"]
        ts_hires = df['new_hires_target_seg_rep']
        ts_transfers = df['transfers_target_seg_rep']
        ts_attrition = df["target_seg_attrition"]
        #take averages and round for multi year inputs
        if len(ts_net_change) > 1:
          ts_hires = df['new_hires_target_seg_rep'].mean().round()
          ts_transfers = df['transfers_target_seg_rep'].mean().round()
          ts_attrition = df["target_seg_attrition"].mean().round()
          ts_net_change = (ts_hires + ts_transfers) - ts_attrition 
 
      
      #net change in non-target segment
      if input.target_scope() == 'Company-wide': 
        non_ts_net_change = (df['new_hires'] - df['new_hires_target_seg_rep']) - df["non_target_seg_attrition"]
        non_ts_hires = df['new_hires'] - df['new_hires_target_seg_rep']
        non_ts_attrition = df["non_target_seg_attrition"]
        #take averages and round for multi year inputs
        if len(non_ts_net_change) > 1:
          non_ts_hires = non_ts_hires.mean().round()
          non_ts_attrition = non_ts_attrition.mean().round()
          non_ts_net_change = non_ts_hires - non_ts_attrition 
      
      elif input.target_scope() == 'Leadership':
        non_ts_net_change = ((df['new_hires'] - df['new_hires_target_seg_rep']) + (df['promotions'] - df['promotions_target_seg_rep'])) - df["non_target_seg_attrition"]
        non_ts_hires = df['new_hires'] - df['new_hires_target_seg_rep']
        non_ts_promotions = df['promotions'] - df['promotions_target_seg_rep']
        non_ts_attrition = df["non_target_seg_attrition"]
        #take averages and round for multi year inputs
        if len(non_ts_net_change) > 1:
          non_ts_hires = non_ts_hires.mean().round()
          non_ts_promotions = non_ts_promotions.mean().round()
          non_ts_attrition = non_ts_attrition.mean().round()
          non_ts_net_change = (non_ts_hires + non_ts_promotions) - non_ts_attrition
        
      elif input.target_scope() == 'Department':
        non_ts_net_change = ((df['new_hires'] - df['new_hires_target_seg_rep']) + (df['transfers'] - df['transfers_target_seg_rep'])) - df["non_target_seg_attrition"]
        non_ts_hires = df['new_hires'] - df['new_hires_target_seg_rep']
        non_ts_transfers = df['transfers'] - df['transfers_target_seg_rep']
        non_ts_attrition = df["non_target_seg_attrition"]
          #take averages and round for multi year inputs
        if len(non_ts_net_change) > 1:
          non_ts_hires = non_ts_hires.mean().round()
          non_ts_transfers = non_ts_transfers.mean().round()
          non_ts_attrition = non_ts_attrition.mean().round()
          non_ts_net_change = (non_ts_hires + non_ts_transfers) - non_ts_attrition
      
      
      #project forward with a loop assuming the same net change each year
      year = date.today().year
      
      #code to stop the projection once the goal was reached
      #projected_target_seg_rep_p = 0
      #projected_target_seg_rep_p < input.target_percent()
      
      while year < date.today().year + 10:
        df.loc[year, "target_seg_rep"] = df.loc[year -1, "target_seg_rep"] + int(ts_net_change)
        df.loc[year, "total_employees"] = df.loc[year -1, "total_employees"] + int(ts_net_change) + int(non_ts_net_change)
        
        #round to 3 decimal places
        df.loc[year, "target_seg_rep_p"] = (df.loc[year, "target_seg_rep"]/df.loc[year, "total_employees"]).round(decimals=3)
        
        #this doesn't have to be in the loop but placing it inside since we might iterate on our method
        df.loc[year, "new_hires_target_seg_rep"] = int(ts_hires)
        df.loc[year, "target_seg_attrition"] = int(ts_attrition)
        df.loc[year, "new_hires"] = int(ts_hires) + int(non_ts_hires)
        df.loc[year, "non_target_seg_attrition"] = int(non_ts_attrition)
        
        if input.target_scope() == 'Leadership':
          df.loc[year, 'promotions'] = int(ts_promotions) + int(non_ts_promotions)
          df.loc[year, 'promotions_target_seg_rep'] = int(ts_promotions)
        elif input.target_scope() == 'Department':
          df.loc[year, 'transfers'] = int(ts_transfers) + int(non_ts_transfers)
          df.loc[year, 'transfers_target_seg_rep'] = int(ts_transfers)
        
        #flag for loop, the percent is given in the ui as an int
        projected_target_seg_rep_p =  df.loc[year, "target_seg_rep_p"]*100
        #fill in the other columns in the loop
        
        #increment the year
        year += 1
        
        #code that was uses to stop projection once the goal was reached or ten years
        #stop calculation if it will take more than 10 years to reach the goal
        #if year > date.today().year + 10:
        #  break
      
      df.sort_values('year', inplace = True)
      
      cols = ["total_employees", "target_seg_rep", "new_hires", "new_hires_target_seg_rep", "non_target_seg_attrition", "target_seg_attrition", "target_seg_rep_p"]

      if input.target_scope() == 'Leadership':
        cols.insert(-1, 'promotions')
        cols.insert(-1, 'promotions_target_seg_rep')
      elif input.target_scope() == 'Department':
        cols.insert(-1, 'transfers')
        cols.insert(-1, 'transfers_target_seg_rep')

      #reorder columns to match how they will be displayed
      df = df[cols]

      return df
    
    
    # Create a reactive value for tracking cell changes
    change_list = []
    cell_changes = reactive.Value()

    def on_cell_changed(cell):
        cell_changes.set(str(cell))
    
    #function to append the cell changes to the list   
    @reactive.Effect
    def append_change_list():
      change_list.append(eval(cell_changes()))
    
    reprojection = reactive.Value(None)
    
    #function to recalculate the projection based on the user input to the output table
    @reactive.effect
    @reactive.event(cell_changes)
    def recalc_projection():
      
      #if no cell changes have been made, use the initial projection otherwise use the newest projection
      if len(change_list) == 1:
        df = project()
      else:
        df = reprojection.get()
      
      #rename back to what the function expects
      df.rename(columns = {'Total Employees':'total_employees', 
                           f'Number of {format_group(input.target_group(), plot_or_table = True)} Employees':'target_seg_rep', 
                           'New Hires':'new_hires', 
                           f'New Hires who are {format_group(input.target_group(), plot_or_table = True)}':'new_hires_target_seg_rep', 
                           f'{format_group(input.target_group(), plot_or_table = True)} Employee Seperations':'target_seg_attrition', 
                           f'Non-{format_group(input.target_group(), plot_or_table = True)} Employee Seperations':'non_target_seg_attrition', 
                           f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)':'target_seg_rep_p',
                           'Promotions': 'promotions',
                           f'# of {format_group(input.target_group(), plot_or_table = True)} Promoted': 'promotions_target_seg_rep',
                           'Transfers':'transfers',
                           f'# of {format_group(input.target_group(), plot_or_table = True)} Transfered': 'transfers_target_seg_rep'}, inplace = True)
      
      df.rename_axis(index = 'year', inplace = True)
                           
      
      if len(change_list) > 0:
      
        #verbose integer index slicing to get the year that was changed, add 1 due to filtering in the displayed data
        change_year = df.iloc[[(change_list[-1]['row'])+1]].index.values[0]
        
        #capture old value to be used with the change year update
        old_value = df.iloc[(change_list[-1]['row'])+1,change_list[-1]['column_index']]

        #make change in df, add 1 due to filtering in the displayed data
        df.iloc[(change_list[-1]['row'])+1,change_list[-1]['column_index']] = change_list[-1]['value']
        
        #update the year that was changed
        changed_column = df.columns[change_list[-1]['column_index']]
        change_in_value = change_list[-1]['value'] - old_value
        if changed_column in ['new_hires_target_seg_rep', 'promotions_target_seg_rep', 'transfers_target_seg_rep']:
          df.loc[change_year, 'target_seg_rep'] = df.loc[change_year, 'target_seg_rep'] + change_in_value
        elif changed_column in ['new_hires', 'promotions', 'transfers']:
          df.loc[change_year,'total_employees'] = df.loc[change_year,'total_employees'] + change_in_value
        elif changed_column == 'target_seg_attrition':
          df.loc[change_year, 'target_seg_rep'] = df.loc[change_year, 'target_seg_rep'] - change_in_value
        elif changed_column == 'non_target_seg_attrition':
          df.loc[change_year,'total_employees'] = df.loc[change_year,'total_employees'] - change_in_value

        #update the target segment representation for the change year
        df.loc[change_year, 'target_seg_rep_p'] = (df.loc[change_year, 'target_seg_rep']/df.loc[change_year,'total_employees']).round(decimals=3) 

        #filter df to take all projected data prior to the change
        temp_df = df[df.index <= change_year]
        
  
        #take averages from the temp df, reuse projection code, will need to inverse any renaming of the columns to reuse the code
        
        #logic for a projection, linear assumptions, for multi-year inputs take average (assume normal distribution)
        #net change in for target and non-target segment (all using numbers)
        if input.target_scope() == 'Company-wide': 
          ts_net_change = temp_df['new_hires_target_seg_rep'] - temp_df["target_seg_attrition"]
          ts_hires = temp_df['new_hires_target_seg_rep']
          ts_attrition = temp_df["target_seg_attrition"]
          non_ts_net_change = (temp_df['new_hires'] - temp_df['new_hires_target_seg_rep']) - temp_df["non_target_seg_attrition"]
          non_ts_hires = temp_df['new_hires'] - temp_df['new_hires_target_seg_rep']
          non_ts_attrition = temp_df["non_target_seg_attrition"]
          #take averages and round for multi year inputs
          if len(ts_net_change) > 1:
            ts_hires = ts_hires.mean().round()
            ts_attrition = ts_attrition.mean().round()
            ts_net_change =  ts_hires - ts_attrition
            non_ts_hires = non_ts_hires.mean().round()
            non_ts_attrition = non_ts_attrition.mean().round()
            non_ts_net_change = non_ts_hires - non_ts_attrition
        
        elif input.target_scope() == 'Leadership':
          ts_net_change = (temp_df['new_hires_target_seg_rep'] + temp_df['promotions_target_seg_rep']) - temp_df["target_seg_attrition"]
          ts_hires = temp_df['new_hires_target_seg_rep']
          ts_promotions = temp_df['promotions_target_seg_rep']
          ts_attrition = temp_df["target_seg_attrition"]
          non_ts_net_change = ((temp_df['new_hires'] - temp_df['new_hires_target_seg_rep']) + (temp_df['promotions'] - temp_df['promotions_target_seg_rep'])) - temp_df["non_target_seg_attrition"]
          non_ts_hires = temp_df['new_hires'] - temp_df['new_hires_target_seg_rep']
          non_ts_promotions = temp_df['promotions'] - temp_df['promotions_target_seg_rep']
          non_ts_attrition = temp_df["non_target_seg_attrition"]
          #take averages and round for multi year inputs
          if len(ts_net_change) > 1:
            ts_hires = ts_hires.mean().round()
            ts_promotions = ts_promotions.mean().round()
            ts_attrition = ts_attrition.mean().round()
            ts_net_change = (ts_hires + ts_promotions) - ts_attrition
            non_ts_hires = non_ts_hires.mean().round()
            non_ts_promotions = non_ts_promotions.mean().round()
            non_ts_attrition = non_ts_attrition.mean().round()
            non_ts_net_change = (non_ts_hires + non_ts_promotions) - non_ts_attrition
        
        elif input.target_scope() == 'Department':
          ts_net_change = (temp_df['new_hires_target_seg_rep'] + temp_df['transfers_target_seg_rep']) - temp_df["target_seg_attrition"]
          ts_hires = temp_df['new_hires_target_seg_rep']
          ts_transfers = temp_df['transfers_target_seg_rep']
          ts_attrition = temp_df["target_seg_attrition"]
          non_ts_net_change = ((temp_df['new_hires'] - temp_df['new_hires_target_seg_rep']) + (temp_df['transfers'] - temp_df['transfers_target_seg_rep'])) - temp_df["non_target_seg_attrition"]
          non_ts_hires = temp_df['new_hires'] - temp_df['new_hires_target_seg_rep']
          non_ts_transfers = temp_df['transfers'] - temp_df['transfers_target_seg_rep']
          non_ts_attrition = temp_df["non_target_seg_attrition"]
          #take averages and round for multi year inputs
          if len(ts_net_change) > 1:
            ts_hires = temp_df['new_hires_target_seg_rep'].mean().round()
            ts_transfers = temp_df['transfers_target_seg_rep'].mean().round()
            ts_attrition = temp_df["target_seg_attrition"].mean().round()
            ts_net_change = (ts_hires + ts_transfers) - ts_attrition
            non_ts_hires = non_ts_hires.mean().round()
            non_ts_transfers = non_ts_transfers.mean().round()
            non_ts_attrition = non_ts_attrition.mean().round()
            non_ts_net_change = (non_ts_hires + non_ts_transfers) - non_ts_attrition
  
  
        #re-project from the change forward
        for year in range(change_year+1, df.index.max()+1):
          df.loc[year, "target_seg_rep"] = df.loc[year -1, "target_seg_rep"] + int(ts_net_change)
          df.loc[year, "total_employees"] = df.loc[year -1, "total_employees"] + int(ts_net_change) + int(non_ts_net_change)
          
          #round to 3 decimal places
          df.loc[year, "target_seg_rep_p"] = (df.loc[year, "target_seg_rep"]/df.loc[year, "total_employees"]).round(decimals=3)
          
          #this doesn't have to be in the loop but placing it inside since we might iterate on our method
          df.loc[year, "new_hires_target_seg_rep"] = int(ts_hires)
          df.loc[year, "target_seg_attrition"] = int(ts_attrition)
          df.loc[year, "new_hires"] = int(ts_hires) + int(non_ts_hires)
          df.loc[year, "non_target_seg_attrition"] = int(non_ts_attrition)
          
          if input.target_scope() == 'Leadership':
            df.loc[year, 'promotions_target_seg_rep'] = int(ts_promotions)
            df.loc[year, 'promotions'] = int(ts_promotions) + int(non_ts_promotions)
          elif input.target_scope() == 'Department':
            df.loc[year, 'transfers_target_seg_rep'] = int(ts_transfers)
            df.loc[year, 'transfers'] = int(ts_transfers) + int(non_ts_transfers)
             

        #after reprojection is made, unset the reactive value to allow the user to make more than one change
        #Set the reprojection to be used in the widgets
        reprojection.unset()
        reprojection.set(df)
        
    @reactive.calc
    def goal_status_annotation():
      if len(change_list) == 0 and reprojection.get() == None:
        samp_df = project()
      else:
        samp_df = reprojection.get()
      # default the time_to_goal as the initial input. If the dynamic goal setting is altered, set that as new time to goal value
      time_to_goal = input.time_to_goal()
      if input.time_to_goal2:
        time_to_goal = input.time_to_goal2()
      # default the target_pct as the initial input. If the dynamic goal setting is altered, set that as new target percent value
      target_pct = input.target_percent()
      if input.target_percent2:
        target_pct = input.target_percent2()
      # Rename Columns
      samp_df = samp_df.rename(columns={'total_employees':'Total Employees', 
                                       'target_seg_rep_p':f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'})
      # Set Year as Index
      samp_df['Year'] = samp_df.index
      # Convert Rep %
      samp_df[f'{format_group(input.target_group())} Representation (%)'] = samp_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'].apply(lambda x: x*100)
      # Plot only projection years
      proj_df = samp_df[samp_df['Year'] > date.today().year-1]
      proj_df = proj_df[0:time_to_goal]
      # Determine annotation message and color based on whether or not the goal was reached
      # Case where projection within the years to goal does not exceed target percentage
      if max(proj_df[format_group(input.target_group(), plot_or_table = True) + ' Representation (%)']) < target_pct:
        # Case where 10 year projection exceeds target percentage
        if max(samp_df[format_group(input.target_group(), plot_or_table = True) + ' Representation (%)'].dropna()) >= target_pct:
          year = samp_df[samp_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'].ge(target_pct)]
          annotation = 'Your goal will be met in **%s**' %year['Year'].iloc[0]
        # Case where target percentage not reached in 10 years
        else:
          annotation = 'Your goal will **not** be met in the next **10 years**'
      # Case where target is reached
      else:
        year = proj_df[proj_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'].ge(target_pct)]
        annotation = 'You will meet your goal in **%s**!' %year['Year'].iloc[0]
      return annotation

    @render.ui
    def goal_status():
      return ui.markdown(goal_status_annotation())

    @render.ui
    def goal_status_icon():
      status = goal_status_annotation()
      #determine the icon to return based on the annotation
      if status.__contains__('Your goal will **not** be met in the next'):
        icon = ICONS['Goal not']
      elif status.__contains__('Your goal will be met in'):
        icon = ICONS['Goal will']
      elif status.__contains__('You will meet your goal'):
        icon = ICONS['cc']
      return icon
    
    @reactive.effect
    def _():
        ttg = input.time_to_goal()
        tp = input.target_percent()
        ui.update_numeric("time_to_goal2", value=ttg)
        ui.update_numeric('target_percent2', value=tp)

    @render_plotly
    def px_plot():
      # Read in dataframe and rename columns with target input
      # if no cell changes have been made, use the initial projection otherwise use the newest projection
      if len(change_list) == 0  and reprojection.get() == None:
        samp_df = project()
      else:
        samp_df = reprojection.get()
        
      # default the time_to_goal as the initial input. If the dynamic goal setting is altered, set that as new time to goal value
      time_to_goal = input.time_to_goal()
      if input.time_to_goal2:
        time_to_goal = input.time_to_goal2()

      # default the target_pct as the initial input. If the dynamic goal setting is altered, set that as new target percent value
      target_pct = input.target_percent()
      if input.target_percent2:
        target_pct = input.target_percent2()
        
      # Rename Columns
      samp_df = samp_df.rename(columns={'total_employees':'Total Employees', 
                                       'target_seg_rep':f'Number of {format_group(input.target_group(), plot_or_table = True)} Employees',
                                       'new_hires':'New Hires',
                                       'target_seg_attrition':f'{format_group(input.target_group(), plot_or_table = True)} Employee Seperations',
                                       'non_target_seg_attrition':f'Non-{format_group(input.target_group(), plot_or_table = True)} Employee Seperations',
                                       'new_hires_target_seg_rep':f'New Hires who are {format_group(input.target_group(), plot_or_table = True)}',
                                       'target_seg_rep_p':f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'})
      
      # Conditional rename for columns specific to leadership
      if input.target_scope() == 'Leadership':
        samp_df = samp_df.rename(columns={'promotions':'Promotions',
                                          'promotions_target_seg_rep': f'# of {format_group(input.target_group(), plot_or_table = True)} Promoted'})
      
      # Conditional rename for columns specific to department
      if input.target_scope() == "Department":
        samp_df = samp_df.rename(columns={'transfers':'Transfers',
                                          'transfers_target_seg_rep': f'# of {format_group(input.target_group(), plot_or_table = True)} Transfered'})
      
      # Set Year as Index
      samp_df['Year'] = samp_df.index

      # Convert Rep %
      samp_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'] = samp_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'].apply(lambda x: x*100)

      #if cell_changes.get():
      #  samp_df.at[eval(cell_changes())['row'], eval(cell_changes())['column']] = eval(cell_changes())['value']

      # Plot only projection years
      proj_df = samp_df[samp_df['Year'] > date.today().year-1]

      proj_df = proj_df[0:time_to_goal]

      y_range = [min(proj_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)']), max(proj_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'])]

      # Scatter Plot, and add an ols trendline
      fig = px.scatter(proj_df.to_dict(), x='Year', y=f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)', trendline='ols')

      # Adjust marker size
      fig.update_traces(marker=dict(size=12, color='rgba(158,214,189,.5)', line=dict(width=1.5, color='rgba(158,214,189,.5)')))

      # Adjust trendline color/opacity
      fig.data[1].update(line_color='rgba(158,214,189,1)')

      # Define x-axis ranges for projection data
      x_range = [min(proj_df['Year']), max(proj_df['Year'])]

      # If plot historical is chosen, plot the projection along with historical points
      if input.plot_type() == 'Plot Historical Data':

        # Define a dataframe consisting only of historical data
        hist_df = samp_df[samp_df['Year'] <= date.today().year-1]
        hist_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'] = hist_df[f'Number of {format_group(input.target_group(), plot_or_table = True)} Employees']*100 / hist_df['Total Employees']

        comb_df = pd.concat([hist_df, proj_df], axis=0)
        y_range = [min(comb_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)']), max(comb_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'])]


        # Re-define x-axis ranges because of historical data
        x_range = [min(comb_df['Year']), max(comb_df['Year'])]


        
        # Separate plot for historical points
        fig_hist = px.scatter(hist_df.to_dict(), x='Year', y=f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)')
        fig_hist.update_traces(marker=dict(size=12, color='rgba(235,121,113,255)'))

        # Combine historical + projection
        fig = go.Figure(data=fig.data + fig_hist.data)
      elif input.plot_type() == 'Overlay Historical Data':

        # Define a dataframe consisting only of historical data
        hist_df = samp_df[samp_df['Year'] <= date.today().year-1]

        # If there are more historical data points than projection points, match the amount of projection points, taking only the most recent historical points
        if len(hist_df) > len(proj_df):
          hist_df = hist_df.tail(len(proj_df))

        # Append new date values for concurrent plotting
        hist_df = hist_df.drop(labels='Year', axis=1)
        hist_df['Year'] = list(proj_df['Year'][0:len(hist_df)])


        hist_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'] = hist_df[f'Number of {format_group(input.target_group(), plot_or_table = True)} Employees']*100 / hist_df['Total Employees']
        comb_df = pd.concat([hist_df, proj_df], axis=0)
        y_range = [min(comb_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)']), max(comb_df[f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'])]

        # Separate plot for historical points
        fig_hist = px.line(hist_df.to_dict(), x='Year', y=f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)')

        # Adjust trendline color/opacity
        fig_hist.data[0].update(line_color='rgba(235,121,113,.3)')

        # Combine historical + projection
        fig = go.Figure(data=fig.data + fig_hist.data)

      # Add a horizontal line to represent the dynamic representation goal set
      fig.add_hline(y=target_pct, line_width=1, line_dash="dash", line_color='rgba(235,170,36,255)', 
              annotation_text="<b>Target Segment Goal<b>", annotation_position="top right", annotation_font_size=15, annotation_font_color='rgba(235,170,36,255)')

      # If the projection does not meet the goal, add a rectangular box between the last projection point and the goal - visualize the distance to goal left
      if proj_df[format_group(input.target_group(), plot_or_table = True) + ' Representation (%)'].iloc[-1] < target_pct:
        fig.add_hrect(y0=proj_df[format_group(input.target_group(), plot_or_table = True) + ' Representation (%)'].iloc[-1], y1=target_pct, line_width=0, fillcolor="rgba(235,170,36,255)", opacity=0.1,
                      annotation_text="<b>Distance to Goal<b>", annotation_position="bottom left", annotation_font_size=15, annotation_font_color='rgba(235,170,36,255)')

      # Plot Aesthetics: 
      # BG Color, 
      # X-axis range: +- 0.2 from the minimum year and maximum year to have nice visual clarity
      # X-axis tick values: Integer count from minimum year to maximum year
      # y-axis range: 
      ## Y-minimum will always be whichever value is smaller between the representation goal - 5 or minimum projection value - 5
      ## Y-maximum will always be whichever value is bigger between representation goal + 5 or maximum projection value + 5
      # X-axis / Y-axis titles
      fig.update_layout(plot_bgcolor='rgba(255,255,255,255)',
                  xaxis={'range': [min(x_range) - .2, max(x_range) + .2], 
                          'tickvals': [*range(int(min(x_range)), int(max(x_range)) + 1)]}, 
                  yaxis_range=[min(target_pct - 5, min(y_range) - 5), 
                                max(target_pct + 5,  max(y_range) + 5)],
                  xaxis_title=dict(text='<b>Year<b>', font=dict(size=18, color='rgba(65,65,65,255)')),
                  yaxis_title=dict(text= '<b>' + format_group(input.target_group(), plot_or_table = True) + ' Representation (%)<b>', font=dict(size=18, color='rgba(65,65,65,255)')),
                  )
      fig.update_xaxes(linewidth=1, linecolor='rgba(180,180,180,255)', mirror=True, ticks='inside', showline=True)
      fig.update_yaxes(linewidth=1, linecolor='rgba(180,180,180,255)', mirror=True, ticks='inside', showline=True)
      return fig

    
    @reactive.effect
    @reactive.event(input.target_scope)
    def reset():
      # lets users change the target scope after they an edit to the table
      # this does reset the user changes, but this seems like an ok behavior
      # I would love if it could be the start of a reset button, but for some reason when I add 
      # a reset button changes made to the table somehow write back to the initial projection 
      # and I don't know how to solve it
      change_list.clear()
      reprojection.set(None)
    
    
    @render_widget
    def tbl_widget():

      if len(change_list) == 0 and reprojection.get() == None:
        display_df = project().copy()
      else:
        display_df = reprojection.get()
      
      display_df = display_df[(display_df.index <= date.today().year + input.time_to_goal2() - 1) & (display_df.index >= date.today().year)]
        
      #rename the columns 
      display_df.rename(columns = {'total_employees':'Total Employees', 
                           'target_seg_rep': f'Number of {format_group(input.target_group(), plot_or_table = True)} Employees', 
                           'new_hires': 'New Hires', 
                           'new_hires_target_seg_rep': 'New Hires who are in the Target Group' if format_group(input.target_group(), plot_or_table = True).__contains__('Target Group') else f'New Hires who are {format_group(input.target_group(), plot_or_table = True)}', 
                           'target_seg_attrition': f'{format_group(input.target_group(), plot_or_table = True)} Employee Seperations', 
                           'non_target_seg_attrition': f'Non-{format_group(input.target_group(), plot_or_table = True)} Employee Seperations', 
                           'target_seg_rep_p': f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)'}, inplace = True)
      display_df.rename_axis(index = 'Year', inplace = True)
      cols = ['Total Employees', f'Number of {format_group(input.target_group(), plot_or_table = True)} Employees', 
              'New Hires', 
              'New Hires who are in the Target Group' if format_group(input.target_group(), plot_or_table = True).__contains__('Target Group') else f'New Hires who are {format_group(input.target_group(), plot_or_table = True)}',               
              f'Non-{format_group(input.target_group(), plot_or_table = True)} Employee Seperations', f'{format_group(input.target_group(), plot_or_table = True)} Employee Seperations',
              ]
      col_size=208
      if input.target_scope() == 'Leadership':
        display_df.rename(columns = {'promotions':'# Promoted',
                             'promotions_target_seg_rep': '# %s Promoted' %format_group(input.target_group(), plot_or_table = True)}, inplace = True)
        cols.append('# Promoted')
        cols.append('# %s Promoted' %format_group(input.target_group(), plot_or_table = True))
        col_size=160
      elif input.target_scope() == 'Department':
        display_df.rename(columns = {'transfers': '# Transfers',
                             'transfers_target_seg_rep': '# %s Transfers' %format_group(input.target_group(), plot_or_table = True)}, inplace = True)
        cols.append('# Transfers')
        cols.append('# %s Transfers' %format_group(input.target_group(), plot_or_table = True))
        col_size = 160
      cols.append(f'{format_group(input.target_group(), plot_or_table = True)} Representation (%)')
      display_df = display_df[cols]

      #code for editable projection table, code taken from: https://stackoverflow.com/questions/77252602/is-there-a-table-widget-for-shiny-for-python-that-calls-back-edited-cells
      tbl = DataGrid(display_df, editable=True, base_column_size=col_size, default_renderer = TextRenderer(text_color="black", font = '15px sans-serif', horizontal_alignment = 'right', vertical_alignment = 'center', background_color = Expr(horizontal_striping)), 
                    header_renderer = TextRenderer(text_color="black", height= '300px', font = '20px sans-serif', horizontal_alignment = 'right', text_wrap = True), 
                    renderers = {'Year': TextRenderer(text_color="black", font = '15px sans-serif', horizontal_alignment = 'right', vertical_alignment = 'center', background_color = Expr(horizontal_striping))},
                    base_column_header_size = 120, base_row_size = 40,
                    grid_style = {'vertical_grid_line_color': '#C0C0C0', 'horizontal_grid_line_color': '#C0C0C0', 'header_vertical_grid_line_color': '#FFFFFF', 'header_horizontal_grid_line_color':'#C0C0C0'})
      register_widget("table", tbl)
      # register callback
      tbl.on_cell_change(on_cell_changed)
      return tbl
    
    @render.download(filename='Included_DEI_Report_%s.txt' %date.today())
    def downloadReport():
      text = llm_output()
      yield text
      
    @render.ui
    def llm_ai():
      return ui.markdown('Powered by AI')

    @reactive.calc
    def llm_output():
       
      if input.llm_gen() == 0:
        #sample output/defualt load
        text ="***These are high level recommendations we have generated for you. When you generate a new recommendation, it may take a moment to appear.***\n\n**Assess the Current State:**\n\n* Conduct a diversity audit to evaluate representation across different demographics (e.g., race, gender, ethnicity, disability, sexual orientation).\n* Gather employee feedback through surveys or focus groups to identify areas for improvement.\n* Review existing policies and practices to identify possible barriers or biases.\n\n**Set Goals and Objectives:**\n\n* Define clear goals for improving DEI, such as increasing representation in leadership roles or reducing pay gaps.\n* Establish measurable objectives to track progress and hold stakeholders accountable.\n\n**Implement Targeted Initiatives:**\n\n* Develop and implement targeted recruitment and hiring programs to attract a diverse candidate pool.\n* Provide training and support for employees to foster inclusive behaviors and reduce unconscious bias.\n* Establish employee resource groups (ERGs) to provide support and advocacy for underrepresented groups.\n\n**Create an Inclusive Culture:**\n\n* Encourage employees to share their perspectives and experiences, and actively listen to their voices.\n* Foster a sense of belonging by celebrating diversity and recognizing contributions from all employees.\n* Implement policies and practices that promote flexibility, work-life balance, and accessibility.\n\n**Empower Leadership:**\n\n* Train leaders on the importance of DEI and their role in creating an inclusive environment.\n* Hold leaders accountable for promoting DEI within their teams and the organization.\n* Encourage leaders to seek feedback from employees and make adjustments as needed.\n\n**Measure and Evaluate Progress:**\n\n* Track key performance indicators (KPIs) such as representation, employee satisfaction, and turnover rates.\n* Conduct regular evaluations to assess the effectiveness of DEI initiatives and make necessary adjustments.\n* Share progress and successes with employees to foster transparency and accountability.\n\n**Continuous Improvement:**\n\n* Recognize that DEI is an ongoing journey, not a destination.\n* Seek continuous feedback from employees and stakeholders to identify areas for improvement.\n* Stay informed about best practices and emerging trends in DEI to enhance the organization's approach.\n\n**Additional Tips:**\n\n* Involve employees in the development and implementation of DEI initiatives to ensure buy-in and support.\n* Communicate DEI goals and initiatives clearly and regularly to employees.\n* Provide ongoing opportunities for employees to learn about and engage with different cultures and perspectives.\n* Partner with external organizations or consultants to provide expertise and support."
      else:
        #set working directory to the location of the file to load the .env file
        os.chdir(os.path.dirname(__file__))
        load_dotenv()
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
    
        df = project()
        df_str = df.to_string()
        
        time = input.time_to_goal()
        group = input.target_group()
        level = input.target_scope()
        industry = input.industry()
        custom = input.llm_option()

      

        prompt = (
            f"Here is a overarching focus to narrow your recommendation:\n{custom}.\n"
            f"You're going to be given some projection data, timeline, and groups for an analysis and insight generation. This is the level \n{level}\n at which I would like the changes to take place."
            f"If this \n{industry}\n is provided incorporate that into the insight recommendations."
            f"Here is the projection of that data:\n{df_str}\n this data extends out 10 years. But the recommendation should be based on the specificed timeline which is this:number of years \n{time}\n" 
            f"Please provide insights based on the projection data that would allow the organization to reach desired goal. Use quantitative recommendations"
            f"What are some \n{group}\n specific changes that can yield immediate improves within the next year?")
        response = model.generate_content(prompt)
        text = response.text
    
      return text
      
     
    llm_response_with_load_message = reactive.value("***These are high level recommendations we have generated for you. When you generate a new recommendation, it may take a moment to appear.***\n\n**Assess the Current State:**\n\n* Conduct a diversity audit to evaluate representation across different demographics (e.g., race, gender, ethnicity, disability, sexual orientation).\n* Gather employee feedback through surveys or focus groups to identify areas for improvement.\n* Review existing policies and practices to identify possible barriers or biases.\n\n**Set Goals and Objectives:**\n\n* Define clear goals for improving DEI, such as increasing representation in leadership roles or reducing pay gaps.\n* Establish measurable objectives to track progress and hold stakeholders accountable.\n\n**Implement Targeted Initiatives:**\n\n* Develop and implement targeted recruitment and hiring programs to attract a diverse candidate pool.\n* Provide training and support for employees to foster inclusive behaviors and reduce unconscious bias.\n* Establish employee resource groups (ERGs) to provide support and advocacy for underrepresented groups.\n\n**Create an Inclusive Culture:**\n\n* Encourage employees to share their perspectives and experiences, and actively listen to their voices.\n* Foster a sense of belonging by celebrating diversity and recognizing contributions from all employees.\n* Implement policies and practices that promote flexibility, work-life balance, and accessibility.\n\n**Empower Leadership:**\n\n* Train leaders on the importance of DEI and their role in creating an inclusive environment.\n* Hold leaders accountable for promoting DEI within their teams and the organization.\n* Encourage leaders to seek feedback from employees and make adjustments as needed.\n\n**Measure and Evaluate Progress:**\n\n* Track key performance indicators (KPIs) such as representation, employee satisfaction, and turnover rates.\n* Conduct regular evaluations to assess the effectiveness of DEI initiatives and make necessary adjustments.\n* Share progress and successes with employees to foster transparency and accountability.\n\n**Continuous Improvement:**\n\n* Recognize that DEI is an ongoing journey, not a destination.\n* Seek continuous feedback from employees and stakeholders to identify areas for improvement.\n* Stay informed about best practices and emerging trends in DEI to enhance the organization's approach.\n\n**Additional Tips:**\n\n* Involve employees in the development and implementation of DEI initiatives to ensure buy-in and support.\n* Communicate DEI goals and initiatives clearly and regularly to employees.\n* Provide ongoing opportunities for employees to learn about and engage with different cultures and perspectives.\n* Partner with external organizations or consultants to provide expertise and support.") 

    @reactive.effect
    @reactive.event(input.llm_gen, ignore_none=False, ignore_init=True)
    def llm_call():
      #this seems to prevent the load to appear at the begining
      llm_response_with_load_message.freeze()
      with ui.Progress(min=1, max=10) as p:

        p.set(message="Generating Recommendations", detail="This may take a while...")

        p.set(5)
        llm_response_with_load_message.set('**Loading**')
        text = llm_output()
        text = text.replace('•', '  *')
        text = textwrap.indent(text, '> ', predicate=lambda _: True)
        llm_response_with_load_message.set(text)

    @render.text
    def llm_response_with_load():
      return ui.markdown(llm_response_with_load_message.get())

    @render.download(filename='Included_DEI_Table_%s.csv' %date.today())
    def downloadData():
      # If no table changes have been made, data will be just the data output from initial projection
      if len(change_list) == 0 and reprojection.get() == None:
        samp_df = project()

      # If table changes have been made, data will be data output from reprojection
      else:
        samp_df = reprojection.get()

      #rename the columns 
      samp_df.rename(columns = {'total_employees':'Total Employees', 
                           'target_seg_rep': f'Number of {format_group(input.target_group())} Employees', 
                           'new_hires': 'New Hires', 
                           'new_hires_target_seg_rep': f'New Hires who are {format_group(input.target_group())}', 
                           'target_seg_attrition': f'{format_group(input.target_group())} Employee Seperations', 
                           'non_target_seg_attrition': f'Non-{format_group(input.target_group())} Employee Seperations', 
                           'target_seg_rep_p': f'{format_group(input.target_group())} Representation (%)'}, inplace = True)
      
      # Define columns for later rearranging
      cols = ['Total Employees', f'Number of {format_group(input.target_group())} Employees', 
              'New Hires', f'New Hires who are {format_group(input.target_group())}', 
              f'Non-{format_group(input.target_group())} Employee Seperations', f'{format_group(input.target_group())} Employee Seperations',
              ]
      
      # Special case if target scope is leadership (specific renaming + column appendage)
      if input.target_scope() == 'Leadership':
        samp_df.rename(columns = {'promotions':'# Promoted',
                             'promotions_target_seg_rep': '# %s Promoted' %format_group(input.target_group())}, inplace = True)
        cols.append('# Promoted')
        cols.append('# %s Promoted' %format_group(input.target_group()))

      # Special case if target scope is department (specific renaming + column appendage)
      elif input.target_scope() == 'Department':
        samp_df.rename(columns = {'transfers': '# Transfers',
                             'transfers_target_seg_rep': '# %s Transfers' %format_group(input.target_group())}, inplace = True)
        cols.append('# Transfers')
        cols.append('# %s Transfers' %format_group(input.target_group()))

      # Append representation % at the very end and rearrange
      cols.append(f'{format_group(input.target_group())} Representation (%)')
      samp_df = samp_df[cols]

      # Return a csv file upon button press
      yield samp_df.to_csv()
        
    #code to make api call to the BLS v1 API, doesn't require an API key but you only get 25 calls per day. Docs here: https://www.bls.gov/developers/
    def get_bls(bls_series, start_year, end_year):
      #make api call to v1 of the BLS API
      headers = {'Content-type': 'application/json'}
      data = json.dumps({"seriesid": bls_series,"startyear":start_year, "endyear":end_year})
      p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
      
      #extract the response dictionaries from the JSON returned by BLS  
      j = p.json()
      dicts = j['Results']['series']
      
      #Initialize the data frame with the first series from the API response
      bls_df = pd.DataFrame.from_dict(dicts[0]['data'])
      bls_df = bls_df.rename(columns= {'value': dicts[0]['seriesID']})
      
      #merge the remaining series from the API response with the alreay created data frame
      for i in range(1, (len(dicts))):
          df = pd.DataFrame.from_dict(dicts[i]['data'])
          df = df.rename(columns= {'value': dicts[i]['seriesID']})
          df.drop(columns = 'footnotes', inplace = True)
          bls_df = bls_df.merge(df, on = ['year', 'period', 'periodName', 'latest'], how = 'outer')
      
      #drop lingering footnote
      bls_df.drop(columns = 'footnotes', inplace = True)
      
      return bls_df 
    
    @reactive.calc
    @reactive.event(input.benchmark_checkbox, ignore_init=True)
    def benchmark_attrition():
      with ui.Progress(min=1, max=10) as p:

        p.set(message="Getting BLS Data", detail="This may take a while...")
        
        p.set(2)
      
        #match industry to BLS seasonally adjusted attrition variable
        #'Industry' Total US All areas Total separations All size classes Rate Seasonally adjusted
        if input.industry() == 'Information':
          bls_series = 'JTS510000000000000TSR'
        elif input.industry() == 'Mining and Logging':
          bls_series =  'JTS110099000000000TSR'
        elif input.industry() == 'Construction':
          bls_series =  'JTS110099000000000TSR'
        elif input.industry() == 'Manufacturing':
          bls_series =  'JTS300000000000000TSR'
        elif input.industry() == 'Trade, Transportation, and Utilities':
          bls_series =  'JTS400000000000000TSR'
        elif input.industry() == 'Finance':
          bls_series =  'JTS510099000000000TSR'
        elif input.industry() == 'Professional and Business Services':
          bls_series =  'JTS540099000000000TSR'
        elif input.industry() == 'Leisure and Hospitality':
          bls_series =  'JTS700000000000000TSR'
        elif input.industry() == 'Government':
          bls_series =  'JTS900000000000000TSR'
        else:
          #Total nonfarm Total US All areas Total separations All size classes Rate Seasonally adjusted 
          bls_series = 'JTS000000000000000TSR'
        
        df = inputs_to_df()

        bls_data = get_bls([bls_series], int(df.index.min()), date.today().year)
        bls_data.rename(columns = {bls_series:'industry_attrition_rate'}, inplace = True)
        
        #cast to float
        bls_data['industry_attrition_rate'] = bls_data['industry_attrition_rate'].astype(float)

        #bls returns number at the monthly level, average up the the year level
        bls_year_agg = bls_data.groupby(['year']).mean(numeric_only=True)

        #convert to decimal
        bls_year_agg['industry_attrition_rate'] = bls_year_agg['industry_attrition_rate']/100

        #calculate overall company attrition rate
        df['overall_attrition'] = (df['target_seg_attrition'] + df['non_target_seg_attrition'])/df['total_employees']

        #make index an inter for the merge
        bls_year_agg.index = bls_year_agg.index.astype(int)

        benchmark_df = df.merge(bls_year_agg, on = ['year'], how='inner')

      return benchmark_df

    @render.text  
    def attrition_benchmark_message():
      
      benchmark_df = benchmark_attrition()

      avg_attrition = (benchmark_df['overall_attrition'].mean()*100).round(1)
      avg_benchmark_attrition = (benchmark_df['industry_attrition_rate'].mean()*100).round(1)

      if input.industry() == 'Prefer not to say':
        industry_string = 'nationwide'
      else:
        industry_string = f'{input.industry()} industry'

      if avg_attrition > avg_benchmark_attrition:
        attrition_message = f'Your overall attrition is {avg_attrition}%, greater than the {industry_string} average of {avg_benchmark_attrition}%'
      elif avg_attrition == avg_benchmark_attrition:
        attrition_message = f'Your overall attrition is {avg_attrition}%, the same as the {industry_string} average'
      else:
        attrition_message = f'Your overall attrition is {avg_attrition}%, less than the {industry_string} average of {avg_benchmark_attrition}%'
      return attrition_message

app = App(app_ui, server)