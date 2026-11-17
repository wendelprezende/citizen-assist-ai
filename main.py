from base_conhecimento import BaseConhecimento
from assistente import Assistente

base = BaseConhecimento("data/base_conhecimento.json")
base.carregar()

assistente = Assistente("Citizen Assist AI", base)

print(f"=== {assistente.nome} ===")
print("Este assistente NÃO é um canal oficial. Não digite dados pessoais.")

while True:
    print("\nMenu principal:")
    print(" 1 - Fazer uma pergunta")
    print(" 2 - Navegar por categorias")
    print(" 3 - Ver indicadores")
    print(" 4 - Exportar atendimentos (CSV)")
    print(" 0 - Sair")
    opcao = assistente.ler_opcao(4)

    if opcao == 1:
        assistente.perguntar()
    elif opcao == 2:
        assistente.navegar()
    elif opcao == 3:
        assistente.indicadores()
    elif opcao == 4:
        assistente.exportar_csv()
    else:
        break

assistente.pedir_nota_facilidade()
assistente.exportar_csv()
print("Obrigado por usar o Citizen Assist AI!")