# 🇧🇷 OSINT Brazuca Ultimate ⚡

> **Central Profissional e Modular de Investigação por Fontes Abertas Brasileiras.**  
> Inspirado e integrado ao catálogo canônico do projeto **OSINT Brazuca**.

---

## 🛡️ Visão Geral & Filosofia

O **OSINT Brazuca Ultimate** é uma plataforma completa e funcional voltada a investigações legítimas, auditoria de dados públicos, inteligência sobre ameaças e análise de infraestrutura digital.

Diferente de protótipos visuais ou páginas estáticas, o sistema possui **frontend moderno, backend reativo em FastAPI, adaptadores automatizados com tratamento de falhas, validação rigorosa de dados e respeito intransigente à privacidade e à LGPD (Lei 13.709/2018)**.

---

## 🎨 Identidade Visual & Design

- **Estética:** Hacker/Gótica, sombria, elegante e de alto contraste operacional.
- **Paleta:** Fundo preto profundo (`#07080b`), vinho escuro (`#26070a`) e destaques em vermelho vivo (`#e50914` / `#ff2a2a`), com acentos de status neon (verde esmeralda, âmbar e ciano).
- **Interface:** 100% em português brasileiro, responsiva para desktop e dispositivos móveis, com fontes monospace para dados forenses, crachás de confiança e grafos visuais.

---

## 📊 Estado Real das Integrações

Em respeito estrito à diretriz de **honestidade operacional**, o sistema nunca simula dados fictícios nem mascara erros:

| Categoria | Conector / Fonte | Status | Detalhes da Integração |
| :--- | :--- | :---: | :--- |
| **CNPJ** | BrasilAPI (Receita Federal) | ✅ Concluído | Razão social, nome fantasia, situação cadastral, CNAEs e **Quadro de Sócios (QSA)**. |
| **CNPJ** | ReceitaWS | ✅ Concluído | Consulta cadastral complementar e porte empresarial. |
| **CPF** | Validador Módulo 11 + Portais | ✅ Concluído | Validação algorítmica, região fiscal emissora, links oficiais (Receita, CNDT, TSE) e **mascaramento estrito**. |
| **Domínio** | RDAP Registro.br & ICANN | ✅ Concluído | Titularidade técnica, datas de criação/expiração e servidores de nomes autoritativos. |
| **Domínio** | Resolução DNS Recursiva | ✅ Concluído | Registros A, AAAA, MX, NS, TXT, CNAME, SOA e checagem de políticas SPF e DMARC. |
| **Domínio** | Certificate Transparency | ✅ Concluído | Descoberta passiva de subdomínios via logs públicos do crt.sh. |
| **Domínio** | Sondagem HTTP Passiva | ✅ Concluído | Título de página, cabeçalhos de segurança (`server`, `HSTS`, `X-Frame-Options`) e status. |
| **IP e Rede** | RDAP IP / ASN | ✅ Concluído | Bloco de rede detentor, Autonomous System (ASN), país e contatos oficiais do RIR. |
| **IP e Rede** | Geolocalização de Rede | ✅ Concluído | Localização aproximada do Ponto de Presença (PoP) com aviso explícito de que não indica moradia física. |
| **Telefone** | Normalização E.164 + Anatel | ✅ Concluído | Identificação de DDD, plano de numeração móvel (9º dígito), ABR Telecom e link de rede WhatsApp. |
| **E-mail** | Auditoria DNS & Provedor | ✅ Concluído | Sintaxe RFC, verificação de servidores MX, SPF, DMARC e detecção de domínios descartáveis. |
| **Username** | APIs Públicas Oficiais | ✅ Concluído | Busca em APIs oficiais do GitHub e GitLab + geração de links parametrizados para redes sociais. |
| **Documentos** | Análise Forense Local | ✅ Concluído | Cálculo 100% local de SHA-256, SHA-1, MD5, tipo MIME e extração de tags EXIF sem vazamento de dados. |
| **Dados Públicos** | Dados.gov.br (CKAN API) | ✅ Concluído | Pesquisa em tempo real de conjuntos de dados governamentais abertos do Governo Federal. |
| **Dados Públicos** | Portal da Transparência / DOU | ✅ Concluído | Links parametrizados para CEIS, CNEP, CEPIM, Compras.gov.br (PNCP) e Querido Diário. |
| **Catálogo** | Base Canônica OSINT Brazuca | ✅ Concluído | Carregamento de **515+ fontes** de `data/sources.json` com filtros por categoria, input, esfera e automação. |

### 🚀 Módulos Futuros Preparados na Arquitetura
A arquitetura do `query_engine` já possui contratos prontos para expansão gradual:
1. *Marcas e Patentes (INPI)*
2. *Licitações e Contratos Aprofundados*
3. *Processos e Certidões Públicas (DataJud/PJe)*
4. *Vulnerabilidades e CVEs (NVD/MITRE)*
5. *Blockchain e Criptoativos*
6. *Análise Técnica de Imagens (Ruído e ELA)*
7. *Monitoramento Contínuo de Ativos*

---

## 🔒 Privacidade e Segurança (LGPD Compliant)

1. **Escuta Restrita:** O backend escuta exclusivamente em `127.0.0.1` por padrão.
2. **Sem Histórico por Padrão:** Consultas não são gravadas em disco, a menos que o operador ative voluntariamente o histórico nas configurações.
3. **Sem Logs Sensíveis:** CPFs, telefones e e-mails não são impressos em logs de depuração.
4. **Mascaramento de Dados:** Dados sensíveis são apresentados no formato `***.456.789-**` e `u***r@d****n.com`.
5. **Prevenção de SSRF:** Bloqueio ativo de IPs privados (RFC 1918), serviços de metadados cloud (`169.254.169.254`) e loopback.
6. **TLS Mandatório:** Validação estrita de certificados digitais em todas as chamadas externas.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.10+ com FastAPI, Pydantic v2, HTTPX, dnspython e Pytest.
- **Frontend:** React 19, TypeScript, Vite, CSS moderno responsivo e Lucide Icons.
- **Relatórios:** Exportador multiplataforma nos formatos **JSON**, **CSV** e **HTML** (Dossiê pericial estilizado).
- **Dados:** `data/sources.json`, `data/index.json` e `data/taxonomy.json` originais do projeto OSINT Brazuca.

---

## 💻 Instalação e Execução no Windows

### Pré-requisitos
- **Python 3.10 ou superior** instalado e acessível pelo prompt de comando.
- **Node.js 18 ou superior** e `npm`.

### 1. Clonar ou Acessar a Pasta do Projeto
Abra o terminal (PowerShell ou Prompt de Comando) na pasta do projeto:
```powershell
cd c:\Users\51478718889\Desktop\osint-brazuca-main
```

### 2. Instalar as Dependências do Backend
```powershell
python -m pip install -r requirements.txt
```

### 3. Instalar as Dependências do Frontend
```powershell
cd frontend
npm install
cd ..
```

---

## 🚀 Como Iniciar o Aplicativo

### Método Rápido (Dois Cliques no Windows)
Basta dar um duplo clique no arquivo:
👉 `iniciar_tudo.bat`

Ele abrirá automaticamente o backend FastAPI na porta `8000` e o frontend na porta `5173`.

### Método Manual via Terminal

**Janela 1 (Backend FastAPI):**
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Janela 2 (Frontend Vite):**
```powershell
cd frontend
npm run dev
```

Abra seu navegador em:
- **Interface de Desenvolvimento:** [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **Interface Produção Integrada:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Swagger da API:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Executando os Testes Automatizados

O sistema conta com 36 testes automatizados cobrindo validadores, isolamento de falhas, catálogo, mascaramento e prevenção contra SSRF.

Para rodar todos os testes:
```powershell
python -m pytest backend/tests -v
```
Ou dê dois cliques em `executar_testes.bat`.

---

## 📖 Como Adicionar Novos Adaptadores

Para plugar uma nova fonte:

1. Crie o arquivo em `backend/app/adapters/{categoria}/{nome_fonte}.py`:
   ```python
   from backend.app.adapters.base import BaseAdapter
   from backend.app.engine.models import SourceExecutionResult, ResultStatus, ConfidenceLevel

   class MinhaNovaFonteAdapter(BaseAdapter):
       adapter_id = "minha_nova_fonte"
       name = "Portal da Minha Fonte"
       category = "cnpj"
       description = "Descrição dos dados fornecidos."
       official_url = "https://minhafonte.gov.br"
       supported_inputs = ["cnpj"]

       async def run(self, target: str, context: dict = None) -> SourceExecutionResult:
           async with self.get_client() as client:
               resp = await client.get(f"https://api.minhafonte.gov.br/{target}")
               return SourceExecutionResult(
                   source_id=self.adapter_id,
                   source_name=self.name,
                   category=self.category,
                   status=ResultStatus.CONFIRMED,
                   data=resp.json(),
                   verification_url=self.official_url,
                   confidence=ConfidenceLevel.HIGH
               )
   ```

2. Adicione a classe à lista em `_register_adapters()` no arquivo `backend/app/engine/orchestrator.py`.
3. A nova fonte será automaticamente executada nas pesquisas e listada nos filtros do painel.

---

## 📜 Licença e Responsabilidade

O **OSINT Brazuca Ultimate** destina-se a fins de segurança cibernética defensiva, jornalismo investigativo, conformidade regulatória e pesquisa acadêmica. O usuário é integralmente responsável pelo uso ético e legal das informações obtidas.

