from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import buscar_expirados

async def remover_expirados(bot):
    expirados = buscar_expirados()
    for user in expirados:
        try:
            await bot.ban_chat_member(user['grupo_id'], user['telegram_id'])
        except Exception as e:
            print(e)

def start_jobs(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remover_expirados, "interval", hours=1, args=[bot])
    scheduler.start()

