# Sistema de Orientação de Carreiras (Python + Tkinter)

Este projeto é um **Sistema Inteligente de Orientação de Carreiras**, desenvolvido em Python, aplicando conceitos de **Programação Orientada a Objetos**, uso de **listas, tuplas, dicionários**, e integração com **interface gráfica (Tkinter)**.

O sistema coleta competências do usuário, compara com requisitos de várias carreiras do futuro e gera **recomendações automáticas** com base no nível de aderência.

---

## 🚀 Funcionalidades

* Cadastro de **perfil profissional**
* Adição de **competências técnicas e comportamentais** com níveis (1 a 10)
* Recomendação automática de carreiras com base no perfil
* **Menu CLI melhorado** e interface moderna
* **Interface gráfica (Tkinter)** funcional
* Salvamento automático do perfil em **JSON**
* Sistema totalmente em **arquivo único** e organizado em classes

---

## 🧩 Estrutura das Classes

* **Competencia** – representa uma competência com nome e nível
* **Perfil** – armazena nome e competências do usuário
* **Carreira** – define requisitos mínimos de competências
* **Recomendador** – avalia aderência e gera recomendações
* **RepositorioCarreiras** – contém carreiras pré-definidas
* **Aplicação (CLI + Tkinter)** – interface para interação do usuário

---

## ▶️ Como executar

### Requisitos:

* Python 3.8 ou superior

### Rodar versão com interface gráfica

```bash
python sistema_carreiras.py
```

A interface Tkinter abrirá automaticamente.

### Rodar versão CLI

No terminal:

```bash
python sistema_carreiras.py --cli
```

---

## 💾 Salvamento Automático

O sistema salva o perfil em:

```
perfil_usuario.json
```

Inclui:

* Nome
* Competências
* Últimas recomendações

---

## 🎯 Objetivo Pedagógico

O projeto atende aos requisitos de:

* Programação orientada a objetos
* Estruturação de dados (listas, dicionários)
* Interface gráfica
* Automação e análise de perfis
* Simulação de ferramenta de orientação profissional


