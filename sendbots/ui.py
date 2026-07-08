from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from sendbots.config import ConfigStore, database_path, logs_dir, mask_token
from sendbots.models import AppConfig, FileGroup, MIN_SCAN_INTERVAL_SECONDS
from sendbots.sender import SenderService
from sendbots.storage import HistoryStore
from sendbots.tray import TrayController
from sendbots.watcher import scan_folder


LOGGER = logging.getLogger(__name__)


class SendBotsApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SendBots")
        self.geometry("1120x720")
        self.minsize(980, 620)

        self.config_store = ConfigStore()
        self.history = HistoryStore()
        self.app_config = self.config_store.load()
        self.monitoring = False
        self.worker_running = False
        self.message_queue: queue.Queue[str] = queue.Queue()
        self.exiting = False
        self.tray = TrayController(self._restore_from_tray_threadsafe, self._quit_from_tray_threadsafe)

        self._build_variables()
        self._build_layout()
        self._load_config_into_form()
        self._refresh_history()
        self._poll_messages()
        self.bind("<Unmap>", self._on_unmap)
        self.protocol("WM_DELETE_WINDOW", self._on_close_request)

    def _build_variables(self) -> None:
        self.api_base_url_var = tk.StringVar()
        self.token_var = tk.StringVar()
        self.folder_var = tk.StringVar()
        self.interval_var = tk.IntVar(value=MIN_SCAN_INTERVAL_SECONDS)
        self.user_id_var = tk.StringVar()
        self.queue_id_var = tk.StringVar()
        self.timeout_var = tk.IntVar(value=30)
        self.retries_var = tk.IntVar(value=3)
        self.send_signature_var = tk.BooleanVar(value=False)
        self.close_ticket_var = tk.BooleanVar(value=False)
        self.require_pair_var = tk.BooleanVar(value=True)
        self.send_together_var = tk.BooleanVar(value=True)
        self.merge_pdfs_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Parado")
        self.next_scan_var = tk.StringVar(value="-")

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(12, 10, 12, 6))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Status:").grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.status_var).grid(row=0, column=1, sticky="w", padx=(6, 16))
        ttk.Label(header, text="Proxima varredura:").grid(row=0, column=2, sticky="e")
        ttk.Label(header, textvariable=self.next_scan_var).grid(row=0, column=3, sticky="w", padx=(6, 0))

        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)

        self.config_tab = ttk.Frame(notebook, padding=12)
        self.operation_tab = ttk.Frame(notebook, padding=12)
        self.history_tab = ttk.Frame(notebook, padding=12)
        notebook.add(self.config_tab, text="Configuracao")
        notebook.add(self.operation_tab, text="Operacao")
        notebook.add(self.history_tab, text="Historico")

        self._build_config_tab()
        self._build_operation_tab()
        self._build_history_tab()

    def _build_config_tab(self) -> None:
        frame = self.config_tab
        frame.columnconfigure(1, weight=1)

        row = 0
        ttk.Label(frame, text="URL base").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.api_base_url_var).grid(row=row, column=1, sticky="ew", pady=4)

        row += 1
        ttk.Label(frame, text="Token Bearer").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.token_var, show="*").grid(row=row, column=1, sticky="ew", pady=4)

        row += 1
        ttk.Label(frame, text="Pasta monitorada").grid(row=row, column=0, sticky="w", pady=4)
        folder_line = ttk.Frame(frame)
        folder_line.grid(row=row, column=1, sticky="ew", pady=4)
        folder_line.columnconfigure(0, weight=1)
        ttk.Entry(folder_line, textvariable=self.folder_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(folder_line, text="Selecionar", command=self._select_folder).grid(row=0, column=1, padx=(6, 0))

        row += 1
        ttk.Label(frame, text="Mensagem").grid(row=row, column=0, sticky="nw", pady=4)
        self.message_text = tk.Text(frame, height=5, wrap="word")
        self.message_text.grid(row=row, column=1, sticky="ew", pady=4)

        row += 1
        numbers = ttk.Frame(frame)
        numbers.grid(row=row, column=1, sticky="ew", pady=4)
        for idx in range(8):
            numbers.columnconfigure(idx, weight=1)
        ttk.Label(frame, text="Parametros").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Label(numbers, text="Intervalo").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(numbers, from_=10, to=86400, textvariable=self.interval_var, width=8).grid(row=0, column=1, sticky="w")
        ttk.Label(numbers, text="Timeout").grid(row=0, column=2, sticky="w", padx=(12, 0))
        ttk.Spinbox(numbers, from_=1, to=600, textvariable=self.timeout_var, width=8).grid(row=0, column=3, sticky="w")
        ttk.Label(numbers, text="Tentativas").grid(row=0, column=4, sticky="w", padx=(12, 0))
        ttk.Spinbox(numbers, from_=0, to=20, textvariable=self.retries_var, width=8).grid(row=0, column=5, sticky="w")

        row += 1
        ttk.Label(frame, text="IDs opcionais").grid(row=row, column=0, sticky="w", pady=4)
        ids = ttk.Frame(frame)
        ids.grid(row=row, column=1, sticky="ew", pady=4)
        ids.columnconfigure(1, weight=1)
        ids.columnconfigure(3, weight=1)
        ttk.Label(ids, text="userId").grid(row=0, column=0, sticky="w")
        ttk.Entry(ids, textvariable=self.user_id_var).grid(row=0, column=1, sticky="ew", padx=(6, 12))
        ttk.Label(ids, text="queueId").grid(row=0, column=2, sticky="w")
        ttk.Entry(ids, textvariable=self.queue_id_var).grid(row=0, column=3, sticky="ew", padx=(6, 0))

        row += 1
        ttk.Label(frame, text="Opcoes").grid(row=row, column=0, sticky="nw", pady=4)
        opts = ttk.Frame(frame)
        opts.grid(row=row, column=1, sticky="ew", pady=4)
        ttk.Checkbutton(opts, text="Assinar mensagem", variable=self.send_signature_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Encerrar ticket", variable=self.close_ticket_var).grid(row=0, column=1, sticky="w", padx=(16, 0))
        ttk.Checkbutton(opts, text="Aguardar nota + boleto", variable=self.require_pair_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Enviar anexos juntos", variable=self.send_together_var).grid(row=1, column=1, sticky="w", padx=(16, 0))
        ttk.Checkbutton(opts, text="Juntar nota e boleto em um PDF", variable=self.merge_pdfs_var).grid(row=2, column=0, columnspan=2, sticky="w")

        row += 1
        actions = ttk.Frame(frame)
        actions.grid(row=row, column=1, sticky="e", pady=(12, 0))
        ttk.Button(actions, text="Salvar", command=self._save_config).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(actions, text="Validar", command=self._validate_config_message).grid(row=0, column=1)

    def _build_operation_tab(self) -> None:
        frame = self.operation_tab
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        actions = ttk.Frame(frame)
        actions.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(actions, text="Iniciar monitoramento", command=self._start_monitoring).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(actions, text="Parar", command=self._stop_monitoring).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(actions, text="Executar varredura agora", command=self._scan_now).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(actions, text="Abrir pasta", command=self._open_folder).grid(row=0, column=3)

        self.log_text = tk.Text(frame, height=18, wrap="word", state="disabled")
        self.log_text.grid(row=1, column=0, sticky="nsew")

    def _build_history_tab(self) -> None:
        frame = self.history_tab
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("created_at", "whatsapp", "status", "detail")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.history_tree.heading("created_at", text="Data")
        self.history_tree.heading("whatsapp", text="WhatsApp")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("detail", text="Detalhe")
        self.history_tree.column("created_at", width=150, stretch=False)
        self.history_tree.column("whatsapp", width=150, stretch=False)
        self.history_tree.column("status", width=100, stretch=False)
        self.history_tree.column("detail", width=640, stretch=True)
        self.history_tree.grid(row=0, column=0, sticky="nsew")

        buttons = ttk.Frame(frame)
        buttons.grid(row=1, column=0, sticky="e", pady=(8, 0))
        ttk.Button(buttons, text="Atualizar", command=self._refresh_history).grid(row=0, column=0)

    def _load_config_into_form(self) -> None:
        config = self.app_config
        self.api_base_url_var.set(config.api_base_url)
        self.token_var.set(config.token)
        self.folder_var.set(config.watched_folder)
        self.interval_var.set(config.scan_interval_seconds)
        self.user_id_var.set(config.user_id)
        self.queue_id_var.set(config.queue_id)
        self.timeout_var.set(config.timeout_seconds)
        self.retries_var.set(config.max_retries)
        self.send_signature_var.set(config.send_signature)
        self.close_ticket_var.set(config.close_ticket)
        self.require_pair_var.set(config.require_pair)
        self.send_together_var.set(config.send_files_together)
        self.merge_pdfs_var.set(config.merge_pdfs_before_send)
        self.message_text.delete("1.0", tk.END)
        self.message_text.insert("1.0", config.message_body)

    def _config_from_form(self) -> AppConfig:
        return AppConfig(
            api_base_url=self.api_base_url_var.get().strip(),
            token=self.token_var.get().strip(),
            watched_folder=self.folder_var.get().strip(),
            scan_interval_seconds=max(int(self.interval_var.get()), MIN_SCAN_INTERVAL_SECONDS),
            message_body=self.message_text.get("1.0", tk.END).strip(),
            user_id=self.user_id_var.get().strip(),
            queue_id=self.queue_id_var.get().strip(),
            send_signature=bool(self.send_signature_var.get()),
            close_ticket=bool(self.close_ticket_var.get()),
            timeout_seconds=int(self.timeout_var.get()),
            max_retries=int(self.retries_var.get()),
            require_pair=bool(self.require_pair_var.get()),
            send_files_together=bool(self.send_together_var.get()),
            merge_pdfs_before_send=bool(self.merge_pdfs_var.get()),
        )

    def _select_folder(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.folder_var.set(selected)

    def _save_config(self) -> bool:
        config = self._config_from_form()
        errors = config.validate()
        if errors:
            messagebox.showerror("Configuracao invalida", "\n".join(errors))
            return False
        self.config_store.save(config)
        self.app_config = config
        self._append_log(f"Configuracao salva. Token: {mask_token(config.token)}")
        messagebox.showinfo("Configuracao", "Configuracao salva com sucesso.")
        return True

    def _validate_config_message(self) -> None:
        config = self._config_from_form()
        errors = config.validate()
        if errors:
            messagebox.showerror("Configuracao invalida", "\n".join(errors))
            return
        messagebox.showinfo("Configuracao", "Configuracao valida.")

    def _start_monitoring(self) -> None:
        if not self._save_config():
            return
        self.monitoring = True
        self.status_var.set("Monitorando")
        self._append_log("Monitoramento iniciado.")
        self._schedule_next_scan(0)

    def _stop_monitoring(self) -> None:
        self.monitoring = False
        self.next_scan_var.set("-")
        self.status_var.set("Parado")
        self._append_log("Monitoramento parado.")

    def _scan_now(self) -> None:
        if not self._save_config():
            return
        self._run_scan_async()

    def _schedule_next_scan(self, delay_ms: int | None = None) -> None:
        if not self.monitoring:
            return
        seconds = self.app_config.scan_interval_seconds
        if delay_ms is None:
            delay_ms = seconds * 1000
        self.next_scan_var.set(f"em {max(delay_ms // 1000, 0)}s")
        self.after(delay_ms, self._monitor_tick)

    def _monitor_tick(self) -> None:
        if not self.monitoring:
            return
        self._run_scan_async()
        self._schedule_next_scan()

    def _run_scan_async(self) -> None:
        if self.worker_running:
            self._append_log("Varredura ignorada: envio anterior ainda em execucao.")
            return
        self.worker_running = True
        thread = threading.Thread(target=self._scan_and_send_worker, daemon=True)
        thread.start()

    def _scan_and_send_worker(self) -> None:
        try:
            folder = Path(self.app_config.watched_folder)
            groups, invalid, skipped = scan_folder(folder)
            self.message_queue.put(
                "Varredura: "
                f"{len(groups)} grupo(s), {len(invalid)} invalido(s), {len(skipped)} ja enviado(s). "
                f"Aguardar par: {'sim' if self.app_config.require_pair else 'nao'}. "
                f"Enviar anexos juntos: {'sim' if self.app_config.send_files_together else 'nao'}. "
                f"Juntar PDFs: {'sim' if self.app_config.merge_pdfs_before_send else 'nao'}."
            )
            for path in invalid:
                detail = (
                    "Nome fora do padrao esperado. Use "
                    "Nfe[NumeroNota]_[WhatsApp]_[ChaveAcesso].pdf ou "
                    "Boleto[NumeroBoleto]_[WhatsApp]_[CodigoBarras].pdf."
                )
                self.message_queue.put(f"Arquivo invalido ignorado: {path}. {detail}")
                self.history.add("", [str(path)], "invalid", detail)
            for path in skipped:
                self.message_queue.put(f"Arquivo ja marcado como enviado ignorado: {path.name}")

            service = SenderService(self.app_config, self.history)
            for group in groups:
                self._process_group(service, group)
            self.message_queue.put("__REFRESH_HISTORY__")
        except Exception as exc:  # noqa: BLE001 - keep UI alive.
            LOGGER.exception("Erro na varredura")
            self.message_queue.put(f"Erro na varredura: {exc}")
        finally:
            self.worker_running = False

    def _process_group(self, service: SenderService, group: FileGroup) -> None:
        names = ", ".join(item.path.name for item in group.files)
        self.message_queue.put(
            f"Processando {group.whatsapp}: {names}. "
            f"Notas: {len(group.notes)}. Boletos: {len(group.boletos)}."
        )
        result = service.process_group(group)
        if result.success:
            self.message_queue.put(f"Enviado para {group.whatsapp}.")
        else:
            detail = result.error or result.response_body or "Item ignorado."
            self.message_queue.put(f"Nao enviado para {group.whatsapp}: {detail}")

    def _poll_messages(self) -> None:
        while True:
            try:
                message = self.message_queue.get_nowait()
            except queue.Empty:
                break
            if message == "__REFRESH_HISTORY__":
                self._refresh_history()
            elif message == "__RESTORE_WINDOW__":
                self._restore_from_tray()
            elif message == "__QUIT_APPLICATION__":
                self._quit_application()
            else:
                self._append_log(message)
        self.after(250, self._poll_messages)

    def _append_log(self, message: str) -> None:
        LOGGER.info(message)
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def _refresh_history(self) -> None:
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        for entry in self.history.latest():
            self.history_tree.insert(
                "",
                "end",
                values=(
                    entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    entry.whatsapp,
                    entry.status,
                    entry.detail,
                ),
            )

    def _open_folder(self) -> None:
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("Pasta", "Configure a pasta monitorada.")
            return
        path = Path(folder)
        if not path.exists():
            messagebox.showwarning("Pasta", "A pasta configurada nao existe.")
            return
        try:
            if self.tk.call("tk", "windowingsystem") == "win32":
                import os

                os.startfile(path)  # type: ignore[attr-defined]
            elif self.tk.call("tk", "windowingsystem") == "aqua":
                import subprocess

                subprocess.Popen(["open", str(path)])
            else:
                import subprocess

                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:  # noqa: BLE001 - user-facing operational error.
            messagebox.showerror("Pasta", f"Nao foi possivel abrir a pasta: {exc}")

    def _on_unmap(self, _event: tk.Event) -> None:
        if self.exiting:
            return
        self.after(100, self._hide_if_iconified)

    def _hide_if_iconified(self) -> None:
        if not self.exiting and self.state() == "iconic":
            self._hide_to_tray()

    def _hide_to_tray(self) -> None:
        if self.exiting:
            return
        if self.tray.start():
            self.withdraw()
            self._append_log("SendBots continua em background na area de notificacao.")
        else:
            self.iconify()
            self._append_log(
                "Nao foi possivel usar a area de notificacao. "
                "Instale as dependencias com ./scripts/run_local_linux.sh ou gere o executavel novamente."
            )

    def _on_close_request(self) -> None:
        should_close = messagebox.askyesno(
            "Fechar SendBots",
            "Deseja fechar o programa?\n\n"
            "Selecione Sim para encerrar o SendBots.\n"
            "Selecione Nao para manter rodando em background.",
        )
        if should_close:
            self._quit_application()
            return
        self._hide_to_tray()

    def _restore_from_tray_threadsafe(self) -> None:
        self.message_queue.put("__RESTORE_WINDOW__")

    def _restore_from_tray(self) -> None:
        if self.exiting:
            return
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()
        self._append_log("Janela restaurada pela area de notificacao.")

    def _quit_from_tray_threadsafe(self) -> None:
        self.message_queue.put("__QUIT_APPLICATION__")

    def _quit_application(self) -> None:
        self.exiting = True
        self.monitoring = False
        self.tray.stop()
        self.destroy()


def show_runtime_locations() -> str:
    return f"Banco: {database_path()}\nLogs: {logs_dir()}"
