import json
import os
import csv
from datetime import datetime

PASTA_DESTINO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_PRODUTOS = os.path.join(PASTA_DESTINO, "produtos.json")
ARQUIVO_HISTORICO = os.path.join(PASTA_DESTINO, "historico_vendas.json")
ARQUIVO_CSV = os.path.join(PASTA_DESTINO, "relatorio_vendas.csv")
ARQUIVO_RELATORIO_TXT = os.path.join(PASTA_DESTINO, "relatorio.txt")
ARQUIVO_HTML = os.path.join(PASTA_DESTINO, "cardapio_v2.html")

if not os.path.exists(PASTA_DESTINO):
    os.makedirs(PASTA_DESTINO)

produtos = [] 
historico_vendas = []


def fazer_login():
    """Sistema de autenticação simples."""
    print("\n" + "="*30 + "\n🔐 ACESSO - CAMPUSBITE\n" + "="*30)
    user = input("Usuário: ").lower()
    senha = input("Senha: ")
    
    if (user == "gerente" and senha == "1234") or (user == "atendente" and senha == "1234"):
        print(f"Bem-vindo, {user.upper()}!")
        return True
    print("Acesso negado!")
    return False

def salvar_dados():
    """Salva produtos e histórico nos arquivos JSON da pasta especificada."""
    try:
        with open(ARQUIVO_PRODUTOS, "w", encoding="utf-8") as f:
            json.dump(produtos, f, indent=4, ensure_ascii=False)
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(historico_vendas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro crítico ao salvar dados: {e}")

def carregar_dados():
    """Carrega os dados salvos ao iniciar o programa."""
    global produtos, historico_vendas
    try:
        if os.path.exists(ARQUIVO_PRODUTOS):
            with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
                produtos = json.load(f)
    except (json.JSONDecodeError, OSError):
        produtos = []
        print("produtos.json inválido. Lista de produtos reiniciada.")
    try:
        if os.path.exists(ARQUIVO_HISTORICO):
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
                historico_vendas = json.load(f)
    except (json.JSONDecodeError, OSError):
        historico_vendas = []
        print("historico_vendas.json inválido. Histórico reiniciado.")
    print(f"Arquivos carregados de: {PASTA_DESTINO}")


def ler_numero_positivo(mensagem, tipo=float):
    while True:
        try:
            valor = tipo(input(mensagem))
            if valor >= 0: return valor
            print("O valor deve ser positivo.")
        except ValueError:
            print(" Entrada inválida. Digite um número.")

def ler_texto_obrigatorio(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Campo obrigatório. Tente novamente.")

def localizar_produto(nome_busca):
    for p in produtos:
        if p['nome'].lower() == nome_busca.lower():
            return p
    return None

# ==========================================
# 3. FUNCIONALIDADES DO SISTEMA
# ==========================================

def adicionar_produto():
    nome = ler_texto_obrigatorio("Nome do produto: ")
    categoria = ler_texto_obrigatorio("Categoria: ")
    preco = ler_numero_positivo("Preço (R$): ", float)
    estoque = ler_numero_positivo("Estoque inicial: ", int)
    produtos.append({"nome": nome, "categoria": categoria, "preco": preco, "estoque": estoque})
    salvar_dados()
    print("✅ Produto cadastrado com sucesso!")

def listar_cardapio():
    print("\n=== CARDÁPIO CAMPUSBITE ===")
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    for p in produtos:
        cor = "\033[91m" if p['estoque'] <= 5 else ""
        print(f"{cor}{p['nome']} | {p['categoria']} | R${p['preco']:.2f} | Estoque: {p['estoque']}\033[0m")

def buscar_produto():
    termo = ler_texto_obrigatorio("Buscar por nome ou categoria: ").lower()
    encontrou = False
    for p in produtos:
        if termo in p['nome'].lower() or termo in p['categoria'].lower():
            print(f"Resultado: {p['nome']} - R${p['preco']:.2f} (Estoque: {p['estoque']})")
            encontrou = True
    if not encontrou: print("Nenhum item encontrado.")

def registrar_venda():
    nome = ler_texto_obrigatorio("Nome do produto vendido: ")
    p = localizar_produto(nome)
    if p:
        qtd = ler_numero_positivo(f"Quantidade de {p['nome']}: ", int)
        if p['estoque'] >= qtd:
            p['estoque'] -= qtd
            total = p['preco'] * qtd
            
            venda = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Produto": p['nome'],
                "Quantidade": qtd,
                "Valor_Unitario": p['preco'],
                "Total": total
            }
            historico_vendas.append(venda)
            salvar_dados()
            print(f"Venda confirmada! Total: R${total:.2f}")
        else:
            print("Estoque insuficiente!")
    else:
        print("Produto não cadastrado.")

def editar_produto():
    nome = ler_texto_obrigatorio("Qual produto deseja editar? ")
    p = localizar_produto(nome)
    if p:
        print(f"Editando: {p['nome']}")
        p['preco'] = ler_numero_positivo(f"Novo preço (Atual R${p['preco']}): ", float)
        p['estoque'] = ler_numero_positivo(f"Novo estoque (Atual {p['estoque']}): ", int)
        salvar_dados()
        print("Dados atualizados!")
    else:
        print("Produto não encontrado.")

def remover_produto():
    nome = ler_texto_obrigatorio("Qual produto deseja remover? ")
    p = localizar_produto(nome)
    if p:
        confirma = input(f"Confirmar remoção de '{p['nome']}'? (s/n): ").lower()
        if confirma == 's':
            produtos.remove(p)
            salvar_dados()
            print("Produto removido do sistema.")
    else:
        print("Não encontrado.")

def gerar_relatorio_gerencial():
    print("\n=== RELATÓRIO DE GESTÃO ===")
    v_estoque = sum(p['preco'] * p['estoque'] for p in produtos)
    v_vendas = sum(v['Total'] for v in historico_vendas)
    print(f"alor total em mercadoria (estoque): R${v_estoque:.2f}")
    print(f"Faturamento total (vendas): R${v_vendas:.2f}")
    print(f"Total de atendimentos: {len(historico_vendas)}")

def gerar_relatorio_txt():
    """Gera relatório textual solicitado na entrega."""
    v_estoque = sum(p['preco'] * p['estoque'] for p in produtos)
    v_vendas = sum(v['Total'] for v in historico_vendas)
    linhas = [
        "RELATÓRIO CAMPUSBITE",
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "="*40,
        f"Valor total em estoque: R${v_estoque:.2f}",
        f"Faturamento total: R${v_vendas:.2f}",
        f"Total de vendas registradas: {len(historico_vendas)}",
        "",
        "VENDAS:",
    ]
    if not historico_vendas:
        linhas.append("Nenhuma venda registrada.")
    else:
        for v in historico_vendas:
            linhas.append(
                f"{v['Data']} | {v['Produto']} | Qtd: {v['Quantidade']} | "
                f"Unit: R${v['Valor_Unitario']:.2f} | Total: R${v['Total']:.2f}"
            )
    try:
        with open(ARQUIVO_RELATORIO_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas))
        print(f"Relatório TXT gerado em: {ARQUIVO_RELATORIO_TXT}")
    except Exception as e:
        print(f"Erro ao gerar relatorio.txt: {e}")

def exportar_csv():
    """Gera um arquivo CSV compatível com Excel."""
    if not historico_vendas:
        print("Não há vendas para exportar.")
        return
    try:
        with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8-sig") as f:
            colunas = ["Data", "Produto", "Quantidade", "Valor_Unitario", "Total"]
            escritor = csv.DictWriter(f, fieldnames=colunas)
            escritor.writeheader()
            escritor.writerows(historico_vendas)
        print(f"Relatório exportado com sucesso em:\n{ARQUIVO_CSV}")
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}")

def gerar_html():
    """Gera o catálogo visual moderno."""
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    caminho_html = ARQUIVO_HTML
    
    html = f'''<html><head><meta charset="utf-8">
    <style>
        body{{font-family: Arial; text-align:center; background:#f4f4f4;}}
        .box{{background:white; width:80%; margin:20px auto; padding:20px; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1);}}
        table{{width:100%; border-collapse:collapse;}}
        th{{background:#d32f2f; color:white; padding:10px;}}
        td{{padding:10px; border-bottom:1px solid #ddd;}}
        .alerta{{color:red; font-weight:bold; background:#fff0f0;}}
    </style></head><body><div class="box">
    <h1>🍔 CampusBite - Cardápio Universitário</h1>
    <p>Atualizado em: {data}</p><table>
    <tr><th>Produto</th><th>Categoria</th><th>Preço</th><th>Estoque</th></tr>'''
    
    for p in produtos:
        classe = 'class="alerta"' if p['estoque'] <= 5 else ""
        html += f"<tr {classe}><td>{p['nome']}</td><td>{p['categoria']}</td><td>R${p['preco']:.2f}</td><td>{p['estoque']}</td></tr>"
    
    html += "</table></div></body></html>"
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Catálogo HTML gerado em: {caminho_html}")

# ==========================================
# LOOP PRINCIPAL DO SISTEMA
# ==========================================

carregar_dados()

if fazer_login():
    while True:
        print("\n=== MENU CAMPUSBITE v3.2 ===")
        print("1. Cadastrar | 2. Vender   | 3. Editar    | 4. Remover")
        print("5. Cardápio  | 6. Buscar   | 7. Relatório | 8. Gerar HTML")
        print("9. Excel CSV | 10. Relatório TXT | 0. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1": adicionar_produto()
        elif opcao == "2": registrar_venda()
        elif opcao == "3": editar_produto()
        elif opcao == "4": remover_produto()
        elif opcao == "5": listar_cardapio()
        elif opcao == "6": buscar_produto()
        elif opcao == "7": gerar_relatorio_gerencial()
        elif opcao == "8": gerar_html()
        elif opcao == "9": exportar_csv()
        elif opcao == "10": gerar_relatorio_txt()
        elif opcao == "0":
            salvar_dados()
            print("Sistema encerrado. Até logo!")
            break
        else:
            print("Opção inválida!")