from typing import List

from poke_env.player import Player
from poke_env.battle import AbstractBattle
from poke_env.battle.move_category import MoveCategory
from poke_env.battle.pokemon import Pokemon
from poke_env.battle.side_condition import SideCondition
from poke_env.player.battle_order import BattleOrder


# team = """
# Zacian-Crowned @ Rusted Sword
# Ability: Intrepid Sword
# Tera Type: Fairy
# EVs: 252 Atk / 4 SpD / 252 Spe
# Jolly Nature
# - Behemoth Blade
# - Close Combat
# - Play Rough
# - Substitute

# Eternatus @ Leftovers
# Ability: Pressure
# Tera Type: Poison
# EVs: 252 HP / 252 SpA / 4 SpD
# Modest Nature
# - Dynamax Cannon
# - Sludge Bomb
# - Recover
# - Toxic

# Mewtwo @ Life Orb
# Ability: Pressure
# Tera Type: Psychic
# EVs: 252 SpA / 4 SpD / 252 Spe
# Timid Nature
# - Psystrike
# - Aura Sphere
# - Calm Mind
# - Ice Beam

# Landorus-Therian @ Choice Scarf
# Ability: Intimidate
# Tera Type: Ground
# EVs: 252 Atk / 4 Def / 252 Spe
# Jolly Nature
# - Earthquake
# - U-turn
# - Stone Edge
# - Rock Slide

# Blissey @ Leftovers
# Ability: Natural Cure
# Tera Type: Fairy
# EVs: 252 HP / 252 Def / 4 SpD
# Bold Nature
# - Seismic Toss
# - Soft-Boiled
# - Thunder Wave
# - Heal Bell

# Dragapult @ Choice Specs
# Ability: Infiltrator
# Tera Type: Dragon
# EVs: 252 SpA / 4 SpD / 252 Spe
# Timid Nature
# - Draco Meteor
# - Shadow Ball
# - Flamethrower
# - U-turn
# """


class CustomAgent(Player):
    ENTRY_HAZARDS = {
        "spikes": SideCondition.SPIKES,
        "stealthrock": SideCondition.STEALTH_ROCK,
        "stickyweb": SideCondition.STICKY_WEB,
        "toxicspikes": SideCondition.TOXIC_SPIKES,
    }

    ANTI_HAZARDS_MOVES = {"rapidspin", "defog"}
    # aaa
    SPEED_COEF = 0.1
    HP_COEF = 0.4
    MATCHUP_THRESHOLD = -2

    def __init__(self, team, *args, **kwargs):
        super().__init__(team=team, *args, **kwargs)

    def _estimate_matchup(self, mon: Pokemon, opponent: Pokemon) -> float:
        if not mon or not opponent:
            return 0
        score = max([opponent.damage_multiplier(t) for t in mon.types if t]) - max(
            [mon.damage_multiplier(t) for t in opponent.types if t]
        )

        if mon.base_stats["spe"] > opponent.base_stats["spe"]:
            score += self.SPEED_COEF
        elif opponent.base_stats["spe"] > mon.base_stats["spe"]:
            score -= self.SPEED_COEF

        score += mon.current_hp_fraction * self.HP_COEF
        score -= opponent.current_hp_fraction * self.HP_COEF
        return score

    def _stat_boosted(self, mon: Pokemon, stat: str) -> float:
        base = mon.base_stats[stat]
        boost_level = mon.boosts[stat]
        if boost_level > 0:
            boost = (2 + boost_level) / 2
        elif boost_level < 0:
            boost = 2 / (2 - boost_level)
        else:
            boost = 1
        return ((2 * base + 31) + 5) * boost

    def _should_dynamax(self, battle: AbstractBattle, remaining: int) -> bool:
        active = battle.active_pokemon
        opponent = battle.opponent_active_pokemon
        if not active or not opponent or not battle.can_dynamax:
            return False
        if remaining == 1:
            return True
        if (
            active.current_hp_fraction == 1
            and self._estimate_matchup(active, opponent) > 0
        ):
            return True
        return False

    def _should_switch_out(self, battle: AbstractBattle) -> bool:
        active = battle.active_pokemon
        opponent = battle.opponent_active_pokemon
        if not active or not opponent:
            return False
        if [
            mon
            for mon in battle.available_switches
            if self._estimate_matchup(mon, opponent) > 0
        ]:
            if active.boosts["def"] <= -3 or active.boosts["spd"] <= -3:
                return True
            if (
                active.boosts["atk"] <= -3
                and active.stats["atk"] >= active.stats["spa"]
            ):
                return True
            if (
                active.boosts["spa"] <= -3
                and active.stats["spa"] >= active.stats["atk"]
            ):
                return True
            if self._estimate_matchup(active, opponent) < self.MATCHUP_THRESHOLD:
                return True
        return False

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        active = battle.active_pokemon
        opponent = battle.opponent_active_pokemon

        if not active or not opponent:
            return self.choose_random_move(battle)

        phys_ratio = self._stat_boosted(active, "atk") / self._stat_boosted(
            opponent, "def"
        )
        spec_ratio = self._stat_boosted(active, "spa") / self._stat_boosted(
            opponent, "spd"
        )

        remaining = len([m for m in battle.team.values() if not m.fainted])
        opp_remaining = 6 - len([m for m in battle.opponent_team.values() if m.fainted])

        if battle.available_moves and (
            not self._should_switch_out(battle) or not battle.available_switches
        ):
            for move in battle.available_moves:
                if (
                    opp_remaining >= 3
                    and move.id in self.ENTRY_HAZARDS
                    and self.ENTRY_HAZARDS[move.id]
                    not in battle.opponent_side_conditions
                ):
                    return self.create_order(move)
                if (
                    battle.side_conditions
                    and move.id in self.ANTI_HAZARDS_MOVES
                    and remaining >= 2
                ):
                    return self.create_order(move)

            if (
                active.current_hp_fraction == 1
                and self._estimate_matchup(active, opponent) > 0
            ):
                for move in battle.available_moves:
                    if (
                        move.boosts
                        and sum(move.boosts.values()) >= 2
                        and move.target == "self"
                    ):
                        if (
                            min(
                                [
                                    active.boosts[stat]
                                    for stat, val in move.boosts.items()
                                    if val > 0
                                ]
                            )
                            < 6
                        ):
                            return self.create_order(move)

            best_move = max(
                battle.available_moves,
                key=lambda m: m.base_power
                * (1.5 if m.type in active.types else 1)
                * (phys_ratio if m.category == MoveCategory.PHYSICAL else spec_ratio)
                * m.accuracy
                * m.expected_hits
                * opponent.damage_multiplier(m),
            )
            return self.create_order(
                best_move, dynamax=self._should_dynamax(battle, remaining)
            )

        if battle.available_switches:
            best_switch = max(
                battle.available_switches,
                key=lambda mon: self._estimate_matchup(mon, opponent),
            )
            return self.create_order(best_switch)

        return self.choose_random_move(battle)
