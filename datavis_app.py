# Import packages
from dash import Dash, html, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uproot
import numpy

# Incorporate data
file = uproot.open("DQM_V0002_R000356381__SingleMuon__Run2022C-10Dec2022-v2__DQMIO.root")
data = file["DQMData/Run 356381/L1T/Run summary/L1TObjects/L1TEtSum/L1TriggerVsReco/"]


#######################################################################################################MET Efficiency threshold=40
MET_40_efficiency = data["efficiencyMET_threshold_40"]
MET_40_efficiency_hist = MET_40_efficiency.to_hist()

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

#######################################################################################################ET hist
#Import L1MET Histogram
ET_hist = data["L1MET"]
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
fig_ET_hist.update_traces(marker_color='rgb(200,0,150)', opacity=1) #can set color of bar with rgb
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
resolution_MET = data["resolutionMET"]
resolution_MET_hist = resolution_MET

#Find bin centers
bin_edges = resolution_MET_hist.to_numpy()[1]
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
L1METvsCaloMET = data["L1METvsCaloMET"]
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


# Initialize the app
external_stylesheets = [dbc.themes.DARKLY]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout

app.layout = html.Div(className='row', children=[
    html.H1("Demo for the L1T offline DQM shifter space"),
    dcc.Dropdown(['Please select a run', '356381'], 'Please select a run'),
    html.Div(children=[
    	dcc.Graph(figure=fig_ET_hist, mathjax=True, style={'display': 'inline-block'}),
        dcc.Graph(figure=fig_met_efficiency, mathjax=True,  style={'display': 'inline-block'}),
        dcc.Graph(figure=fig_resolution_MET, mathjax=True,  style={'display': 'inline-block'}),
        dcc.Graph(figure=fig_L1vsCaloMET, mathjax=True,  style={'display': 'inline-block'})
    ])
])


# Run the app
if __name__ == '__main__':
        app.run_server(debug=True)
