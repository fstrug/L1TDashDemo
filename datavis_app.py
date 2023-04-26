# Import packages
from dash import Dash, html, dash_table, dcc, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uproot
import numpy

# Incorporate data
test_file = uproot.open("DQM_V0002_R000356381__SingleMuon__Run2022C-10Dec2022-v2__DQMIO.root")
test_data = test_file["DQMData/Run 356381/L1T/Run summary/L1TObjects/L1TEtSum/L1TriggerVsReco/"]
ref_file = uproot.open("DQM_V0001_R000355559__SingleMuon__Run2022B-10Dec2022-v2__DQMIO.root")
ref_data = ref_file["DQMData/Run 355559/L1T/Run summary/L1TObjects/L1TEtSum/L1TriggerVsReco/"]

#Function to create efficiency plot
def efficiency_fig_gen(test_data, ref_data = None, compare = False):
    MET_40_efficiency = test_data["efficiencyMET_threshold_40"]
    MET_40_efficiency_hist = MET_40_efficiency.to_hist()
    
    #if comparison requested, grab ref data
    if compare == True:
        MET_40_efficiency_ref = ref_data["efficiencyMET_threshold_40"]
        MET_40_efficiency_ref_hist = MET_40_efficiency_ref.to_hist()
        
    #Find bin centers and bin widths
    bin_edges = MET_40_efficiency_hist.to_numpy()[1]
    bin_center_array = numpy.array([])
    bin_width_array = numpy.array([])


    for i in range(len(bin_edges)-1):
        bin_width_array = numpy.append(bin_width_array, (bin_edges[i+1] - bin_edges[i])/2)
    for i in range((len(bin_edges)-1)):
        bin_center = (bin_edges[i] + bin_edges[i+1])/2.0
        bin_center_array = numpy.append(bin_center_array, bin_center)

    #Cap off vertical uncertainty
    error_y_plus = numpy.array([])
    MET_40_efficiency_values = MET_40_efficiency.values()
    MET_40_efficiency_errors = MET_40_efficiency.errors()
    for i, element in enumerate(MET_40_efficiency_values):
        if (MET_40_efficiency_errors[i]+element) > 1:
            error_y_plus = numpy.append(error_y_plus, 1-element)
        else:
            error_y_plus = numpy.append(error_y_plus, MET_40_efficiency_errors[i])

    fig_met_efficiency = go.Figure(data=[go.Scatter(x = bin_center_array, y=MET_40_efficiency_values,
                                                    error_y = dict(
                                                                   type='data',
                                                                   symmetric=False,
                                                                   array=error_y_plus,
                                                                   arrayminus=MET_40_efficiency.errors(),
                                                                   visible=True),
                                                    error_x = dict(
                                                                   type='data',
                                                                   array = bin_width_array,
                                                                   visible=True),
                                                    mode="markers"
                                                    )]
                                   )
    fig_met_efficiency.update_layout(
                    title= "$$\\text{Offline}~E_T^{miss}~\\text{efficiency for L1}~E_T^{miss} >40~\\text{GeV}$$",
                    xaxis=dict(
                               title = "$$\\text{Offline}~E_T^{miss}~\\text{[GeV]}$$"
                              ),
                    yaxis=dict(
                               title = "Efficiency"
                               ),
                    template="plotly_dark"
    )
    #add comparison data to figure
    if compare == True:
        #cap vertical uncertainty of ref data
        error_y_plus_ref = numpy.array([])
        MET_40_efficiency_ref_values = MET_40_efficiency_ref.values()
        MET_40_efficiency_ref_errors = MET_40_efficiency_ref.errors()
        for i, element in enumerate(MET_40_efficiency_ref_values):
            if (MET_40_efficiency_errors[i]+element) > 1:
                error_y_plus_ref = numpy.append(error_y_plus_ref, 1-element)
            else:
                error_y_plus_ref = numpy.append(error_y_plus_ref, MET_40_efficiency_errors[i])
        
        fig_met_efficiency.add_trace(go.Scatter(x = bin_center_array, y = MET_40_efficiency_ref.values(),
                                            error_y = dict(
                                                           symmetric = False,
                                                           type="data",
                                                           array = error_y_plus_ref,
                                                           arrayminus = MET_40_efficiency_ref.errors(),
                                                           visible=True),
                                            error_x = dict(
                                                           type="data",
                                                           array = bin_width_array,
                                                           visible=True),
                                            mode="markers",
                                            opacity=0.75))
    
    return(fig_met_efficiency)

#######################################################################################################ET hist
#Import L1MET Histogram
ET_hist = test_data["L1MET"]
#Find bin centers and bid widths
bin_edges = ET_hist.to_numpy()[1] #edges are stored in the 1th position
bin_center_array = []
bin_width = (bin_edges[1] - bin_edges[0])/2 #for fixed width
for i in range((len(bin_edges)-1)):
    bin_center = (bin_edges[i] + bin_edges[i+1])/2.0
    bin_center_array.append(bin_center)
#Plot as a bar graph
fig_ET_hist = go.Figure(data=[go.Bar(x = bin_center_array, y=ET_hist.values(), width = 2*numpy.ones(len(bin_center_array))*bin_width,
                                         error_y = dict(
                                                             type='data', #not sure why type='data' is needed
                                                             array=ET_hist.errors(),
                                                             visible=True),
                                         error_x = dict(
                                                             type='data',
                                                             array = numpy.ones(len(bin_center_array))*bin_width,
                                                             visible=True))]
                               )
#fig_ET_hist.update_traces(marker_color='rgb(200,0,150)', opacity=1) #can set color of bar with rgb
fig_ET_hist.update_layout(
            title="$$L1\, E_T^{miss}$$",
            xaxis=dict(
                title = "$$\\text{L1}~E_T^{miss}~\\text{[GeV]}$$"
            ),
            yaxis=dict(
                title = "Events"
            ),
            template="plotly_dark"
        )
#######################################################################################################MET resolution
resolution_MET = test_data["resolutionMET"]
resolution_MET_hist = resolution_MET

#Set color of each bar
bin_edges = resolution_MET_hist.to_numpy()[1]
colors = ["blue",]*(len(bin_edges)-1)
colors[-1] = "crimson"

#Find bin centers
bin_center_array = []
bin_width = (bin_edges[1] - bin_edges[0])/2
for i in range((len(bin_edges)-1)):
   bin_center = (bin_edges[i] + bin_edges[i+1])/2.0
   bin_center_array.append(bin_center)

#Plot as a bar graph
fig_resolution_MET = go.Figure(data=[go.Bar(x = bin_center_array, y=resolution_MET_hist.values(), width= 2*numpy.ones(len(bin_center_array))*bin_width,
                                         error_y = dict(
                                                             type='data', # value of error bar given in data coordinates
                                                             array=resolution_MET_hist.errors(),
                                                             visible=True),
                                         error_x = dict(
                                                             type='data',
                                                             array = numpy.ones(len(bin_center_array))*bin_width,
                                                             visible=True))]
                               )
fig_resolution_MET.update_traces(marker_color = colors)
fig_resolution_MET.update_layout(
            title=resolution_MET.title,
            xaxis=dict(
                title = "$$\\frac{\\text{L1}~E_T^{miss} - \\text{offline}~E_T^{miss}}{\\text{offline}~E_T^{miss}}$$"
            ),
            yaxis=dict(
                title = "Events"
            ),
            template="plotly_dark"
        )
#######################################################################################################L1METvsCaloMET
L1METvsCaloMET = test_data["L1METvsCaloMET"]
L1METvsCaloMET_hist = L1METvsCaloMET.to_hist()
L1METvsCaloMET_numpy = L1METvsCaloMET_hist.to_numpy()
fig_L1vsCaloMET = go.Figure(data=go.Heatmap(
                  x = L1METvsCaloMET_numpy[1],
                  y = L1METvsCaloMET_numpy[2],
                  z = L1METvsCaloMET_numpy[0],
                  type = 'heatmap',
                  colorscale = 'Viridis'))

fig_L1vsCaloMET.update_layout(
            title="$$\\text{L1}~E_T^{miss}~\\text{vs offline}~E_T^{miss}$$",
            xaxis=dict(
                title = "$$\\text{offline}~E_T^{miss}~\\text{[GeV]}$$"
            ),
            yaxis=dict(
                title = "$$\\text{L1}~E_T^{miss}~\\text{[GeV]}$$"
            ),
            template="plotly_dark"
        )


#######################################################################################################Initialize the app
external_stylesheets = [dbc.themes.DARKLY]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout

app.layout = html.Div(className='row', children=[
    html.H1("Demo for the L1T offline DQM shifter space"),
    dcc.Dropdown(['Please select a run', '356381'], 'Please select a run'),
    html.Div(children=[
    	dcc.Graph(figure=fig_ET_hist, mathjax=True, style={'display': 'inline-block'}),
        html.Div(children=[
            dcc.Checklist([{'label':'Compare', 'value':True}], value=[], id = "controls-and-checklist"),
            html.Div(children = [], id = "run_selection"),
            dcc.Graph(figure=efficiency_fig_gen(test_data), mathjax=True, style={'display': 'inline-block'}, id = "controls-and-graph")],
            style={'display':'inline-block'}),
        dcc.Graph(figure=fig_resolution_MET, mathjax=True,  style={'display': 'inline-block'}),
        dcc.Graph(figure=fig_L1vsCaloMET, mathjax=True,  style={'display': 'inline-block'})
    ])
])

###Add controls to build the interaction

#Updates efficiency plot to show/hide reference run
@app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-checklist', component_property='value')
)
def update_graph(compare_bool):
    if compare_bool == [True]:
        fig = efficiency_fig_gen(test_data, ref_data = ref_data, compare = True)
        return fig
    else:
        fig = efficiency_fig_gen(test_data, compare = False)
        return fig

#Updates dropdown to show possible reference runs
@app.callback(
    Output(component_id = "run_selection", component_property = "children"),
    Input(component_id = "controls-and-checklist", component_property="value")
)
def dropdown_updater(compare_bool):
    if compare_bool == [True]:
        return(dcc.Dropdown(["Please select a run", '356382']))
    else:
        return([])

# Run the app
if __name__ == '__main__':
        app.run_server(debug=True)
