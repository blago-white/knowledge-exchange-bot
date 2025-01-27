from models.worker import Worker
from services.worker import WorkersService


async def generate_main_stats_message_text(
        template: str,
        worker: Worker,
        workers_service: WorkersService
) -> str:
    week_profit = await workers_service.get_week_profit()

    return template.format(
        user_id=worker.id,
        selled_students=await workers_service.get_selled_count(),
        week_profit=str(week_profit),
        total_profit=await workers_service.get_total_profit(),
        referals_count="Скоро будет...",
        meet_link=worker.meet_link or "А по этой ссылке ученики зайдут на урок!"
    )
