import discord
import os
import io
import math
import random
from dataclasses import dataclass
from typing import Tuple
from enum import Enum
from PIL import Image, ImageDraw, ImageColor, ImageFont
from model import *
from asyncio import get_event_loop

IMAGE_DIR = "img"

@dataclass(frozen=True)
class PlayerBaseItem:
    path: str

@dataclass(frozen=True)
class PlayerBase:
    p5: PlayerBaseItem
    p6: PlayerBaseItem
    p7: PlayerBaseItem
    p8: PlayerBaseItem
    p9: PlayerBaseItem
    p10: PlayerBaseItem

@dataclass(frozen=True)
class Skin:
    """A class that represents a skin for game images."""
    path: str
    assassin: str
    background: str
    board: PlayerBase
    evil_servants: List[str]
    fail_choice: str
    fail_mark: str
    logo: str
    loyal_servants: List[str]
    merlin: str
    mordred: str
    morgana: str
    oberon: str
    percival: str
    reject_mark: str
    role_back: str
    success_choice: str
    success_mark: str
    table: PlayerBase
    font: str
    def get_image(self, path:str):
        return IMAGE_DIR + os.path.sep + self.path + os.path.sep +  path
    def get_image_file(self, path:str):
        return discord.File(self.get_image(path))
    async def send_image(self, path: str, channel):
        await channel.send(file=self.get_image_file(path))
    async def send_board(self, gamestate, channel):
        def _make_board():
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
            with Image.open(self.get_image(path)) as boardIm:
                circleWidth = int(boardIm.width / 10)
                with Image.open(self.get_image(self.reject_mark)) \
                 .resize((circleWidth, circleWidth)) as attemptIm:
                    left_times = 5 - gamestate.team_attempts
                    boardIm.alpha_composite(attemptIm, dest=(
                        int(boardIm.width / 16 + left_times * (boardIm.width / 27 + circleWidth)),
                        int(boardIm.height * 9.4 / 12)
                    ))
                    circleWidth = int(boardIm.width / 6.3)
                    with Image.open(self.get_image(self.success_mark)) \
                        .resize((circleWidth, circleWidth)) as successIm, \
                        Image.open(self.get_image(self.fail_mark)) \
                            .resize((circleWidth, circleWidth)) as failIm:
                        for quest, index in zip(gamestate.quests, range(0, len(gamestate.quests))):
                            pos = (int(boardIm.width / 27 + index * (boardIm.width / 34 + circleWidth)),
                             int(boardIm.height / 2.47))
                            if (quest.winning_team is Team.GOOD):
                                boardIm.alpha_composite(successIm, dest=pos)
                            if (quest.winning_team is Team.EVIL):
                                boardIm.alpha_composite(failIm, dest=pos)
                        arr = io.BytesIO()
                        boardIm.save(arr, format='PNG')
                        arr.seek(0)
                        return discord.File(arr, "board.png")
        await channel.send(file=await get_event_loop().run_in_executor(None, _make_board))
    async def send_table(self, gamestate, channel):
        def _make_table():
            path = self.table.p10.path
            if len(gamestate.players) == 5:
                path = self.table.p5.path
            elif len(gamestate.players) == 6:
                path = self.table.p6.path
            elif len(gamestate.players) == 7:
                path = self.table.p7.path
            elif len(gamestate.players) == 8:
                path = self.table.p8.path
            elif len(gamestate.players) == 9:
                path = self.table.p9.path
            with Image.open(self.get_image(path)) as tableIm:
                tableImDraw = ImageDraw.Draw(tableIm)
                tableCenter = (int(tableIm.width / 2.75), int(tableIm.height / 1.83))
                tableRadius = int(tableIm.width / 3.6)
                player_list = gamestate.players
                firstAngle = 2 * math.pi / len(player_list)
                stepAngle = 2 * math.pi / len(player_list)
                font = ImageFont.truetype(self.get_image(self.font), size=20)
                for player, index in zip(player_list, range(0, len(player_list))):
                    xOffset = tableRadius * math.cos(firstAngle - index * stepAngle)
                    yOffset = -(tableRadius * math.sin(firstAngle - index * stepAngle))
                    if (index == gamestate.leader):
                        fillColor = ImageColor.getrgb("yellow")
                    else:
                        fillColor = ImageColor.getrgb("white")
                    tableImDraw.text(xy=(tableCenter[0] + xOffset, tableCenter[1] + yOffset),
                        text=player.name, fill=fillColor, font=font, align="center")
                roles_list = list(map(lambda p: p.role, gamestate.players))
                roles_list.sort(key=lambda role: role.name)
                role_height = int(tableIm.height / len(roles_list))

                def get_image_for_role(role):
                    if role in SERVANTS:
                        return Image.open(self.get_image(random.choice(self.loyal_servants)))
                    elif role in MINIONS:
                        return Image.open(self.get_image(random.choice(self.evil_servants)))
                    elif role is MERLIN:
                        return Image.open(self.get_image(self.merlin))
                    elif role is PERCIVAL:
                        return Image.open(self.get_image(self.percival))
                    elif role is ASSASSIN:
                        return Image.open(self.get_image(self.assassin))
                    elif role is MORGANA:
                        return Image.open(self.get_image(self.morgana))
                    elif role is MORDRED:
                        return Image.open(self.get_image(self.mordred))
                    elif role is OBERON:
                        return Image.open(self.get_image(self.oberon))
                def get_resized_image_for_role(role):
                    roleIm = get_image_for_role(role)
                    return roleIm.resize((int(role_height * roleIm.width / roleIm.height), int(role_height)))
                
                if all(role for role in roles_list):
                    images_width = []
                    for index, role in zip(range(0, len(roles_list)), roles_list):
                        with get_resized_image_for_role(role) as roleIm:
                            images_width.append(roleIm.width)
                    table_offset = max(images_width)
                    newIm = Image.new("RGBA", (tableIm.width + table_offset, tableIm.height))
                    newIm.alpha_composite(tableIm, dest=(table_offset, 0))
                    for index, role in zip(range(0, len(roles_list)), roles_list):
                        with get_resized_image_for_role(role) as roleIm:
                                newIm.alpha_composite(roleIm, dest=(0, index * role_height))
                    tableIm = newIm
                arr = io.BytesIO()
                tableIm.save(arr, format='PNG')
                arr.seek(0)
                return discord.File(arr, "table.png")
        await channel.send(file=await get_event_loop().run_in_executor(None, _make_table))
    async def get_votes_file(self, channel, success_votes:int, fail_votes:int):
        def _make_votes():
            with Image.open(self.get_image(self.success_choice)) as successIm, \
                Image.open(self.get_image(self.fail_choice)) as failIm:
                total_votes = success_votes + fail_votes
                total_width = success_votes * successIm.width + fail_votes * failIm.width + max(0, (10 - total_votes) * successIm.width)
                total_height = max(successIm.height, failIm.height)
                vote_list = [True] * success_votes + [False] * fail_votes
                random.shuffle(vote_list)
                newIm = Image.new("RGBA", (total_width, total_height))
                current_width = 0
                for vote, index in zip(vote_list, range(total_votes)):
                    if vote:
                        newIm.alpha_composite(successIm, dest=(current_width, 0))
                        current_width += successIm.width
                    else:
                        newIm.alpha_composite(failIm, dest=(current_width, 0))
                        current_width += failIm.width
                arr = io.BytesIO()
                newIm.save(arr, format='PNG')
                arr.seek(0)
                return discord.File(arr, "votes.png")
        return await get_event_loop().run_in_executor(None, _make_votes)




Skins = dict(
    AVALON = Skin(
        path="avalon",
        assassin="assassin.png",
        background="wood_bg.jpg",
        board=PlayerBase(
            p5=PlayerBaseItem("5_players_board.png"),
            p6=PlayerBaseItem("6_players_board.png"),
            p7=PlayerBaseItem("7_players_board.png"),
            p8=PlayerBaseItem("8_players_board.png"),
            p9=PlayerBaseItem("9_players_board.png"),
            p10=PlayerBaseItem("10_players_board.png")
        ),
        evil_servants=["evil_servant.png"],
        fail_choice="fail_choose_card.png",
        fail_mark="fail_mark.png",
        logo="logo.png",
        loyal_servants=["loyal_servant.png"],
        merlin="merlin.png",
        mordred="mordred.png",
        morgana="morgana.png",
        oberon="oberon.png",
        percival="percival.png",
        reject_mark="reject_mark.png",
        role_back="role_back.png",
        success_choice="success_choose_card.png",
        success_mark="success_mark.png",
        table=PlayerBase(
            p5=PlayerBaseItem("5_players_table.png"),
            p6=PlayerBaseItem("6_players_table.png"),
            p7=PlayerBaseItem("7_players_table.png"),
            p8=PlayerBaseItem("8_players_table.png"),
            p9=PlayerBaseItem("9_players_table.png"),
            p10=PlayerBaseItem("10_players_table.png")
        ),
        font="medieval.ttf"
    ),
    STARWARS = Skin(
        path="starwars",
        assassin="boba_fett_assassin.png",
        background="stars_bg.jpg",
        board=PlayerBase(
            p5=PlayerBaseItem("5_players_board.png"),
            p6=PlayerBaseItem("6_players_board.png"),
            p7=PlayerBaseItem("7_players_board.png"),
            p8=PlayerBaseItem("8_players_board.png"),
            p9=PlayerBaseItem("9_players_board.png"),
            p10=PlayerBaseItem("10_players_board.png")
        ),
        evil_servants=["trooper_evil.png"],
        fail_choice="fail_choose_card.png",
        fail_mark="fail_mark.png",
        logo="logo.png",
        loyal_servants=["ally_0.png", "ally_1.png", "ally_2.png", "ally_3.png", "ally_4.png", "ally_5.png"],
        merlin="obiwan.png",
        mordred="palpatine.png",
        morgana="dartfener.png",
        oberon="jabba.png",
        percival="luke.png",
        reject_mark="reject_mark.png",
        role_back="role_back.png",
        success_choice="success_choose_card.png",
        success_mark="success_mark.png",
        table=PlayerBase(
            p5=PlayerBaseItem("5_players_table.png"),
            p6=PlayerBaseItem("6_players_table.png"),
            p7=PlayerBaseItem("7_players_table.png"),
            p8=PlayerBaseItem("8_players_table.png"),
            p9=PlayerBaseItem("9_players_table.png"),
            p10=PlayerBaseItem("10_players_table.png")
        ),
        font="starjedi.ttf"
    )
)

