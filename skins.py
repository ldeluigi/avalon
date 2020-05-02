import discord
import os
import io
import math
from dataclasses import dataclass
from typing import Tuple
from enum import Enum
from PIL import Image, ImageDraw, ImageColor, ImageFont
from enums import Team

IMAGE_DIR = "img"

@dataclass(frozen=True)
class Board:
    path: str

@dataclass(frozen=True)
class Boards:
    p5: Board
    p6: Board
    p7: Board
    p8: Board
    p9: Board
    p10: Board

@dataclass(frozen=True)
class Skin:
    """A class that represents a skin for game images."""
    path: str
    assassin: str
    background: str
    board: Boards
    evil_servants: Tuple[str]
    fail_choice: str
    fail_mark: str
    logo: str
    loyal_servants: Tuple[str]
    merlin: str
    mordred: str
    morgana: str
    oberon: str
    percival: str
    reject_mark: str
    role_back: str
    success_choice: str
    success_mark: str
    table: str
    font: str
    def get_image(self, path:str):
        return IMAGE_DIR + os.path.sep + self.path + os.path.sep +  path
    async def send_image(self, path: str, channel):
        await channel.send(file=discord.File(self.get_image(path)))
    async def send_board(self, gamestate, channel):
        path = self.board.p10.path
        if len(gamestate.players) == 5:
            path = self.board.p5.path
        elif len(gamestate.players) == 6:
            path = self.board.p6.path
        elif len(gamestate.players) == 7:
            path = self.board.p7.path
        elif len(gamestate.players) == 8:
            path = self.board.p8.path
        elif len(gamestate.players) == 9:
            path = self.board.p9.path
        boardIm: Image = Image.open(self.get_image(path))
        circleWidth = int(boardIm.width / 10)
        attemptIm = Image.open(self.get_image(self.reject_mark)).resize((circleWidth, circleWidth))
        left_times = 5 - gamestate.team_attempts
        boardIm.alpha_composite(attemptIm, dest=(int(boardIm.width / 16 + left_times * (boardIm.width / 27 + circleWidth)), int(boardIm.height * 9.4 / 12)))
        circleWidth = int(boardIm.width / 6.3)
        successIm = Image.open(self.get_image(self.success_mark)).resize((circleWidth, circleWidth))
        failIm = Image.open(self.get_image(self.fail_mark)).resize((circleWidth, circleWidth))
        for quest, index in zip(gamestate.quests, range(0, len(gamestate.quests))):
            pos = (int(boardIm.width / 26 + index * (boardIm.width / 34 + circleWidth)), int(boardIm.height / 2.47))
            if (quest.winning_team is Team.GOOD):
                boardIm.alpha_composite(successIm, dest=pos)
            if (quest.winning_team is Team.EVIL):
                boardIm.alpha_composite(failIm, dest=pos)
        arr = io.BytesIO()
        boardIm.save(arr, format='PNG')
        arr.seek(0)
        result_file = discord.File(arr, "board.png")
        await channel.send(file=result_file)
        boardIm.close()
        attemptIm.close()
        successIm.close()
        failIm.close()
    async def send_table(self, gamestate, channel):
        tableIm = Image.open(self.get_image(self.table))
        tableImDraw = ImageDraw.Draw(tableIm)
        tableCenter = (int(tableIm.width / 2.75), int(tableIm.height / 1.83))
        tableRadius = int(tableIm.width / 3.6)
        firstAngle = math.pi / 2.8
        rotated_list = gamestate.players[gamestate.leader:] + gamestate.players[:gamestate.leader]
        stepAngle = 2 * math.pi / len(rotated_list)
        font = ImageFont.truetype(self.get_image(self.font), size=20)
        for player, index in zip(rotated_list, range(0, len(rotated_list))):
            xOffset = tableRadius * math.cos(firstAngle - index * stepAngle)
            yOffset = -(tableRadius * math.sin(firstAngle - index * stepAngle))
            if (index is 0):
                fillColor = ImageColor.getrgb("yellow")
            else:
                fillColor = ImageColor.getrgb("black")
            tableImDraw.text(xy=(tableCenter[0] + xOffset, tableCenter[1] + yOffset),
                text=player.name, fill=fillColor, font=font, align="center")
        arr = io.BytesIO()
        tableIm.save(arr, format='PNG')
        arr.seek(0)
        result_file = discord.File(arr, "table.png")
        await channel.send(file=result_file)
        tableIm.close()


Skins = dict(
    AVALON = Skin(
        path="avalon",
        assassin="assassin.png",
        background="wood_bg.jpg",
        board=Boards(
            p5=Board("5_players_board.png"),
            p6=Board("6_players_board.png"),
            p7=Board("7_players_board.png"),
            p8=Board("8_players_board.png"),
            p9=Board("9_players_board.png"),
            p10=Board("10_players_board.png")
        ),
        evil_servants=("evil_servant.png",),
        fail_choice="fail_choose_card.png",
        fail_mark="fail_mark.png",
        logo="logo.png",
        loyal_servants=("loyal_servant.png",),
        merlin="merlin.png",
        mordred="mordred.png",
        morgana="morgana.png",
        oberon="oberon.png",
        percival="percival.png",
        reject_mark="reject_mark.png",
        role_back="role_back.png",
        success_choice="success_choose_card.png",
        success_mark="success_mark.png",
        table="table.png",
        font="medieval.ttf"
    )
)

