import csv
import json
import time
from datetime import datetime

CAMPOS_CSV = ["data", "origem", "pergunta", "orientacao_id", "encontrou",
              "ajudou", "tentativas", "tempo_segundos", "facilidade"]


def contem_dado_pessoal(texto):
    digitos = 0
    for caractere in texto:
        if caractere.isdigit():
            digitos += 1
    return digitos >= 8 or "@" in texto


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.historico = self.carregar_historico()
        self.inicio_sessao = len(self.historico)

    def carregar_historico(self):
        try:
            with open(self.caminho_historico, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Histórico ilegível. Começando um novo.")
            return []

        if not isinstance(dados, list):
            print("Histórico ilegível. Começando um novo.")
            return []
        return dados

    def salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=4)
        except OSError:
            print("Não foi possível salvar o histórico.")

    def ler_sim_nao(self, texto):
        while True:
            resposta = input(texto).strip().lower()
            if resposta in ("s", "n"):
                return resposta == "s"
            print("Digite apenas s ou n.")

    def registrar(self, origem, pergunta, orientacao_id, encontrou, ajudou, tentativas, inicio):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "orientacao_id": orientacao_id,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
        }
        self.historico.append(atendimento)
        self.salvar_historico()

    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        encontrou = False
        orientacao_id = None
        ultima_pergunta = ""

        while True:
            pergunta = input("Digite sua dúvida (0 para voltar): ").strip()

            if pergunta == "0":
                if tentativas > 0:
                    self.registrar("pergunta", ultima_pergunta, orientacao_id,
                                   encontrou, False, tentativas, inicio)
                return

            if pergunta == "":
                print("Você não digitou nada. Escreva sua dúvida.")
                continue

            if contem_dado_pessoal(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)

            if not resultados or resultados[0][0] < 3:
                print("Não encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (por exemplo, o nome do documento) "
                      "ou volte e use as categorias.")
                continue

            encontrou = True
            pontos, melhor = resultados[0]
            orientacao_id = melhor.id
            nivel = "ALTA" if pontos >= 6 else "MÉDIA"

            print(f"\nConfiança da resposta: {nivel} ({pontos} pontos)")
            melhor.exibir()

            alternativas = []
            for pontos_alt, alternativa in resultados[1:3]:
                if pontos_alt >= 3:
                    alternativas.append(alternativa)
            if alternativas:
                print("Veja também:")
                for alternativa in alternativas:
                    print(f" - {alternativa.titulo}")

            if self.ler_sim_nao("Essa orientação respondeu sua dúvida? (s/n): "):
                self.registrar("pergunta", ultima_pergunta, orientacao_id,
                               True, True, tentativas, inicio)
                return

    def ler_opcao(self, total):
        while True:
            entrada = input("Escolha uma opção: ").strip()
            if entrada.isdecimal() and int(entrada) <= total:
                return int(entrada)
            print(f"Opção inválida. Digite um número de 0 a {total}.")

    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("Nenhuma categoria disponível.")
            return

        while True:
            inicio = time.time()
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f" {numero} - {categoria}")
            print(" 0 - Voltar")

            opcao = self.ler_opcao(len(categorias))
            if opcao == 0:
                return
            self.navegar_categoria(categorias[opcao - 1], inicio)

    def navegar_categoria(self, categoria, inicio):
        orientacoes = self.base.por_categoria(categoria)

        while True:
            print(f"\n{categoria}:")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f" {numero} - {orientacao.titulo}")
            print(" 0 - Voltar")

            opcao = self.ler_opcao(len(orientacoes))
            if opcao == 0:
                return

            orientacao = orientacoes[opcao - 1]
            print()
            orientacao.exibir()
            ajudou = self.ler_sim_nao("Essa orientação respondeu sua dúvida? (s/n): ")
            self.registrar("categoria", orientacao.titulo, orientacao.id,
                           True, ajudou, 1, inicio)
            inicio = time.time()

    def pedir_nota_facilidade(self):
        sessao = self.historico[self.inicio_sessao:]
        if not sessao:
            return

        while True:
            entrada = input("De 1 a 5, o quão fácil foi usar o assistente? ").strip()
            if entrada in ("1", "2", "3", "4", "5"):
                nota = int(entrada)
                break
            print("Digite um número de 1 a 5.")

        for atendimento in sessao:
            atendimento["facilidade"] = nota
        self.salvar_historico()

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            print("Ainda não há atendimentos registrados.")
            return

        encontrados = 0
        ajudaram = 0
        soma_tempo = 0
        soma_tentativas = 0
        notas = []
        sem_solucao = []

        for atendimento in self.historico:
            if atendimento["encontrou"]:
                encontrados += 1
            if atendimento["ajudou"]:
                ajudaram += 1
                soma_tempo += atendimento ["tempo_segundos"]
            else:
                if atendimento["pergunta"] not in sem_solucao:
                    sem_solucao.append(atendimento["pergunta"])
            soma_tentativas += atendimento["tentativas"]
            if "facilidade" in atendimento:
                notas.append(atendimento["facilidade"])

        print("\n=== Indicadores ===")
        print(f"Atendimentos registrados: {total}")
        print(f"Resposta encontrada: {encontrados / total * 100:.1f}%")
        print(f"Taxa de acerto (ajudou): {ajudaram / total * 100:.1f}%")
        if ajudaram > 0:
            print(f"Tempo médio para encontrar: {soma_tempo / ajudaram:.1f} s")
        else:
            print("Tempo médio para encontrar: sem dados")
        print(f"Tentativas por atendimento: {soma_tentativas / total:.1f}")
        if notas:
            print(f"Facilidade de uso (1 a 5): {sum(notas) / len(notas):.1f}")
        else:
            print("Facilidade de uso (1 a 5): sem dados")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for duvida in sem_solucao:
                print(f" - {duvida}")
        else:
            print(" (nenhuma)")

    def exportar_csv(self, caminho="data/atendimentos.csv"):
        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, restval="")
                escritor.writeheader()
                escritor.writerows(self.historico)
        except OSError:
            print("Não foi possível exportar o CSV.")
            return
        print(f"{len(self.historico)} atendimentos exportados para {caminho}.")