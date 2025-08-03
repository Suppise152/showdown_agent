from typing import List

from poke_env.player import Player
from poke_env.battle import AbstractBattle
from poke_env.battle.move_category import MoveCategory
from poke_env.battle.pokemon import Pokemon
from poke_env.battle.side_condition import SideCondition
from poke_env.player.battle_order import BattleOrder


team = """
Zacian-Crowned @ Rusted Sword
Ability: Intrepid Sword
Tera Type: Fairy
EVs: 252 Atk / 4 SpD / 252 Spe
Jolly Nature
- Behemoth Blade
- Close Combat
- Play Rough
- Substitute

Eternatus @ Leftovers
Ability: Pressure
Tera Type: Poison
EVs: 252 HP / 252 SpA / 4 SpD
Modest Nature
- Dynamax Cannon
- Sludge Bomb
- Recover
- Toxic

Mewtwo @ Life Orb
Ability: Pressure
Tera Type: Psychic
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Psystrike
- Aura Sphere
- Calm Mind
- Ice Beam

Landorus-Therian @ Choice Scarf
Ability: Intimidate
Tera Type: Ground
EVs: 252 Atk / 4 Def / 252 Spe
Jolly Nature
- Earthquake
- U-turn
- Stone Edge
- Rock Slide

Blissey @ Leftovers
Ability: Natural Cure
Tera Type: Fairy
EVs: 252 HP / 252 Def / 4 SpD
Bold Nature
- Seismic Toss
- Soft-Boiled
- Thunder Wave
- Heal Bell

Dragapult @ Choice Specs
Ability: Infiltrator
Tera Type: Dragon
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Draco Meteor
- Shadow Ball
- Flamethrower
- U-turn
"""


# sdssddddd
class CustomAgent(Player):
    ENTRY_HAZARDS = {
        "spikes": SideCondition.SPIKES,
        "stealthrock": SideCondition.STEALTH_ROCK,
        "stickyweb": SideCondition.STICKY_WEB,
        "toxicspikes": SideCondition.TOXIC_SPIKES,
    }

    ANTI_HAZARDS_MOVES = {"rapidspin", "defog"}
    SPEED_COEF = 0.1
    HP_COEF = 0.4
    MATCHUP_THRESHOLD = -2

    def __init__(self, *args, **kwargs):
        super().__init__(team=team, *args, **kwargs)

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        return self.choose_random_move(battle)
