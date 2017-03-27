from .models import NewsItem
from apps.scrumdocelery import app


@app.task
def purge_old():
    NewsItem.purgeOld(365*2)
