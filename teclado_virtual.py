import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser, ttk
from utils import load_config, save_config, send_return


# ======================= CONFIG VISUAL ======================
BTN_WIDTH = 8
BTN_HEIGHT = 1
BTN_FONT = ("Segoe UI", 8)
TITLE_FONT = ("Segoe UI", 11)
LAYOUTS_DIR = os.path.join(os.path.dirname(__file__), "layouts")


# ======================= TOOLTIP (DICA DE TECLA) ======================
class ToolTip:
    """Exibe uma dica (tooltip) quando o mouse passa sobre o botão."""

    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text or ""
        self.tip_window = None

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return

        # posição do mouse na tela
        if event is not None:
            x = event.x_root + 10
            y = event.y_root + 10
        else:
            x = self.widget.winfo_rootx() + 40
            y = self.widget.winfo_rooty() + 30

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=5, ipady=3)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None



# ======================= JANELA PRINCIPAL ======================
class TecladoVirtual(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teclado Virtual Programável")
        self.geometry("855x350")
        self.resizable(True, True)

        # carregar layout inicial
        self.layout_atual = "pdv_principal.json"
        self.cfg = self._carregar_layout(self.layout_atual)

        # cabeçalho
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(top, text="Layout:", font=TITLE_FONT).pack(side=tk.LEFT, padx=(0, 5))
        self.combo_layouts = ttk.Combobox(top, state="readonly", width=30)
        self._atualizar_lista_layouts()
        self.combo_layouts.set(self.layout_atual)
        self.combo_layouts.pack(side=tk.LEFT)
        self.combo_layouts.bind("<<ComboboxSelected>>", self._trocar_layout)

        self.btn_editar = tk.Button(top, text="⚙️ Editar Layout", command=self._abrir_editor)
        self.btn_editar.pack(side=tk.RIGHT, padx=5)

        self.btn_teste = tk.Button(top, text="Teste retorno", command=self._teste)
        self.btn_teste.pack(side=tk.RIGHT, padx=5)

        # grid de botões
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._montar_botoes()

        # rodapé
        self.lbl_descricao = tk.Label(self, text="", fg="#333", font=("Segoe UI", 9))
        self.lbl_descricao.pack(pady=(0, 5))

        rodape = tk.Label(
            self,
            text="Passe o mouse sobre uma tecla para ver a descrição | Clique para enviar o retorno à janela alvo",
            fg="#555"
        )
        rodape.pack(pady=(0, 8))

    # ============ LAYOUT E ARQUIVOS ============
    def _atualizar_lista_layouts(self):
        arquivos = [f for f in os.listdir(LAYOUTS_DIR) if f.endswith(".json")]
        self.combo_layouts["values"] = arquivos

    def _carregar_layout(self, nome_arquivo):
        caminho = os.path.join(LAYOUTS_DIR, nome_arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def _salvar_layout(self):
        caminho = os.path.join(LAYOUTS_DIR, self.layout_atual)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=2)

    def _trocar_layout(self, event=None):
        self.layout_atual = self.combo_layouts.get()
        self.cfg = self._carregar_layout(self.layout_atual)
        self._montar_botoes()
        self.lbl_descricao.config(text="")

    # ============ CONSTRUÇÃO DOS BOTÕES ============
    def _montar_botoes(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        linhas = int(self.cfg.get('linhas', 3))
        colunas = int(self.cfg.get('colunas', 4))
        teclas = self.cfg.get('teclas', [])

        r = c = 0
        for t in teclas:
            nome = t.get('nome', '—')
            retorno = t.get('retorno', '')
            cor = t.get('cor', '#dddddd')
            descricao = t.get('descricao', '')

            btn = tk.Button(
                self.grid_frame,
                text=nome,
                width=BTN_WIDTH,
                height=BTN_HEIGHT,
                bg=cor,
                fg='white',
                activebackground=cor,
                font=BTN_FONT,
                command=lambda rtr=retorno, nm=nome: self._enviar(nm, rtr)
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

            # tooltip + descrição no rodapé
            tooltip = ToolTip(btn, descricao)

            btn.bind(
                "<Enter>",
                lambda e, d=descricao, tt=tooltip: (
                    self._mostrar_descricao(d),
                    tt.show_tip(e)
                ),
                add="+"
            )
            btn.bind(
                "<Leave>",
                lambda e, tt=tooltip: (
                    self.lbl_descricao.config(text=""),
                    tt.hide_tip(e)
                ),
                add="+"
            )


            c += 1
            if c >= colunas:
                c = 0
                r += 1

    def _mostrar_descricao(self, texto):
        self.lbl_descricao.config(text=texto)

    # ============ FUNCIONALIDADE ============
    def _enviar(self, nome, retorno):
        try:
            send_return(retorno)
        except Exception as e:
            messagebox.showerror("Erro ao enviar", f"Tecla: {nome}\nRetorno: {retorno}\n\n{e}")

    def _teste(self):
        messagebox.showinfo("Teste", "Foque a janela alvo e clique em uma tecla para ver o retorno digitado.")

    def _abrir_editor(self):
        EditorLayout(self)

    def recarregar_layout(self):
        self.cfg = self._carregar_layout(self.layout_atual)
        self._montar_botoes()


# ======================= EDITOR DE LAYOUT ======================
class EditorLayout(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Editor de Layout")
        self.geometry("720x520")
        self.resizable(False, False)
        self.master = master
        self.cfg = master.cfg

        tk.Label(self, text=f"Editando: {self.cfg.get('layout','Sem nome')}", font=TITLE_FONT).pack(pady=8)

        frame_cfg = tk.Frame(self)
        frame_cfg.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(frame_cfg, text="Janela Alvo:").grid(row=0, column=0, sticky="w")
        self.entry_janela = tk.Entry(frame_cfg, width=40)
        self.entry_janela.insert(0, self.cfg.get("janela_alvo", ""))
        self.entry_janela.grid(row=0, column=1, padx=5)

        tk.Label(frame_cfg, text="Linhas:").grid(row=1, column=0, sticky="w")
        self.spin_linhas = tk.Spinbox(frame_cfg, from_=1, to=10, width=5)
        self.spin_linhas.delete(0, tk.END)
        self.spin_linhas.insert(0, self.cfg.get("linhas", 3))
        self.spin_linhas.grid(row=1, column=1, sticky="w")

        tk.Label(frame_cfg, text="Colunas:").grid(row=1, column=2, sticky="w", padx=(10, 0))
        self.spin_colunas = tk.Spinbox(frame_cfg, from_=1, to=10, width=5)
        self.spin_colunas.delete(0, tk.END)
        self.spin_colunas.insert(0, self.cfg.get("colunas", 4))
        self.spin_colunas.grid(row=1, column=3, sticky="w")

        # lista de teclas
        self.listbox = tk.Listbox(self, height=12, font=("Segoe UI", 10))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self._carregar_lista()

        # botões
        frame_btns = tk.Frame(self)
        frame_btns.pack(pady=5)

        tk.Button(frame_btns, text="➕ Adicionar", command=self._adicionar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="✏️ Editar", command=self._editar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="🗑️ Excluir", command=self._excluir).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="💾 Salvar", command=self._salvar).pack(side=tk.LEFT, padx=5)

    def _carregar_lista(self):
        self.listbox.delete(0, tk.END)
        for t in self.cfg.get("teclas", []):
            desc = t.get("descricao", "")
            self.listbox.insert(tk.END, f"{t['nome']}  →  {t['retorno']} ({desc})")

    def _adicionar(self):
        nome = simpledialog.askstring("Nova tecla", "Nome da tecla:")
        if not nome:
            return
        retorno = simpledialog.askstring("Nova tecla", "Retorno (ex.: ESC[13~ ou CTRL+F):")
        if not retorno:
            return
        descricao = simpledialog.askstring("Nova tecla", "Descrição da função:")
        cor = colorchooser.askcolor(title="Escolher cor da tecla")[1] or "#007bff"

        self.cfg["teclas"].append({
            "nome": nome,
            "retorno": retorno,
            "cor": cor,
            "descricao": descricao or ""
        })
        self._carregar_lista()

    def _editar(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showinfo("Editar tecla", "Selecione uma tecla.")
            return
        i = idx[0]
        tecla = self.cfg["teclas"][i]

        novo_nome = simpledialog.askstring("Editar tecla", "Novo nome:", initialvalue=tecla["nome"])
        novo_retorno = simpledialog.askstring("Editar tecla", "Novo retorno:", initialvalue=tecla["retorno"])
        nova_descricao = simpledialog.askstring("Editar tecla", "Nova descrição:", initialvalue=tecla.get("descricao", ""))
        nova_cor = colorchooser.askcolor(title="Escolher nova cor")[1] or tecla["cor"]

        self.cfg["teclas"][i] = {
            "nome": novo_nome or tecla["nome"],
            "retorno": novo_retorno or tecla["retorno"],
            "cor": nova_cor,
            "descricao": nova_descricao or ""
        }
        self._carregar_lista()

    def _excluir(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showinfo("Excluir tecla", "Selecione uma tecla.")
            return
        i = idx[0]
        nome = self.cfg["teclas"][i]["nome"]
        if messagebox.askyesno("Excluir", f"Deseja excluir '{nome}'?"):
            del self.cfg["teclas"][i]
            self._carregar_lista()

    def _salvar(self):
        self.cfg["janela_alvo"] = self.entry_janela.get()
        self.cfg["linhas"] = int(self.spin_linhas.get())
        self.cfg["colunas"] = int(self.spin_colunas.get())

        caminho = os.path.join(LAYOUTS_DIR, self.master.layout_atual)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Salvo", "Layout atualizado com sucesso!")
        self.master.recarregar_layout()
