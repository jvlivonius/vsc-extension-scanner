"""
HTML Report Components.

Individual components for building HTML security reports.
"""

from ..base_component import BaseComponent
from .header import HeaderComponent
from .controls import ControlsComponent
from .footer import FooterComponent
from .charts import ChartComponents
from .detail_view import DetailViewComponent
from .overview_table import OverviewTableComponent
from .module_breakdown import ModuleBreakdownComponent
from .security_notes import SecurityNotesComponent
from .score_contributions import ScoreContributionsComponent

__all__ = [
    "BaseComponent",
    "HeaderComponent",
    "ControlsComponent",
    "FooterComponent",
    "ChartComponents",
    "DetailViewComponent",
    "OverviewTableComponent",
    "ModuleBreakdownComponent",
    "SecurityNotesComponent",
    "ScoreContributionsComponent",
]
