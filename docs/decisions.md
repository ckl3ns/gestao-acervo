# ADRs Iniciais (resumo)

1. **Separação por camadas desde o bootstrap** para evitar acoplamento Streamlit-domínio.
2. **Persistência simples e auditável** com schema SQL explícito versionável.
3. **Busca com FTS5** desde início para validar requisito de busca global.
4. **Matching conservador**: serviço de score básico título+autor com RapidFuzz.
5. **Escopo controlado**: sem MCP operacional, IA/LLM, autenticação e integrações online.
