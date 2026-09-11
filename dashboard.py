import tkinter as tk
import webbrowser
from PIL import Image, ImageTk

from config import PALETTE, MAX_PANELS
from log import info_API
from cache import save_infos, get_infos
from widget import WIDGET_LIST, WIDGET_CLASSES

class Dashboard:

    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard di Prova")
        self.root.geometry("1000x600")

        self.fullscreen = False
        self.root.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.panels = {}
        self.n_panels = 0

        self.FRED_API_KEY = get_infos("fred_api_key")

        # Grid layout for header, body and footer
        root.rowconfigure(0, weight=0, minsize=40) # header
        root.rowconfigure(1, weight=1) # body
        root.columnconfigure(0, weight=1)

        # HEADER
        header = tk.Frame(root, bg=PALETTE[7][0])
        header.grid(row=0, column=0, sticky="nsew")

        inner_header = tk.Frame(header, bg=PALETTE[7][0])
        inner_header.pack(fill="both", expand=True)
        # BODY
        body = tk.Frame(root, bg=PALETTE[1][0])
        body.grid(row=1, column=0, sticky="nsew")

        # HEADER BUTTONS
        self.settings_btn = tk.Button(
            inner_header,
            text="⚙️",
            font=("Arial", 9, "bold"),
            command=lambda: self._settings_popup(),
            bg=PALETTE[2][0],
            width=6,
            height=1,
            borderwidth=1,
            relief="solid"
        )
        self.settings_btn.pack(side=tk.LEFT, fill = "y")

        self.save_btn = tk.Button(
            inner_header,
            text="💾",
            font=("Arial", 9, "bold"),
            bg=PALETTE[2][0],
            width=6,
            height=1,
            borderwidth=1,
            relief="solid"
        )
        self.save_btn.pack(side=tk.RIGHT, fill = "y")

        self.load_btn = tk.Button(
            inner_header,
            text="📂",
            font=("Arial", 9, "bold"),
            bg=PALETTE[2][0],
            width=6,
            height=1,
            borderwidth=1,
            relief="solid"
        )
        self.load_btn.pack(side=tk.RIGHT, fill = "y")
        
        self.fullscreen_btn = tk.Button(
            inner_header,
            text="⛶",
            font=("Arial", 9, "bold"),
            bg=PALETTE[2][0],
            width=6,
            height=1,
            borderwidth=1,
            relief="solid",
            command=self._toggle_fullscreen
        )

        self.fullscreen_btn.pack(side=tk.LEFT, fill="y")

        # HEADER LABEL
        self.current_dashboard = "Default Dashboard"
        self.dash_label = tk.Label(
            inner_header,
            text=self.current_dashboard,
            font=("Arial", 9, "bold"),
            fg=PALETTE[6][0],
            bg=PALETTE[2][0]
        )
        self.dash_label.pack(side=tk.RIGHT, anchor="s", padx=30)

        panel_default = tk.Frame(body, bg=PALETTE[1][0], relief="flat")
        panel_default.pack(fill="both", expand=True)

        panel_default.columnconfigure(0, weight=1)
        panel_default.rowconfigure(0, weight=0, minsize= 30)
        panel_default.rowconfigure(1, weight=20)

        panel_default_head = tk.Frame(panel_default, bg=PALETTE[0][0])
        panel_default_head.grid(row=0, column=0, sticky="nsew")

        panel_default_body = tk.Frame(panel_default, bg=PALETTE[1][0])
        panel_default_body.grid(row=1, column=0, sticky="nsew")

        id_default = self._register_panel(panel_default, header=panel_default_head, body=panel_default_body)
        self.panels[id_default]["children"] = [panel_default_head, panel_default_body]

        hor_icon = Image.open("icons/hor_split.png")
        hor_icon = hor_icon.resize((15, 15))

        self.hor_split_icon = ImageTk.PhotoImage(hor_icon)
        
        btn_hor_split = tk.Button(
            panel_default_head,
            image=self.hor_split_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command=lambda pid=id_default: self._split_panel(pid)
        )
        btn_hor_split.pack(side=tk.RIGHT, padx=10)

        vert_icon = Image.open("icons/vert_split.png")
        vert_icon = vert_icon.resize((15, 15))

        self.vert_split_icon = ImageTk.PhotoImage(vert_icon)
        
        btn_vert_split = tk.Button(
            panel_default_head,
            image=self.vert_split_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command=lambda pid=id_default: self._split_panel(pid, orient="vertical")
        )
        btn_vert_split.pack(side=tk.RIGHT, padx=5)

        btn_default = tk.Button(
            panel_default_body,
            text="📈",
            font=("Arial", 14, "bold"),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            bd=0,
            bg = PALETTE[7][0],
            overrelief="flat",
            width=5,
            height=2,
            command= lambda: self._add_object_popup(id_default)
        )
        btn_default.place(relx=0.5, rely=0.5, anchor="center")

        # WIDGET
        self.objects = WIDGET_LIST

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

        if self.fullscreen:
            self.fullscreen_btn.config(text="🗗")
        else:
            self.fullscreen_btn.config(text="⛶")

    def _settings_popup(self) -> None:
        popup = tk.Toplevel(self.root)
        popup.title("Settings")
        popup.geometry("550x300")
        popup.transient(self.root)
        popup.grab_set()

        popup.rowconfigure(0, weight=0, minsize=30)  # Header
        popup.rowconfigure(1, weight=10)  # Upper body
        popup.rowconfigure(2, weight=10)  # Lower body
        popup.rowconfigure(3, weight=0, minsize=30)  # Footer
        popup.columnconfigure(0, weight=1)

        self.API_entry = tk.Entry(popup)
        self.API_entry.insert(0, self.FRED_API_KEY if self.FRED_API_KEY is not None else "")
        self.API_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        tk.Label(popup, text="Insert your FRED API key").grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        tk.Label(popup, text=info_API).grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        tk.Button(
        popup,
        text="Add",
        width=10,
        relief="flat",
        bg=PALETTE[7][0],
        activebackground=PALETTE[2][0],
        overrelief="flat",
        highlightthickness=0,
        bd=0,
        command=lambda: self._add_key(popup)
        ).grid(row=3, column=0, sticky="e", padx=20)

        tk.Button(
        popup,
        text="Get your API key",
        width=20,
        relief="flat",
        bg=PALETTE[7][0],
        activebackground=PALETTE[2][0],
        overrelief="flat",
        highlightthickness=0,
        bd=0,
        command=lambda: webbrowser.open("https://fred.stlouisfed.org/docs/api/api_key.html")
        ).grid(row=3, column=0, sticky="w", padx=20)
    
    def _add_key(self, popup: tk.Toplevel) -> None:
        new_api = self.API_entry.get()
        self.FRED_API_KEY = new_api
        save_infos("fred_api_key", new_api)
        popup.destroy()

    def _add_object_popup(self, panel_id: str) -> None:
        popup = tk.Toplevel(self.root)
        popup.title("Object selection")
        popup.geometry("500x300")
        popup.transient(self.root)
        popup.grab_set()

        # POPUP GRID
        popup.rowconfigure(0, weight=2)  # Header
        popup.rowconfigure(1, weight=10)  # Upper body
        popup.rowconfigure(2, weight=15)  # Lower body
        popup.rowconfigure(3, weight=3)  # Footer
        popup.columnconfigure(0, weight=1)

        tk.Label(popup, text="Select an object to add to the panel:").grid(row=0, column=0, padx=20)

        tk.Button(
        popup,
        text="Close",
        width=10,
        relief="flat",
        bg=PALETTE[7][0],
        activebackground=PALETTE[2][0],
        overrelief="flat",
        highlightthickness=0,
        bd=0,
        command=popup.destroy,
        ).grid(row=3, column=0, sticky="w", padx=20)
    
        self.entry = tk.Entry(popup)
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.entry.bind("<KeyRelease>", self._autocomplete)

        self.listbox = tk.Listbox(popup)
        self.listbox.grid(row=2, column=0, padx=20, pady=10)

        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        tk.Button(
        popup,
        text="Add",
        width=10,
        relief="flat",
        bg=PALETTE[7][0],
        activebackground=PALETTE[2][0],
        overrelief="flat",
        highlightthickness=0,
        bd=0,
        command=lambda: self._add_object(self.entry.get(), panel_id, popup=popup)
        ).grid(row=3, column=0, sticky="e", padx=20)

    
    def _autocomplete(self, event) -> None:
        typed = self.entry.get().lower()
        self.listbox.delete(0, tk.END)

        if typed == "":
            return
        
        for obj in self.objects:
            if typed in obj.lower():
                self.listbox.insert(tk.END, obj)
    
    def _on_select(self, event) -> None:
        selected = self.listbox.curselection()

        if not selected:
            return
        
        selection = self.listbox.get(selected[0])

        self.entry.delete(0, tk.END)
        self.entry.insert(0, selection)

        self.listbox.delete(0, tk.END)
    
    def _add_object(self, name: str, panel_id: str, save = True, popup = None, autorun = False):
        panel = self.panels[panel_id]["body"]

        for child in panel.winfo_children():
            child.destroy()
        
        state = self.panels[panel_id].get("content") or {}

        if popup is not None:
            state =  {"type": name}
        
        widget_class = WIDGET_CLASSES[name]

        widget = widget_class(
            panel,
            state=state,
            autorun=autorun
        )
        widget.pack(fill="both", expand=True)

        if save:
            self.panels[panel_id]["content"] = widget.get_state()

        if popup is not None:
            popup.destroy()
    
    def _split_panel(self, panel_id, orient: str = "horizontal") -> None:
        
        if len(self.panels) + 1 > MAX_PANELS:
            self._limit_popup()
            return
        
        old_panel = self.panels[panel_id]["frame"]

        old_data = self.panels[panel_id]
        old_panel._parent_pane = old_data["parent_pane"]
        old_panel._container = old_data["container"]
        old_panel._level = old_data["level"]

        for child in old_panel.winfo_children():
            child.destroy()

        del self.panels[panel_id]
        
        new_pane = tk.PanedWindow(old_panel, orient=orient, sashwidth=2)
        new_pane.pack(fill="both", expand=True)

        panel_1 = tk.Frame(new_pane, bg=PALETTE[1][0], relief="flat")
        panel_2 = tk.Frame(new_pane, bg=PALETTE[1][0], relief="flat")

        panel_1.columnconfigure(0, weight=1)
        panel_1.rowconfigure(0, weight=0, minsize=26)
        panel_1.rowconfigure(1, weight=1)
        panel_2.columnconfigure(0, weight=1)
        panel_2.rowconfigure(0, weight=0, minsize=26)
        panel_2.rowconfigure(1, weight=1)
        
        head_1 = tk.Frame(panel_1, bg=PALETTE[0][0]) # Header panel 1
        head_1.grid(row=0, column=0, sticky="nsew")
        head_2 = tk.Frame(panel_2, bg=PALETTE[0][0]) # Header panel 2
        head_2.grid(row=0, column=0, sticky="nsew")
        body_1 = tk.Frame(panel_1, bg=PALETTE[1][0]) # Body panel 1
        body_1.grid(row=1, column=0, sticky="nsew")
        body_2 = tk.Frame(panel_2, bg=PALETTE[1][0]) # Body panel 2
        body_2.grid(row=1, column=0, sticky="nsew")

        new_pane.add(panel_1, minsize = 150)
        new_pane.add(panel_2, minsize = 150)

        id1 = self._register_panel(panel_1, new_pane, head_1, body_1, old_panel)
        id2 = self._register_panel(panel_2, new_pane, head_2, body_2, old_panel)

        for id in [id1, id2]:
            child_list = []
            for child in self.panels[id]["frame"].winfo_children():
                child_list.append(child)
            self.panels[id]["children"] = child_list
        
        self._add_header_button(id1)
        self._add_body_button(id1)
        self._add_header_button(id2)
        self._add_body_button(id2)

    def _add_header_button(self, id) -> None:
        head = self.panels[id]["header"]

        split_hor = tk.Button(
            head,
            image=self.hor_split_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command=lambda: self._split_panel(id, "horizontal")
        )
        split_hor.pack(side=tk.RIGHT, padx=10)
        split_vert = tk.Button(
            head,
            image=self.vert_split_icon,
            relief="flat",
            bg=PALETTE[0][0],
            activebackground=PALETTE[2][0],
            overrelief="flat",
            highlightthickness=0,
            command=lambda: self._split_panel(id, "vertical")
        )
        split_vert.pack(side=tk.RIGHT, padx=5)
        delete = tk.Button(
            head,
            text="✕",
            relief="flat",
            fg=PALETTE[6][0],
            bg=PALETTE[0][0],
            activebackground=PALETTE[4][0],
            overrelief="flat",
            highlightthickness=0,
            command=lambda: self._delete_panel(id)
        )
        delete.pack(side=tk.LEFT, padx=10)
        self._add_hover_effect(delete,PALETTE[0][0],PALETTE[4][0])

    def _add_body_button(self, id) -> None:
        present_panel = self.panels[id]["body"]
        body_btn = tk.Button(
            present_panel,
            text="📈",
            font=("Arial", 14, "bold"),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            bd=0,
            bg = PALETTE[7][0],
            overrelief="flat",
            width=5,
            height=2,
            command=lambda: self._add_object_popup(id)
        )
        body_btn.place(relx=0.5, rely=0.5, anchor="center")

    def _register_panel(self, frame, parent_pane=None, header=None, body=None, container=None, level=None) -> str:
        self.n_panels += 1
        panel_id = f"panel_{self.n_panels}"

        if level is None:
            level = 0

        self.panels[panel_id]={
            "frame": frame,
            "parent_pane": parent_pane,
            "header": header,
            "body" : body,
            "children": [],
            "content": None,
            "level": level,
            "container": container
        }

        frame.panel_id = panel_id
        return panel_id

    def _delete_panel(self, panel_id):
        panel_data = self.panels[panel_id]

        panel = panel_data["frame"]
        parent_pane = panel_data["parent_pane"]
        container = panel_data["container"]

        if parent_pane is None:
            return

        panes = parent_pane.panes()
        sibling_path = [p for p in panes if p != str(panel)][0]
        sibling = self.root.nametowidget(sibling_path)
        sibling_id = sibling.panel_id

        self._save_panel_content(sibling_id)
        sibling_data = self.panels[sibling_id].copy()

        for child in container.winfo_children():
            child.destroy()

        self.panels.pop(panel_id, None)
        self.panels.pop(sibling_id, None)

        new_id = self._create_panel_from_data(container, sibling_data)

        return new_id
    
    def _create_panel_from_data(self, container, data):
        panel = container

        for child in panel.winfo_children():
            child.destroy()

        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(0, weight=0, minsize=26)
        panel.rowconfigure(1, weight=1)

        header = tk.Frame(panel, bg=PALETTE[0][0])
        header.grid(row=0, column=0, sticky="nsew")

        body = tk.Frame(panel, bg=PALETTE[1][0])
        body.grid(row=1, column=0, sticky="nsew")

        new_id = self._register_panel(
            panel,
            parent_pane=getattr(container, "_parent_pane", None),
            header=header,
            body=body,
            container=getattr(container, "_container", None),
            level=max((data.get("level") or 0) - 1, 0)
        )

        self.panels[new_id]["content"] = data.get("content")

        self._add_header_button(new_id)
        self._render_panel_content(new_id)

        return new_id

    def _render_panel_content(self, panel_id):
        content = self.panels[panel_id]["content"]
        body = self.panels[panel_id]["body"]

        if content is None:
            self._add_body_button(panel_id)
            return

        for child in body.winfo_children():
            child.destroy()

        self._add_object(content["type"], panel_id, save = False, autorun=True)

    def _limit_popup(self) -> None:
        popup = tk.Toplevel(self.root)
        popup.title("Panels Limit")
        popup.geometry("300x120")
        popup.transient(self.root)
        popup.grab_set()
        tk.Label(
            popup,
            text=f"You have reached the limit of {MAX_PANELS} panels!.",
            padx=20,
            pady=20
        ).pack()

        tk.Button(
            popup,
            text="OK",
            command=popup.destroy
        ).pack()

    def _save_panel_content(self, panel_id):
        body = self.panels[panel_id]["body"]

        for child in body.winfo_children():
            if hasattr(child, "get_state"):
                self.panels[panel_id]["content"] = child.get_state()
                return

        self.panels[panel_id]["content"] = None

    def _add_hover_effect(self, widget, normal_bg, hover_bg):
        widget.bind("<Enter>", lambda event: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda event: widget.config(bg=normal_bg))

    def _dividend_calendar(self) -> None:
        pass
    
    
    
        