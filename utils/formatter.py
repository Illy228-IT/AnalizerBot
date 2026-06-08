def loading_message() -> str:
    return (
        "🔎 Анализирую рынок...\n\n"
        "Проверяю:\n"
        "• BTCUSDT\n"
        "• BTC.D\n"
        "• 4H / 1H / 15M\n"
        "• SMC структуру\n"
        "• ликвидность\n"
        "• FVG / OB\n"
    )


def start_message() -> str:
    return (
        "🤖 SMC AI BOT запущен\n\n"
        "Напиши:\n\n"
        "➡️ дальше\n\n"
        "И я найду одну альт-монету, проверю BTC + BTC.D + SMC "
        "и дам анализ."
    )


def unknown_command_message() -> str:
    return "Напиши: дальше"