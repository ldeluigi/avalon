import asyncio
from collections import deque

# Listends for Discord messages asynchronously to avoids dropping messages.
# Adds messages to a queue and removes them in the order they were received.
class MsgQueue:
	def __init__(self, client, check):
		self.client = client
		self.check = check

	def __enter__(self):
		self.queue = deque()
		self.task = asyncio.create_task(self.__wait_for_message())
		return self

	def __exit__(self, type, value, tb):
		if self.task:
			self.task.cancel()
			self.task = None
		if self.queue:
			self.queue.clear()
			self.queue = None

	async def next(self):
		if self.queue == None:
			raise RuntimeError("next() must be called from inside of a with block")
		while True:
			try:
				return self.queue.popleft()
			except IndexError:
				if self.task:
					await self.task
				else:
					raise RuntimeError("MsgQueue exited while next() was in progress")

	async def __wait_for_message(self):
		message = await self.client.wait_for("message", check=self.check)
		self.queue.append(message)
		self.task = asyncio.create_task(self.__wait_for_message())
