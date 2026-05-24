# # old hsr
# GESTURE_KEY_MAP = {
#     'Pointing_Up': 'w',
#     'Open_Palm': 'space',
#     'Thumb_Up': 'a',
#     'Thumb_Down': 'd',
#     'ILoveYou': 'q',
#     'Victory': 'e'
# }


# # For Arknights: Endfield
# GESTURE_KEY_MAP = {
#     'Pointing_Up': 'w',
#     'Open_Palm': 'space',
#     'Thumb_Up': 'a',
#     'Thumb_Down': 'd',
#     'ILoveYou': '1',
#     'Victory': 'e'
# }

# template
DEFAULT_KEY_MAP = {
    'one': 'none',
    'two_up': 'none',
    'two_up_inverted': 'none',
    'three': 'none',
    'three2': 'none',
    'three3': 'none',
    'four': 'none',

    'like': 'none',       # Thumbs up
    'dislike': 'none',    # Thumbs down
    'ok': 'none',         # OK sign
    'peace': 'none',
    'peace_inverted': 'none',
    'rock': 'none',       # Rock on sign
    'holy': 'none',

    'call': 'none',
    'mute': 'none',
    'stop': 'none',
    'stop_inverted': 'none',
    'three_gun': 'none',

    'fist': 'none',
    'grip': 'none',
    'palm': 'none',

    'thumb_index': 'none',	# L sign
    'middle_finger': 'none',
    'little_finger': 'none',

    # based on the model's confusion matrix, these gestures have poor performance and are not recommended to be used
    'grabbing': 'none',
    'point': 'none',

}

WUTHERING_KEY_MAP = {
	# for movement control
    # controller is just a placeholder term
    'two_up': 'controller',
    'two_up_inverted': 'controller',
    'three_gun': 'controller',

    #dodge + jump
    'like': 'shift',       # Thumbs up
    'palm': 'space',

    #teammates
    'one': '1',
    'peace': '2',
    'three': '3',
    'four': '4',

    # abilities
    'rock': 'e',       # Rock on sign
    'call': 'r',
    'dislike': 'q',    # Thumbs down

    # misc
    'ok': 'f',         # OK sign
    'grip': 'alt',
    'thumb_index': 'left_click',	# L sign
    'little_finger': 'right_click',
    'holy': 'esc',
    'three2': 'tab',
    'peace_inverted': 't',

    #aiming
    'three3': 'g',

    'fist': 'none',
    'stop_inverted': 'none',

    # reset
    'stop': 'none',

    # not recommended to use
    'mute': 'none', # too easy to accidentally trigger
    'point': 'none', # confused with other gestures
    'grabbing': 'none', # confused with other gestures 
    'middle_finger': 'none', # offensive
}

GESTURE_PROFILES = {
	'template': DEFAULT_KEY_MAP,
    'game': WUTHERING_KEY_MAP
}