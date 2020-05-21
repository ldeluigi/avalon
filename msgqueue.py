import asyncio
from collections import deque

# Listends for Discord messages asynchronously to avoids dropping messages.
# Adds messages to a queue and removes them in the order they were received.
class MsgQueue:
	def __init__(self, client, check):
		self.__client = client
		self.__check = check

	def __enter__(self):
		self.__queue = deque()
		self.__task = asyncio.create_task(self.__wait_for_message())
		return self

	def __exit__(self, type, value, tb):
		if self.__task:
			self.__task.cancel()
			self.__task = None
		if self.__queue:
			self.__queue.clear()
			self.__queue = None

	async def nextmsg(self):
		if self.__queue == None:
			raise RuntimeError("next() must be called from inside of a with block")
		while True:
			try:
				return self.__queue.popleft()
			except IndexError:
				if self.__task:
					await self.__task
				else:
					raise RuntimeError("MsgQueue exited while next() was in progress")

	async def __wait_for_message(self):
		message = await self.__client.wait_for("message", check=self.__check)
		self.__queue.append(message)
		self.__task = asyncio.create_task(self.__wait_for_message())
