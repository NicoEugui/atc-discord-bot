import os
import discord
import datetime

class EmbedHelper:
    def __init__(self):
        self.color = 0x6699ff
        self.author_name = os.getenv("EMBED_AUTHOR_NAME", "ATC Bot")
        self.thumbnail_url = os.getenv("EMBED_THUMBNAIL_URL", "")
        self.author_icon_url = os.getenv("EMBED_AUTHOR_ICON_URL", "")
        self.footer_text = os.getenv("EMBED_FOOTER_TEXT", "ATC Bot")
        self.footer_icon_url = os.getenv("EMBED_FOOTER_ICON_URL", "")

    # Function to create a common information embed
    def create_info_embed(self, title, description, timestamp=None):
        if timestamp is None:
            timestamp = datetime.datetime.now(datetime.timezone.utc)
        embed = discord.Embed(title=title, description=description, colour=self.color, timestamp=timestamp)
        embed.set_author(name=self.author_name, icon_url=self.author_icon_url)
        embed.set_footer(text=self.footer_text, icon_url=self.footer_icon_url)
        embed.set_thumbnail(url=self.thumbnail_url)
        return embed

    # Function to send an information embed
    async def send_info_embed(self, ctx, title, description, timestamp=None):
        embed = self.create_info_embed(title, description, timestamp)
        await ctx.send(embed=embed)

    # Function to send an error information embed
    async def send_error_embed(self, ctx, title, description, timestamp=None):
        embed = self.create_info_embed(title, description, timestamp)
        await ctx.send(embed=embed)
        print(f"Error: {description}")


# Example usage:
# embed_helper = EmbedHelper()
# await embed_helper.send_info_embed(ctx, "Embed Title", "This is an information message.")
# await embed_helper.send_error_embed(ctx, "Error", "An error occurred while processing your request.")
