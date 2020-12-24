import pandas as pd
import seaborn as sn
import scipy
import numpy as np
import plotly.express as px
from statsmodels.distributions.empirical_distribution import ECDF
import streamlit as st

@st.cache
def cargamos_base_datos():

    esi = pd.read_csv("/Users/pipe/Documents/repos/esi2019-modelos/datos/esi-2019.csv",
                      sep=';', encoding='latin')
    region_comuna = pd.read_csv("/Users/pipe/Documents/repos/esi2019-modelos/datos/region_comuna.csv",
                                sep=';')

    esi = pd.merge(esi, region_comuna, left_on='r_p_c', right_on='Código Comuna 2018', how='left')
    esi.drop(['region'], axis=1, inplace=True)

    columns_map = {
    'id_identificacion': 'id_hogar',
    'idrph': 'id_persona',
    'tipo': 'tipo_estrato',
    't_muestra': 'tipo_muestra',
    'd1_monto': 'sueldo_neto',
    'Nombre Región': 'region',
    'Nombre Provincia': 'provincia',
    'Nombre Comuna': 'comuna',
    'b1': 'grupo_ocupacion',
    'cise': 'categoria_empleo',
    'b8': 'tiene_contrato',
    'b12': 'est_subcontratado',
    'b13_rev4cl_cae': 'rubro',
    'c1': 'tipo_jornada',
    }

    esi = esi.rename(columns=columns_map)

    values_map = {
    'parentesco': {
        1: 'Jefe de hogar',
        2: 'Cónyuge',
        3: 'Conviviente',
        4: 'Hijo(a) / Hijastro(a)',
        5: 'Yerno / Nuera',
        6: 'Nieto(a)',
        7: 'Hermano(a) / Cuñado(a)',
        8: 'Padres / Suegros',
        9: 'Otro pariente',
        10: 'No pariente',
        11: 'Servicio doméstico',
        12: 'Fuera del hogar',
        13: 'Fallecido',
    }
    ,
    
    'nivel': {
        0: 'Nunca estudió',
        1: 'Sala cuna',
        2: 'Kínder',
        3: 'Básica o primaria 4 Media común',
        5: 'Media técnico profesional 6 Humanidades',
        7: 'Centro formación técnica 8 Instituto profesional',
        9: 'Universitario 10 Postítulo',
        11: 'Magíster',
        12: 'Doctorado',
        14: 'Normalista',
        99: 'Nivel ignorado',
        999: 'Nivel ignorado',
    }
    ,
    
    'tipo_estrato': {
        1: 'Ciudad',
        2: 'Resto area urbana',
        3: 'Rural'
    }
    ,
    
    'sexo': {
        1: 'Hombre',
        2: 'Mujer'
    }
    ,
    
    'termino_nivel': {
        1: "Si",
        2: "No"
    }
    ,
    
    'cine': {
        1: "Nunca estudió",
        2: "Educación preescolar",
        3: 'Educación primaria (nivel 1)',
        4: 'Educación primaria (nivel 2)',
        5: 'Educación secundaria',
        6: 'Educación técnica',
        7: 'Educación universitaria',
        8: 'Postítulo y maestría',
        9: 'Doctorado',
        999: None
    }
    ,
    
    'est_conyugal': {
        0: None,
        1: "Casade",
        2: "Coviviente",
        3: "Soltere",
        4: "Viude",
        5: "Separade",
        6: "Divorciade"
    }
    ,
    
    #'nacionalidad': {}
    
   
    }


    for variable, mapping in values_map.items():
        esi[variable] = esi[variable].map(mapping)
    
    def procesar_monto(x):
        try:
            if ',' in x:
                x = x.replace(',', '.')
            return float(x)
        except:
            return x

    esi['sueldo_neto'] = esi['sueldo_neto'].apply(procesar_monto)
    return esi