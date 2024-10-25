import sqlite3
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style, ttk
from datetime import datetime
import tkinter.font as tkFont
from PIL import Image, ImageTk


# Conectar ou criar o banco de dados
conn = sqlite3.connect("salon_manager.db")
cursor = conn.cursor()

# Criar a tabela de procedimentos, se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS procedures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    procedure_date TEXT,
    procedure TEXT,
    value REAL,
    product TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (id)
)
""")
conn.commit()

class SalonManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Clientes")
        self.style = Style()
        
        # Notebook para as abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Página Inicial
        self.home_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.home_tab, text="Início")

        # Definindo a fonte padrão
        self.default_font = tkFont.Font(family="Helvetica", size=12)

        # Configurando o estilo do Treeview
        self.style.configure("Treeview", font=self.default_font, rowheight=25, bordercolor="gray", borderwidth=1, highlightthickness=1)
        self.style.configure("Treeview.Heading", font=("Helvetica", 12))
        self.style.map("Treeview", background=[("selected", "lightblue"), ("", "white"), ("alternate", "#f9f9f9")])

        # Estilo dos botões e entrada
        self.style.configure("TButton", borderwidth=1)
        self.style.map("TButton", background=[("active", "#f6a3c1")])  # Cor de fundo ao clicar
        self.style.configure("TEntry", borderwidth=2, relief="solid")  # Define borda padrão para Entry
        self.style.map("TEntry", bordercolor=[("focus", "#f6a3c1")])

        # Configurando o estilo para todos os widgets
        self.root.option_add("*Font", self.default_font)

        # Chamar o método para criar a tela inicial
        self.create_home_tab()

        # Criar as abas
        self.create_tabs()

    def create_home_tab(self):
        # Título
        title_label = ttk.Label(self.home_tab, text="Gestão de Clientes", font=("Helvetica", 20))
        title_label.grid(row=0, column=0, padx=100, pady=10, sticky="w")

        # Botões para as abas
        register_button = ttk.Button(self.home_tab, text="Cadastro de Cliente", command=lambda: self.notebook.select(self.register_frame))
        register_button.grid(row=1, column=0, padx=100, pady=10, sticky="w")

        table_button = ttk.Button(self.home_tab, text="Tabela de Clientes", command=lambda: self.notebook.select(self.table_frame))
        table_button.grid(row=2, column=0, padx=100, pady=10, sticky="w")

        # Adicionar a imagem do salão
        self.add_salon_image(self.home_tab)

    def add_salon_image(self, parent):
        # Carregar a imagem
        try:
            salon_image = Image.open("pngtree.jpeg")  # Altere para o caminho correto da imagem
            salon_image = salon_image.resize((300, 300))  # Ajustar o tamanho da imagem
            salon_photo = ImageTk.PhotoImage(salon_image)

            # Criar um rótulo para exibir a imagem
            image_label = ttk.Label(parent, image=salon_photo)
            image_label.image = salon_photo  # Manter uma referência da imagem
            image_label.grid(row=0, column=2, rowspan=8, padx=200, pady=20, sticky="ne")  # Fixar na coluna 2, alinhado à direita
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            
    def create_tabs(self):
        # Aba de Cadastro
        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="Cadastro de Cliente")
        self.create_register_tab()
        self.add_salon_image(self.register_frame)  # Adiciona a imagem na aba de Cadastro

        # Aba de Tabela de Clientes
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Tabela de Clientes")
        self.create_table_tab()
        
    def create_register_tab(self):
        # Labels e Entradas de Dados
        ttk.Label(self.register_frame, text="Nome:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ttk.Entry(self.register_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(self.register_frame, text="Contato:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.contact_entry = ttk.Entry(self.register_frame)
        self.contact_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(self.register_frame, text="Data da Visita:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.date_entry = ttk.Entry(self.register_frame)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.date_entry.insert(0, datetime.today().strftime('%d-%m-%Y'))  # Data atual
        
        ttk.Label(self.register_frame, text="Procedimento:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.procedure_entry = ttk.Entry(self.register_frame)
        self.procedure_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(self.register_frame, text="Valor:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.value_entry = ttk.Entry(self.register_frame)
        self.value_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(self.register_frame, text="Produto Utilizado:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.product_entry = ttk.Entry(self.register_frame)
        self.product_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")
        
        # Botão de Cadastro
        register_button = ttk.Button(self.register_frame, text="Cadastrar Cliente", command=self.register_client)
        register_button.grid(row=6, column=0, columnspan=2, pady=20)

    def register_client(self):
        # Captura e valida os dados
        name = self.name_entry.get()
        contact = self.contact_entry.get()
        date = self.date_entry.get()
        procedure = self.procedure_entry.get()
        value = self.value_entry.get()
        product = self.product_entry.get()
        
        if name and contact:
            try:
                # Inserindo o cliente
                cursor.execute("INSERT INTO clients (name, contact) VALUES (?, ?)", (name, contact))
                conn.commit()

                # Pegando o ID do cliente recém-inserido
                client_id = cursor.lastrowid
                
                # Inserindo o procedimento
                cursor.execute("INSERT INTO procedures (client_id, procedure_date, procedure, value, product) VALUES (?, ?, ?, ?, ?)",
                            (client_id, date, procedure, value, product))
                conn.commit()
                
                # Exibe uma mensagem de sucesso
                messagebox.showinfo("Sucesso", "Cliente e procedimento cadastrados com sucesso!")
                
                # Limpa os campos de entrada e atualiza a tabela
                self.clear_entries()
                self.load_clients()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Contato já cadastrado.")
        else:
            messagebox.showerror("Erro", "Nome e Contato são obrigatórios.")
        
    def clear_entries(self):
        # Limpa todas as caixas de texto da aba de cadastro
        self.name_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime('%d-%m-%Y'))  # Redefine para a data atual
        self.procedure_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)
        self.product_entry.delete(0, tk.END)

    def delete_client(self, client_id):
        if messagebox.askyesno("Confirmar Exclusão", "Você tem certeza que deseja excluir este cliente e todos os seus procedimentos?"):
            try:
                # Excluindo os procedimentos do cliente
                cursor.execute("DELETE FROM procedures WHERE client_id = ?", (client_id,))
                # Excluindo o cliente
                cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
                conn.commit()

                messagebox.showinfo("Sucesso", "Cliente e seus procedimentos foram excluídos com sucesso!")
                self.load_clients()  # Atualiza a tabela de clientes
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao excluir o cliente: {str(e)}")
    
    def display_client_info(self, client):
        # Limpa os resultados anteriores
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Exibe informações básicas do cliente
        ttk.Label(self.results_frame, text="Nome: " + client[1]).grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self.results_frame, text="Contato: " + client[2]).grid(row=1, column=0, padx=10, pady=5)
        
        # Histórico de Procedimentos
        ttk.Label(self.results_frame, text="Histórico de Procedimentos:").grid(row=2, column=0, columnspan=2, pady=10)
        
        # Exibe os procedimentos anteriores
        cursor.execute("SELECT procedure_date, procedure, value, product FROM procedures WHERE client_id = ?", (client[0],))
        procedures = cursor.fetchall()
        
        # Define idx como 3, a próxima linha após o cabeçalho do histórico
        idx = 3
        for proc in procedures:
            procedure_text = f"Data: {proc[0]} | Procedimento: {proc[1]} | Valor: {proc[2]} | Produto: {proc[3]}"
            ttk.Label(self.results_frame, text=procedure_text).grid(row=idx, column=0, columnspan=2, padx=10, pady=5)
            idx += 1  # Incrementa idx para cada procedimento exibido
        
    def create_table_tab(self):
        # Caixa de pesquisa para filtrar clientes
        ttk.Label(self.table_frame, text="Buscar Cliente:").grid(row=0, column=0, padx=10, pady=10)
        self.table_search_entry = ttk.Entry(self.table_frame)
        self.table_search_entry.bind("<Return>", lambda event: self.search_in_table())
        self.table_search_entry.grid(row=0, column=1, padx=10, pady=10)

        search_table_button = ttk.Button(self.table_frame, text="Buscar", command=self.search_in_table)
        search_table_button.grid(row=0, column=2, padx=10, pady=10)

        # Configurando o Treeview para exibir a tabela de clientes
        self.clients_tree = ttk.Treeview(self.table_frame, columns=("ID", "Nome", "Contato", "Última Visita", "Procedimento"), show="headings")
        self.clients_tree.heading("ID", text="ID")
        self.clients_tree.heading("Nome", text="Nome")
        self.clients_tree.heading("Contato", text="Contato")
        self.clients_tree.heading("Última Visita", text="Última Visita")
        self.clients_tree.heading("Procedimento", text="Procedimento")

        # Centralizando o texto nas colunas
        for col in ("ID", "Nome", "Contato", "Última Visita", "Procedimento"):
            self.clients_tree.heading(col, anchor="center")  # Centraliza o cabeçalho
            self.clients_tree.column(col, anchor="center")   # Centraliza o conteúdo

        self.clients_tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Adicionar evento para exibir histórico ao clicar em um cliente
        self.clients_tree.bind("<Double-1>", self.view_client_history)

        # Botão para excluir cliente
        delete_client_button = ttk.Button(self.table_frame, text="Excluir Cliente", command=self.delete_selected_client)
        delete_client_button.grid(row=2, column=0, padx=10, pady=10)

        # Configura o grid para expandir o Treeview
        self.table_frame.grid_rowconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=1)

        # Carregar todos os clientes inicialmente
        self.load_clients()

    def load_clients(self):
        # Limpa a tabela antes de recarregar
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        # Consulta para obter todos os clientes e seu último procedimento
        cursor.execute("""
            SELECT c.id, c.name, c.contact, p.procedure_date, p.procedure 
            FROM clients AS c
            LEFT JOIN (
                SELECT client_id, procedure_date, procedure
                FROM procedures
                WHERE (client_id, procedure_date) IN (
                    SELECT client_id, MAX(procedure_date)
                    FROM procedures
                    GROUP BY client_id
                )
            ) AS p ON c.id = p.client_id
            ORDER BY c.name ASC, p.procedure_date DESC
        """)
        
        for row in cursor.fetchall():
            self.clients_tree.insert("", "end", values=row)

    def delete_selected_client(self):
        selected_item = self.clients_tree.selection()
        if selected_item:
            client_id = self.clients_tree.item(selected_item)["values"][0]
            self.delete_client(client_id)
        else:
            messagebox.showwarning("Atenção", "Nenhum cliente selecionado.")

    def search_in_table(self):
        search_query = self.table_search_entry.get()
        # Limpa a tabela antes de recarregar
        for row in self.clients_tree.get_children():
            self.clients_tree.delete(row)

        if search_query:
            # Buscar clientes cujo nome ou contato contenham o texto da pesquisa
            cursor.execute(""" 
                SELECT c.id, c.name, c.contact, p.procedure_date, p.procedure 
                FROM clients AS c
                LEFT JOIN (
                    SELECT client_id, procedure_date, procedure
                    FROM procedures
                    WHERE (client_id, procedure_date) IN (
                        SELECT client_id, MAX(procedure_date)
                        FROM procedures
                        GROUP BY client_id
                    )
                ) AS p ON c.id = p.client_id
                WHERE c.name LIKE ? OR c.contact LIKE ?
                ORDER BY c.name ASC, p.procedure_date DESC  -- Ordena os resultados da busca
            """, (f"%{search_query}%", f"%{search_query}%"))
        else:
            # Se a busca estiver vazia, carrega todos os clientes com ordenação
            cursor.execute("""
                SELECT c.id, c.name, c.contact, p.procedure_date, p.procedure 
                FROM clients AS c
                LEFT JOIN (
                    SELECT client_id, procedure_date, procedure
                    FROM procedures
                    WHERE (client_id, procedure_date) IN (
                        SELECT client_id, MAX(procedure_date)
                        FROM procedures
                        GROUP BY client_id
                    )
                ) AS p ON c.id = p.client_id
                ORDER BY c.name ASC, p.procedure_date DESC  -- Ordena a lista de clientes
            """)

        for client in cursor.fetchall():
            self.clients_tree.insert("", "end", values=client)

    def view_client_history(self, event):
        selected_item = self.clients_tree.selection()
        if selected_item:
            client_id = self.clients_tree.item(selected_item)["values"][0]
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            client_data = cursor.fetchone()

            # Janela para mostrar o histórico do cliente
            history_window = tk.Toplevel(self.root)
            history_window.title(f"Histórico de {client_data[1]}")

            ttk.Label(history_window, text=f"Cliente: {client_data[1]}").grid(row=0, column=0, padx=10, pady=10)
            ttk.Label(history_window, text=f"Contato: {client_data[2]}").grid(row=1, column=0, padx=10, pady=10)

            # Treeview para exibir o histórico dos procedimentos do cliente
            history_tree = ttk.Treeview(history_window, columns=("Data", "Procedimento", "Valor", "Produto"), show="headings")
            history_tree.heading("Data", text="Data")
            history_tree.heading("Procedimento", text="Procedimento")
            history_tree.heading("Valor", text="Valor")
            history_tree.heading("Produto", text="Produto")
            
            # Centralizando o texto nas colunas
            for col in ("Data", "Procedimento", "Valor", "Produto"):
                history_tree.heading(col, anchor="center")  # Centraliza o cabeçalho
                history_tree.column(col, anchor="center")   # Centraliza o conteúdo

            history_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

            # Adiciona o histórico dos procedimentos do cliente na Treeview
            cursor.execute("SELECT procedure_date, procedure, value, product FROM procedures WHERE client_id = ?", (client_id,))
            for procedure in cursor.fetchall():
                history_tree.insert("", "end", values=procedure)
                
            # Entradas para adicionar novo procedimento
            ttk.Label(history_window, text="Novo Procedimento:").grid(row=3, column=0, padx=10, pady=5)
            self.new_procedure_entry = ttk.Entry(history_window)
            self.new_procedure_entry.grid(row=3, column=1, padx=10, pady=5)
            
            ttk.Label(history_window, text="Data:").grid(row=4, column=0, padx=10, pady=5)
            self.new_date_entry = ttk.Entry(history_window)
            self.new_date_entry.grid(row=4, column=1, padx=10, pady=5)
            self.new_date_entry.insert(0, datetime.today().strftime('%d-%m-%Y'))
            
            ttk.Label(history_window, text="Valor:").grid(row=5, column=0, padx=10, pady=5)
            self.new_value_entry = ttk.Entry(history_window)
            self.new_value_entry.grid(row=5, column=1, padx=10, pady=5)
            
            ttk.Label(history_window, text="Produto Utilizado:").grid(row=6, column=0, padx=10, pady=5)
            self.new_product_entry = ttk.Entry(history_window)
            self.new_product_entry.grid(row=6, column=1, padx=10, pady=5)

        # Função para adicionar o novo procedimento ao banco de dados
        def add_procedure():
            procedure = self.new_procedure_entry.get()
            date = self.new_date_entry.get()
            value = self.new_value_entry.get()
            product = self.new_product_entry.get()
            
            # Insere o novo procedimento na tabela procedures
            cursor.execute(
                "INSERT INTO procedures (client_id, procedure_date, procedure, value, product) VALUES (?, ?, ?, ?, ?)",
                (client_id, date, procedure, value, product)
            )
            conn.commit()

            # Atualiza a Treeview com o novo procedimento
            history_tree.insert("", "end", values=(date, procedure, value, product))
            
            # Limpa as entradas após o cadastro do novo procedimento
            self.new_procedure_entry.delete(0, tk.END)
            self.new_date_entry.delete(0, tk.END)
            self.new_value_entry.delete(0, tk.END)
            self.new_product_entry.delete(0, tk.END)

        # Botão para confirmar a adição do novo procedimento
        add_procedure_button = ttk.Button(history_window, text="Adicionar Procedimento", command=add_procedure)
        add_procedure_button.grid(row=7, column=0, columnspan=2, pady=10)

# Inicialização da Aplicação
root = tk.Tk()
app = SalonManagerApp(root)
root.mainloop()
