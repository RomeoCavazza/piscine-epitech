import random

### SELECT A RANDOM MOLECULE ###

molecules = ["penicillin", "aspirin", "ibuprofen", "paracetamol", "insulin", "adrenaline", "oxytocin", "dopamine", "caffeine", "nicotine", "morphine", "cocaine", "heroine", "vitaminA", "vitaminC", "vitaminD", "vitaminK", "remdesivir", "chloroquine", "azithromycin", "serotonin", "melatonin", "testosterone", "estrogen"]
secret_word = random.choice(molecules).upper()

### INIT GAME STATE ###

mask = ["_"] * len(secret_word)
population = 1000
zombies = 0
INFECT_LETTER = 0.10   
INFECT_WORD = 0.50 

### EVENTS ###

dramatic_events = [
    
    # STAGE 1 — WARNING
    "📡 Strange radio silence in the capital…",
    "📰 Rumors spread about a new infection…",
    "😰 People panic-buy food and supplies…",
    "🚑 First hospitals report unusual cases…",
    "⚠️ Government issues first health alert…",
    
    # STAGE 2 — COLLAPSE
    "💥 The military base collapsed!",
    "🏥 Hospitals are overflowing with the infected…",
    "📡 Radio silence from London…",
    "😱 Panic in New York, chaos everywhere!",
    "🔬 A scientist has been bitten during research!",
    "🚁 Evacuation failed, helicopter crashed!",
    "🌍 Governments collapsing one by one…",
    
    # STAGE 3 — HORROR
    "🧪 Experiments gone wrong, zombies mutating!",
    "🎙️ Last radio DJ screams: 'Save yourselves!'",
    "🧟 Horde spotted near the Eiffel Tower!",
    "🩸 Blood floods the streets…",
    "☢️ Nuclear plant meltdown spreads toxic gas!",
    "🔥 Entire cities burned to contain outbreak!",
    "🪦 Mass graves overflow in the countryside…",
    "☠️ Humanity is on the brink of extinction…",
]

### WELCOME SCREEN ###

print("🧟‍♂️ WELCOME TO HANGMAN – INFECTION ZOMBIE")
print("Find the antidote molecule before humanity is lost!")
print(" ".join(mask), "/", f"{population} humans alive, {zombies} zombies")

### MAIN LOOP ###

while population > 0 and "_" in mask:
    guess = input("Type a letter or a molecule name: ").upper()
    
    if guess == "":
        continue
    
    ### CASE 1 : SINGLE LETTER ###
    if len(guess) == 1:
        letter = guess
        found = False
        
        for i in range(len(secret_word)):
            if secret_word[i] == letter:
                mask[i] = letter
                found = True
                
        if found:
            print(f"💉 Antidote clue found: {letter}")
            
        else:
            lost = int(1000 * INFECT_LETTER)
            population -= lost
            zombies += lost
            idx = min(zombies // 100, len(dramatic_events) - 1)
            print(f"🪦 Wrong letter! -{lost} humans")
            print(dramatic_events[idx])

    ### CASE 2 : FULL WORD ###
    else:
        
        if guess == secret_word:
            mask = list(secret_word)
            break
    
        else:
            lost = int(1000 * INFECT_WORD)
            population -= lost
            zombies += lost
            idx = min(zombies // 100, len(dramatic_events) - 1)
            print(f"💀 Wrong molecule! -{lost} humans")
            print(dramatic_events[idx])

    if population < 0:
        zombies = 1000
        population = 0

    ### SHOW CURRENT STATE ###
    bar = "█" * (population // 100) + "-" * (zombies // 100)
    print(" ".join(mask))
    print(f"Population: {population} humans left, {zombies} zombies roaming")
    print(f"[{bar}]")

### END OF GAME ###

if "_" not in mask:
    print("🎉 Humanity saved! The molecule was:", secret_word)
    print("Antidote discovered, infection stopped.")
else:
    print("☠️ The world is lost…")
    print("Zombies rule the Earth. The molecule was:", secret_word)
