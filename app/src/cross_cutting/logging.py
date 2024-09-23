import json
import logging
from typing import Any, Callable, Dict, List, Optional
import time

class TraceLogger:
    """Classe Singleton que gerencia o rastreamento de métodos."""
    _instance: Optional['TraceLogger'] = None

    def __new__(cls) -> 'TraceLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.execution_tree: List[Dict[str, Any]] = []
        return cls._instance

    def add_to_tree(self, class_name: str, method_name: str, args: Any, result: Any, duration: float, log_entry: str, log_exit: str) -> None:
        """Adiciona detalhes do método à árvore de execução."""
        node = {
            "class": class_name,
            "method": method_name,
            "args": args,
            "result": result,
            "duration": duration,
            "logs": [log_entry, log_exit]
        }
        self.execution_tree.append(node)

    def show_tree(self) -> None:
        """Exibe a árvore de execução em formato JSON."""
        print(json.dumps(self.execution_tree, ensure_ascii=False, indent=4))


class MethodTraceContext:
    """Context manager para rastreamento de métodos."""

    def __init__(self, logger: TraceLogger, target: Any) -> None:
        self.logger = logger
        self.target = target

    def __enter__(self) -> None:
        # Wrap all methods in the target class
        for name in dir(self.target):
            if callable(getattr(self.target, name)) and not name.startswith('__'):
                setattr(self.target, name, self.wrap_method(getattr(self.target, name), name))
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        self.logger.show_tree()  # Exibe a árvore ao sair do contexto

    def wrap_method(self, original_method: Callable, name: str) -> Callable:
        """Wrap a method to add tracing."""

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()  # Início do rastreamento
            args_repr = [repr(arg) for arg in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            input_repr = ", ".join(args_repr + kwargs_repr)

            log_entry = f"Entrando: {self.target.__class__.__name__}.{name} com args: {input_repr}"
            logging.info(log_entry)  # Log de entrada

            result = original_method(*args, **kwargs)

            end_time = time.time()  # Fim do rastreamento
            duration = end_time - start_time
            log_exit = f"Saindo: {self.target.__class__.__name__}.{name} com resultado: {result!r}, duração: {duration:.3f}s"
            logging.info(log_exit)  # Log de saída

            self.logger.add_to_tree(self.target.__class__.__name__, name, args, result, duration, log_entry, log_exit)
            return result

        return wrapped
