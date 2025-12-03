import argparse
import sys
import time
from pathlib import Path
from typing import List

from . import config
from .agent import Agent
from .transport import FirebaseTransport, drop_stale_response


def cmd_config_set(args: argparse.Namespace) -> None:
    cfg = config.set_value(args.key, args.value)
    print(f"set {args.key} -> {cfg.get(args.key)}")


def cmd_set(args: argparse.Namespace) -> None:
    key_map = {
        "account_name": "uid",
        "password": "password",
    }
    key = key_map.get(args.field)
    if not key:
        print("unsupported field", file=sys.stderr)
        sys.exit(1)
    cfg = config.set_value(key, args.value)
    print(f"set {args.field} -> {args.value}")


def cmd_call(args: argparse.Namespace) -> None:
    cfg = config.load_config()
    uid = args.uid or cfg.get("uid", "")
    password = args.password or cfg.get("password", "")
    if not uid or not password:
        print("uid/password required", file=sys.stderr)
        sys.exit(1)
    call_id = f"{int(time.time() * 1000)}"
    body = {
        "uid": uid,
        "password": password,
        "app": args.app,
        "args": args.args,
        "call_id": call_id,
        "ts": int(time.time()),
    }
    transport = FirebaseTransport(cfg.get("firebase_url", ""), cfg.get("api_key", ""))
    transport.enqueue_request(uid, call_id, body)
    print(f"enqueued call {call_id}, waiting for response...")
    start = time.time()
    timeout = 30
    while time.time() - start < timeout:
        resp = transport.read_response(uid, call_id)
        if not resp:
            time.sleep(1)
            continue
        ts_resp = resp.get("ts", 0)
        if drop_stale_response(body["ts"], ts_resp):
            print("stale response dropped")
            break
        print(resp)
        break
    else:
        print("timeout waiting for response", file=sys.stderr)


def cmd_run_agent(args: argparse.Namespace) -> None:
    Agent(Path(__file__).resolve().parent.parent).run_forever()


def cmd_logs(args: argparse.Namespace) -> None:
    log_path = Path(__file__).resolve().parent.parent / "logs" / f"{args.app}.log"
    if not log_path.exists():
        print("no logs found")
        return
    print(log_path.read_text())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="village", add_help=True)
    sub = parser.add_subparsers(dest="command")

    p_set = sub.add_parser("set", help="set account_name/password")
    p_set.add_argument("field", choices=["account_name", "password"])
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_config = sub.add_parser("config", help="config set key value")
    p_config_sub = p_config.add_subparsers(dest="action")
    p_config_set = p_config_sub.add_parser("set")
    p_config_set.add_argument("key")
    p_config_set.add_argument("value")
    p_config_set.set_defaults(func=cmd_config_set)

    p_call = sub.add_parser("call", help="call UID PASSWORD app arg1 arg2")
    p_call.add_argument("uid")
    p_call.add_argument("password")
    p_call.add_argument("app")
    p_call.add_argument("args", nargs=argparse.REMAINDER)
    p_call.set_defaults(func=cmd_call)

    p_agent = sub.add_parser("agent", help="run background agent loop")
    p_agent.set_defaults(func=cmd_run_agent)

    p_run = sub.add_parser("run", help="alias for agent")
    p_run.set_defaults(func=cmd_run_agent)

    p_logs = sub.add_parser("logs", help="logs app")
    p_logs.add_argument("app")
    p_logs.set_defaults(func=cmd_logs)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
