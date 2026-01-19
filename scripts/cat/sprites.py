import logging
import os
from copy import copy

import pygame
import ujson

from scripts.cat.enums import CatGroup
from scripts.game_structure import constants, image_cache
from scripts.game_structure.game.settings import game_setting_get
from scripts.special_dates import SpecialDate, is_today

logger = logging.getLogger(__name__)


class Sprites:
    cat_tints = {}
    white_patches_tints = {}
    eye_colors = {}
    pelt_colors = {}
    skin_colors = {}
    clan_symbols = []

    def __init__(self):
        """Class that handles and hold all spritesheets.
        Size is normally automatically determined by the size
        of the lineart. If a size is passed, it will override
        this value."""
        self.symbol_dict = None
        self.size = None
        self.spritesheets = {}
        self.images = {}
        self.sprites = {}

        # Shared empty sprite for placeholders
        self.blank_sprite = None

        self.load_tints()
        self.load_spritesheet_json()
        self.load_pelt_jsons()

    def load_tints(self):
        try:
            with open("sprites/dicts/tint.json", "r", encoding="utf-8") as read_file:
                self.cat_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading Tints")

        try:
            with open(
                "sprites/dicts/white_patches_tint.json", "r", encoding="utf-8"
            ) as read_file:
                self.white_patches_tints = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading White Patches Tints")

    def load_pelt_jsons(self):
        # open eye colors
        try:
            with open("sprites/dicts/eye_colors.json", "r", encoding="utf-8") as read_file:
                self.eye_colors = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading eye_colors.json")

        # open white patches
        try:
            with open("sprites/dicts/white_patches.json", "r", encoding="utf-8") as read_file:
                self.white_patches = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading white_patches.json")

        # open pelt colors
        try:
            with open(
                "sprites/dicts/pelt_colors.json", "r", encoding="utf-8"
            ) as read_file:
                self.pelt_colors = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading pelt_colors.json")

        # open skin colors
        try:
            with open("sprites/dicts/skin_colors.json", "r", encoding="utf-8") as read_file:
                self.skin_colors = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading skin_colors.json")

        # open skin
        try:
            with open("sprites/dicts/skin.json", "r", encoding="utf-8") as read_file:
                self.skin = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading skin.json")

        # open accessories
        try:
            with open("sprites/dicts/accessories.json", "r", encoding="utf-8") as read_file:
                self.accessories = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading accessories.json")

        # open extra traits
        try:
            with open("sprites/dicts/extra_traits.json", "r", encoding="utf-8") as read_file:
                self.extra_traits = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading extra_traits.json")

        # open scars
        try:
            with open("sprites/dicts/scars.json", "r", encoding="utf-8") as read_file:
                self.scars = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading scars.json")

        # open tortie
        try:
            with open("sprites/dicts/tortie.json", "r", encoding="utf-8") as read_file:
                self.tortie = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading tortie.json")

    def load_spritesheet_json(self):
        # open modded sprites
        try:
            with open(
                "sprites/dicts/spritesheets.json", "r", encoding="utf-8"
            ) as read_file:
                self.spritesheets_json = ujson.loads(read_file.read())
        except IOError:
            print("ERROR: Reading pelt_colors.json")

    def spritesheet(self, a_file, name):
        """
        Add spritesheet called name from a_file.

        Parameters:
        a_file -- Path to the file to create a spritesheet from.
        name -- Name to call the new spritesheet.
        """
        self.spritesheets[name] = pygame.image.load(a_file).convert_alpha()

    def make_group(self,
                   spritesheet,
                   pos,
                   name,
                   sprites_x=3,
                   sprites_y=8,
                   no_index=False,
                    palettes: list = None):  # pos = ex. (2, 3), no single pixels

        """
        Divide sprites on a spritesheet into groups of sprites that are easily accessible
        :param spritesheet: Name of spritesheet file
        :param pos: (x,y) tuple of offsets. NOT pixel offset, but offset of other sprites
        :param name: Name of group being made
        :param sprites_x: default 3, number of sprites horizontally
        :param sprites_y: default 7, number of sprites vertically
        :param no_index: default False, set True if sprite name does not require cat pose index:
        :param palettes: list of palette names
        """
        # pulls the defaults from the pose_sprite_data.json file
        group_x_ofs = pos[0] * sprites_x * self.size
        group_y_ofs = pos[1] * sprites_y * self.size
        i = 0

        # splitting group into singular sprites and storing into self.sprites section
        for y in range(sprites_y):
            for x in range(sprites_x):
                if no_index:
                    full_name = f"{name}"
                else:
                    full_name = f"{name}{i}"

                try:
                    new_sprite = pygame.Surface.subsurface(
                        self.spritesheets[spritesheet],
                        group_x_ofs + x * self.size,
                        group_y_ofs + y * self.size,
                        self.size,
                        self.size,
                    )

                except ValueError:
                    # Fallback for non-existent sprites
                    print(f"WARNING: nonexistent sprite - {full_name}")
                    if not self.blank_sprite:
                        self.blank_sprite = pygame.Surface(
                            (self.size, self.size), pygame.HWSURFACE | pygame.SRCALPHA
                        )
                    new_sprite = self.blank_sprite

                if palettes:
                    self.apply_palettes(i, name, new_sprite, palettes)
                else:
                    self.sprites[full_name] = new_sprite
                i += 1

    def apply_palettes(
        self, sprite_index: int, name: str, new_sprite, palette_names: list
    ):
        """
        Creates sprites for each color palette variation
        :param sprite_index: index of sprite
        :param name: name of sprite
        :param new_sprite: the sprite object to create variations of
        :param palette_names: list of palette names
        """
        # first we create an array of our palette map
        full_map = pygame.image.load(f"sprites/palettes/{name}_palette.png")
        map_array = pygame.PixelArray(full_map)
        # then create a dictionary associating the palette name with its row of the array
        color_palettes = {}
        palette_names = palette_names.copy()
        palette_names.insert(0, "BASE")
        for row in range(
            0, map_array.shape[1]  # pylint: disable=unsubscriptable-object
        ):
            color_name = palette_names[row]
            color_palettes.update(
                {color_name: [full_map.unmap_rgb(px) for px in map_array[::, row]]}
            )

        base_palette = color_palettes["BASE"]

        # now we recolor the sprite
        for color_name, palette in color_palettes.items():
            if color_name == "BASE":
                continue
            recolor_sprite = pygame.PixelArray(new_sprite.copy())
            # we replace each base_palette color with it's matching index from the color_palette
            for color_i, color in enumerate(palette):
                recolor_sprite.replace(base_palette[color_i], color)
            # convert back into a surface
            _sprite = recolor_sprite.make_surface()
            # add it to our sprite dict!
            self.sprites[f"{name}_{color_name}{sprite_index}"] = _sprite
            # close the pixel array now that we're done
            recolor_sprite.close()

        map_array.close()

    def load_all(self):
        # get the width and height of the spritesheet
        lineart = pygame.image.load("sprites/lineart.png")
        width, height = lineart.get_size()
        del lineart  # unneeded

        # if anyone changes lineart for whatever reason update this
        if isinstance(self.size, int):
            pass
        elif width / 3 == height / 8:
            self.size = width / 3
        else:
            self.size = 50  # default, what base clangen uses
            print(
                f"lineart.png is strange, falling back to {self.size}"
            )
            print(
                f"if you are a modder, please update sheet_layout in sprites/dicts/pose_sprite_data.json"
            )

        del width, height  # unneeded

        for key, sheet in self.spritesheets_json.items():
            self.load_sheet(sheet, key)

        for x in [
            'lineart', 'base', 'wingsbase', 'batskin', 'wingmarks',
            'batmane', 'batmanemarkings',
            'eyesnew', 'scars', 'missingscars',
            'collars', 'bellcollars', 'bowcollars', 'nyloncollars', 'medcatherbs', 'wild', 
            'shadersnewwhite',
            'lightingnew', 'fademask',
            'fadestarclan', 'fadedarkforest', 'fadeunknownresidence',
            'wingscars',
            'symbols',
            'winglineart', 'winglineartdead', 'winglineartdf', 'winglineartur',
            "lineartur", "lineartdf", 'lineartdead',
            "line_ur_underlay",
            "line_ur_overlay",
            "line_sc_overlay",
            "gradient_ur"

        ]:
            if (
                "lineart" in x
                and (
                    constants.CONFIG["fun"]["april_fools"]
                    or is_today(SpecialDate.APRIL_FOOLS)
                )
                and x != "lineartur"
            ):
                self.spritesheet(f"sprites/{x}_aprilfools.png", x)
            else:
                self.spritesheet(f"sprites/{x}.png", x)


        # Lineart - this looks bad I'm too tired to make this neater
        self.make_group('lineart', (0, 0), 'lines')

        self.make_group('winglineart', (0, 0), 'bat cat_1_lines')
        self.make_group('winglineart', (1, 0), 'bird cat_1_lines')
        self.make_group('winglineart', (2, 0), 'bat cat_0_lines')
        self.make_group('winglineart', (3, 0), 'bird cat_0_lines')
        for a, i in enumerate(
                ['df', 'dead', 'ur']):
            self.make_group(f'lineart{i}', (0, 0), f'lineart{i}')
            self.make_group(f'winglineart{i}', (0, 0), f'bird cat_1_lineart{i}')
            self.make_group(f'winglineart{i}', (0, 1), f'bat cat_1_lineart{i}')
            self.make_group(f'winglineart{i}', (1, 0), f'bird cat_0_lineart{i}')
            self.make_group(f'winglineart{i}', (1, 1), f'bat cat_0_lineart{i}')

        self.make_group("line_sc_overlay", (0, 0), "sc_overlay")
        self.make_group("line_ur_underlay", (0, 0), "ur_underlay")
        self.make_group("line_ur_overlay", (0, 0), "ur_overlay")
        self.make_group("gradient_ur", (0, 0), "gradient_ur")

        # Base
        self.make_group('base', (0, 0), 'base')
        for a, i in enumerate(
                ['bat cat', 'bird cat']):
            self.make_group('wingsbase', (a, 0), f'{i}_1_base')
            self.make_group('wingsbase', (a, 1), f'{i}_0_base')

        # Bat skin
        self.make_group('batskin', (0, 0), 'batskin')
        
        # Eyes
        for a, i in enumerate(
                ['base', 'shade', 'pupil', 'shine']):
            self.make_group('eyesnew', (a, 0), f'eyes1{i}')
            self.make_group('eyesnew', (a, 1), f'eyes2{i}')

        # Shaders
        self.make_group('shadersnewwhite', (0, 0), 'shaders')
        self.make_group('shadersnewwhite', (1, 0), 'bat catshaders')
        self.make_group('shadersnewwhite', (2, 0), 'bird catshaders')

        #lighting
        self.make_group('lightingnew', (0, 0), 'lighting')
        self.make_group('lightingnew', (1, 0), 'bat catlighting')
        self.make_group('lightingnew', (2, 0), 'bird catlighting')

        # bird wing markings
        for a, i in enumerate(['FLECKS', 'TIPS', 'STRIPES', 'STREAKS', 'COVERTS', 'PRIMARIES', 'SPOTS']):
            self.make_group('wingmarks', (a, 0), f'bird catwingmarks{i}')

        # bat mane
        for a, i in enumerate(['lines', 'base', 'shaders', 'lighting', 'lineartdead', 'lineartdf']):
            self.make_group('batmane', (a, 0), f'bat_mane{i}')
        for a, i in enumerate(['overfur', 'underfur']):
            self.make_group('batmane', (a, 1), f'bat_mane{i}')

        # bat mane markings
        for a, i in enumerate(['FULL', 'FADE', 'INVERTFADE', 'STRIPES', 'SPOTS', 'SMOKE']):
            self.make_group('batmanemarkings', (a, 0), f'bat_manemarkings{i}')

        # Fading Fog
        for i in range(0, 3):
            self.make_group("fademask", (i, 0), f"fademask{i}")
            self.make_group("fadestarclan", (i, 0), f"fadestarclan{i}")
            self.make_group("fadedarkforest", (i, 0), f"fadedf{i}")
            self.make_group("fadeunknownresidence", (i, 0), f"fadeur{i}")


        # Define skin colors 
        skin_colors = [
            ["BLACK", "RED", "PINK", "DARKBROWN", "BROWN", "LIGHTBROWN"],
            ["DARK", "DARKGREY", "GREY", "DARKSALMON", "SALMON", "PEACH"],
            ["DARKMARBLED", "MARBLED", "LIGHTMARBLED", "DARKBLUE", "BLUE", "LIGHTBLUE"],
        ]

        for row, colors in enumerate(skin_colors):
            for col, color in enumerate(colors):
                self.make_group("skin", (col, row), f"skin{color}")

        self.load_scars()
        self.load_accessories()
        self.load_symbols()

    def load_scars(self):

        # Define scars
        scars_data = [
            [
                "ONE",
                "TWO",
                "THREE",
                "MANLEG",
                "BRIGHTHEART",
                "MANTAIL",
                "BRIDGE",
                "RIGHTBLIND",
                "LEFTBLIND",
                "BOTHBLIND",
                "BURNPAWS",
                "BURNTAIL",
            ],
            [
                "BURNBELLY",
                "BEAKCHEEK",
                "BEAKLOWER",
                "BURNRUMP",
                "CATBITE",
                "RATBITE",
                "FROSTFACE",
                "FROSTTAIL",
                "FROSTMITT",
                "FROSTSOCK",
                "QUILLCHUNK",
                "QUILLSCRATCH",
            ],
            [
                "TAILSCAR",
                "SNOUT",
                "CHEEK",
                "SIDE",
                "THROAT",
                "TAILBASE",
                "BELLY",
                "TOETRAP",
                "SNAKE",
                "LEGBITE",
                "NECKBITE",
                "FACE",
            ],
            [
                "HINDLEG",
                "BACK",
                "QUILLSIDE",
                "SCRATCHSIDE",
                "TOE",
                "BEAKSIDE",
                "CATBITETWO",
                "SNAKETWO",
                "FOUR",
            ],
        ]

        # define missing parts
        missing_parts_data = [
            [
                "LEFTEAR",
                "RIGHTEAR",
                "NOTAIL",
                "NOLEFTEAR",
                "NORIGHTEAR",
                "NOEAR",
                "HALFTAIL",
                "NOPAW",
            ]
        ]

        # scars
        for row, scars in enumerate(scars_data):
            for col, scar in enumerate(scars):
                self.make_group("scars", (col, row), f"scars{scar}")

        # missing parts
        for row, missing_parts in enumerate(missing_parts_data):
            for col, missing_part in enumerate(missing_parts):
                self.make_group("missingscars", (col, row), f"scars{missing_part}")

        # wing scars
        for a, i in enumerate(['CLIPPED']):
            self.make_group('wingscars', (a, 0), f'bat catscar{i}')
            self.make_group('wingscars', (a, 1), f'bird catscar{i}')
            self.make_group('wingscars', (a, 2), f'bat catbackscar{i}')
            self.make_group('wingscars', (a, 3), f'bird catbackscar{i}')

    def load_accessories(self):
        # accessories
        # to my beloved modders, im very sorry for reordering everything <333 -clay
        medcatherbs_data = [
            [
                "MAPLE LEAF",
                "HOLLY",
                "BLUE BERRIES",
                "FORGET ME NOTS",
                "RYE STALK",
                "CATTAIL",
                "POPPY",
                "ORANGE POPPY",
                "CYAN POPPY",
                "WHITE POPPY",
                "PINK POPPY",
            ],
            [
                "BLUEBELLS",
                "LILY OF THE VALLEY",
                "SNAPDRAGON",
                "HERBS",
                "PETALS",
                "NETTLE",
                "HEATHER",
                "GORSE",
                "JUNIPER",
                "RASPBERRY",
                "LAVENDER",
            ],
            [
                "OAK LEAVES",
                "CATMINT",
                "MAPLE SEED",
                "LAUREL",
                "BULB WHITE",
                "BULB YELLOW",
                "BULB ORANGE",
                "BULB PINK",
                "BULB BLUE",
                "CLOVER",
                "DAISY",
            ],
            [
                "WISTERIA",
                "ROSE MALLOW",
                "PICKLEWEED",
                "GOLDEN CREEPING JENNY",
                "DESERT WILLOW",
                "CACTUS FLOWER",
                "PRAIRIE FIRE",
                "VERBENA EAR",
                "VERBENA PELT",
            ],
        ]
        dryherbs_data = [["DRY HERBS", "DRY CATMINT", "DRY NETTLES", "DRY LAURELS"]]
        wild_data = [
            [
                "RED FEATHERS",
                "BLUE FEATHERS",
                "JAY FEATHERS",
                "GULL FEATHERS",
                "SPARROW FEATHERS",
                "MOTH WINGS",
                "ROSY MOTH WINGS",
                "MORPHO BUTTERFLY",
                "MONARCH BUTTERFLY",
                "CICADA WINGS",
                "BLACK CICADA",
            ],
            [
                "ROAD RUNNER FEATHER",
            ],
        ]

        collars_data = [
            ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"],
            ["GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE"],
            ["PINK", "PURPLE", "MULTI", "INDIGO"],
        ]

        bellcollars_data = [
            [
                "CRIMSONBELL",
                "BLUEBELL",
                "YELLOWBELL",
                "CYANBELL",
                "REDBELL",
                "LIMEBELL",
            ],
            ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL"],
            ["PINKBELL", "PURPLEBELL", "MULTIBELL", "INDIGOBELL"],
        ]

        bowcollars_data = [
            ["CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW"],
            ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW"],
            ["PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW"],
        ]

        nyloncollars_data = [
            [
                "CRIMSONNYLON",
                "BLUENYLON",
                "YELLOWNYLON",
                "CYANNYLON",
                "REDNYLON",
                "LIMENYLON",
            ],
            ["GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON"],
            ["PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON"],
        ]

        # medcatherbs
        for row, herbs in enumerate(medcatherbs_data):
            for col, herb in enumerate(herbs):
                self.make_group("medcatherbs", (col, row), f"acc_herbs{herb}")
        # dryherbs
        for row, dry in enumerate(dryherbs_data):
            for col, dryherbs in enumerate(dry):
                self.make_group("medcatherbs", (col, 4), f"acc_herbs{dryherbs}")
        # wild
        for row, wilds in enumerate(wild_data):
            for col, wild in enumerate(wilds):
                self.make_group("wild", (col, row), f"acc_wild{wild}")

        # collars
        for row, collars in enumerate(collars_data):
            for col, collar in enumerate(collars):
                self.make_group("collars", (col, row), f"collars{collar}")

        # bellcollars
        for row, bellcollars in enumerate(bellcollars_data):
            for col, bellcollar in enumerate(bellcollars):
                self.make_group("bellcollars", (col, row), f"collars{bellcollar}")

        # bowcollars
        for row, bowcollars in enumerate(bowcollars_data):
            for col, bowcollar in enumerate(bowcollars):
                self.make_group("bowcollars", (col, row), f"collars{bowcollar}")

        # nyloncollars
        for row, nyloncollars in enumerate(nyloncollars_data):
            for col, nyloncollar in enumerate(nyloncollars):
                self.make_group("nyloncollars", (col, row), f"collars{nyloncollar}")

    def load_sheet(self, data, file):
        # load file as sheet
        self.spritesheet(f"sprites/{file}.png", file)

        # create sprites
        for row, items in enumerate(data["sprite_names"]):
            for col, item in enumerate(items):
                if "types" in data:
                    self.make_group(file, (col, row), f"{data['types'][row]}{item}")
                    print(f"Loaded: {item}, {file} - {data['types'][row]}{item}")
                else:
                    self.make_group(file, (col, row), f"{data['type']}{item}")
                    print(f"Loaded: {item}, {file} - {data['type']}{item}")

    def load_symbols(self):
        """
        loads clan symbols
        """

        if os.path.exists("resources/dicts/clan_symbols.json"):
            with open(
                "resources/dicts/clan_symbols.json", encoding="utf-8"
            ) as read_file:
                self.symbol_dict = ujson.loads(read_file.read())

        # U and X omitted from letter list due to having no prefixes
        letters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "V",
            "W",
            "Y",
            "Z",
        ]

        # sprite names will format as "symbol{PREFIX}{INDEX}", ex. "symbolSPRING0"
        y_pos = 1
        for letter in letters:
            x_mod = 0
            for i, symbol in enumerate(
                [
                    symbol
                    for symbol in self.symbol_dict
                    if letter in symbol and self.symbol_dict[symbol]["variants"]
                ]
            ):
                if self.symbol_dict[symbol]["variants"] > 1 and x_mod > 0:
                    x_mod += -1
                for variant_index in range(self.symbol_dict[symbol]["variants"]):
                    x_pos = i + x_mod

                    if self.symbol_dict[symbol]["variants"] > 1:
                        x_mod += 1
                    elif x_mod > 0:
                        x_pos += -1

                    self.clan_symbols.append(f"symbol{symbol.upper()}{variant_index}")
                    self.make_group(
                        "symbols",
                        (x_pos, y_pos),
                        f"symbol{symbol.upper()}{variant_index}",
                        sprites_x=1,
                        sprites_y=1,
                        no_index=True,
                    )

            y_pos += 1

    def get_symbol(self, symbol: str, force_light=False):
        """Change the color of the symbol to match the requested theme, then return it
        :param Surface symbol: The clan symbol to convert
        :param force_light: Use to ignore dark mode and always display the light mode color
        """
        symbol = self.sprites.get(symbol)
        if symbol is None:
            logger.warning("%s is not a known Clan symbol! Using default.")
            symbol = self.sprites[self.clan_symbols[0]]

        recolored_symbol = copy(symbol)
        var = pygame.PixelArray(recolored_symbol)
        var.replace(
            (87, 76, 45),
            (
                pygame.Color(constants.CONFIG["theme"]["dark_mode_clan_symbols"])
                if not force_light and game_setting_get("dark mode")
                else pygame.Color(constants.CONFIG["theme"]["light_mode_clan_symbols"])
            ),
            distance=0,
        )
        del var

        return recolored_symbol

    @staticmethod
    def get_platform(biome, season, show_nest, group: CatGroup) -> pygame.Surface:
        """
        Returns the relevant platform
        :param biome: The current game biome
        :param season: The current game season
        :param show_nest: If true, displays the nest
        :param group: Used to determine appropriate afterlife platform
        :return: pygame.Surface containing the desired platform
        """
        offset = 0 if game_setting_get("dark mode") else 80
        """Used to choose the dark mode version of platforms"""

        available_biome = ["Forest", "Mountainous", "Plains", "Beach"]

        if biome not in available_biome:
            biome = available_biome[0]
        if show_nest:
            biome = "nest"

        biome = biome.lower()

        platformsheet = image_cache.load_image(
            "resources/images/platforms.png"
        ).convert_alpha()

        order = ["beach", "forest", "mountainous", "nest", "plains", "dead"]

        if group and group.is_afterlife():
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index("dead") * 70, 640, 70)
            )

            if group == CatGroup.DARK_FOREST:
                return biome_platforms.subsurface(pygame.Rect(0 + offset, 0, 80, 70))
            elif group == CatGroup.STARCLAN:
                return biome_platforms.subsurface(pygame.Rect(160 + offset, 0, 80, 70))
            elif group == CatGroup.UNKNOWN_RESIDENCE:
                return biome_platforms.subsurface(pygame.Rect(320 + offset, 0, 80, 70))

        biome_platforms = platformsheet.subsurface(
            pygame.Rect(0, order.index(biome) * 70, 640, 70)
        ).convert_alpha()
        season_x = {
            "greenleaf": 0 + offset,
            "leaf-bare": 160 + offset,
            "leaf-fall": 320 + offset,
            "newleaf": 480 + offset,
        }

        return biome_platforms.subsurface(
            pygame.Rect(
                season_x[season.lower()],
                0,
                80,
                70,
            )
        )


# CREATE INSTANCE
sprites = Sprites()


def subtract_lineart(surface, mask_surf, bg_color):
    """
    Though I doubt there will be a use-case for this in the future, this is a helper function I wrote to extract the
    semitransparent layer of sparkles from our original StarClan sprites. It requires a mask to work but could probably
    be altered to remove the need. honestly, I just want this in here so that we have it in at least one commit if
    we turn out to need something like this again lol it was AWFUL to figure out
    """
    width, height = surface.get_size()
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)

    bg_r, bg_g, bg_b = bg_color.r, bg_color.g, bg_color.b

    surface.lock()
    overlay.lock()

    for y in range(height):
        for x in range(width):
            r, g, b, a = surface.get_at((x, y))

            # If fully transparent, skip
            if a == 0 or mask_surf.get_at((x, y)).a < 120:
                overlay.set_at((x, y), (r, g, b, a))
                continue

            best_error = float("inf")
            best_color = (0, 0, 0)
            best_alpha = 0

            alpha_steps = 255
            # do a heinous process where we eyeball the alpha
            for step in range(1, alpha_steps + 1):
                alpha = step / alpha_steps

                try:
                    # Recover overlay color for this alpha
                    o_r = (r - (1 - alpha) * bg_r) / alpha
                    o_g = (g - (1 - alpha) * bg_g) / alpha
                    o_b = (b - (1 - alpha) * bg_b) / alpha
                except ZeroDivisionError:
                    continue

                # if it makes no sense, skip
                if not (0 <= o_r <= 255 and 0 <= o_g <= 255 and 0 <= o_b <= 255):
                    continue

                # Simulate the blend & compare
                sim_r = o_r * alpha + bg_r * (1 - alpha)
                sim_g = o_g * alpha + bg_g * (1 - alpha)
                sim_b = o_b * alpha + bg_b * (1 - alpha)

                error = abs(sim_r - r) + abs(sim_g - g) + abs(sim_b - b)

                if error < best_error:
                    best_error = error
                    best_color = (int(round(o_r)), int(round(o_g)), int(round(o_b)))
                    best_alpha = int(round(alpha * 255))

            # Set recovered overlay color
            overlay.set_at((x, y), (*best_color, best_alpha))

    surface.unlock()
    overlay.unlock()
    return overlay
