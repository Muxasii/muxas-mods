import logging
import pygame
import ujson

from scripts.cat.enums import CatAge, CatGroup
from scripts.cat.sprites.load_sprites import sprites
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure import constants, image_cache
from scripts.game_structure.game import game_setting_get
from scripts.ui.scale import ui_scale_dimensions
from scripts.cat.pelts import Pelt

logger = logging.getLogger(__name__)

def generate_sprite(
    cat,
    life_state=None,
    scars_hidden=False,
    acc_hidden=False,
    always_living=False,
    disable_sick_sprite=False,
) -> pygame.Surface:
    """
    Generates the sprite for a cat, with optional arguments that will override certain things.

    :param life_state: sets the age life_stage of the cat, overriding the one set by its age. Set to string.
    :param scars_hidden: If True, doesn't display the cat's scars. If False, display cat scars.
    :param acc_hidden: If True, hide the accessory. If false, show the accessory.
    :param always_living: If True, always show the cat with living lineart
    :param disable_sick_sprite: If true, never use the not_working lineart.
                    If false, use the cat.not_working() to determine the no_working art.
    """

    def _recolor_lineart(
                sprite, color=None, source: pygame.Surface = None
            ) -> pygame.Surface:
                """
                Helper function to set the appropriate lineart color for the living status of the cat
                :param sprite: lineart to recolor
                :param color: color to apply to all pixels
                :param source: source surface of same size as sprite to use instead of color
                :return:
                """
                if not dead:
                    return sprite

                if color is None and source is None:
                    raise ValueError(
                        "Must provide either `color` or `source` for _recolor_lineart"
                    )

                out = sprite.copy()
                if color:
                    pixel_array = pygame.PixelArray(out)
                    pixel_array.replace((0, 0, 0), color, distance=0)
                    del pixel_array
                    return out

                width, height = sprite.get_size()
                for x in range(width):
                    for y in range(height):
                        if sprite.get_at((x, y)) == pygame.Color(0, 0, 0):
                            color = source.get_at((x, y))
                            sprite.set_at((x, y), color)
                return out

    def create_base(cat_sprite, colors, markings, cat, tortie_colors=None, tortie_markings=None):
        """
        Function for creating the cat base.
        :param cat_sprite: 
        """
        finished_sprite = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )

        finished_sprite.blit(sprites.sprites['base' + cat_sprite], (0, 0))
        base_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        base_tint.fill(colors["base"])
        finished_sprite.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        for layer_name, layer in markings.items():
            if layer_name.lower() == "none":
                return 
            finished_sprite.blit(create_layer(cat_sprite, layer_name, layer, colors))

        if (cat.name in ["Tortie", "Calico"] and not tortie_colors):
            tortie_sprite = pygame.Surface(
                (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
            )
            tortie_sprite.blit(create_base(cat_sprite, tortie_colors, tortie_markings, cat, tortie=True))
            tortie_sprite.blit(sprites.sprites["tortiemask" + cat.tortie_marking + cat_sprite], (0, 0),  special_flags=pygame.BLEND_RGBA_MULT)

            finished_sprite.blit(tortie_sprite)

        if not tortie_colors:
            # TINTS
            if (
                cat.tint != "none"
                and cat.tint in sprites.cat_tints["tint_colours"]
            ):
                # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
                # entire surface. To get around this, we first blit the tint onto a white background to dull it,
                # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.tint]))
                finished_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            if (
                cat.tint != "none"
                and cat.tint in sprites.cat_tints["dilute_tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.tint]))
                finished_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            # draw white patches
            if cat.white_patches is not None:
                white_patches = sprites.sprites[
                    "white" + cat.white_patches + cat_sprite
                ].copy()

                # Apply tint to white patches.
                if (
                    cat.white_patches_tint != "none"
                    and cat.white_patches_tint
                    in sprites.white_patches_tints["tint_colours"]
                ):
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(
                        tuple(
                            sprites.white_patches_tints["tint_colours"][
                                cat.white_patches_tint
                            ]
                        )
                    )
                    white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                finished_sprite.blit(white_patches, (0, 0))

            # draw vit & points

            if cat.points:
                points = sprites.sprites["white" + cat.points + cat_sprite].copy()
                if (
                    cat.white_patches_tint != "none"
                    and cat.white_patches_tint
                    in sprites.white_patches_tints["tint_colours"]
                ):
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(
                        tuple(
                            sprites.white_patches_tints["tint_colours"][
                                cat.white_patches_tint
                            ]
                        )
                    )
                    points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                finished_sprite.blit(points, (0, 0))

            if cat.vitiligo:
                finished_sprite.blit(
                    sprites.sprites["white" + cat.vitiligo + cat_sprite], (0, 0)
                )

        return finished_sprite

    def create_accessories(cat_sprite, accessories, acc_hidden):
        finished_sprite = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )
        # draw accessories
        from scripts.cat.pelts import Pelt

        if not acc_hidden and accessories:
            categories = [
                "collar_accessories",
                "tail_accessories",
                "body_accessories",
                "head_accessories",
            ]
            for category in categories:
                for accessory in accessories:
                    if accessory in getattr(Pelt, category):
                        if accessory in Pelt.plant_accessories:
                            sprite_name = f"{sprites.PLANT_DATA['spritesheet']}{accessory}{cat_sprite}"
                            finished_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )
                        elif accessory in Pelt.wild_accessories:
                            sprite_name = f"{sprites.WILD_DATA['spritesheet']}{accessory}{cat_sprite}"
                            finished_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )
                        elif accessory in Pelt.collar_accessories:
                            sprite_name = f"{sprites.COLLAR_DATA['spritesheet']}{accessory}{cat_sprite}"
                            finished_sprite.blit(
                                _recolor_lineart(
                                    sprites.sprites[sprite_name],
                                    lineart_color,
                                    gradient_surface,
                                ),
                                (0, 0),
                            )

        return finished_sprite

    def create_layer(cat_sprite, layer_name, layer, colors, layer_sprite_override=None, prefix="", disable_suffix=False):
        #print(f"Creating layer: {layer_name} - {layer}")
        finished_layer = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )
        
        if layer_sprite_override:
            layer_sprite = layer_sprite_override
        else:
            layer_sprite = layer["sprite_name"]
        overfur_sprite = layer["overfur"]
        underfur_sprite = layer["underfur"]

        cat_layer_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        cat_layer_tint.fill(colors[layer_name])

        cat_layer = sprites.sprites[prefix + layer_sprite + cat_sprite].copy()
        cat_layer.blit(cat_layer_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        if underfur_sprite:
            underfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            if disable_suffix:
                underfur_tint.fill(colors[layer_name])
            else:
                underfur_tint.fill(colors[f"{layer_name}_underfur"])

            underfur = sprites.sprites[prefix + underfur_sprite + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            underfur.blit(sprites.sprites[prefix + layer_sprite + cat_sprite], special_flags=pygame.BLEND_RGBA_MULT)
            cat_layer.blit(underfur)

        if overfur_sprite:
            overfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            if disable_suffix:
                overfur_tint.fill(colors[layer_name])
            else:
                overfur_tint.fill(colors[f"{layer_name}_overfur"])

            overfur = sprites.sprites[prefix + overfur_sprite + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            overfur.blit(sprites.sprites[prefix + layer_sprite + cat_sprite], special_flags=pygame.BLEND_RGBA_MULT)

            cat_layer.blit(overfur)
        
        cat_layer.blit(sprites.sprites[prefix + layer_sprite + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        finished_layer.blit(cat_layer, (0, 0))

        return finished_layer

    def create_eyes(cat_sprite, colors):
        finished_sprite = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )
        eye_base = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        eye_base.fill(colors["base"])

        eye_s = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        eye_s.fill(colors["shade"])

        eye_p = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        eye_p.fill(colors["pupil"])

        # base
        eyes = sprites.sprites[f'eye_layers' + 'base' + cat_sprite].copy()
        eyes.blit(eye_base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        eyes.blit(sprites.sprites[f'eye_layers' + 'base' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # draw eye shade
        eye_shade = sprites.sprites[f'eye_layers' + 'shade' + cat_sprite].copy()
        eye_shade.blit(eye_s, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        eye_shade.blit(sprites.sprites[f'eye_layers' + 'shade' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # draw pupil
        eye_pupil = sprites.sprites[f'eye_layers' + 'pupil' + cat_sprite].copy()
        eye_pupil.blit(eye_p, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        eye_pupil.blit(sprites.sprites[f'eye_layers' + 'pupil' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # combine
        eyes.blit(eye_shade, (0, 0))
        eyes.blit(eye_pupil, (0, 0))

        finished_sprite.blit(eyes, (0, 0))

        return finished_sprite
    
    ############################
    #     Sprite Generation    #
    ############################

    poses: list = sprites.POSE_DATA["poses"]
    sprite_poses = {x: str(poses.index(x)) for x in poses}

    if life_state is not None:
        age = life_state
    else:
        age = cat.age

    if always_living:
        dead = False
    else:
        dead = cat.dead

    # setting the cat_sprite (bc this makes things much easier)

    # sick sprites
    if (
        not disable_sick_sprite
        and cat.not_working()
        and age != CatAge.NEWBORN
        and constants.CONFIG["cat_sprites"]["sick_sprites"]
    ):
        if age in (CatAge.KITTEN, CatAge.ADOLESCENT):
            cat_sprite = sprite_poses["sick_young0"]
        else:
            cat_sprite = sprite_poses["sick_adult0"]

    # paralyzed sprites
    elif cat.pelt.paralyzed and age != CatAge.NEWBORN:
        if age in (CatAge.KITTEN, CatAge.ADOLESCENT):
            cat_sprite = sprite_poses["para_young0"]
        else:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites["para_adult"]]

    # default sprites
    else:
        if constants.CONFIG["fun"]["all_cats_are_newborn"]:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites["newborn"]]
        else:
            cat_sprite = sprite_poses[cat.pelt.cat_sprites[age]]

    # init variables
    cat_colors = {}
    eye_colors = {}
    cat_colors_tortie = {}
    cat_layers_tortie = {}
    cat_layers = {}
    
    # obtain eye colors
    eye_colors[cat.pelt.eye_colour] = sprites.eye_colors["eye_colors"][cat.pelt.eye_colour]
    if cat.pelt.eye_colour2 is not None:
        eye_colors[cat.pelt.eye_colour2] = sprites.eye_colors["eye_colors"][cat.pelt.eye_colour2]

    # obtain pelt colors
     # tortie and calico use the pelt.name which is smelly
    if cat.pelt.name not in ['Tortie', 'Calico']:
        if cat.pelt.name.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
            cat_marking = "SINGLECOLOUR"
        else:
            cat_marking = cat.pelt.name.upper()

        
        color_type = sprites.pelt_layers[cat_marking]["color_type"]
        if age in sprites.pelt_colors[color_type]:
            cat_colors = sprites.pelt_colors[color_type][cat.pelt.colour][age]
        else: 
            cat_colors = sprites.pelt_colors[color_type][cat.pelt.colour]["default"]

        cat_layers = sprites.pelt_layers[cat_marking]["layers"]
    else:
        if cat.pelt.tortie_base.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
            cat_marking = "SINGLECOLOUR"
        else:
            cat_marking = cat.pelt.tortie_base.upper()
        
        if cat.pelt.tortie_pattern.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
            tortie_pattern = "SINGLECOLOUR"
        else:
            tortie_pattern = cat.pelt.tortie_pattern.upper()
        
        color_type = sprites.pelt_layers[cat_marking]["color_type"]

        if age in sprites.pelt_colors[color_type]:
            cat_colors = sprites.pelt_colors[color_type][cat.pelt.colour][age]
        else: 
            cat_colors = sprites.pelt_colors[color_type][cat.pelt.colour]["default"]

        color_type = sprites.pelt_layers[tortie_pattern]["color_type"]
        if age in sprites.pelt_colors[color_type]:
            cat_colors_tortie = sprites.pelt_colors[color_type][cat.pelt.tortie_colour][age]
        else: 
            cat_colors_tortie = sprites.pelt_colors[color_type][cat.pelt.tortie_colour]["default"]

        cat_layers = sprites.pelt_layers[cat_marking]["layers"]
        cat_layers_tortie = sprites.pelt_layers[tortie_pattern]["layers"]

    new_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    
    # generating the sprite
    try:
        # setting the lineart color to override on accessories & missing bits
        lineart_color = (
            pygame.Color(
                constants.CONFIG["cat_sprites"]["lineart_color_sc"]
                if cat.status.group == CatGroup.STARCLAN
                else constants.CONFIG["cat_sprites"]["lineart_color_df"]
            )
            if cat.status.group != CatGroup.UNKNOWN_RESIDENCE
            else None
        )

        gradient_surface = (
            sprites.sprites["line_ur_gradient" + cat_sprite]
            if dead and cat.status.group == CatGroup.UNKNOWN_RESIDENCE
            else None
        )

        #-----------------
        # create base
        #-----------------
        new_sprite.blit(create_base(cat_sprite, cat_colors, cat_layers, cat.pelt, cat_colors_tortie, cat_layers_tortie))

        # draw eye colors
        new_sprite.blit(create_eyes(cat_sprite, eye_colors[cat.pelt.eye_colour]))
        if cat.pelt.eye_colour2:
            eyes2 = pygame.Surface(
                (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
            )
            eyes2.blit(create_eyes(cat_sprite, eye_colors[cat.pelt.eye_colour2]))
            eyes2.blit(
                sprites.sprites["heterochromiamask" + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )
            new_sprite.blit(eyes2)

        # draw scars
        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.missing_part_scars:
                    sprite_name = f"{sprites.SCAR_MISSING_PART_DATA['spritesheet']}{scar}{cat_sprite}"
                    new_sprite.blit(
                        _recolor_lineart(
                            sprites.sprites[sprite_name],
                            lineart_color,
                            gradient_surface,
                        ),
                        (0, 0),
                        special_flags=blendmode,
                    )


        # draw lineart & shading
        if game_setting_get("shaders") and not dead:
            new_sprite.blit(
                sprites.sprites["shaders" + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGB_MULT,
            )
            new_sprite.blit(sprites.sprites["lighting" + cat_sprite], (0, 0),
                special_flags=pygame.BLEND_RGB_ADD)

        if not dead:
            new_sprite.blit(sprites.sprites["lineart" + cat_sprite], (0, 0))
        elif cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
            new_sprite.blit(sprites.sprites["lineart_ur" + cat_sprite], (0, 0))
        elif cat.status.group == CatGroup.DARK_FOREST:
            new_sprite.blit(sprites.sprites["lineart_df" + cat_sprite], (0, 0))
        elif dead:
            new_sprite.blit(sprites.sprites["lineart_sc" + cat_sprite], (0, 0))

        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        new_sprite.blit(sprites.sprites["skin" + cat.pelt.skin + cat_sprite], (0, 0))

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.scars2:
                    new_sprite.blit(
                        sprites.sprites["scars" + scar + cat_sprite],
                        (0, 0),
                        special_flags=blendmode,
                    )
        
        #-----------------
        # create accessories
        #-----------------

        new_sprite.blit(create_accessories(cat_sprite, cat.pelt.accessory, acc_hidden))

        #-----------------
        # fading fog
        #-----------------
        if (
            cat.pelt.opacity <= 97
            and not cat.prevent_fading
            and get_clan_setting("fading")
            and dead
        ):
            stage = "0"
            if 80 >= cat.pelt.opacity > 45:
                # Stage 1
                stage = "1"
            elif cat.pelt.opacity <= 45:
                # Stage 2
                stage = "2"

            new_sprite.blit(
                sprites.sprites["fademask" + stage + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

            if cat.status.group == CatGroup.DARK_FOREST:
                temp = sprites.sprites["fadedf" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            else:
                temp = sprites.sprites["fadestarclan" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp

        #-----------------
        # flip that cat
        #-----------------
        if cat.pelt.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

    except (TypeError, KeyError):
        logger.exception("Failed to load sprite")
        print(cat)

        # Placeholder image
        new_sprite = image_cache.load_image(
            f"sprites/error_placeholder.png"
        ).convert_alpha()

    return new_sprite

def update_sprite(cat):
    # First, check if the cat is faded.
    if cat.faded:
        # Don't update the sprite if the cat is faded.
        return

    # apply
    cat.sprite = generate_sprite(cat)
    # update class dictionary
    cat.all_cats[cat.ID] = cat


def update_mask(cat):
    if cat.faded or cat.dead:
        # should never need a mask since they can't appear on the Clan screen
        cat.sprite_mask = None
        return

    val = pygame.mask.from_surface(
        pygame.transform.scale(cat.sprite, ui_scale_dimensions((50, 50))), threshold=250
    )

    inflated_mask = pygame.Mask(
        (
            val.get_size()[0] + 10,
            val.get_size()[1] + 10,
        )
    )
    inflated_mask.draw(val, (5, 5))
    for _ in range(3):
        outline = inflated_mask.outline()
        for point in outline:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    try:
                        inflated_mask.set_at((point[0] + dx, point[1] + dy), 1)
                    except IndexError:
                        continue
    cat.sprite_mask = inflated_mask