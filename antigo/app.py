import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
import sqlite3

# Conexão com o banco de dados SQLite
conn = sqlite3.connect('clientes.db')
c = conn.cursor()

# Criar ou atualizar a tabela de clientes
c.execute('''CREATE TABLE IF NOT EXISTS clientes (
            nome TEXT, contato TEXT, data_visita TEXT, visitas INTEGER, procedimento TEXT, valor REAL, produto_utilizado TEXT)''')

# Criar ou atualizar a tabela de procedimentos
c.execute('''CREATE TABLE IF NOT EXISTS procedimentos (
            contato TEXT, procedimento TEXT, data_visita TEXT, valor REAL, produto_utilizado TEXT)''')

conn.commit()

contatos_cadastrados = []

# Função para cadastrar cliente
def cadastrar_cliente():
    nome = entry_nome.get()
    contato = entry_contato.get()
    data_visita = entry_data_visita.get()
    visitas = entry_visitas.get()
    procedimento = entry_procedimento.get()
    valor = entry_valor.get()
    produto_utilizado = entry_produto.get()

    if contato in contatos_cadastrados:
        tk.messagebox.showerror("Erro", "Número para contato já cadastrado!")
        return
    
    contatos_cadastrados.append(contato)

    if nome and contato and data_visita and visitas and procedimento and valor and produto_utilizado:
        c.execute("INSERT INTO clientes (nome, contato, data_visita, visitas, procedimento, valor, produto_utilizado) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (nome, contato, data_visita, visitas, procedimento, valor, produto_utilizado))
        c.execute("INSERT INTO procedimentos (contato, procedimento, data_visita, valor, produto_utilizado) VALUES (?, ?, ?, ?, ?)",
                  (contato, procedimento, data_visita, valor, produto_utilizado))
        conn.commit()
        messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
        limpar_campos()
        exibir_todos_clientes()
    else:
        messagebox.showwarning("Erro", "Preencha todos os campos.")

# Função para buscar cliente pelo número de contato
def buscar_cliente():
    contato = entry_buscar_contato.get()
    if contato:
        c.execute("SELECT * FROM clientes WHERE contato=?", (contato,))
        resultado = c.fetchone()
        if resultado:
            entry_nome_atual.config(state='normal')
            entry_procedimento_novo.config(state='normal')
            entry_data_visita_nova.config(state='normal')
            entry_valor.config(state='normal')
            entry_produto.config(state='normal')
            entry_nome_atual.delete(0, tk.END)
            entry_nome_atual.insert(0, resultado[0])
            entry_nome_atual.config(state='readonly')
            entry_data_visita_nova.delete(0, tk.END)
            entry_data_visita_nova.insert(0, resultado[3])
        else:
            messagebox.showwarning("Erro", "Cliente não encontrado.")
    else:
        messagebox.showwarning("Erro", "Informe o número de contato para busca.")

# Função para adicionar novo procedimento
def adicionar_procedimento():
    contato = entry_buscar_contato.get()
    novo_procedimento = entry_procedimento_novo.get()
    nova_data_visita = entry_data_visita_nova.get()
    novo_valor = entry_valor_procedimento.get()
    novo_produto_utilizado = entry_produto_usado.get()

    if novo_procedimento and nova_data_visita and novo_valor and novo_produto_utilizado:
        c.execute("SELECT visitas FROM clientes WHERE contato=?", (contato,))
        resultado = c.fetchone()
        if resultado:
            visitas_atualizadas = resultado[0] + 1
            c.execute("UPDATE clientes SET visitas=?, data_visita=?, procedimento=?, valor=?, produto_utilizado=? WHERE contato=?",
                      (visitas_atualizadas, nova_data_visita, novo_procedimento, novo_valor, novo_produto_utilizado, contato))
            c.execute("INSERT INTO procedimentos (contato, procedimento, data_visita, valor, produto_utilizado) VALUES (?, ?, ?, ?, ?)",
                      (contato, novo_procedimento, nova_data_visita, novo_valor, novo_produto_utilizado))
            conn.commit()
            messagebox.showinfo("Sucesso", "Novo procedimento adicionado!")
            limpar_campos_novo_procedimento()
            exibir_todos_clientes()
        else:
            messagebox.showwarning("Erro", "Cliente não encontrado.")
    else:
        messagebox.showwarning("Erro", "Preencha todos os campos para adicionar o procedimento.")

# Função para exibir todos os clientes na tabela
def exibir_todos_clientes():
    # Remove todos os dados anteriores da tabela
    for i in tree.get_children():
        tree.delete(i)
    
    c.execute("SELECT * FROM clientes")
    for row in c.fetchall():
        tree.insert("", "end", values=row)

# Função para buscar e filtrar clientes
def filtrar_clientes():
    termo_busca = entry_busca.get().lower()
    for i in tree.get_children():
        tree.delete(i)  # Limpa a tabela antes de filtrar
    
    c.execute("SELECT * FROM clientes")
    for row in c.fetchall():
        if termo_busca in row[0].lower() or termo_busca in row[2]:  # Filtra por nome ou contato
            tree.insert("", "end", values=row)


# Função para excluir cliente selecionado
def excluir_cliente():
    try:
        # Verificar se um cliente foi selecionado
        item = tree.selection()
        if not item:
            messagebox.showwarning("Erro", "Selecione um cliente para excluir.")
            return
        
        # Obter o cliente selecionado
        item = item[0]
        cliente_contato = tree.item(item, 'values')[2]  # Certifique-se de que o contato está na posição correta (coluna 3)

        # Pedir confirmação para a exclusão
        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir o cliente?")
        if not confirmar:
            return  # Se o usuário cancelar, a exclusão é interrompida
        
        # Excluir o cliente do banco de dados
        c.execute("DELETE FROM clientes WHERE contato=?", (cliente_contato,))
        c.execute("DELETE FROM procedimentos WHERE contato=?", (cliente_contato,))
        conn.commit()

        # Remover o item do treeview
        tree.delete(item)

        # Mostrar mensagem de sucesso
        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")

        # Atualizar a tabela após exclusão
        exibir_todos_clientes()
    
    except IndexError:
        messagebox.showwarning("Erro", "Selecione um cliente para excluir.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Função para exibir histórico de procedimentos ao clicar no cliente
def exibir_historico_cliente(event):
    item = tree.selection()[0]
    cliente_contato = tree.item(item, 'values')[2]
    
    c.execute("SELECT nome FROM clientes WHERE contato=?", (cliente_contato,))
    cliente_nome = c.fetchone()
    if cliente_nome:
        cliente_nome = cliente_nome[0]
    else:
        cliente_nome = "Desconhecido"

    # Cria uma nova aba para exibir o histórico de procedimentos
    aba_historico = ttk.Frame(notebook)
    notebook.add(aba_historico, text=f"Histórico {cliente_nome}")
    notebook.select(aba_historico)
    
    # Exibir o histórico de procedimentos do cliente
    ttk.Label(aba_historico, text=f"Histórico de Procedimentos de: {cliente_nome}").grid(row=0, column=0, padx=10, pady=10)
    
    tree_historico = ttk.Treeview(aba_historico, columns=("Procedimento", "Data da Visita", "Valor", "Produto"), show="headings")
    tree_historico.heading("Procedimento", text="Procedimento")
    tree_historico.heading("Data da Visita", text="Data da Visita")
    tree_historico.heading("Valor", text="Valor")
    tree_historico.heading("Produto", text="Produto")
    tree_historico.grid(row=1, column=0)
    
    c.execute("SELECT procedimento, data_visita FROM procedimentos WHERE contato=?", (cliente_contato,))
    for row in c.fetchall():
        tree_historico.insert("", "end", values=row)
    
    ttk.Button(aba_historico, text="Fechar Aba", command=lambda: notebook.forget(aba_historico)).grid(row=2, column=0, pady=10)

# Função para exportar os dados para uma planilha Excel
def exportar_planilha():
    c.execute("SELECT * FROM clientes")
    dados = c.fetchall()
    df = pd.DataFrame(dados, columns=["Nome", "CPF", "Data da Visita", "Visitas", "Procedimento"])
    df.to_excel("clientes.xlsx", index=False)
    messagebox.showinfo("Sucesso", "Planilha exportada com sucesso!")

# Função para limpar campos
def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_contato.delete(0, tk.END)
    entry_data_visita.delete(0, tk.END)
    entry_visitas.delete(0, tk.END)
    entry_procedimento.delete(0, tk.END)
    entry_valor.delete(0,tk.END)
    entry_produto.delete(0, tk.END)

def limpar_campos_novo_procedimento():
    entry_procedimento_novo.delete(0, tk.END)
    entry_data_visita_nova.delete(0, tk.END)
    entry_valor_procedimento.delete(0, tk.END)
    entry_produto_usado.delete(0, tk.END)

# Função para mudar de aba
def mostrar_aba(aba):
    notebook.select(aba)

# Interface gráfica com tkinter
win_width, win_height = 1280, 1024
app = tk.Tk()
app.geometry(f'{win_width}x{win_height}')
app.title("Gerenciamento de Clientes - Salão de Cabelo")

# Criação do Notebook (abas)
notebook = ttk.Notebook(app)
notebook.grid(row=0, column=0, padx=10, pady=10)

# Aba principal
aba_principal = ttk.Frame(notebook)
notebook.add(aba_principal, text="Menu Principal")

# Aba cadastro de cliente
aba_cadastro = ttk.Frame(notebook)
notebook.add(aba_cadastro, text="Cadastro de Cliente")

# Aba busca de cliente
aba_busca = ttk.Frame(notebook)
notebook.add(aba_busca, text="Buscar Cliente")

# Aba ver todos os clientes
aba_todos = ttk.Frame(notebook)
notebook.add(aba_todos, text="Ver Todos os Clientes")

# ----------- Conteúdo da Aba Principal (Menu) ----------- 
ttk.Button(aba_principal, text="Cadastro de Cliente", command=lambda: mostrar_aba(aba_cadastro)).grid(row=0, column=0, padx=10, pady=10)
ttk.Button(aba_principal, text="Buscar Cliente", command=lambda: mostrar_aba(aba_busca)).grid(row=1, column=0, padx=10, pady=10)
ttk.Button(aba_principal, text="Ver Todos os Clientes", command=lambda: mostrar_aba(aba_todos)).grid(row=2, column=0, padx=10, pady=10)
ttk.Button(aba_principal, text="Exportar Planilha", command=exportar_planilha).grid(row=3, column=0, padx=10, pady=10)

# ----------- Conteúdo da Aba Cadastro de Cliente ----------- 
ttk.Label(aba_cadastro, text="Nome:").grid(row=0, column=0)
entry_nome = ttk.Entry(aba_cadastro)
entry_nome.grid(row=0, column=1)

ttk.Label(aba_cadastro, text="Contato:").grid(row=1, column=0)
entry_contato = ttk.Entry(aba_cadastro)
entry_contato.grid(row=1, column=1)

ttk.Label(aba_cadastro, text="Data da Visita:").grid(row=2, column=0)
entry_data_visita = DateEntry(aba_cadastro, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
entry_data_visita.grid(row=2, column=1)

ttk.Label(aba_cadastro, text="Número de Visitas:").grid(row=3, column=0)
entry_visitas = ttk.Entry(aba_cadastro)
entry_visitas.grid(row=3, column=1)

ttk.Label(aba_cadastro, text="Procedimento:").grid(row=4, column=0)
entry_procedimento = ttk.Entry(aba_cadastro)
entry_procedimento.grid(row=4, column=1)

ttk.Label(aba_cadastro, text="Valor:").grid(row=5, column=0)
entry_valor = ttk.Entry(aba_cadastro)
entry_valor.grid(row=5, column=1)

ttk.Label(aba_cadastro, text="Produto Utilizado:").grid(row=6, column=0)
entry_produto = ttk.Entry(aba_cadastro)
entry_produto.grid(row=6, column=1)

ttk.Button(aba_cadastro, text="Cadastrar Cliente", command=cadastrar_cliente).grid(row=7, column=0, columnspan=2, pady=10)

# ----------- Conteúdo da Aba Buscar Cliente ----------- 
ttk.Label(aba_busca, text="Contato do Cliente:").grid(row=0, column=0)
entry_buscar_contato = ttk.Entry(aba_busca)
entry_buscar_contato.grid(row=0, column=1)

ttk.Button(aba_busca, text="Buscar Cliente", command=buscar_cliente).grid(row=0, column=2, padx=5)

ttk.Label(aba_busca, text="Nome Atual:").grid(row=1, column=0)
entry_nome_atual = ttk.Entry(aba_busca, state='readonly')
entry_nome_atual.grid(row=1, column=1)

ttk.Label(aba_busca, text="Novo Procedimento:").grid(row=2, column=0)
entry_procedimento_novo = ttk.Entry(aba_busca)
entry_procedimento_novo.grid(row=2, column=1)

ttk.Label(aba_busca, text="Nova Data da Visita:").grid(row=3, column=0)
entry_data_visita_nova = DateEntry(aba_busca, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
entry_data_visita_nova.grid(row=3, column=1)

# Novo campo para o valor do procedimento
ttk.Label(aba_busca, text="Valor do Procedimento:").grid(row=4, column=0)
entry_valor_procedimento = ttk.Entry(aba_busca)
entry_valor_procedimento.grid(row=4, column=1)

# Novo campo para o produto usado no procedimento
ttk.Label(aba_busca, text="Produto Usado:").grid(row=5, column=0)
entry_produto_usado = ttk.Entry(aba_busca)
entry_produto_usado.grid(row=5, column=1)

ttk.Button(aba_busca, text="Adicionar Procedimento", command=adicionar_procedimento).grid(row=6, column=0, columnspan=2, pady=10)

# ----------- Conteúdo da Aba Ver Todos os Clientes ----------- 
ttk.Label(aba_todos, text="Buscar Cliente:").grid(row=0, column=0, padx=10, pady=10)
entry_busca = ttk.Entry(aba_todos)
entry_busca.grid(row=0, column=1, padx=10, pady=10)

ttk.Button(aba_todos, text="Filtrar", command=filtrar_clientes).grid(row=0, column=2, padx=10, pady=10)

# Tabela para exibir todos os clientes
tree = ttk.Treeview(aba_todos, columns=("Nome", "Contato", "Data da Visita", "Visitas", "Procedimento", "Valor", "Produto"), show="headings")
tree.heading("Nome", text="Nome")
tree.heading("Contato", text="Contato")
tree.heading("Data da Visita", text="Data da Visita")
tree.heading("Visitas", text="Visitas")
tree.heading("Procedimento", text="Procedimento")
tree.heading("Valor", text="Valor")
tree.heading("Produto", text="Produto")
tree.grid(row=1, column=0, columnspan=3)

# Adicionar botão de exclusão
ttk.Button(aba_todos, text="Excluir Cliente", command=excluir_cliente).grid(row=2, column=0, columnspan=3, pady=10)

# Preencher a tabela inicialmente com todos os clientes
exibir_todos_clientes()

# Evento de clique na tabela para exibir histórico de procedimentos
tree.bind("<Double-1>", exibir_historico_cliente)

app.mainloop()

# Fecha a conexão com o banco de dados ao fechar o aplicativo
conn.close()