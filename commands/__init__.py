from .check_cmd import register as register_check
from .filters_cmd import register as register_filters
from .help_cmd import register as register_help
from .monitoring_cmd import register as register_monitoring
from .resetfilters_cmd import register as register_resetfilters
from .start_cmd import register as register_start
from .unknown_cmd import register as register_unknown


def register_handlers(bot):
    register_start(bot)
    register_help(bot)
    register_filters(bot)
    register_resetfilters(bot)
    register_check(bot)
    register_monitoring(bot)

    # Ultimo para que no interfiera con otros comandos
    register_unknown(bot)
