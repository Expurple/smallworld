"""Tests for `smawg.engine` module.

This module can also be seen as a collection of usage examples.
"""

import json
import unittest
from contextlib import nullcontext

import jsonschema.exceptions

from smawg import _ASSETS_DIR
from smawg.engine import Ability, Game, GameEnded, Race, RulesViolation


class TestAbility(unittest.TestCase):
    """Tests for `smawg.engine.Ability` class."""

    def test_valid_json(self):
        """Check if `Ability.__init__` propetly parses the given json."""
        ability = Ability({"name": "Some Name", "n_tokens": 4})
        self.assertEqual(ability.name, "Some Name")
        self.assertEqual(ability.n_tokens, 4)

    def test_invalid_jsons(self):
        """Check if `Ability.__init__` raises when given invalid jsons."""
        # Missing "name" and "n_tokens"
        self.assertInvalid({"random keys": "and values"})
        self.assertInvalid({})
        # Missing "name"
        self.assertInvalid({"n_tokens": 4})
        # Missing "n_tokens"
        self.assertInvalid({"name": "Some Name"})
        # Invalid type of "n_tokens"
        self.assertInvalid({"name": "Some Name", "n_tokens": None})
        self.assertInvalid({"name": "Some Name", "n_tokens": 4.5})
        self.assertInvalid({"name": "Some Name", "n_tokens": "4"})
        # Invalid value of "n_tokens"
        self.assertInvalid({"name": "Some Name", "n_tokens": -4})

    def assertInvalid(self, json: dict):
        """Check if `Ability.__init__` raises when given this `json`."""
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            _ = Ability(json)


class TestRace(unittest.TestCase):
    """Tests for `smawg.engine.Race` class."""

    INVALID_JSONS = [
        # Missing required properties
        {"random keys": "and values"},
        {},
        {"n_tokens": 4, "max_n_tokens": 9},
        {"name": "Some Name", "max_n_tokens": 9},
        {"name": "Some Name", "n_tokens": 4},
        # Invalid types
        {"name": None, "n_tokens": 4, "max_n_tokens": 9},
        {"name": "Some Name", "n_tokens": 4.5, "max_n_tokens": 9},
        {"name": "Some Name", "n_tokens": 4, "max_n_tokens": None},
        # Invalid values
        {"name": "Some Name", "n_tokens": -4, "max_n_tokens": 9},
        {"name": "Some Name", "n_tokens": 4, "max_n_tokens": -9}
    ]

    def test_valid_json(self):
        """Check if `Race.__init__` propetly parses the given json."""
        race = Race({"name": "Some Name", "n_tokens": 4, "max_n_tokens": 9})
        self.assertEqual(race.name, "Some Name")
        self.assertEqual(race.n_tokens, 4)
        self.assertEqual(race.max_n_tokens, 9)

    def test_invalid_jsons(self):
        """Check if `Race.__init__` raises when given invalid jsons."""
        for j in TestRace.INVALID_JSONS:
            self.assertInvalid(j)

    def assertInvalid(self, json: dict):
        """Check if `Race.__init__` raises when given this `json`."""
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            _ = Race(json)


class TestGame(unittest.TestCase):
    """General tests for `smawg.engine.Game` class.

    Test for particular methods are extracted into separate test fixtures.
    """

    @classmethod
    def setUpClass(cls):
        """Preload game assets once."""
        with open(f"{_ASSETS_DIR}/tiny.json") as file:
            cls.TINY_ASSETS: dict = json.load(file)

    def test_tiny_game_scenario(self):
        """Run a full game based on `tiny.json` asssets.

        Make sure that valid gameplay doesn't raise any exceptions.
        Then, check if all `Game` methods raise `GameEnded` after the game end.
        """
        game = Game(TestGame.TINY_ASSETS, shuffle_data=False)
        with nullcontext("Player 0, turn 1:"):
            game.select_combo(1)
            game.conquer(0)
            game.conquer(1)
            game.conquer(2)
            game.end_turn()
        with nullcontext("Player 1, turn 1:"):
            game.select_combo(0)
            game.conquer(3)
            game.conquer(0)
            game.end_turn()
        with nullcontext("Both players do nothing on turns 2-3:"):
            for _ in range(2):
                game.deploy(game.player.tokens_on_hand, 1)
                game.end_turn()
                game.deploy(game.player.tokens_on_hand, 3)
                game.end_turn()
        self.assertEnded(game)

    def test_redeployment_pseudo_turn(self):
        """Check if redeployment pseudo-turn works as expected."""
        assets = {**TestGame.TINY_ASSETS, "n_players": 3}
        game = Game(assets, shuffle_data=False)
        with nullcontext("Player 0, turn 1:"):
            game.select_combo(0)
            game.conquer(0)
            game.conquer(1)
            game.conquer(2)
            game.end_turn()
        with nullcontext("Player 1, turn 1:"):
            game.select_combo(0)
            game.conquer(3)
            game.conquer(0)  # Region owned by player 0.
            game.end_turn()
        with nullcontext("Player 0 redeploys tokens:"):
            self.assertEqual(game.player_id, 0)
            self.assertEqual(game.player.tokens_on_hand, 2)
            with self.assertRaises(RulesViolation):
                game.select_combo(0)  # Method not allowed during redeployment.
            with self.assertRaises(RulesViolation):
                game.conquer(4)  # Method not allowed during redeployment.
            with self.assertRaises(RulesViolation):
                game.decline()  # Method not allowed during redeployment.
            with self.assertRaises(RulesViolation):
                game.end_turn()  # Must redeploy tokens first.
            game.deploy(game.player.tokens_on_hand, 1)
            game.end_turn()
        with nullcontext("Player 2, turn 1:"):
            self.assertEqual(game.current_turn, 1)
            self.assertEqual(game.player_id, 2)

    def test_coin_rewards(self):
        """Check if coin rewards work as expected."""
        game = Game(TestGame.TINY_ASSETS, shuffle_data=False)
        self.assertBalances(game, [1, 1])  # Initial coin balances
        with nullcontext("Player 0, turn 1:"):
            game.select_combo(1)
            self.assertBalances(game, [0, 1])  # Paid 1 coin for combo 1
            game.conquer(0)
            game.conquer(1)
            game.conquer(2)
            game.end_turn()
        self.assertBalances(game, [3, 1])  # Reward for active regions
        with nullcontext("Player 1, turn 1:"):
            game.select_combo(0)
            self.assertBalances(game, [3, 2])  # Combo 0 had coin from player 0
            game.conquer(3)
            game.conquer(0)
            game.end_turn()
        self.assertBalances(game, [3, 4])  # Reward for active regions
        with nullcontext("Player 0, turn 2:"):
            game.decline()
            game.end_turn()
        self.assertBalances(game, [5, 4])  # Reward for decline regions 1 and 2

    def assertBalances(self, game: Game, expected: list[int]):
        """Check if all player balances match the `expected`."""
        actual = [p.coins for p in game.players]
        msg = "Player has incorrect amount of coins"
        self.assertListEqual(actual, expected, msg=msg)

    def assertEnded(self, game: Game):
        """Check if `game` is in end state and all methods raise GameEnded."""
        self.assertTrue(game.has_ended)
        with self.assertRaises(GameEnded):
            game.select_combo(0)
        with self.assertRaises(GameEnded):
            game.decline()
        with self.assertRaises(GameEnded):
            game.conquer(0)
        with self.assertRaises(GameEnded):
            game.start_redeployment()
        with self.assertRaises(GameEnded):
            game.deploy(1, 0)
        with self.assertRaises(GameEnded):
            game.end_turn()


class TestGameDecline(unittest.TestCase):
    """Tests for `smawg.engine.Game.decline()` method."""

    def test_exceptions(self):
        """Check if the method raises expected exceptions.

        This doesn't include `GameEnded`, which is tested separately for
        convenience.
        """
        assets = {**TestGame.TINY_ASSETS, "n_players": 1}
        game = Game(assets, shuffle_data=False)
        with nullcontext("Player 0, turn 1:"):
            with self.assertRaises(RulesViolation):
                game.decline()  # There's no active race yet.
            game.select_combo(0)
            with self.assertRaises(RulesViolation):
                game.decline()  # Just got a new race during this turn.
            game.conquer(0)
            game.deploy(game.player.tokens_on_hand, 0)
            game.end_turn()
        with nullcontext("Player 0, turn 2:"):
            game.conquer(1)
            with self.assertRaises(RulesViolation):
                game.decline()  # Already used the active race during this turn
            game.deploy(game.player.tokens_on_hand, 1)
            game.end_turn()
        with nullcontext("Player 0, turn 3:"):
            game.decline()
            with self.assertRaises(RulesViolation):
                game.decline()  # Already in decline


class TestGameSelectCombo(unittest.TestCase):
    """Tests for `smawg.engine.Game.select_combo()` method."""

    def test_exceptions(self):
        """Check if the method raises expected exceptions.

        This doesn't include `GameEnded`, which is tested separately for
        convenience.
        """
        assets = {**TestGame.TINY_ASSETS, "n_players": 1}
        game = Game(assets, shuffle_data=False)
        with nullcontext("Player 0, turn 1:"):
            for combo in [-10, -1, len(game.combos), 999]:
                # "combo_index must be between 0 and {len(game.combos)}"
                with self.assertRaises(ValueError):
                    game.select_combo(combo)
            game.select_combo(0)
            with self.assertRaises(RulesViolation):
                game.select_combo(0)  # The player isn't in decline.
            game.conquer(0)
            game.deploy(game.player.tokens_on_hand, 0)
            game.end_turn()
        with nullcontext("Player 0, turn 2:"):
            game.decline()
            with self.assertRaises(RulesViolation):
                game.select_combo(0)  # Has just declined during this turn.


class TestGameConquer(unittest.TestCase):
    """Tests for `smawg.engine.Game.conquer()` method."""

    def test_functionality(self):
        """Check if the method behaves as expected if used correctly."""
        game = Game(TestGame.TINY_ASSETS, shuffle_data=False)
        with nullcontext("Player 0, turn 1:"):
            game.select_combo(1)
            self.assertEqual(game.players[0].tokens_on_hand, 9)
            game.conquer(0)
            self.assertEqual(game.players[0].tokens_on_hand, 6)
            self.assertEqual(game.players[0].active_regions, {0: 3})
            game.conquer(1)
            self.assertEqual(game.players[0].tokens_on_hand, 3)
            self.assertEqual(game.players[0].active_regions, {0: 3, 1: 3})
            game.conquer(2)
            self.assertEqual(game.players[0].tokens_on_hand, 0)
            self.assertEqual(game.players[0].active_regions,
                             {0: 3, 1: 3, 2: 3})
            game.end_turn()
        with nullcontext("Player 1, turn 1:"):
            game.select_combo(0)
            game.conquer(3)
            self.assertEqual(game.players[1].tokens_on_hand, 6)
            self.assertEqual(game.players[1].active_regions, {3: 3})
            game.conquer(0)
            self.assertEqual(game.players[1].tokens_on_hand, 0)
            self.assertEqual(game.players[1].active_regions, {0: 6, 3: 3})
            self.assertEqual(game.players[0].tokens_on_hand, 2)
            self.assertEqual(game.players[0].active_regions, {1: 3, 2: 3})

    def test_exceptions(self):
        """Check if the method raises expected exceptions.

        This doesn't include `GameEnded`, which is tested separately for
        convenience.
        """
        game = Game(TestGame.TINY_ASSETS, shuffle_data=False)
        with self.assertRaises(RulesViolation):
            game.conquer(0)  # Attempt to conquer without an active race.
        game.select_combo(0)
        for region in [-10, -1, len(TestGame.TINY_ASSETS["map"]["tiles"]), 99]:
            # "region must be between 0 and {len(assets["map"]["tiles"])}"
            with self.assertRaises(ValueError):
                game.conquer(region)
        with self.assertRaises(RulesViolation):
            game.conquer(2)  # First conquest not at the map border.
        game.conquer(0)
        with self.assertRaises(RulesViolation):
            game.conquer(0)  # Attempt to conquer own region.
        with self.assertRaises(RulesViolation):
            game.conquer(4)  # Attempt to conquer non-adjacent region.
        game.conquer(1)
        game.conquer(2)
        with self.assertRaises(RulesViolation):
            game.conquer(3)  # Not enough tokens on hand.
        game.start_redeployment()
        with self.assertRaises(RulesViolation):
            game.conquer(3)  # Attempt to conquer during redeployment.


class TestGameStartRedeployment(unittest.TestCase):
    """Tests for `smawg.engine.Game.start_redeployment()` method."""

    def test_functionality(self):
        """Check if the method behaves as expected when used correctly."""
        assets = {**TestGame.TINY_ASSETS, "n_players": 1}
        game = Game(assets, shuffle_data=False)
        game.select_combo(0)
        TOKENS_TOTAL = game.player.tokens_on_hand
        game.conquer(0)
        game.conquer(1)
        self.assertDictEqual(game.player.active_regions, {0: 3, 1: 3})
        self.assertEqual(game.player.tokens_on_hand, TOKENS_TOTAL - 6)
        game.start_redeployment()
        self.assertDictEqual(game.player.active_regions, {0: 1, 1: 1})
        self.assertEqual(game.player.tokens_on_hand, TOKENS_TOTAL - 2)

    def test_exceptions(self):
        """Check if the method raises expected exceptions.

        This doesn't include `GameEnded`, which is tested separately for
        convenience.
        """
        assets = {**TestGame.TINY_ASSETS, "n_players": 1}
        game = Game(assets, shuffle_data=False)
        with nullcontext("Player 0, turn 1:"):
            with self.assertRaises(RulesViolation):
                game.start_redeployment()  # No active race.
            game.select_combo(0)
            with self.assertRaises(RulesViolation):
                game.start_redeployment()  # No active regions to redeploy to.
            game.conquer(0)
            game.start_redeployment()
            game.deploy(game.player.tokens_on_hand, 0)
            with self.assertRaises(RulesViolation):
                game.start_redeployment()  # Called during redeployment.
            game.end_turn()
        with nullcontext("Player 0, turn 2:"):
            game.decline()
            with self.assertRaises(RulesViolation):
                game.start_redeployment()  # No active race.


class TestGameDeploy(unittest.TestCase):
    """Tests for `smawg.engine.Game.deploy()` method."""

    def test_functionality(self):
        """Check if the method behaves as expected when used correctly."""
        game = Game(TestGame.TINY_ASSETS, shuffle_data=False)
        CHOSEN_COMBO = 0
        CHOSEN_REGION = 0
        game.select_combo(CHOSEN_COMBO)
        TOKENS_TOTAL = game.combos[CHOSEN_COMBO].base_n_tokens
        game.conquer(CHOSEN_REGION)
        self.assertEqual(game.player.tokens_on_hand, TOKENS_TOTAL - 3)
        self.assertEqual(game.player.active_regions,
                         {CHOSEN_REGION: 3})
        game.deploy(game.player.tokens_on_hand, CHOSEN_REGION)
        self.assertEqual(game.player.tokens_on_hand, 0)
        self.assertEqual(game.player.active_regions,
                         {CHOSEN_REGION: TOKENS_TOTAL})

    def test_exceptions(self):
        """Check if the method raises expected exceptions.

        This doesn't include `GameEnded`, which is tested separately for
        convenience.
        """
        game = Game(TestGame.TINY_ASSETS, shuffle_data=False)
        CHOSEN_COMBO = 0
        CHOSEN_REGION = 0
        game.select_combo(CHOSEN_COMBO)
        with self.assertRaises(RulesViolation):
            # Must control the region.
            game.deploy(1, CHOSEN_REGION)
        game.conquer(CHOSEN_REGION)
        with self.assertRaises(RulesViolation):
            # Not enough tokens on hand.
            game.deploy(game.player.tokens_on_hand + 1, CHOSEN_REGION)
        for n_tokens in [-99, -1, 0]:
            # "n_tokens must be greater then 0"
            with self.assertRaises(ValueError):
                game.deploy(n_tokens, CHOSEN_REGION)
        for region in [-10, -1, len(TestGame.TINY_ASSETS["map"]["tiles"]), 99]:
            # "region must be between 0 and {len(assets["map"]["tiles"])}"
            with self.assertRaises(ValueError):
                game.deploy(1, region)


class TestGameEndTurn(unittest.TestCase):
    """Tests for `smawg.engine.Game.end_turn()` method."""

    def test_exceptions(self):
        """Check if the method raises expected exceptions.

        This doesn't include `GameEnded`, which is tested separately for
        convenience.
        """
        game = Game(TestGame.TINY_ASSETS, shuffle_data=False)
        with self.assertRaises(RulesViolation):  # Must pick a combo first.
            game.end_turn()
        game.select_combo(0)
        with self.assertRaises(RulesViolation):  # Must deploy tokens first.
            game.end_turn()
