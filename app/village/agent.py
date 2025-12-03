import importlib.util
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict

from . import config
from .transport import FirebaseTransport


def load_handler(handler_path: Path) -> Callable[[Dict[str, Any]], Any]:
    spec = importlib.util.spec_from_file_location("village_app", handler_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load handler")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    if not hasattr(module, "handler"):
        raise RuntimeError("handler(event) not found")
    return getattr(module, "handler")


class Agent:
    def __init__(self, app_root: Path) -> None:
        self.app_root = app_root
        self.cfg = config.load_config()
        self.transport = FirebaseTransport(
            firebase_url=self.cfg.get("firebase_url", ""),
            api_key=self.cfg.get("api_key", ""),
        )
        self.handler = load_handler(self.app_root / "village" / "main.py")
        self.uid = self.cfg.get("uid", "")
        self.password = self.cfg.get("password", "")
        self.app_name = self.cfg.get("apps", [None])[0] or "default"
        self.log = self._setup_log()

    def _setup_log(self) -> logging.Logger:
        logs_dir = self.app_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = logs_dir / "agent.log"
        logger = logging.getLogger("village.agent")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def heartbeat(self) -> None:
        if self.uid:
            self.transport.heartbeat(self.uid, "online")

    def poll_once(self) -> None:
        next_req = self.transport.read_next_request(self.uid, self.app_name)
        if not next_req:
            return
        call_id = next_req["call_id"]
        payload = next_req["request"]
        self.log.info("received call %s", call_id)
        try:
            result = self.handler(payload)
            body = {
                "call_id": call_id,
                "status": "ok",
                "result": result,
                "ts": int(time.time()),
            }
        except Exception as exc:  # pragma: no cover
            self.log.exception("handler failed for call %s", call_id)
            body = {
                "call_id": call_id,
                "status": "error",
                "message": str(exc),
                "ts": int(time.time()),
            }
        self.transport.write_response(self.uid, call_id, body)
        self.transport.ack_request(self.uid, call_id)
        self.log.info("responded to call %s with status %s", call_id, body["status"])

    def run_forever(self, sleep_seconds: int = 2) -> None:
        while True:
            self.heartbeat()
            self.poll_once()
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    Agent(Path(__file__).resolve().parent.parent).run_forever()
