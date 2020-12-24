import streamlit as st
from utils import cargamos_base_datos
from statsmodels.distributions.empirical_distribution import ECDF
import numpy as np
import plotly.express as px


def main():
    st.title('Análisis de datos exploratorio de ingresos del INE')
    esi = cargamos_base_datos()
    #st.table(df.head())
    graficar_sueldo_neto(esi)
    st.balloons()
    
    
def graficar_sueldo_neto(esi):
    sueldo_col_name = 'sueldo_neto'

    cdf_function = ECDF(esi[sueldo_col_name].dropna().values)
    layout = dict(
    title = "<span style='font-size:26px'>Study of age groups</span><br><span style='color:#999; font-size: 16px; font-weight:200'>students and professionals</span>",
    plot_bgcolor='#f5f5f5',
    margin = dict(t=50, l=0, r=0),
    legend=dict(yanchor='top',xanchor='right', x=0.992, y=0.98, font=dict(size= 12),traceorder='normal'),
    xaxis = dict(domain=[0,1]),
    barmode="overlay",
    bargap = 0.1,
    width = 765
    )
    sueldo_range = np.linspace(0, esi[sueldo_col_name].max(), 10000)
    fig = px.line(x=sueldo_range, y=100*cdf_function(sueldo_range),
                 title=f'curva de densidad acumulada de {sueldo_col_name}', layout=layout)
    fig.update_layout(xaxis=dict(title='Sueldo neto'), yaxis=dict(title='Percentil'))
    st.plotly_chart(fig)
    
    

    
    
main()