class Style:
    RESET            = '\033[0m'  

    BOLD             = "\033[1m"
    DIM              = "\033[2m"
    UNDERLINED       = "\033[4m"  
    BLINK            = "\033[5m"  # Text will blink. Won't work on all systems.
    REVERSE          = "\033[7m"  # Background color is changed. Not the text.
    HIDDEN           = "\033[8m"  # Hidden but still able to be copied.

    RESET_BOLD       = "\033[21m"
    RESET_DIM        = "\033[22m"
    RESET_UNDERLINED = "\033[24m"
    RESET_BLINK      = "\033[25m"
    RESET_REVERSE    = "\033[27m"
    RESET_HIDDEN     = "\033[28m"

    DEFAULT          = "\033[39m"
    GREY             = "\033[30m"
    RED              = "\033[31m"
    GREEN            = "\033[32m"
    YELLOW           = "\033[33m"
    PURPLE           = "\033[34m"
    MAGENTA          = "\033[35m"
    CYAN             = "\033[36m"
    OFF_WHITE        = "\033[37m"
    ASHY_NAVY_BLUE   = "\033[90m"
    LIGHT_RED        = "\033[91m"
    LIGHT_GREEN      = "\033[92m"
    LIGHT_YELLOW     = "\033[93m"
    LIGHT_PURPLE     = "\033[94m"
    LIGHT_MAGENTA    = "\033[95m"
    LIGHT_CYAN       = "\033[96m"
    WHITE            = "\033[97m"


RESET = Style.RESET
MAGENTA = Style.MAGENTA
YELLOW = Style.YELLOW
RED = Style.RED
GREEN = Style.GREEN