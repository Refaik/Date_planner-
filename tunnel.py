import asyncio
import logging
import re
import shutil

logger = logging.getLogger(__name__)

URL_RE = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

async def _drain(stream):
    """
    Фоновое непрерывное чтение вывода cloudflared.
    Без этого буфер pipe (stdout) переполнится (64 КБ), и процесс cloudflared зависнет.
    """
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode(errors="ignore").strip()
            if text and ("ERR" in text or "connIndex" in text or "error" in text.lower()):
                logger.debug(f"[cloudflared] {text}")
    except Exception:
        pass

async def start_tunnel(port: int):
    """
    Запускает Cloudflare Tunnel с протоколом http2 (TCP вместо блокируемого QUIC/UDP)
    и ждёт реального установления соединения ('Registered tunnel connection').
    """
    cloudflared_path = shutil.which("cloudflared") or "cloudflared"

    cmd = [
        cloudflared_path,
        "tunnel",
        "--url", f"http://127.0.0.1:{port}",
        "--protocol", "http2",      # http2 через TCP 443 не блокируется в отличие от QUIC (UDP)
        "--no-autoupdate",
    ]

    print("⏳ Запуск Cloudflare Tunnel, ожидание регистрации соединения...")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    url = None
    registered = False

    while True:
        line = await proc.stdout.readline()
        if not line:
            raise RuntimeError(
                "cloudflared завершился до подключения. Проверьте соединение с интернетом."
            )
        text = line.decode(errors="ignore")
        print(text, end="")  # Отображаем логи cloudflared в консоли в реальном времени

        match = URL_RE.search(text)
        if match:
            url = match.group(0)

        # Ждем обязательного подтверждения регистрации туннеля на серверах Cloudflare!
        if "Registered tunnel connection" in text:
            registered = True

        # Возвращаем адрес только тогда, когда получен URL И соединение реально зарегистрировано!
        if url and registered:
            break

    # Запускаем фоновое чтение, чтобы буфер вывода процесса никогда не забивался
    asyncio.create_task(_drain(proc.stdout))
    return url, proc