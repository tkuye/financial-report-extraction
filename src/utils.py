from scipy import stats
from functools import wraps, partial
import asyncio

def wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run

@wrap
def find_column_count(wordClusters):
	"""Find the number of columns in a word cluster.
	Args:
		wordClusters (_type_): _description_
	"""
	num_columns = stats.mode(list(map(len, wordClusters)))[0][0]
	return num_columns


