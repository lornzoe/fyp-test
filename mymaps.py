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
    'two_up': 'controller',
    'two_up_inverted': 'controller',
    'three_gun': 'controller',

	# for minor cursor control
    'one': '1',
    'point': 'none',

    'three': '3',
    'three2': 'none',
    'three3': 'none',
    'four': '4',

    'like': 'none',       # Thumbs up
    'dislike': 'none',    # Thumbs down
    'ok': 'F',         # OK sign
    'peace': '2',
    'peace_inverted': 'none',
    'rock': 'none',       # Rock on sign
    'holy': 'esc',

    'call': 'none',
    'mute': 'none',
    'stop': 'none',
    'stop_inverted': 'none',

    'fist': 'none',
    'grabbing': 'none',
    'grip': 'alt',
    'palm': 'none',

    'thumb_index': 'left_click',	# L sign
    'middle_finger': 'none',
    'little_finger': 'none',

    # not recommended to use
}

GESTURE_PROFILES = {
	'template': DEFAULT_KEY_MAP,
    'game': WUTHERING_KEY_MAP
}