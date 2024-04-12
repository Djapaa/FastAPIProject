import aioredis

redis = aioredis.from_url("redis://redis", encoding="utf8", decode_responses=True)