### 📂 **Estrutura CORRETA de arquivos**:
1. `CONTRIBUTING.md` (acima)
2. `CODE_OF_CONDUCT.md` (arquivo separado)
3. `docs/DEVELOPMENT.md` (arquivo separado)
4. `.github/workflows/ci.yml` (arquivo separado)

---

### 🚨 **O que estava errado**:
1. Você estava colocando **todos os conteúdos juntos** em um único arquivo
2. Os blocos de código estavam sendo fechados incorretamente
3. As issues e CI/CD não devem estar nos arquivos de documentação

---

### ✅ **Como corrigir**:
1. **Exclua** o arquivo atual `CONTRIBUTING.md`
2. Crie **4 arquivos separados** com os nomes exatos acima
3. Cole o conteúdo correspondente em cada um

---

### 📌 **Passo a passo para fazer certo**:
```bash
# Dentro da pasta do projeto:
rm CONTRIBUTING.md  # Remove o arquivo atual

# Cria os arquivos corretamente:
touch CONTRIBUTING.md CODE_OF_CONDUCT.md docs/DEVELOPMENT.md .github/workflows/ci.yml

# Adiciona conteúdo específico em cada um (copie meus templates)
