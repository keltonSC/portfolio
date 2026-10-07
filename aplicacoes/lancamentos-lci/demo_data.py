"""Fixture criada para apresentação pública; não lê a planilha histórica."""
import pandas as pd


def dados_demo():
    return pd.DataFrame({
        "Nome do Empreendimento": ["Projeto fictício Aurora", "Projeto fictício Jardim", "Projeto fictício Horizonte"],
        "Construtora": ["Construtora fictícia A", "Construtora fictícia B", "Construtora fictícia A"],
        "Status": ["Em construção", "Planejamento", "Concluído"],
        "Previsão de Entrega": ["2027-05-01", "2028-09-01", None],
        "Segmento": ["Residencial", "Residencial", "Comercial"],
        "VGV Médio": [1500000, 2000000, 900000],
        "Média  m²": ["60, 90", "80, 120", "40, 70"],
        "Bairro/Cidade": ["Bairro fictício Norte", "Bairro fictício Sul", "Bairro fictício Norte"],
        "Endereço": ["Endereço fictício A", "Endereço fictício B", "Endereço fictício C"],
        "Tipologia": ["2 e 3 quartos", "3 quartos", "Salas"],
        "Atualização google earth ": [None, None, None],
    })
