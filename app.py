import pandas as pd
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

#Import data

df = pd.read_excel("For Dashboard_Consolidated.xlsx")
df.columns = df.iloc[0]
df = df.drop([0])

companies_list = []

for company in df["Company Name"]:
    if type(company) ==  str:
        companies_list.append(company)
    else:
        print(company)

companies_list = list(set(companies_list))

companies_dict = []

for company in companies_list:
    dict1 = {'label': company, 'value': company}
    companies_dict.append(dict1)

#years_df = df[df["Company "]]
def get_year_dict(company_name):
    year_dict = {}
    df_company = df[df['Company Name'] == company_name]
    for year in df_company['Analysis year']:
        year_dict[str(year)] = year

    return year_dict

total_score_columns = ['Total Score - M', 'Total Score - T', 'Total Score - D', 'Total Score - I','Total Score - F']

sections_list = ['Materiality', 'Targets', 'Delivery', 'Innovation', 'Flexibility']
sections_dict = []
for section in sections_list:
    dict1 = {'label': section, 'value': section}
    sections_dict.append(dict1)
#App layout

app.layout = html.Div([

    html.Div([
        html.H2("Panarchy Partners Web Dashboard - Draft 1", style={'text-align': 'center'}),
        html.Img(src = "/assets/panarchy_logo.png")
    ], className = "banner"),


    dcc.Dropdown(id = "Company",
                 options = companies_dict,
                 multi = False,
                 value = df["Company Name"][1],
                 style = {'width': '40%'}),

    html.Br(),

    dcc.Dropdown(id = "year-dropdown",
                 multi = False,
                 style = {'width': '40%'}),


    html.Div(id = "output_container",
             children = []),

    html.Br(),

    html.Div(children =[
        dcc.Graph(id = 'bar-chart',
                  figure = {},
                  style = {'display': 'inline-block'}),
        dcc.Graph(id = 'spider_plot',
                  figure = {},
                  style = {'display': 'inline-block'})

    ], style = {'width': '96%', 'padding-left': '12%', 'padding-right': '1%'}),

    html.Br(),

    dcc.Dropdown(id = 'section-dropdown',
                 multi = False,
                 options = sections_dict,
                 style = {'width' : '40%'}),

    html.Div(children =[
        dcc.Graph(id = 'section-chart',
                  figure = {},
                  style = {'display': 'inline-block'}),
        dcc.Graph(id = 'tbc',
                  figure = {},
                  style = {'display': 'inline-block'})
    ], style = {'width': '96%', 'padding-left': '12%', 'padding-right': '1%'}),


])

@app.callback(
    Output('year-dropdown', 'options'),
    Input('Company', 'value')
)

def get_year_dict(company_name):
    df_company = df[df['Company Name'] == company_name]

    return [{'label': i, 'value': i} for i in df_company['Analysis year']]


@app.callback(
    [Output(component_id = 'output_container', component_property = 'children'),
     Output(component_id = 'spider_plot', component_property = 'figure')],
    [Input(component_id = "Company", component_property = 'value'),
     Input(component_id = "year-dropdown", component_property = 'value')]
)
def update_spidergraph(Company, Year):
    print(Year)

    container = f"The year selected is: {Year}"

    spidergram = []
    dff = df.copy()
    dfff = dff[dff["Company Name"] == Company]
    row = dfff.loc[dfff['Analysis year'] == Year]

    for total in total_score_columns:
        spidergram.append(row.iloc[0][total])

    spider_df = pd.DataFrame(dict(r = spidergram, theta = total_score_columns))

    fig = px.line_polar(spider_df,
                        r = 'r',
                        theta = 'theta',
                        line_close = True,
                        title = f'Total Score Distribution for {Company} in {Year}')
    fig.update_traces(fill = 'toself')

    return container, fig


@app.callback(
    Output(component_id = 'bar-chart', component_property = 'figure'),
    [Input(component_id = "Company", component_property = 'value')]
)
def update_barchart(Company):
    dff = df.copy()
    df_company = dff[dff['Company Name'] == Company]
    bar_df = df_company[["Analysis year", "Aggregate Score"]]
    fig = px.bar(bar_df, x='Analysis year', y='Aggregate Score', title = f"Aggregate Score Over Time for {Company}")

    return fig

@app.callback(
    [Output(component_id = 'section-chart', component_property = 'figure')],
    [Input(component_id = "Company", component_property = 'value'),
     Input(component_id = "year-dropdown", component_property = 'value'),
     Input(component_id = "section-dropdown", component_property = 'value')]
)

def update_section_chart(company, year, metric_chosen):
    individual_scores_dict = {'Materiality': ' - M', 'Targets': ' - T', 'Delivery': ' - D', 'Innovation': ' - I', 'Flexibility': ' - F'}
    list_of_metrics = ['FIN','ENV','SOC','HUM']
    dff = df.copy()

    metrics_df = dff[dff["Company Name"] == company]
    metrics_df = dff.loc[dff["Analysis year"] == year]
    list_to_use = []
    spidergram = []
    if (metric_chosen == 'Innovation'):
        list_to_use = ['R&D', 'Collaboration', 'New Product Launches', 'Extra-ordinary Innovation']
    elif (metric_chosen == 'Flexibility'):
        list_to_use = ['T&D', 'Diversity', 'Whistle-blowing', 'Exception Policy']
    else:
        for metric in list_of_metrics:
            list_to_use.append(metric + individual_scores_dict[metric_chosen])

    for metric in list_to_use:
        print(metric)
        spidergram.append(metrics_df.iloc[0][metric])

    spider_df = pd.DataFrame(dict(r = spidergram, theta = list_to_use))
    title = f"Breakdown of {metric_chosen} for {company} in {year}"
    fig = px.line_polar(spider_df,
                            r = 'r',
                            theta = 'theta',
                            line_close = True,
                            title = title)
    fig.update_traces(fill = 'toself')


    return [fig]


#CALLBACKS

if __name__ == "__main__":
    app.run_server(debug=True)
