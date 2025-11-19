"""
Sistema de Orienta\u00e7\u00e3o de Carreiras (OOP, Python)
Arquivo: sistema_orientacao_carreiras.py
Descri\u00e7\u00e3o: Implementa classes para Competencia, Perfil, Carreira e Recomendador
Interface: CLI simples para cadastrar perfis, adicionar compet\u00eancias, salvar/carregar e gerar recomendacoes.
Requisitos atendidos:
- Estruturado em classes e m\u00f3dulos (arquivo unico, mas organizado por classes)
- Usa listas, tuplas e dicion\u00e1rios para modelar dados
- Serializa perfis em JSON
- L\u00f3gica de recomenda\u00e7\u00e3o baseada em pesos e gap analysis

Como usar:
> python sistema_orientacao_carreiras.py

"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from datetime import datetime

PROFILES_DIR = "profiles"
if not os.path.exists(PROFILES_DIR):
    os.makedirs(PROFILES_DIR)


@dataclass
class Competencia:
    nome: str
    categoria: str  # 'técnica' ou 'comportamental'
    nivel: float     # 0.0 - 10.0

    def as_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Competencia":
        return Competencia(nome=d["nome"], categoria=d["categoria"], nivel=d["nivel"])


class Perfil:
    """Representa um perfil profissional com um conjunto de competências."""

    def __init__(self, nome: str, idade: Optional[int] = None, descricao: str = ""):
        self.nome = nome
        self.idade = idade
        self.descricao = descricao
        self.competencias: List[Competencia] = []
        self.criado_em = datetime.now().isoformat()

    def adicionar_competencia(self, comp: Competencia) -> None:
        # substitui se existir mesma competencia (mesmo nome)
        for i, c in enumerate(self.competencias):
            if c.nome.lower() == comp.nome.lower():
                self.competencias[i] = comp
                return
        self.competencias.append(comp)

    def remover_competencia(self, nome: str) -> bool:
        nome = nome.lower()
        for i, c in enumerate(self.competencias):
            if c.nome.lower() == nome:
                del self.competencias[i]
                return True
        return False

    def obter_nivel(self, nome: str) -> Optional[float]:
        for c in self.competencias:
            if c.nome.lower() == nome.lower():
                return c.nivel
        return None

    def medias_por_categoria(self) -> Dict[str, float]:
        soma: Dict[str, float] = {}
        cont: Dict[str, int] = {}
        for c in self.competencias:
            soma[c.categoria] = soma.get(c.categoria, 0.0) + c.nivel
            cont[c.categoria] = cont.get(c.categoria, 0) + 1
        return {cat: (soma[cat] / cont[cat]) for cat in soma}

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "idade": self.idade,
            "descricao": self.descricao,
            "competencias": [c.as_dict() for c in self.competencias],
            "criado_em": self.criado_em,
        }

    @staticmethod
    def from_dict(d: dict) -> "Perfil":
        p = Perfil(nome=d["nome"], idade=d.get("idade"), descricao=d.get("descricao", ""))
        p.competencias = [Competencia.from_dict(cd) for cd in d.get("competencias", [])]
        p.criado_em = d.get("criado_em", datetime.now().isoformat())
        return p

    def salvar(self, filename: Optional[str] = None) -> str:
        if filename is None:
            safe_name = "_".join(self.nome.split()).lower()
            filename = os.path.join(PROFILES_DIR, f"{safe_name}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return filename

    @staticmethod
    def carregar(filename: str) -> "Perfil":
        with open(filename, "r", encoding="utf-8") as f:
            d = json.load(f)
        return Perfil.from_dict(d)


class Carreira:
    """Modelo simples de carreira com requisitos (competencia -> (peso, nivel_desejado))."""

    def __init__(self, nome: str, requisitos: Dict[str, Tuple[float, float]], descricao: str = ""):
        self.nome = nome
        # requisitos: { 'Python': (peso, nivel_desejado)}
        self.requisitos = {k: (float(v[0]), float(v[1])) for k, v in requisitos.items()}
        self.descricao = descricao

    def to_dict(self) -> dict:
        return {"nome": self.nome, "requisitos": self.requisitos, "descricao": self.descricao}


class Recomendador:
    """L\u00f3gica de recomendacao: pontua carreiras segundo o alinhamento do perfil com os requisitos."""

    def __init__(self, carreiras: Optional[List[Carreira]] = None):
        self.carreiras = carreiras if carreiras is not None else []

    def adicionar_carreira(self, carreira: Carreira) -> None:
        self.carreiras.append(carreira)

    def recomendar(self, perfil: Perfil, top_n: int = 5) -> List[Dict]:
        resultados = []
        for carreira in self.carreiras:
            score_total = 0.0
            peso_total = 0.0
            gaps: Dict[str, float] = {}

            for req_nome, (peso, nivel_desejado) in carreira.requisitos.items():
                nivel_usuario = perfil.obter_nivel(req_nome)
                peso_total += peso
                if nivel_usuario is None:
                    # falta totalmente -> gap = nivel_desejado
                    gap = nivel_desejado
                    contrib = 0.0
                else:
                    gap = max(0.0, nivel_desejado - nivel_usuario)
                    # se usuario excede nivel desejado, contibuicao maxima
                    contrib = max(0.0, (nivel_usuario / nivel_desejado)) if nivel_desejado > 0 else 1.0
                    if contrib > 1.0:
                        contrib = 1.0
                # soma ponderada
                score_total += contrib * peso
                if gap > 0:
                    gaps[req_nome] = gap

            # normaliza score para 0-100
            normalized = (score_total / peso_total * 100.0) if peso_total > 0 else 0.0
            resultados.append({
                "carreira": carreira,
                "score": round(normalized, 2),
                "gaps": gaps,
            })

        # ordena por score desc
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:top_n]

    def gerar_trilha(self, perfil: Perfil, carreira: Carreira, top_k: int = 5) -> List[str]:
        """Gera recomenda\u00e7\u00f5es de aprendizagem a partir dos maiores gaps."""
        # calcula gaps
        gaps: List[Tuple[str, float, float]] = []  # nome, gap, nivel_desejado
        for req_nome, (peso, nivel_desejado) in carreira.requisitos.items():
            nivel_usuario = perfil.obter_nivel(req_nome) or 0.0
            gap = max(0.0, nivel_desejado - nivel_usuario)
            if gap > 0:
                gaps.append((req_nome, gap, nivel_desejado))
        # ordena por gap desc
        gaps.sort(key=lambda x: x[1], reverse=True)

        # transforma em recomendações práticas (strings)
        recomenda = []
        for nome, gap, nivel_alvo in gaps[:top_k]:
            recomenda.append(f"Aprender/Praticar '{nome}' até nivel {nivel_alvo:.1f} (gap {gap:.1f})")
        if not recomenda:
            recomenda.append("Perfil alinhado: consolidar conhecimentos e buscar especializacoes.")
        return recomenda


# exemplo de carreiras pre-carregadas
def carregar_carreiras_exemplo() -> List[Carreira]:
    carreiras = [
        Carreira(
            "Cientista de Dados",
            requisitos={
                "Python": (3.0, 7.0),
                "Estatística": (2.0, 6.0),
                "Aprendizado de Máquina": (3.0, 6.0),
                "Comunicação": (1.0, 6.0),
            },
            descricao="Analisa dados e cria modelos preditivos.",
        ),
        Carreira(
            "Engenheiro de Software",
            requisitos={
                "Algoritmos": (3.0, 7.0),
                "Estruturas de Dados": (3.0, 7.0),
                "Python": (2.0, 6.0),
                "Trabalho em Equipe": (1.0, 6.0),
            },
            descricao="Desenvolve sistemas e aplica engenharia de software.",
        ),
        Carreira(
            "Especialista em Automacao e IoT",
            requisitos={
                "Eletronica Basica": (2.0, 6.0),
                "Python": (2.0, 6.0),
                "Sistemas Embarcados": (3.0, 7.0),
                "Adaptabilidade": (1.0, 6.0),
            },
            descricao="Integra dispositivos, sensores e automacoes.",
        ),
        Carreira(
            "Designer de Experiencia (UX)",
            requisitos={
                "Criatividade": (3.0, 7.0),
                "Prototipacao": (2.0, 6.0),
                "Pesquisa com Usuarios": (2.0, 6.0),
                "Empatia": (2.0, 7.0),
            },
            descricao="Projeta experiencias digitais centradas no usuario.",
        ),
    ]
    return carreiras


# ===== CLI =====

def listar_profiles() -> List[str]:
    arquivos = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
    return arquivos


def mostrar_profile(perfil: Perfil) -> None:
    print("\n--- Perfil ---")
    print(f"Nome: {perfil.nome}")
    print(f"Idade: {perfil.idade}")
    print(f"Descricao: {perfil.descricao}")
    print(f"Criado em: {perfil.criado_em}")
    print("Competencias:")
    for c in perfil.competencias:
        print(f" - {c.nome} ({c.categoria}) : {c.nivel:.1f}")
    medias = perfil.medias_por_categoria()
    if medias:
        print("Medias por categoria:")
        for k, v in medias.items():
            print(f"  * {k}: {v:.2f}")
    print("-------------\n")


def entrada_float(prompt: str, minv: float = 0.0, maxv: float = 10.0) -> float:
    while True:
        try:
            v = float(input(prompt))
            if v < minv or v > maxv:
                print(f"Valor deve estar entre {minv} e {maxv}")
                continue
            return v
        except ValueError:
            print("Entrada invalida. Tente novamente.")


def menu_principal():
    perfil_atual: Optional[Perfil] = None
    recomendador = Recomendador(carreiras=carregar_carreiras_exemplo())

    while True:
        print("=== Sistema de Orientacao de Carreiras ===")
        print("1) Criar novo perfil")
        print("2) Carregar perfil")
        print("3) Salvar perfil atual")
        print("4) Adicionar/Atualizar competencia no perfil")
        print("5) Remover competencia")
        print("6) Mostrar perfil atual")
        print("7) Gerar recomendacoes")
        print("8) Listar perfis salvos")
        print("9) Sair")
        opt = input("Escolha: ").strip()

        if opt == "1":
            nome = input("Nome: ").strip()
            idade = input("Idade (opcional): ").strip()
            idade = int(idade) if idade.isdigit() else None
            desc = input("Descricao (opcional): ").strip()
            perfil_atual = Perfil(nome=nome, idade=idade, descricao=desc)
            print("Perfil criado.")

        elif opt == "2":
            arquivos = listar_profiles()
            if not arquivos:
                print("Nenhum perfil salvo.")
                continue
            print("Perfis:")
            for i, a in enumerate(arquivos, 1):
                print(f"{i}) {a}")
            escolha = input("Escolha numero: ").strip()
            if escolha.isdigit() and 1 <= int(escolha) <= len(arquivos):
                perfil_atual = Perfil.carregar(os.path.join(PROFILES_DIR, arquivos[int(escolha) - 1]))
                print(f"Perfil '{perfil_atual.nome}' carregado.")
            else:
                print("Escolha invalida.")

        elif opt == "3":
            if perfil_atual is None:
                print("Nenhum perfil em memoria.")
                continue
            fname = perfil_atual.salvar()
            print(f"Perfil salvo em: {fname}")

        elif opt == "4":
            if perfil_atual is None:
                print("Crie ou carregue um perfil primeiro.")
                continue
            nome_comp = input("Nome da competencia: ").strip()
            categoria = input("Categoria ('técnica' ou 'comportamental'): ").strip() or "técnica"
            nivel = entrada_float("Nivel (0.0-10.0): ")
            perfil_atual.adicionar_competencia(Competencia(nome=nome_comp, categoria=categoria, nivel=nivel))
            print("Competencia adicionada/atualizada.")

        elif opt == "5":
            if perfil_atual is None:
                print("Crie ou carregue um perfil primeiro.")
                continue
            nome_comp = input("Nome da competencia a remover: ").strip()
            if perfil_atual.remover_competencia(nome_comp):
                print("Removido.")
            else:
                print("Competencia nao encontrada.")

        elif opt == "6":
            if perfil_atual is None:
                print("Nenhum perfil carregado.")
                continue
            mostrar_profile(perfil_atual)

        elif opt == "7":
            if perfil_atual is None:
                print("Crie ou carregue um perfil primeiro.")
                continue
            resultados = recomendador.recomendar(perfil_atual, top_n=10)
            print("Recomendacoes (pontuacao 0-100):")
            for i, r in enumerate(resultados, 1):
                carre = r["carreira"]
                print(f"{i}) {carre.nome} - score: {r['score']:.1f} - {carre.descricao}")
                if r["gaps"]:
                    gaps_str = ", ".join([f"{k} (gap {v:.1f})" for k, v in r["gaps"].items()])
                    print(f"   Gaps: {gaps_str}")
                # exibir trilha sugerida para a top 1 opcao
            if resultados:
                melhor = resultados[0]
                trilha = recomendador.gerar_trilha(perfil_atual, melhor["carreira"], top_k=5)
                print("\nTrilha sugerida para a melhor opcao:")
                for t in trilha:
                    print(f" - {t}")

        elif opt == "8":
            arquivos = listar_profiles()
            if not arquivos:
                print("Nenhum perfil salvo.")
            else:
                print("Perfis salvos:")
                for a in arquivos:
                    print(f" - {a}")

        elif opt == "9":
            print("Saindo...")
            break

        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    menu_principal()
