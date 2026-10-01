"""Conversor Excel (ERP) -> TXT, ordenado pela data do lançamento.

Executar:  streamlit run painel.py  (a partir de C:\\Projetos)
"""
import pandas as pd
import streamlit as st

COLUNAS = ["Data", "Conta bancária", "Descrição", "Categoria", "Cliente", "Nr. doc.", "Valor"]
SEPARADORES = {"Ponto e vírgula ( ; )": ";", "Barra vertical ( | )": "|", "Tabulação": "\t", "Vírgula ( , )": ","}
FORMATOS_DATA = {"dd/mm/aaaa": "%d/%m/%Y", "ddmmaaaa": "%d%m%Y", "aaaa-mm-dd": "%Y-%m-%d"}
QUEBRAS = {"Windows (CRLF)": "\r\n", "Unix (LF)": "\n"}


def ler_excel(arquivo) -> pd.DataFrame:
    df = pd.read_excel(arquivo, dtype=object)
    df.columns = [str(c).strip() for c in df.columns]
    if "Data" not in df.columns:
        raise ValueError("Coluna 'Data' não encontrada na primeira linha do arquivo.")
    for c in COLUNAS:
        if c not in df.columns:
            df[c] = ""
    df = df.dropna(how="all").reset_index(drop=True)
    df["_ordem"] = range(len(df))  # preserva a ordem original dentro do mesmo dia
    df["_data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    return df


def gerar_linhas(df, colunas, sep, fmt_data, valor_virgula, cabecalho, ignorar_sem_dado):
    d = df.copy()
    d["_valor"] = pd.to_numeric(d["Valor"], errors="coerce")
    if ignorar_sem_dado:
        d = d[d["_data"].notna() & d["_valor"].notna()]
    d = d.sort_values(["_data", "_ordem"], kind="stable")

    def limpa(x):
        if pd.isna(x):
            return ""
        return str(x).replace("\r", " ").replace("\n", " ").replace("\t", " ").replace(sep, " ").strip()

    linhas = []
    for _, r in d.iterrows():
        campos = []
        for c in colunas:
            if c == "Data":
                campos.append(r["_data"].strftime(fmt_data) if pd.notna(r["_data"]) else "")
            elif c == "Valor":
                if pd.isna(r["_valor"]):
                    campos.append("")
                else:
                    s = f"{r['_valor']:.2f}"
                    campos.append(s.replace(".", ",") if valor_virgula else s)
            else:
                campos.append(limpa(r[c]))
        linhas.append(sep.join(campos))
    if cabecalho:
        linhas.insert(0, sep.join(colunas))
    return linhas


# ------------------------------- Interface -------------------------------
st.page_link("painel.py", label="Voltar ao painel", icon="🏠")
st.title("🔄 Conversor Excel → TXT")
st.caption("Envie o Excel original do ERP. O TXT sai ordenado pela data do lançamento.")

arquivo = st.file_uploader("1. Arquivo Excel", type=["xlsx", "xls", "xlsm"])

with st.expander("2. Layout do TXT", expanded=True):
    colunas = st.multiselect("Colunas (na ordem em que aparecem)", COLUNAS, default=COLUNAS)
    c1, c2, c3 = st.columns(3)
    sep = SEPARADORES[c1.selectbox("Separador", list(SEPARADORES))]
    fmt_data = FORMATOS_DATA[c2.selectbox("Formato da data", list(FORMATOS_DATA))]
    valor_virgula = c3.selectbox("Valor", ["1234,56 (vírgula)", "1234.56 (ponto)"]).startswith("1234,")
    c4, c5, c6 = st.columns(3)
    codificacao = c4.selectbox("Codificação", ["ANSI (Windows-1252)", "UTF-8"])
    quebra = QUEBRAS[c5.selectbox("Quebra de linha", list(QUEBRAS))]
    cabecalho = c6.selectbox("Cabeçalho", ["Sem cabeçalho", "Com cabeçalho"]) == "Com cabeçalho"
    ignorar = st.checkbox("Ignorar linhas sem data ou valor (ex.: saldo anterior)", value=True)

if arquivo is None:
    st.info("Carregue um arquivo para ver a pré-visualização.")
    st.stop()

if not colunas:
    st.warning("Selecione ao menos uma coluna.")
    st.stop()

try:
    df = ler_excel(arquivo)
except Exception as e:
    st.error(f"Erro ao ler o arquivo: {e}")
    st.stop()

linhas = gerar_linhas(df, colunas, sep, fmt_data, valor_virgula, cabecalho, ignorar)
texto = quebra.join(linhas) + quebra
dados = texto.encode("utf-8") if codificacao == "UTF-8" else texto.encode("cp1252", errors="replace")

st.subheader("3. Pré-visualização e download")
st.code("\n".join(linhas[:15]) + ("\n…" if len(linhas) > 15 else ""), language=None)
st.caption(f"{len(df)} linhas lidas · {len(linhas)} linhas no TXT · ordenadas por data "
           "(no mesmo dia, mantém a ordem original do Excel).")

nome = arquivo.name.rsplit(".", 1)[0] + ".txt"
st.download_button("⬇️ Baixar .txt", data=dados, file_name=nome, mime="text/plain", type="primary")
