# Autotrader — Pacote de Melhorias Estruturais v1
**Gerado em:** 2025-10-19T15:50:11.584597 (BRT)

## O que é
Estrutura base com CI, Render, banco, logs e esqueleto de código, **sem mudar lógica de sinais/painéis**. Serve para padronizar e destravar os “required checks” do GitHub e o deploy na Render.

## Passo a passo (clique por clique)
1) **GitHub → Repositório do projeto** → *Add file* → *Create new file* / *Upload files*.
2) Copie/cole os arquivos **exatamente nos mesmos caminhos** desta pasta. Se um arquivo já existir, **substitua**.
3) *Settings* → *Branches* → *Branch protection for main* → marque **Require status checks to pass** e selecione:
   - `ci (Lint/Type/Test)`
4) *Actions* (GitHub) → verifique o workflow rodando e ficando verde.
5) **Render** → *New +*:
   - **Web Service** → *Build Command*: `pip install -r requirements.txt`
     - *Start Command*: `streamlit run dash/app.py --server.port $PORT --server.address 0.0.0.0`
   - **Cron Job (*/10)** → *Command*: `python ops/worker.py`
   - Adicione variáveis de ambiente conforme `.env.example` (use *Secrets*).
6) Banco: crie a instância **Postgres** (Render), copie a URL em `DATABASE_URL`. Rode o SQL de `ops/migrations/0001_init.sql` (Render Shell ou cliente).

## Ordem de trabalho
1) Subir este **pacote estrutural**.
2) Confirmar CI verde + Render saudável.
3) Iniciar **PAINEL EMAIL** (etapa seguinte).
