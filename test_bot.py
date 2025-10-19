import asyncio
import types
import pytest

from types import SimpleNamespace

# We'll import bot module and monkeypatch telegram objects where needed

@pytest.mark.asyncio
async def test_set_reactions_parallel_builds_reaction_types(monkeypatch):
    import bot as mybot

    captured = {}

    class FakeBot:
        async def set_message_reaction(self, chat_id, message_id, reaction):
            captured['chat_id'] = chat_id
            captured['message_id'] = message_id
            captured['reaction'] = reaction

    # Provide a fake ReactionTypeEmoji that records the emoji
    class FakeReactionTypeEmoji:
        def __init__(self, emoji):
            self.emoji = emoji
        def __repr__(self):
            return f"FakeReactionTypeEmoji({self.emoji!r})"

    monkeypatch.setattr(mybot, 'ReactionTypeEmoji', FakeReactionTypeEmoji)

    bot = FakeBot()
    await mybot.set_reactions_parallel(bot, chat_id=123, message_id=456, emojis=["👍", "🔥", "😂"]) 

    assert captured['chat_id'] == 123
    assert captured['message_id'] == 456
    assert isinstance(captured['reaction'], list)
    assert [r.emoji for r in captured['reaction']] == ["👍", "🔥", "😂"]


@pytest.mark.asyncio
async def test_react_command_validates_input(monkeypatch):
    import bot as mybot

    sent_messages = []

    class FakeMessage:
        def __init__(self, text=None, reply_to_message=None, chat_id=1, message_id=2):
            self.text = text
            self.reply_to_message = reply_to_message
            self.chat_id = chat_id
            self.message_id = message_id
        async def reply_text(self, text):
            sent_messages.append(text)

    class FakeContext:
        def __init__(self):
            self.args = []
            self.bot = object()

    # Case 1: Not replying
    update = SimpleNamespace(message=FakeMessage())
    context = FakeContext()
    await mybot.react_command(update, context)
    assert "Please reply to a message" in sent_messages[-1]

    # Case 2: No emojis
    sent_messages.clear()
    update = SimpleNamespace(message=FakeMessage(reply_to_message=FakeMessage()))
    context = FakeContext()
    await mybot.react_command(update, context)
    assert "Provide emojis" in sent_messages[-1]


@pytest.mark.asyncio
async def test_react_command_calls_helper(monkeypatch):
    import bot as mybot

    calls = {}

    async def fake_set_reactions_parallel(bot, chat_id, message_id, emojis):
        calls['bot'] = bot
        calls['chat_id'] = chat_id
        calls['message_id'] = message_id
        calls['emojis'] = list(emojis)

    # Monkeypatch helper
    monkeypatch.setattr(mybot, 'set_reactions_parallel', fake_set_reactions_parallel)

    sent_messages = []

    class FakeMessage:
        def __init__(self, reply_to_message, chat_id=321, message_id=654):
            self.reply_to_message = reply_to_message
            self.chat_id = chat_id
            self.message_id = message_id
        async def reply_text(self, text):
            sent_messages.append(text)

    class FakeContext:
        def __init__(self):
            self.args = ["👍", "🔥"]
            self.bot = object()

    update = SimpleNamespace(message=FakeMessage(reply_to_message=SimpleNamespace(message_id=777)))
    context = FakeContext()

    await mybot.react_command(update, context)

    assert calls['emojis'] == ["👍", "🔥"]
    assert isinstance(sent_messages[-1], str) and "Reactions added" in sent_messages[-1]
