from typing import Dict
import discord

def format_dictionary_response(word: str, word_info: Dict) -> discord.Embed:
    """
    Formats the dictionary response into a Discord embed
    """
    embed = discord.Embed(
        title=f"📚 Definition of '{word}'",
        color=discord.Color.blue()
    )

    # Add definitions
    definitions_text = ""
    for i, definition in enumerate(word_info['definitions'], 1):
        definitions_text += f"{i}. {definition}\n\n"
    embed.add_field(
        name="📖 Definitions",
        value=definitions_text or "No definitions found.",
        inline=False
    )

    # Add examples if available
    if word_info['examples']:
        examples_text = "\n\n".join(f"• {example}" for example in word_info['examples'])
        embed.add_field(
            name="💭 Examples",
            value=examples_text,
            inline=False
        )

    # Add etymology if available
    if word_info['etymology']:
        embed.add_field(
            name="📜 Etymology",
            value=word_info['etymology'],
            inline=False
        )

    # Add usage notes if available
    if word_info.get('usage_notes'):
        notes_text = "\n\n".join(f"• {note}" for note in word_info['usage_notes'])
        embed.add_field(
            name="📝 Usage Notes",
            value=notes_text,
            inline=False
        )

    embed.set_footer(text="Source: dictionary.com")
    return embed