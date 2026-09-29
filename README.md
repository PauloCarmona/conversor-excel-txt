# Conversor Excel → TXT

Aplicativo em Streamlit que converte o Excel exportado do ERP em um arquivo `.txt`, ordenado pela **data do lançamento**.

## Como usar

1. Envie o Excel original do ERP (`.xlsx`, `.xls` ou `.xlsm`).
2. Ajuste o layout do TXT, se necessário.
3. Confira a pré-visualização.
4. Clique em **Baixar .txt**.

## Instalação

Requer Python 3.9 ou superior.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

O app abre no navegador em `http://localhost:8501`.

## Formato esperado do Excel

A primeira linha deve conter os cabeçalhos abaixo. A coluna `Data` é obrigatória; as demais que faltarem saem vazias no TXT.

| Data | Conta bancária | Descrição | Categoria | Cliente | Nr. doc. | Valor |
|------|----------------|-----------|-----------|---------|----------|-------|

## Regras de conversão

- **Ordem:** da data mais antiga para a mais recente. Lançamentos do mesmo dia mantêm a ordem original do Excel.
- **Linhas sem data ou valor** (como "Saldo anterior") são ignoradas por padrão, com opção de manter.
- **Separador dentro dos textos:** se uma descrição contiver o separador escolhido, ele é trocado por espaço, para não quebrar as colunas.
- **Quebras de linha e tabulações** dentro dos campos viram espaço.

## Opções de layout

| Opção | Escolhas |
|-------|----------|
| Colunas | qualquer combinação das 7 colunas |
| Separador | `;` (padrão), `\|`, tabulação, `,` |
| Data | `dd/mm/aaaa` (padrão), `ddmmaaaa`, `aaaa-mm-dd` |
| Valor | vírgula (padrão, `1234,56`) ou ponto (`1234.56`) |
| Codificação | ANSI / Windows-1252 (padrão) ou UTF-8 |
| Quebra de linha | Windows CRLF (padrão) ou Unix LF |
| Cabeçalho | sem (padrão) ou com |

Na codificação ANSI, caracteres que não existem em Windows-1252 são substituídos por `?`.

## Privacidade

O arquivo é processado localmente, na máquina onde o app roda. O `.gitignore` do projeto impede que planilhas e TXTs com dados de clientes sejam enviados ao GitHub por engano.

## Estrutura

```
├── app.py             # aplicativo Streamlit
├── requirements.txt   # dependências
├── .gitignore
└── README.md
```
