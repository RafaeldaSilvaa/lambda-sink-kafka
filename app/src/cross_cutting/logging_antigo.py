import logging
import time
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type


class LoggerInterface:
    """Interface de logger para seguir o princípio DIP (Dependency Inversion Principle)."""
    def log_message(self, message: str) -> None:
        raise NotImplementedError

    def log_json(self, log_data: Dict[str, Any]) -> None:
        raise NotImplementedError


class SimpleLogger(LoggerInterface):
    """Classe responsável por registrar logs, aplicando SRP (Single Responsibility Principle)."""
    def __init__(self, logger_name: str = "TraceLogger") -> None:
        self._logger = logging.getLogger(logger_name)
        self.configure_logging()

    def configure_logging(self) -> None:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    def log_message(self, message: str) -> None:
        self._logger.info(message)

    def log_json(self, log_data: Dict[str, Any]) -> None:
        self._logger.info(json.dumps(log_data, ensure_ascii=False))


class TraceLogger:
    """Classe Singleton que gerencia o rastreamento de métodos."""
    _instance: Optional['TraceLogger'] = None

    def __new__(cls) -> 'TraceLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.execution_tree: List[Dict[str, Any]] = []
            cls._instance.logger = SimpleLogger()
        return cls._instance

    def log_method(self, method: Callable) -> Callable:
        """Decora métodos para rastreamento automático."""
        @wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            class_name = args[0].__class__.__name__ if args else "N/A"
            method_name = method.__name__
            logger: LoggerInterface = self.logger

            start_time = time.time()
            start_str = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(start_time)) + f".{int(start_time * 1000) % 1000:03d}"

            # Captura o nome dos argumentos e seus valores
            arg_names = method.__code__.co_varnames[1:]
            args_repr = [f"{name}={value!r}" for name, value in zip(arg_names, args[1:])]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            input_repr = ", ".join(args_repr + kwargs_repr)

            log_entry = f"[{start_str}] {class_name}.{method_name} Início - Entrada: {input_repr}"
            logger.log_message(log_entry)

            inputs = {name: value for name, value in zip(arg_names, args[1:])}
            inputs.update(kwargs)  # Merge kwargs into inputs

            logger.log_json({
                "event": "start",
                "class": class_name,
                "method": method_name,
                "timestamp": start_str,
                "inputs": inputs
            })

            result = method(*args, **kwargs)

            end_time = time.time()
            duration = end_time - start_time
            end_str = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(end_time)) + f".{int(end_time * 1000) % 1000:03d}"

            log_exit = f"[{end_str}] {class_name}.{method_name} Fim - Saída: {result!r}, Tempo: {duration:.3f}s"
            logger.log_message(log_exit)

            # Log JSON para a saída
            logger.log_json({
                "event": "end",
                "class": class_name,
                "method": method_name,
                "timestamp": end_str,
                "duration_seconds": duration,
                "output": result
            })

            # Adiciona o log na árvore
            self.add_to_tree(class_name, method_name, start_str, end_str, duration, input_repr, result, [log_entry, log_exit])

            return result

        return wrapper

    def add_to_tree(self, class_name: str, method_name: str, start: str, end: str, duration: float, 
                    input_repr: str, result: Any, logs: List[str]) -> None:
        """Adiciona detalhes do método à árvore de execução."""
        node = {
            "class": class_name,
            "method": method_name,
            "start_time": start,
            "end_time": end,
            "duration_seconds": duration,
            "inputs": input_repr,
            "output": result,
            "logs": logs,
            "children": []
        }

        self.execution_tree.append(node)

    def show_tree(self) -> None:
        """Exibe a árvore de execução em formato JSON."""
        print(json.dumps(self.execution_tree, ensure_ascii=False, indent=4))

    def clear_tree(self) -> None:
        """Limpa a árvore de execução."""
        self.execution_tree = []


class MethodTraceContext:
    """Context manager para o rastreamento dos métodos."""
    def __init__(self, logger: TraceLogger, method: Callable) -> None:
        self.logger = logger
        self.method = method

    def __enter__(self) -> Callable:
        return self.logger.log_method(self.method)

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        self.logger.show_tree()
        #ass  # Aqui poderíamos adicionar algum tratamento de exceção se necessário.



# # Exemplo de uso sem herança
# class ExampleService:
#     def __init__(self) -> None:
#         self.logger = TraceLogger()
#
#     def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
#         """Processa os dados e retorna um novo dicionário"""
#         processed_data = {key: str(value).upper() for key, value in data.items()}
#         return processed_data
#
#     def helper_method(self) -> None:
#         """Método auxiliar que pode ser rastreado se necessário."""
#         pass
#
#
# # Exemplo de uso
# service = ExampleService()
#
# with MethodTraceContext(service.logger, service.process_data) as method:
#     method({"nome": "ChatGPT", "tarefa": "refatorar código"})
#
# # Exibe a árvore de execução
# service.logger.show_tree()
