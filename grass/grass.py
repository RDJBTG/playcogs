"""
MIT License

Copyright (c) 2020-2021 phenom4n4n

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import functools
from io import BytesIO
from typing import Literal, Optional

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps
from redbot.core import checks, commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import pagify

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

from .converters import FuzzyMember


class Grass(commands.Cog):
    """
    Make images from avatars!
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=82345678897346,
            force_registration=True,
        )

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        return

    @checks.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["grassytouch"], cooldown_after_parsing=True)
    async def touchgrass(self, ctx, *, member: FuzzyMember = None):
        """Make them touch grass..."""
        if not member:
            member = ctx.author

        async with ctx.typing():
            avatar = await self.get_avatar(member)
            task = functools.partial(self.gen_touchgrass, ctx, avatar)
            image = await self.generate_image(ctx, task)
        if isinstance(image, str):
            await ctx.send(image)
        else:
            await ctx.send(file=image)

    async def generate_image(self, ctx: commands.Context, task: functools.partial):
        task = self.bot.loop.run_in_executor(None, task)
        try:
            image = await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            return "An error occurred while generating this image. Try again later."
        else:
            return image

    async def get_avatar(self, member: discord.User):
        avatar = BytesIO()
        await member.avatar_url.save(avatar, seek_begin=True)
        return avatar

    def bytes_to_image(self, image: BytesIO, size: int):
        image = Image.open(image).convert("RGBA")
        image = image.resize((size, size), Image.ANTIALIAS)
        return image

    def gen_touchgrass(self, ctx, member_avatar):
        member_avatar = self.bytes_to_image(member_avatar, 270x270)
        # base canvas
        im = Image.new("RGBA", (620, 483), None)
        # touchgrass = Image.open(f"{bundled_data_path(self)}/touchgrass/touchgrass.png", mode="r").convert("RGBA")
        touchgrassmask = Image.open(f"{bundled_data_path(self)}/touchgrass/touchgrassmask.png", mode="r").convert(
            "RGBA"
        )
        # im.paste(touchgrass, (0, 0), touchgrass)

        # pasting the pfp
        im.paste(member_avatar, (251, 36), member_avatar)
        im.paste(touchgrassmask, (0, 0), touchgrassmask)
        touchgrassmask.close()
        member_avatar.close()

        fp = BytesIO()
        im.save(fp, "PNG")
        fp.seek(0)
        im.close()
        _file = discord.File(fp, "touchgrass.png")
        fp.close()
        return _file
