# Based on EmojiTerra Top 100, checked on 2026-05-13:
# https://emojiterra.com/top-100/

# Mac-style grouping for easier editing.

ROUND_FACE_SMILEYS = (
    "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚"
    "😋😛😜🤪😝🫠🤗🤭🫢🫣🤫🫡🤔🫨🤐🤨🧐🤓😎🥸"
    "🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺🥹😢😭😤😠😡🤬"
    "😳🥵🥶😱😨😰😥😓😶🫥😐🫤😑🙄😬😮‍💨🤥"
    "😴🤤😪😵😵‍💫🤯🥴🤢🤮🤧😷🤒🤕🤑"
)

SMILEYS_AND_PEOPLE = (
    ROUND_FACE_SMILEYS
    + "☺️🥲🙂‍↔️🙂‍↕️😈💀🤡👻🤖"
    "👋🫰🫵👍👏🫶🙏💪🫀👀🫦🤦‍♀️🗣️🫂"
)

HEARTS_AND_EMOTION = (
    "💔❤️‍🔥❤️‍🩹❤️🩷💚💙🩵💜🖤🩶🤍"
    "💯💥💬"
)

FRUITS_AND_BERRIES = "🍎🍏🍐🍊🍋🍋‍🟩🍌🍉🍇🍓🫐🍒🍑🥭🍍🥝🥥"

VEGETABLES = "🥑🍅🫒🥕🌽🌶️🫑🥒🥬🥦🧄🧅🍄🥔🫘"

CAKES_AND_SWEETS = "🎂🧁🍰🥧🍪🍩🍫🍬🍭"

FOOD_AND_DRINK = FRUITS_AND_BERRIES + VEGETABLES + CAKES_AND_SWEETS + "☕"

SPORTS = "⚽🏀🏈⚾🎾🏐🏉🥏🎱🏓🏸🥊🥋⛳🏒🏑🥍🏏🛹⛷️🏂🏋️‍♀️🤺"

ACTIVITY = SPORTS + "🎉🎀🏆🎮"

TRAVEL_AND_PLACES = "🏠✈️🚀☀️"

OBJECTS = "👑💎📢🎶📱📞💡📚🗓️📈📍🪬🗿"

SYMBOLS = "⭐⚡🔥✨⚠️🔞➡️⬇️‼️❗✅✔️❌🚩"

FLAGS = "🇦🇺🇨🇦🇬🇧🇮🇳🇵🇭🇺🇸"

EMOJIS = "".join(
    (
        SMILEYS_AND_PEOPLE,
        HEARTS_AND_EMOTION,
        FOOD_AND_DRINK,
        ACTIVITY,
        TRAVEL_AND_PLACES,
        OBJECTS,
        SYMBOLS,
        FLAGS,
    )
)
