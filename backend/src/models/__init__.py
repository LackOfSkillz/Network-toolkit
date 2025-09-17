"""Import all model modules so SQLAlchemy mappers are registered when the package is imported."""
from . import user  # noqa: F401
from . import network_configuration  # noqa: F401
from . import network_device  # noqa: F401
from . import firewall_rule  # noqa: F401
from . import audit_log  # noqa: F401
from . import compliance_report  # noqa: F401
from . import diagnostic_test  # noqa: F401
from . import credential_group  # noqa: F401
from . import saved_view  # noqa: F401
from . import dashboard_widget  # noqa: F401
from . import custom_compliance_policy  # noqa: F401
